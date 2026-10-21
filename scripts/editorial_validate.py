"""Independent source/coverage and pixel validation; detailed evidence stays local."""
import collections
import hashlib
import html
import json
import re
from html.parser import HTMLParser
from pathlib import Path

import fitz
from PIL import Image, ImageChops, ImageStat

from editorial_convert import MARKER, checked_source, digest, get_lines, math_risk, safe_output, write_json, source_annotations, boundary_findings


class Blocks(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.blocks={}
        self.stack=[]
        self.active=None
        self.skip=0

    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        previous=self.active
        if 'data-source-block' in a:
            self.active=a['id']
            if self.active in self.blocks:raise ValueError('Duplicate rendered block')
            self.blocks[self.active]={'kind':a['data-source-kind'],'text':''}
        ignored=tag=='small' and 'aria-label' in a
        if ignored:self.skip+=1
        if tag not in ('meta','img','link','br','input','hr','source'):
            self.stack.append((tag,previous,ignored))

    def handle_endtag(self,tag):
        if self.stack:
            _,previous,ignored=self.stack.pop()
            self.active=previous
            if ignored:self.skip-=1

    def handle_data(self,data):
        if self.active and not self.skip:self.blocks[self.active]['text']+=data


def normalized(text):
    return re.sub(r'\s+',' ',text).strip()


_CANONICAL={}
_RENDER_DIFFERENCES=[]


def check_pixels(pdf,page_number,bbox,asset,path,output,page_asset):
    if digest(path.read_bytes())!=asset['sha256']:raise ValueError(f'Changed asset: {path.name}')
    page=pdf[page_number-1]
    if _CANONICAL.get('page')!=page_number:
        _CANONICAL.clear();_CANONICAL.update(page=page_number,image=Image.open(output/page_asset['path']).convert('RGB'))
    bounds=(fitz.Rect(bbox)&page.rect)*fitz.Matrix(asset['dpi']/72,asset['dpi']/72)
    expected=_CANONICAL['image'].crop(tuple(bounds.irect))
    with Image.open(path) as image:
        if image.size!=expected.size or image.convert('RGB').tobytes()!=expected.tobytes():
            raise ValueError(f'Source pixel mismatch: {path.name}')
        if digest(image.convert('RGB').tobytes())!=asset['pixelSha256']:raise ValueError('Changed canonical pixels')
    if asset['path']==page_asset['path']:
        pix=page.get_pixmap(matrix=fitz.Matrix(asset['dpi']/72,asset['dpi']/72),alpha=False,annots=True)
        fresh=Image.frombytes('RGB',(pix.width,pix.height),pix.samples)
        difference=ImageChops.difference(expected,fresh)
        mean=sum(ImageStat.Stat(difference).mean)/3
        maximum=ImageChops.lighter(ImageChops.lighter(difference.getchannel(0),difference.getchannel(1)),difference.getchannel(2))
        significant=sum(maximum.histogram()[33:])/max(1,maximum.width*maximum.height)
        if mean>.1 or significant>.002:raise ValueError(f'Fresh source rendering differs beyond antialias tolerance: PDF {page_number}, mean {mean}')
        _RENDER_DIFFERENCES.append({'pdfPage':page_number,'meanChannelDifference':mean,'fractionPixelsOver32':significant})


def validate(source,output):
    output=safe_output(output)
    evidence=checked_source(source)
    data=json.loads((output/'chapter.json').read_text('utf-8'))
    if data['marker']!=MARKER or data['source']['sha256']!=evidence['sha256'] or data['publicationAuthorization']!='not-established':
        raise ValueError('Incorrect edition or publication boundary')
    expected=[p for p in evidence['pages'] if p['printedPage'] is None or 13<=p['printedPage']<=111]
    actual=[{'pdfPage':p['pdfPage'],'printedPage':p['printedPage']} for p in data['pages']]
    if actual!=expected:raise ValueError('Missing, duplicated or reordered source page')
    pdf=fitz.open(source)
    page_assets={p['pdfPage']:p['originalPage'] for p in data['pages']}
    counts=collections.Counter()
    flags=[]
    source_glyphs=0
    source_lines=0
    semantic_glyphs=0
    numbered=set()
    for region in data['regions']:
        if boundary_findings(pdf[region['pdfPage']-1],region['bbox']):raise ValueError(f'A source word/image crosses crop boundary: {region["id"]}')
        if region.get('figureNumber'):numbered.add(region['figureNumber'])
        counts['regions:'+region['kind']]+=1
        check_pixels(pdf,region['pdfPage'],region['bbox'],region['asset'],output/region['asset']['path'],output,page_assets[region['pdfPage']])
        for asset in region.get('cellAssets',[]):
            check_pixels(pdf,region['pdfPage'],asset['bbox'],asset,output/asset['path'],output,page_assets[region['pdfPage']])
            counts['tableCellAssets']+=1
        for flag in region['reviewFlags']:
            flags.append({'pdfPage':region['pdfPage'],'printedPage':region['printedPage'],'regionId':region['id'],'flag':flag})
    if numbered!=set(range(1,48)):raise ValueError('A numbered original illustration is missing')
    for page in data['pages']:
        n=page['pdfPage']
        fresh=get_lines(pdf[n-1],n)
        if source_annotations(pdf[n-1])!=page['pdfAnnotations']:raise ValueError('An original PDF comment/highlight is missing')
        counts['originalPdfAnnotations']+=len(page['pdfAnnotations'])
        if fresh!=page['lines']:raise ValueError(f'Source glyphs, fonts or positions changed on PDF {n}')
        original_text=pdf[n-1].get_text(sort=False)
        if digest(original_text.encode())!=page['sourceTextSha256']:raise ValueError('Unmodified source text audit failed')
        by_line={l['id']:l for l in fresh}
        coverage={l['id']:[0]*len(l['glyphs']) for l in fresh}
        owners={b['id']:b for b in page['blocks']}
        parser=Blocks()
        reader=(output/'reader'/f'pdf-{n:03}.html').read_text('utf-8')
        parser.feed(reader)
        if MARKER not in reader or 'editorial-publication-status' not in reader:raise ValueError('Private edition marker missing')
        for block in page['blocks']:
            counts['blocks:'+block['kind']]+=1
            pieces=[]
            for lid,a,b in block['lineRanges']:
                if lid not in coverage or not 0<=a<=b<=len(coverage[lid]):raise ValueError('Invalid source character range')
                for i in range(a,b):
                    coverage[lid][i]+=1
                    if page['glyphOwners'][lid][i]!=block['id']:raise ValueError('Source owner mismatch')
                pieces.append(''.join(g['c'] for g in by_line[lid]['glyphs'][a:b]))
            if '\n'.join(pieces)!=block['sourceText']:raise ValueError('Source text silently edited')
            if block['kind']!='page-furniture' and block['id'] not in parser.blocks:raise ValueError('A source block is absent from preview')
            if block['kind'] in ('paragraph','list-item','heading'):
                if normalized(parser.blocks[block['id']]['text'])!=normalized(block['sourceText']):raise ValueError(f'HTML text changed: {block["id"]}')
                semantic_glyphs+=sum(b-a for _,a,b in block['lineRanges'])
                if any(0xe000<=ord(c)<=0xf8ff or c=='\ufffd' for c in block['sourceText']):
                    raise ValueError(f'Undecoded special-font equation was exposed as text: {block["id"]}')
            if 'asset' in block:
                check_pixels(pdf,n,block['bbox'],block['asset'],output/block['asset']['path'],output,page_assets[n])
        for lid,values in coverage.items():
            if any(v!=1 for v in values):raise ValueError(f'Lost or duplicated source glyph: {lid}')
            rebuilt=''.join(by_line[lid]['glyphs'][i]['c'] for i in range(len(values)))
            if rebuilt!=by_line[lid]['text']:raise ValueError('Lossless source reconstruction failed')
        if any(not im['owners'] for im in page['imageObjects']):raise ValueError(f'An original image object is absent from responsive flow: PDF {n}')
        check_pixels(pdf,n,[0,0,page['width'],page['height']],page['originalPage'],output/page['originalPage']['path'],output,page_assets[n])
        if not (output/'compare'/f'pdf-{n:03}.html').exists():raise ValueError('Missing side-by-side source comparison')
        source_glyphs+=page['sourceGlyphCount'];source_lines+=page['sourceLineCount']
        counts['sourceImageObjects']+=len(page['imageObjects'])
        counts['sourceVectorObjects']+=len(page['vectorObjects'])
        if n%10==0:print(f'Validated through PDF {n}: exact glyph coverage and original pixels',flush=True)
    ids={q['id'] for q in json.loads((Path(__file__).resolve().parents[1]/'public/data/questions.json').read_text('utf-8')) if q.get('is_published') is True}
    for note in data['annotations']:
        page=next(p for p in data['pages'] if p['pdfPage']==note['pdfPage'])
        line=next(l for l in page['lines'] if l['id']==note['lineId'])
        if line['text'][note['start']:note['end']]!=note['quote'] or note['count']!=len(set(note['questionIds'])) or not set(note['questionIds'])<=ids:
            raise ValueError('Annotation changed source text or included unpublished questions')
    report={'schemaVersion':1,'marker':MARKER,'editionId':data['source']['editionId'],
            'sourceSha256':data['source']['sha256'],'publicationAuthorization':'not-established',
            'physicalPages':len(data['pages']),'numberedPages':99,'unnumberedInsertions':1,
            'printedRange':[13,111],'sourceTextLines':source_lines,'sourceGlyphs':source_glyphs,
            'semanticTextGlyphs':semantic_glyphs,'numberedFigures':len(numbered),'counts':dict(counts),
            'checks':{'allSourcePagesInOrder':True,'exactSourceCharactersAndFonts':True,'everyGlyphOwnedExactlyOnce':True,
                      'nativeHTMLTextUnchanged':True,'allImageObjectsAccountedFor':True,
                      'completeWordAndImageCropBoundaries':True,'originalPdfAnnotationsRetained':True,
                      'losslessCropsMatchCanonicalPagePixels':True,'freshSourceRenderWithinAntialiasTolerance':True,'allNumberedFiguresPresent':True,
                      'allComparisonPagesPresent':True,'publishedOnlyAnnotations':True},
            'reviewFlags':flags,'reviewFlagCounts':dict(collections.Counter(f['flag'] for f in flags)),
            'renderTolerance':{'maxMeanChannelDifference':.1,'maxFractionPixelsOver32':.002,
                               'observedMaxMean':max(r['meanChannelDifference'] for r in _RENDER_DIFFERENCES)},
            'unanchoredConcepts':data['unanchoredConcepts'],
            'fidelity':'Complete local source preservation, with responsive semantic text and original pixel-preserved complex regions. Paragraph/region classification and manual crop semantics remain reviewable; automated coverage does not certify a final publication-quality transcription.',
            'semanticLimitations':['Raster-only tables retain the original cell contents visually; complete accessible cell transcription requires manual review.',
                                   'Special-font and spatial mathematics use exact original renderings rather than guessed Unicode or invented MathML.',
                                   'Automatic fragment/vector boundaries and paragraph segmentation are explicitly review candidates, not silently certified.']}
    write_json(output/'validation-report.json',report)
    summary={k:v for k,v in report.items() if k!='reviewFlags'}
    write_json(output/'validation-summary.json',summary)
    rows=''.join(f'<tr><td>{html.escape(k)}</td><td>{html.escape(str(v))}</td></tr>' for k,v in counts.items())
    flag_rows=''.join(f'<tr><td>{f["printedPage"]}</td><td>{f["pdfPage"]}</td><td><a href="assets.html#{f["regionId"]}">{html.escape(f["regionId"])}</a></td><td>{html.escape(f["flag"])}</td></tr>' for f in flags)
    (output/'validation.html').write_text(f'<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><meta name="robots" content="noindex,nofollow"><link rel="stylesheet" href="editorial.css"><title>Local source fidelity audit</title><main class="review-index"><a href="index.html">← Editorial workspace</a><h1>Completeness and fidelity audit</h1><p>{html.escape(report["fidelity"])}</p><p>100 physical pages · 99 printed pages · 47 numbered figures · {source_glyphs:,} source characters accounted for exactly once.</p><table>{rows}</table><h2>Uncertainties retained for review</h2><ul>{"".join(f"<li>{html.escape(t)}</li>" for t in report["semanticLimitations"])}</ul><p>These flags do not remove source material: full original regions and source-page renders remain available for comparison.</p><table><thead><tr><th>Printed</th><th>PDF</th><th>Region</th><th>Review flag</th></tr></thead><tbody>{flag_rows}</tbody></table></main></html>','utf-8')
    print(json.dumps({k:v for k,v in summary.items() if k not in ('semanticLimitations','fidelity','unanchoredConcepts')},indent=2),flush=True)
    return report
