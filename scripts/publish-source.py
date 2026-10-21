"""Create the owner-approved public Chapter 1 reader bundle from its verified local edition.

Builds consume only this committed bundle; raw extraction/review tools stay local.
"""
import html
import json
import re
from pathlib import Path
from PIL import Image

from editorial_convert import ROOT, OUT, digest, write_json
from editorial_preview import annotated_line, semantic_table, original_ref

APPROVAL=ROOT/'docs/development/editorial/chapter1-publication.json'
CONTENT=ROOT/'src/content/source-hardware'
ASSETS=ROOT/'public/textbook/hardware'
MANIFEST=ROOT/'src/content/hardware-source-release.json'


def normalized(text):return re.sub(r'\s+',' ',text).strip()


def publish():
    approval=json.loads(APPROVAL.read_text('utf-8'))
    data=json.loads((OUT/'chapter.json').read_text('utf-8'))
    audit=json.loads((OUT/'validation-summary.json').read_text('utf-8'))
    if approval['status']!='owner-approved' or approval['sourceSha256']!=data['source']['sha256'] or audit['sourceSha256']!=approval['sourceSha256']:
        raise ValueError('An approved, verified source edition is required')
    if not all(audit['checks'].values()) or audit['physicalPages']!=100:raise ValueError('Source validation must pass before release')
    definitions=json.loads((ROOT/'src/content/hardware-lessons.json').read_text('utf-8'))
    concepts=json.loads((ROOT/'src/content/concepts.json').read_text('utf-8'))
    CONTENT.mkdir(parents=True,exist_ok=True);ASSETS.mkdir(parents=True,exist_ok=True)
    prefix=approval['releaseId']+'-'
    regions={r['id']:r for r in data['regions']}
    images={};used_paths=set()

    def asset(relative):
        if relative not in images:
            source=(OUT/relative).resolve()
            if not source.is_relative_to(OUT.resolve()):raise ValueError('Source asset escapes local edition')
            with Image.open(source) as original:
                image=original.convert('RGB')
                name=digest(image.tobytes()+str(image.size).encode())+'.webp'
                target=ASSETS/name
                if not target.exists():image.save(target,'WEBP',lossless=True,method=6)
                with Image.open(target) as encoded:
                    if encoded.convert('RGB').tobytes()!=image.tobytes():raise ValueError('Source pixels changed during optimization')
                images[relative]={'path':f'textbook/hardware/{name}','sha256':digest(target.read_bytes()),
                                 'pixelSha256':digest(image.tobytes()),'width':image.width,'height':image.height,'bytes':target.stat().st_size}
        used_paths.add(images[relative]['path'])
        return '/'+images[relative]['path']

    def notes_for_page(page):return [n for n in data['annotations'] if n['pdfPage']==page['pdfPage']]

    def page_body(page,lesson,emitted_aliases):
        lines={l['id']:l for l in page['lines']}
        result=[];records=[];headings=[]
        notes=notes_for_page(page)
        aliases={}
        for concept in concepts:
            note=next((n for n in notes if n['conceptId']==concept['id']),None)
            if note and concept.get('anchor'):aliases.setdefault(note['blockId'],[]).append(concept['anchor'])
        first=next(b for b in page['blocks'] if b['kind']!='page-furniture')
        for concept in concepts:
            anchored_elsewhere=any(c.get('anchor')==concept.get('anchor') and any(n['conceptId']==c['id'] for n in data['annotations']) for c in concepts)
            if concept['sectionId']==lesson['id'] and concept.get('anchor') and not anchored_elsewhere and concept['id'] in {'bit-masks','three-dimensional-printing'} and page['pdfPage']==next(p['pdfPage'] for p in data['pages'] if p['printedPage']==lesson['pages'][0]):
                aliases.setdefault(first['id'],[]).append(concept['anchor'])
        for block in page['blocks']:
            if block['kind']=='page-furniture':continue
            block_id=prefix+block['id']
            for alias in aliases.get(block['id'],[]):
                if alias not in emitted_aliases:
                    result.append(f'<span id="{html.escape(alias)}" class="source-alias" aria-hidden="true"></span>')
                    emitted_aliases.add(alias)
            attrs=f'id="{block_id}" data-reading-block data-source-block="{block["id"]}" data-source-kind="{block["kind"]}"'
            if 'asset' in block:
                parts=[regions[r] for r in block['regionIds']]
                captions=[r['caption']['text'].strip() for r in parts if r.get('caption')]
                alt=normalized('; '.join(dict.fromkeys(captions)) or '; '.join(dict.fromkeys(r['description'] for r in parts)))
                grid=next((r for r in parts if r['kind']=='table' and r.get('origin')=='strict-source-grid'),None)
                table=semantic_table(grid,page,OUT) if grid and len(parts)==1 else None
                if table:
                    def cell(match):return 'src="'+asset(match[1])+'"'
                    visual=re.sub(r'src="\.\./([^"]+)"',cell,table)
                    visual=visual.replace('Original source cell; transcription requires review','Original table cell, including its source notation')
                else:
                    path=asset(block['asset']['path']);width=round(block['asset']['width']*72/block['asset']['dpi']*1.4)
                    visual=f'<div class="source-visual-scroll" tabindex="0" role="region" aria-label="Figure; scroll horizontally to read all labels"><a href="{path}" target="_blank" rel="noopener" aria-label="Open original figure at full size"><img src="{path}" width="{block["asset"]["width"]}" height="{block["asset"]["height"]}" style="width:{width}px" alt="{html.escape(alt,quote=True)}" loading="lazy" decoding="async"></a></div>'
                result.append(f'<figure {attrs}>{visual}<figcaption>{html.escape(original_ref(page))}</figcaption></figure>')
            else:
                value=' '.join(annotated_line(lines[l],a,b,notes) for l,a,b in block['lineRanges'])
                for note in notes:
                    old=f'class="concept-highlight" data-concept="{note["conceptId"]}"'
                    value=value.replace(old,f'class="concept-highlight" id="concept-{note["conceptId"]}" data-concept="{note["conceptId"]}"')
                value=value.replace('https://itpecfetextbook.pages.dev/practice/','/practice/').replace(' target="_blank" rel="noopener"','')
                value=re.sub(r'<small aria-label="(\d+) published questions"> ↗ (\d+)</small>',lambda m:f'<span class="concept-count" aria-label="{m[1]} published questions"> · {m[1]} {"question" if m[1]=="1" else "questions"}</span>',value)
                if block['kind']=='heading':
                    level=block.get('level') or 4
                    result.append(f'<h{level} {attrs}>{value}</h{level}>')
                    headings.append({'id':block_id,'title':normalized(block['sourceText']),'level':level,'printedPage':page['printedPage']})
                elif block['kind']=='list-item':result.append(f'<ul class="source-list"><li {attrs}>{value}</li></ul>')
                else:result.append(f'<p {attrs}>{value}</p>')
            records.append({'id':block_id,'sourceId':block['id'],'kind':block['kind'],'textSha256':digest(normalized(block['sourceText']).encode()),'regionIds':block.get('regionIds',[])})
        label=f'Original textbook · p. {page["printedPage"]}' if page['printedPage'] is not None else 'Original textbook · unnumbered insertion'
        body=f'<section class="source-page" data-pdf-page="{page["pdfPage"]}" data-printed-page="{page["printedPage"] or "unnumbered"}" aria-label="{label}"><p class="source-badge" id="source-pdf-{page["pdfPage"]:03}">{label}</p>'+''.join(result)+'</section>'
        return body,records,headings

    lessons=[]
    for lesson in definitions:
        first,last=lesson['pages']
        selected=[p for p in data['pages'] if p['printedPage'] is not None and first<=p['printedPage']<=last or p['printedPage'] is None and lesson['slug']=='cpu-and-main-memory']
        bodies=[];pages=[];headings=[];emitted_aliases=set()
        for page in selected:
            body,records,outline=page_body(page,lesson,emitted_aliases);bodies.append(body);headings.extend(outline)
            pages.append({'pdfPage':page['pdfPage'],'printedPage':page['printedPage'],'sourceTextSha256':page['sourceTextSha256'],'blocks':records})
        content=''.join(bodies)+'\n'
        file=CONTENT/f'{lesson["slug"]}.html';file.write_text(content,'utf-8',newline='\n')
        lessons.append({'id':lesson['id'],'slug':lesson['slug'],'path':f'/chapters/hardware/{lesson["slug"]}/','htmlSha256':digest(content.encode()),'pages':pages,'headings':headings})
    for old in ASSETS.glob('*.webp'):
        if f'textbook/hardware/{old.name}' not in used_paths:old.unlink()
    manifest={'schemaVersion':1,'editionId':approval['editionId'],'releaseId':approval['releaseId'],'sourceSha256':approval['sourceSha256'],
              'publicationStatus':'owner-approved','sourceEdition':data['source']['edition'],'physicalPages':100,'printedRange':[13,111],
              'numberedFigures':47,'lessons':lessons,'assets':sorted({a['path']:a for a in images.values()}.values(),key=lambda a:a['path']),
              'annotations':[{'conceptId':n['conceptId'],'blockId':prefix+n['blockId'],'pdfPage':n['pdfPage'],'count':n['count']} for n in data['annotations']],
              'unanchoredConcepts':[n['conceptId'] for n in data['unanchoredConcepts']]}
    write_json(MANIFEST,manifest)
    print(f'Approved source release: {len(lessons)} routes, 100 source pages, {len(manifest["assets"])} lossless WebP assets, {sum(a["bytes"] for a in manifest["assets"]):,} bytes')


if __name__=='__main__':publish()
