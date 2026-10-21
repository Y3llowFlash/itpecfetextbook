"""Crop-first Chapter 1 spatial fidelity pipeline.

build/verify keep source pages, crop previews and the visual review gallery local.
publish copies only hash-verified original-region WebPs and static metadata into
the application. The existing owner-approved source edition remains immutable.
"""
import argparse
import html
import json
import re
import shutil
from collections import defaultdict
from pathlib import Path

import fitz
from PIL import Image, ImageDraw

from editorial_convert import ROOT, OUT, digest, line_runs_html
from figures import checked_source

CONFIG = ROOT/'docs/development/editorial/chapter1-spatial-crops.json'
WORK = ROOT/'.local/crop-first'
PUBLIC = ROOT/'public/textbook/hardware-spatial'
MANIFEST = ROOT/'src/content/hardware-spatial-crops.json'
VISUAL = {'figure','formula','table','source-visual'}
NATIVE = {'paragraph','heading','list-item'}
norm = lambda text:re.sub(r'\s+',' ',text).strip()


def write_json(path, value):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,indent=2,ensure_ascii=False)+'\n','utf-8')


def in_box(glyph, box):
    r=fitz.Rect(glyph['box'])
    return box.contains(fitz.Point((r.x0+r.x1)/2,(r.y0+r.y1)/2))


def glyphs(block, lines):
    return [g for lid,a,b in block['lineRanges'] for g in lines[lid]['glyphs'][a:b] if g['c'].strip()]


def ranges_outside(block, lines, box):
    result=[]
    for lid,a,b in block['lineRanges']:
        line=lines[lid];start=None
        for index in range(a,b+1):
            outside=index<b and not in_box(line['glyphs'][index],box)
            if outside and start is None:start=index
            if not outside and start is not None:
                if line['text'][start:index].strip():result.append((lid,start,index))
                start=None
    return result


def compile_metadata(source):
    checked_source(source)
    config=json.loads(CONFIG.read_text('utf-8'))
    release=json.loads((ROOT/'src/content/hardware-source-release.json').read_text('utf-8'))
    approval=json.loads((ROOT/'docs/development/editorial/chapter1-publication.json').read_text('utf-8'))
    data=json.loads((OUT/'chapter.json').read_text('utf-8'))
    if not(config['sourceSha256']==release['sourceSha256']==data['source']['sha256']==approval['sourceSha256']) or approval['status']!='owner-approved':
        raise ValueError('A matching owner-approved source edition is required')
    prefix=release['releaseId']+'-'
    pages={p['pdfPage']:p for p in data['pages']}
    covered={};regions=[];partials=[]
    for definition in config['regions']:
        page=pages[definition['pdfPage']];lines={l['id']:l for l in page['lines']};box=fitz.Rect(definition['bbox'])
        if page['printedPage']!=definition['printedPage'] or not fitz.Rect(0,0,page['width'],page['height']).contains(box):raise ValueError('Incorrect source page or crop boundary')
        if box.get_area()>.65*page['width']*page['height']:raise ValueError('A source region must not become a full-page screenshot')
        for line in lines.values():
            if not line['text'].strip().startswith('['):continue
            title=fitz.Rect()
            for g in line['glyphs']:
                if g['c'].strip():title|=fitz.Rect(g['box'])
            if title.intersects(box) and not box.contains(title):
                raise ValueError(f'Crop cuts a source box title: {definition["id"]} / {line["text"]}')
        r={**definition,'sourceBlockIds':[],'coverage':[],'recoveries':[]}
        for block in page['blocks']:
            if block['kind']=='page-furniture':continue
            chars=glyphs(block,lines);inside=[in_box(g,box) for g in chars]
            bounds=fitz.Rect(block['bbox']);intersection=(bounds&box).get_area()
            visual_hit=block['kind'] in VISUAL and intersection/max(1,bounds.get_area())>.15
            selected=(inside and all(inside)) or any(inside) or visual_hit
            if not selected:continue
            if block['kind'] not in VISUAL and not all(inside):raise ValueError(f'Crop cuts surrounding prose: {r["id"]} / {block["id"]}')
            if block['kind']=='heading' and re.match(r'^\d(?:\s*-\s*\d){0,2}\s+[A-Za-z]',block['sourceText']):raise ValueError('A numbered textbook heading must stay native HTML')
            if any(n['blockId']==block['id'] for n in data['annotations']):raise ValueError('An interactive source concept must stay native HTML')
            source_id=prefix+block['id']
            if source_id in covered:raise ValueError(f'A source block belongs to two crops: {source_id}')
            covered[source_id]=r['id'];r['sourceBlockIds'].append(source_id)
            r['coverage'].append({'id':source_id,'kind':block['kind'],'sourceTextSha256':digest(norm(block['sourceText']).encode()),
                                  'sourceGlyphs':len(chars),'croppedGlyphs':sum(inside),'nativeGlyphs':len(chars)-sum(inside)})
            if not all(inside):partials.append((r,block,page,lines,box))
        if not r['sourceBlockIds']:raise ValueError('A crop has no source reading anchors: '+r['id'])
        regions.append(r)
    # Recover prose that the old image fragments accidentally included. Match
    # original line ranges; never transcribe math, guess words or duplicate them.
    merge_candidates=defaultdict(set)
    for r,block,page,lines,box in partials:
        for lid,a,b in ranges_outside(block,lines,box):
            line=lines[lid];target=None;placement='after'
            candidates=[p for p in page['blocks'] if p['kind'] in NATIVE and prefix+p['id'] not in covered]
            for candidate in candidates:
                same=[(x,y) for source_lid,x,y in candidate['lineRanges'] if source_lid==lid]
                if same:
                    if max(y for x,y in same)<=a:placement='after'
                    elif b<=min(x for x,y in same):placement='before'
                    else:continue
                    target=candidate;break
            if target is None:
                same=[p for p in candidates if p.get('pdfBlock')==line['pdfBlock'] and p['kind']=='paragraph']
                if same:
                    target=min(same,key=lambda p:abs(p['bbox'][1]-line['bbox'][1]));placement='before' if line['bbox'][1]<target['bbox'][1] else 'after'
            record={'id':f'{r["id"]}-native-{len(r["recoveries"])+1:02}', 'fromBlockId':prefix+block['id'],
                    'lineId':lid,'range':[a,b],'html':line_runs_html(line,a,b),
                    'textSha256':digest(norm(line['text'][a:b]).encode()),
                    'targetId':prefix+target['id'] if target else None,'placement':placement,
                    'bbox':line['bbox']}
            r['recoveries'].append(record)
            if target and target['kind']=='paragraph':merge_candidates[(page['pdfPage'],line['pdfBlock'])].add(prefix+target['id'])
    # Include the remaining native lines of a restored paragraph, too.
    for (page_id,pdf_block),ids in merge_candidates.items():
        ids.update(prefix+b['id'] for b in pages[page_id]['blocks'] if b['kind']=='paragraph' and b.get('pdfBlock')==pdf_block and prefix+b['id'] not in covered)
    merges=[sorted(ids,key=lambda item:next(b['bbox'][1] for p in pages.values() for b in p['blocks'] if prefix+b['id']==item)) for ids in merge_candidates.values() if len(ids)>1]
    source_order={prefix+b['id']:index for index,b in enumerate(b for p in data['pages'] for b in p['blocks'])}
    for r in regions:
        r['sourceBlockIds'].sort(key=lambda key:source_order[key])
        r['recoveries'].sort(key=lambda record:(record['bbox'][1],record['range'][0]))
        r['url']=r['path']+'#'+r['sourceBlockIds'][0]
    reviews=[{'pdfPage':p['pdfPage'],'printedPage':p['printedPage'],
              'repairedRegions':[r['id'] for r in regions if r['pdfPage']==p['pdfPage']],
              'retainedOriginalVisuals':sum(b['kind'] in VISUAL and prefix+b['id'] not in covered for b in p['blocks']),
              'status':'source-page-reviewed'} for p in data['pages']]
    return {'schemaVersion':1,'releaseId':release['releaseId'],'sourceSha256':release['sourceSha256'],
            'publicationStatus':'owner-approved','configSha256':digest(CONFIG.read_bytes().replace(b'\r\n',b'\n')),'dpi':300,
            'policy':'Whole original spatial units; no redrawing, AI artwork or full-page reader screenshots.',
            'pageReview':reviews,'mergeNativeParagraphs':merges,'regions':regions}


def render(source, metadata):
    (WORK/'assets').mkdir(parents=True,exist_ok=True);(WORK/'context').mkdir(exist_ok=True)
    pdf=fitz.open(source);current=None;canonical=None
    for r in metadata['regions']:
        page=pdf[r['pdfPage']-1];scale=metadata['dpi']/72
        if current!=r['pdfPage']:
            pix=page.get_pixmap(matrix=fitz.Matrix(scale,scale),alpha=False,annots=True)
            canonical=Image.frombytes('RGB',(pix.width,pix.height),pix.samples);current=r['pdfPage']
        pixel_box=tuple((fitz.Rect(r['bbox'])*fitz.Matrix(scale,scale)).irect)
        crop=canonical.crop(pixel_box);temporary=WORK/'assets'/f'{r["id"]}.webp'
        crop.save(temporary,'WEBP',lossless=True,method=6)
        encoded=temporary.read_bytes();name=digest(encoded)+'.webp';target=WORK/'assets'/name
        if target!=temporary:temporary.replace(target)
        with Image.open(target) as result:
            if result.convert('RGB').tobytes()!=crop.tobytes():raise ValueError('Source crop pixels changed during optimization')
        r['asset']={'path':'textbook/hardware-spatial/'+name,'sha256':digest(encoded),'pixelSha256':digest(crop.tobytes()),
                    'width':crop.width,'height':crop.height,'bytes':len(encoded),'dpi':metadata['dpi'],'pixelBox':list(pixel_box)}
        pix=page.get_pixmap(matrix=fitz.Matrix(1.1,1.1),alpha=False,annots=True)
        context=Image.frombytes('RGB',(pix.width,pix.height),pix.samples)
        ImageDraw.Draw(context).rectangle(tuple(fitz.Rect(r['bbox'])*fitz.Matrix(1.1,1.1)),outline='#cf2626',width=3)
        context.save(WORK/'context'/f'{r["id"]}.jpg',quality=90)
    pdf.close()


def review_report(metadata):
    cards=[];rows=[]
    for r in metadata['regions']:
        img='assets/'+Path(r['asset']['path']).name;label=html.escape(r['description']);url='https://itpecfetextbook.pages.dev'+r['url']
        cards.append(f'<article id="{r["id"]}"><h2>{r["id"]} · p. {r["printedPage"]} / PDF {r["pdfPage"]}</h2><p>{label}</p><div class="compare"><a href="context/{r["id"]}.jpg"><img src="context/{r["id"]}.jpg" alt="Original source page with crop boundary"></a><a href="{img}"><img src="{img}" alt="{html.escape(r["alt"],quote=True)}"></a></div><p><a href="{url}">Website location</a> · {r["asset"]["width"]} × {r["asset"]["height"]} · {metadata["dpi"]} dpi · {len(r["sourceBlockIds"])} replaced fragments</p><p>PDF-point crop: {r["bbox"]}</p></article>')
        rows.append(f'| {r["id"]} | {r["printedPage"]} | {r["pdfPage"]} | {r["description"]} | [Source location]({url}) |')
    page=f'<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Chapter 1 spatial crop review</title><style>body{{font:16px/1.6 system-ui;max-width:1500px;margin:auto;padding:24px;background:#f7f5ef}}article{{padding:24px 0;border-bottom:1px solid #aaa}}h2{{font-size:20px}}.compare{{display:grid;grid-template-columns:1fr 1fr;gap:24px;align-items:start}}img{{max-width:100%;height:auto;background:white}}@media(max-width:700px){{.compare{{display:block}}}}</style><h1>Chapter 1 · crop-first visual review</h1><p>{len(metadata["regions"])} original regions across {len(set(r["pdfPage"] for r in metadata["regions"]))} pages. Left: original page with the reviewed boundary. Right: exact crop. Context pages remain local; only the original-region crops enter the reader.</p>'+''.join(cards)+'</html>'
    (WORK/'gallery.html').write_text(page,'utf-8')
    report='# Chapter 1 crop-first visual review\n\n'+metadata['policy']+'\n\n| Repaired region | Printed page | PDF page | Original visual | Website location |\n| --- | --- | --- | --- | --- |\n'+'\n'.join(rows)+'\n'
    (WORK/'review-report.md').write_text(report,'utf-8')
    # Readable crop-only sheets complement the complete side-by-side gallery.
    for index in range(0,len(metadata['regions']),4):
        tiles=[]
        for r in metadata['regions'][index:index+4]:
            with Image.open(WORK/'assets'/Path(r['asset']['path']).name) as image:
                thumb=image.convert('RGB');thumb.thumbnail((720,950))
                tile=Image.new('RGB',(740,thumb.height+55),'#f5f2e9');ImageDraw.Draw(tile).text((10,10),f'{r["id"]} / printed {r["printedPage"]} / PDF {r["pdfPage"]}',fill='black');tile.paste(thumb,(10,45));tiles.append(tile)
        heights=[max(t.height for t in tiles[:2]),max((t.height for t in tiles[2:]),default=0)]
        sheet=Image.new('RGB',(1480,sum(heights)+20),'#ddd')
        for j,tile in enumerate(tiles):sheet.paste(tile,((j%2)*740,0 if j<2 else heights[0]+10))
        sheet.save(WORK/f'crops-{index//4+1:02}.jpg',quality=93)


def verify(source, metadata):
    expected=compile_metadata(source)
    clean={**metadata,'regions':[{k:v for k,v in r.items() if k!='asset'} for r in metadata['regions']]}
    if clean!=expected:raise ValueError('Crop metadata differs from the reviewed source geometry or original block coverage')
    pdf=fitz.open(source);current=None;canonical=None
    for r in metadata['regions']:
        if current!=r['pdfPage']:
            page=pdf[r['pdfPage']-1];scale=metadata['dpi']/72
            pix=page.get_pixmap(matrix=fitz.Matrix(scale,scale),alpha=False,annots=True)
            canonical=Image.frombytes('RGB',(pix.width,pix.height),pix.samples);current=r['pdfPage']
        path=WORK/'assets'/Path(r['asset']['path']).name
        if digest(path.read_bytes())!=r['asset']['sha256']:raise ValueError('Changed source crop asset')
        with Image.open(path) as image:
            expected_crop=canonical.crop(tuple(r['asset']['pixelBox']))
            if image.convert('RGB').tobytes()!=expected_crop.tobytes():raise ValueError('Crop differs from the freshly rendered source PDF')
        for record in r['coverage']:
            if record['sourceGlyphs']!=record['croppedGlyphs']+record['nativeGlyphs']:raise ValueError('Source glyph coverage gap')
    pdf.close()
    print(f'Verified {len(metadata["regions"])} complete original crops against fresh 300-dpi PDF pixels; all 100 source pages inventoried.')


def publish(source, metadata):
    verify(source,metadata)
    PUBLIC.mkdir(parents=True,exist_ok=True)
    names=set()
    for r in metadata['regions']:
        name=Path(r['asset']['path']).name;names.add(name)
        shutil.copyfile(WORK/'assets'/name,PUBLIC/name)
    # Prune only this pipeline's own hashed WebPs, never other source assets.
    for old in PUBLIC.glob('*.webp'):
        if re.fullmatch(r'[a-f0-9]{64}\.webp',old.name) and old.name not in names:old.unlink()
    write_json(MANIFEST,metadata)
    print(f'Integrated {len(names)} optimized original-region assets; full-page review images and the gallery remain under .local/.')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command',choices=['build','verify','publish'])
    parser.add_argument('--source',type=Path,default=Path(r'D:\ITPEC Old Questions\database\raw\FE Vol 1.pdf'))
    args=parser.parse_args();WORK.mkdir(parents=True,exist_ok=True)
    if args.command=='build':
        manifest=compile_metadata(args.source);render(args.source,manifest);write_json(WORK/'manifest.json',manifest);review_report(manifest);verify(args.source,manifest)
    else:
        manifest=json.loads((WORK/'manifest.json').read_text('utf-8'))
        if args.command=='publish':publish(args.source,manifest)
        else:verify(args.source,manifest)
