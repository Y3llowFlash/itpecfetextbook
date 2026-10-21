"""Render only the local source edition. This module is never imported by Astro."""
import html
import json
import re
from pathlib import Path

from editorial_convert import ROOT, MARKER, line_runs_html, center_inside, rect, write_json, safe_output

CSS = '''
:root{--paper:#fbfaf6;--surface:#f1eee4;--ink:#29303a;--muted:#5e6268;--rule:#d8d5cb;--yellow:#fff0a9}*{box-sizing:border-box}body{margin:0;background:var(--paper);color:var(--ink);font:16px/1.6 Arial,sans-serif}a{color:inherit}a:focus-visible,button:focus-visible,summary:focus-visible{outline:3px solid #305c9d;outline-offset:4px}.masthead{padding:18px 24px;border-bottom:1px solid var(--rule);display:flex;gap:18px;justify-content:space-between;align-items:center}.brand{font-weight:bold;text-decoration:none}.editorial-status{font-size:12px;max-width:44ch;color:var(--muted)}.layout{display:grid;grid-template-columns:220px minmax(0,1fr) 250px;min-height:100vh}.chapter-nav{padding:24px 16px;border-right:1px solid var(--rule);font-size:13px;overflow-wrap:anywhere}.chapter-nav nav,.companion>div{position:sticky;top:16px;max-height:95vh;overflow:auto}.chapter-nav a{display:block;text-decoration:none;padding:7px 8px;min-height:36px}.chapter-nav a:hover{background:var(--surface)}.chapter-nav .level-3{font-weight:bold;margin-top:12px}.chapter-nav .level-4{padding-left:20px}.chapter-nav .level-2{font-weight:bold;font-size:15px}.chapter-nav [aria-current]{background:var(--yellow)}main{min-width:0;padding:36px clamp(20px,4vw,64px)}.reader{max-width:730px;margin:auto}.reader-body{font:22px/1.7 Georgia,serif;overflow-wrap:anywhere}.reader-body p{margin:0 0 1.2em}.reader-body h2,.reader-body h3,.reader-body h4{line-height:1.3;margin:1.6em 0 .7em;scroll-margin-top:32px}.reader-body h2{font-size:1.65em}.reader-body h3{font-size:1.35em}.reader-body h4{font:600 1.02em/1.4 Arial,sans-serif}.source-badge{display:block;font:12px/1.5 Arial,sans-serif;color:var(--muted);margin:8px 0 24px}.page-nav{display:flex;justify-content:space-between;gap:20px;font:14px/1.5 Arial,sans-serif;margin:28px 0}.reader figure{margin:28px 0;padding:12px;background:var(--surface);border:1px solid var(--rule);border-radius:4px}.reader figure img{display:block;max-width:100%;height:auto;margin:auto}.reader figcaption{font:13px/1.6 Arial,sans-serif;color:var(--muted);margin-top:12px}.reader figcaption a{display:inline-block;min-height:30px}.visual-scroll{overflow:auto}.visual-scroll img{min-width:0}.review-tag{font:12px/1.4 Arial,sans-serif;background:#fff3d1;color:#5c471f;padding:5px 8px;display:inline-block}.source-list{list-style:none;padding-left:1em;margin:0 0 1.2em}.source-list li{margin-bottom:12px}.source-table{overflow:auto;margin:24px 0;font:17px/1.5 Arial,sans-serif}.source-table table{border-collapse:collapse;min-width:100%;width:max-content;max-width:none}.source-table th,.source-table td{border:1px solid #8e8c83;padding:8px 12px;max-width:230px;min-width:40px;vertical-align:top}.source-table th{background:#f5dce8;font-weight:normal}.source-table .cell-image{max-width:230px;max-height:130px;width:auto;height:auto}.companion{border-left:1px solid var(--rule);padding:28px 20px;font-size:14px}.companion h2{font:28px/1.2 Georgia,serif}.practice-link{display:block;padding:12px 0;border-bottom:1px solid var(--rule);text-decoration:none}.practice-link small{display:block;color:var(--muted)}.concept-highlight{background:var(--yellow);color:#24282d;border-bottom:1px solid #bf9f28;text-decoration:none;padding:1px 3px}.concept-highlight small{font:12px Arial,sans-serif;white-space:nowrap}.review-tools{font:13px Arial,sans-serif;display:flex;flex-wrap:wrap;gap:16px;margin:16px 0 30px}.comparison{max-width:1800px;margin:auto;padding:20px}.compare-grid{display:grid;grid-template-columns:1fr 1fr;gap:20px}.compare-grid img{width:100%;height:auto}.compare-grid iframe{width:100%;height:88vh;border:1px solid var(--rule);background:var(--paper)}.source-page-image{position:sticky;top:10px}.comparison select{font-size:16px;padding:8px;max-width:100%}.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,310px),1fr));gap:20px}.cards article{padding:16px;background:white;border:1px solid var(--rule);overflow-wrap:anywhere}.cards img{max-width:100%;height:auto}.cards h2{font-size:17px}.cards p{font-size:13px}.review-index{max-width:1000px;margin:40px auto;padding:20px}.review-index h1{font:42px/1.1 Georgia,serif}.mobile-nav{display:none}.sr-only{position:absolute;width:1px;height:1px;overflow:hidden;clip-path:inset(50%)}sup{font-size:.72em;vertical-align:super;line-height:0}footer{padding:24px;border-top:1px solid var(--rule);font-size:13px;color:var(--muted)}[data-source-block]{scroll-margin-top:32px}body.embedded .masthead,body.embedded .chapter-nav,body.embedded .companion,body.embedded .mobile-nav,body.embedded footer{display:none}body.embedded .layout{display:block}body.embedded main{padding:24px}
@media(max-width:1100px){.layout{grid-template-columns:200px minmax(0,1fr)}.companion{grid-column:2;border-left:0;border-top:1px solid var(--rule)}.companion>div{position:static;max-height:none}}@media(max-width:700px){.masthead{padding:14px 16px;align-items:flex-start}.editorial-status{max-width:28ch}.layout{display:block}.chapter-nav{display:none}.mobile-nav{display:block;padding:12px 16px;border-bottom:1px solid var(--rule)}.mobile-nav nav{max-height:50vh;overflow:auto}.mobile-nav a{display:block;padding:8px;font-size:14px}.companion{padding:24px 16px}.companion>div{position:static}.reader-body{font-size:18px}.reader-body h2{font-size:1.5em}main{padding:24px 16px}.reader figure{padding:8px;margin:24px 0}.compare-grid{display:block}.source-page-image{position:static}.compare-grid iframe{height:85vh}.review-index h1{font-size:32px}.source-table{font-size:16px}}'''

JS = '''
const key='itpecTextbook:editorial:source:v1';
if(new URLSearchParams(location.search).get('embedded')==='1')document.body.classList.add('embedded');
const article=document.querySelector('[data-editorial-reader]');
const capture=()=>{if(!article)return;const blocks=[...article.querySelectorAll('[data-source-block]')];const block=[...blocks].reverse().find(b=>b.getBoundingClientRect().top<=100)||blocks[0];if(!block)return;try{localStorage.setItem(key,JSON.stringify({pdfPage:Number(article.dataset.pdfPage),blockId:block.id,offset:block.getBoundingClientRect().top,source:article.dataset.sourceSha}));}catch{}};
if(article&&!document.body.classList.contains('embedded')){let timer;addEventListener('scroll',()=>{clearTimeout(timer);timer=setTimeout(capture,250)},{passive:true});addEventListener('pagehide',capture);for(const link of article.querySelectorAll('.concept-highlight'))link.addEventListener('click',capture);if(new URLSearchParams(location.search).get('resume')==='1'){try{const saved=JSON.parse(localStorage.getItem(key));if(saved?.source===article.dataset.sourceSha&&saved.pdfPage===Number(article.dataset.pdfPage)){const block=document.getElementById(saved.blockId);if(block)requestAnimationFrame(()=>scrollTo(0,scrollY+block.getBoundingClientRect().top-saved.offset));}}catch{}}}
const resume=document.querySelector('[data-editorial-resume]');if(resume){try{const saved=JSON.parse(localStorage.getItem(key));if(saved&&Number.isInteger(saved.pdfPage)&&saved.pdfPage>=18&&saved.pdfPage<=117&&/^[a-zA-Z0-9:_-]+$/.test(saved.blockId)){resume.href=`reader/pdf-${String(saved.pdfPage).padStart(3,'0')}.html?resume=1#${saved.blockId}`;resume.hidden=false;}}catch{}}
const select=document.querySelector('[data-page-select]');if(select)select.addEventListener('change',()=>location.href=select.value);
'''


def esc(value):
    return html.escape(str(value), quote=True)


def original_ref(page):
    return f'Original textbook · p. {page["printedPage"]}' if page['printedPage'] is not None else 'Unnumbered inserted page · physical PDF 83'


def heading_inventory(dataset):
    return [{'pdfPage': p['pdfPage'], 'printedPage': p['printedPage'], 'blockId': b['id'],
             'level': b['level'], 'text': b['sourceText']}
            for p in dataset['pages'] for b in p['blocks'] if b['kind'] == 'heading']


def annotations(dataset):
    concepts = json.loads((ROOT / 'src/content/concepts.json').read_text('utf-8'))
    bank = json.loads((ROOT / 'public/data/questions.json').read_text('utf-8'))
    eligible = {q['id'] for q in bank if q.get('is_published') is True}
    anchors = {
        'cache-memory': (70, 72, r'cache memory'),
        'radix-conversion': (26, 28, r'radix conversion'),
        'floating-point': (37, 40, r'floating point numbers'),
        'signed-shifts': (43, 45, r'arithmetic shift'),
        'cpu-registers': (47, 47, r'[Rr]egister'),
        'interrupts': (59, 60, r'[Ii]nterrupt'),
        'bus-transfer': (48, 48, r'[Bb]us'),
        'logic-gates': (61, 64, r'logic circuit'),
        'disk-access': (83, 85, r'access time'),
        'defragmentation': (85, 85, r'defragmentation'),
        'usb-interface': (107, 108, r'USB'),
    }
    result, missing = [], []
    for concept in concepts:
        ids = sorted(set(concept['questionIds']) & eligible)
        anchor = anchors.get(concept['id'])
        found = None
        if anchor:
            first, last, pattern = anchor
            for page in dataset['pages']:
                if page['printedPage'] is None or not first <= page['printedPage'] <= last:
                    continue
                lines = {line['id']: line for line in page['lines']}
                for block in page['blocks']:
                    if block['kind'] not in ('paragraph', 'list-item'):
                        continue
                    for line_id, a, b in block['lineRanges']:
                        match = re.search(pattern, lines[line_id]['text'][a:b], re.I)
                        if match:
                            found = {'conceptId': concept['id'], 'title': concept['title'], 'blockId': block['id'],
                                     'pdfPage': page['pdfPage'], 'printedPage': page['printedPage'], 'lineId': line_id,
                                     'start': a+match.start(), 'end': a+match.end(), 'quote': match[0],
                                     'questionIds': ids, 'count': len(ids),
                                     'url': f'https://itpecfetextbook.pages.dev/practice/{concept["id"]}/',
                                     'status': 'source-quote-anchor; existing concept mapping retained'}
                            break
                    if found:
                        break
                if found:
                    break
        if found:
            result.append(found)
        else:
            missing.append({'conceptId': concept['id'], 'reason': 'No exact reviewed source-phrase anchor selected; no source text invented or changed'})
    dataset['annotations'], dataset['unanchoredConcepts'] = result, missing
    return concepts


def annotated_line(line, a, b, notes):
    notes = [n for n in notes if n['lineId'] == line['id'] and a <= n['start'] and n['end'] <= b]
    if not notes:
        return line_runs_html(line, a, b)
    pieces, cursor = [], a
    for note in notes:
        pieces.append(line_runs_html(line, cursor, note['start']))
        pieces.append(f'<a class="concept-highlight" data-concept="{esc(note["conceptId"])}" href="{esc(note["url"])}" target="_blank" rel="noopener">{line_runs_html(line,note["start"],note["end"])}<small aria-label="{note["count"]} published questions"> ↗ {note["count"]}</small></a>')
        cursor = note['end']
    pieces.append(line_runs_html(line, cursor, b))
    return ''.join(pieces)


def semantic_table(region, page, output):
    """Reflow genuine source grids; render undecodable cells exactly as source pixels."""
    if region.get('origin') != 'strict-source-grid':
        return None
    cells = region['cells']
    xs = sorted(set(round(v, 1) for c in cells for v in (c[0], c[2])))
    ys = sorted(set(round(v, 1) for c in cells for v in (c[1], c[3])))
    # The strict finder can expose near-coincident borders. Do not invent a grid.
    if any(b-a < 2 for a,b in zip(xs,xs[1:])) or any(b-a < 2 for a,b in zip(ys,ys[1:])):
        return None
    rows = []
    for row_number, y in enumerate(ys[:-1]):
        rendered = []
        for cell_index, cell in enumerate(cells):
            if abs(cell[1]-y) > .2:
                continue
            x0, x1 = min(range(len(xs)), key=lambda i: abs(xs[i]-cell[0])), min(range(len(xs)), key=lambda i: abs(xs[i]-cell[2]))
            y1 = min(range(len(ys)), key=lambda i: abs(ys[i]-cell[3]))
            pieces = []
            for line in sorted(page['lines'],key=lambda l:(l['bbox'][1],l['bbox'][0])):
                inside=[i for i,g in enumerate(line['glyphs']) if center_inside(g['box'],cell)]
                if inside:
                    pieces.append(line_runs_html(line,min(inside),max(inside)+1))
            text = '<br>'.join(pieces)
            unknown = any(center_inside(g['box'],cell) and (0xE000<=ord(g['c'][0])<=0xF8FF or g['c']=='\ufffd') for line in page['lines'] for g in line['glyphs'] if g['c'])
            raster_cell = any(center_inside(im['bbox'],cell) for im in page['imageObjects'])
            if unknown or raster_cell:
                # Pixel cell is generated by the conversion stage, never a replacement drawing.
                cell_file = output / 'cells' / f'{region["id"]}-{cell_index:03}.png'
                if not cell_file.exists():
                    raise ValueError(f'Original source table cell is missing: {cell_file.name}')
                text = f'<img class="cell-image" src="../cells/{cell_file.name}" alt="Original source cell; transcription requires review">'
            tag = 'th' if row_number == 0 else 'td'
            rendered.append((x0, f'<{tag} colspan="{max(1,x1-x0)}" rowspan="{max(1,y1-row_number)}"{(" scope=\"col\"" if tag=="th" else "")}>{text}</{tag}>'))
        rows.append('<tr>'+''.join(t for _,t in sorted(rendered))+'</tr>')
    return '<div class="source-table"><table aria-label="Original source table">'+''.join(rows)+'</table></div>'


def page_body(dataset, page, output):
    lines = {line['id']: line for line in page['lines']}
    regions = {r['id']:r for r in dataset['regions']}
    result = []
    for block in page['blocks']:
        if block['kind'] == 'page-furniture':
            continue
        attrs = f'id="{block["id"]}" data-source-block data-source-kind="{block["kind"]}"'
        if 'asset' in block:
            parts=[regions[r] for r in block['regionIds']]
            caption = '\n'.join(r['caption']['text'] for r in parts if r.get('caption'))
            alt = caption.strip() or 'Original source visual; labels and notation preserved from the PDF'
            grid = next((r for r in parts if r['kind']=='table' and r.get('origin')=='strict-source-grid'),None)
            table = semantic_table(grid,page,output) if grid and len(parts)==1 else None
            display_width=round(block['asset']['width']*72/block['asset']['dpi']*1.4)
            visual = table if table else f'<div class="visual-scroll" tabindex="0" role="region" aria-label="Original figure; scroll horizontally to read labels"><a href="../{block["asset"]["path"]}" target="_blank" rel="noopener"><img src="../{block["asset"]["path"]}" style="width:{display_width}px;max-width:none" width="{block["asset"]["width"]}" height="{block["asset"]["height"]}" alt="{esc(alt)}" loading="lazy"></a></div>'
            result.append(f'<figure {attrs}>{visual}<figcaption><span>{esc(original_ref(page))} · PDF {page["pdfPage"]}</span><br><a href="../{block["asset"]["path"]}" target="_blank" rel="noopener">Open original region at full size</a>{("<span class=\"review-tag\">Editorial review flagged</span>" if block.get("reviewFlags") else "")}</figcaption></figure>')
        else:
            value=' '.join(annotated_line(lines[l],a,b,dataset['annotations']) for l,a,b in block['lineRanges'])
            if block['kind']=='heading':
                level=block.get('level') or 4
                result.append(f'<h{level} {attrs}>{value}</h{level}>')
            elif block['kind']=='list-item':
                result.append(f'<ul class="source-list"><li {attrs}>{value}</li></ul>')
            else:
                result.append(f'<p {attrs}>{value}</p>')
    return ''.join(result)


def shell(title, body, prefix='../'):
    return f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width"><meta name="robots" content="noindex,nofollow"><meta name="editorial-publication-status" content="not-authorized"><title>{esc(title)}</title><link rel="stylesheet" href="{prefix}editorial.css"><script src="{prefix}editorial.js" defer></script></head><body data-local-source-edition="{MARKER}">{body}</body></html>'


def build_preview(dataset, output):
    output=safe_output(output)
    concepts=annotations(dataset)
    outline=heading_inventory(dataset)
    eligible={q['id'] for q in json.loads((ROOT/'public/data/questions.json').read_text('utf-8')) if q.get('is_published') is True}
    companion='<div><p class="source-badge">YOUR STUDY COMPANION</p><h2>Read the source.<br>Try an exam question.</h2><p>Reviewed practice opens in a new tab. This local source reader stays open at your position.</p>'
    for c in concepts:
        count=len(set(c['questionIds'])&eligible)
        companion+=f'<a class="practice-link" href="https://itpecfetextbook.pages.dev/practice/{c["id"]}/" target="_blank" rel="noopener">{esc(c["title"])}<small>{count} published {"question" if count==1 else "questions"} ↗</small></a>'
    companion+='<p><a href="https://itpecfetextbook.pages.dev/progress/" target="_blank" rel="noopener">Existing progress and Google account ↗</a></p><p class="source-badge">Local source reading is separate from published-edition progress until release authorization.</p></div>'
    (output/'reader').mkdir(exist_ok=True)
    for index,page in enumerate(dataset['pages']):
        n=page['pdfPage']
        nav='<nav aria-label="Original chapter structure"><a href="../index.html">Chapter 1 · Hardware</a>'
        for h in outline:
            if h['level']>3:
                continue
            nav+=f'<a class="level-{h["level"]}" href="pdf-{h["pdfPage"]:03}.html#{h["blockId"]}"{(" aria-current=\"page\"" if h["pdfPage"]==n else "")}>{esc(h["text"].strip())}</a>'
        nav+='</nav>'
        prev=dataset['pages'][index-1] if index else None
        following=dataset['pages'][index+1] if index+1<len(dataset['pages']) else None
        links='<nav class="page-nav" aria-label="Source reading order">'
        if prev:links+=f'<a rel="prev" href="pdf-{prev["pdfPage"]:03}.html">← {esc(original_ref(prev))}</a>'
        if following:links+=f'<a rel="next" href="pdf-{following["pdfPage"]:03}.html">{esc(original_ref(following))} →</a>'
        links+='</nav>'
        body=f'<header class="masthead"><a class="brand" href="../index.html">ITPEC FE · Source edition</a><span class="editorial-status">LOCAL EDITORIAL PREVIEW<br>Reproduced source · publication not authorized</span></header><details class="mobile-nav"><summary>Original chapter navigation</summary>{nav}</details><div class="layout"><aside class="chapter-nav">{nav}</aside><main><article class="reader" data-editorial-reader data-pdf-page="{n}" data-source-sha="{dataset["source"]["sha256"]}"><h1>Chapter 1 · Hardware</h1><span class="source-badge" title="{esc(dataset["source"]["edition"])}">{esc(original_ref(page))} · {esc(dataset["source"]["edition"])}</span><div class="review-tools"><a href="../compare/pdf-{n:03}.html">Compare with source page</a><a href="../assets.html#pdf-{n:03}">Original asset library</a></div>{links}<div class="reader-body">{page_body(dataset,page,output)}</div>{links}</article></main><aside class="companion" aria-label="Study companion">{companion}</aside></div><footer>Local reproduced source edition. The current public site remains the independently authored fallback. No publication authorization is implied.</footer>'
        (output/'reader'/f'pdf-{n:03}.html').write_text(shell(f'Hardware · {original_ref(page)}',body),'utf-8')
    (output/'compare').mkdir(exist_ok=True)
    for page in dataset['pages']:
        n=page['pdfPage']
        options=''.join(f'<option value="pdf-{p["pdfPage"]:03}.html"{(" selected" if p["pdfPage"]==n else "")}>{esc(original_ref(p))} / PDF {p["pdfPage"]}</option>' for p in dataset['pages'])
        body=f'<main class="comparison"><p><a href="../index.html">← Editorial workspace</a></p><h1>PDF versus digital reading</h1><label>Source page <select data-page-select>{options}</select></label><p>{esc(original_ref(page))} · physical PDF {n}. Compare original text, reading order, figures, table cells and formulas. <a href="../reader/pdf-{n:03}.html">Open responsive reader</a></p><div class="compare-grid"><section><h2>Original PDF rendering</h2><a href="../{page["originalPage"]["path"]}" target="_blank" rel="noopener"><img class="source-page-image" src="../{page["originalPage"]["path"]}" width="{page["originalPage"]["width"]}" height="{page["originalPage"]["height"]}" alt="Original source page, printed {page["printedPage"]}, PDF {n}"></a></section><section><h2>Responsive digital source</h2><iframe src="../reader/pdf-{n:03}.html?embedded=1" title="Digital source conversion for physical PDF {n}" loading="lazy"></iframe></section></div></main>'
        (output/'compare'/f'pdf-{n:03}.html').write_text(shell(f'Compare PDF {n}',body),'utf-8')
    cards=[]
    comments=[]
    for page in dataset['pages']:
        for a in page.get('pdfAnnotations',[]):
            content=a['info'].get('content','')
            if content:comments.append(f'<tr><td>{esc(original_ref(page))} / PDF {page["pdfPage"]}</td><td>{esc(a["type"][1])}</td><td>{esc(content)}</td></tr>')
    (output/'source-annotations.html').write_text(shell('Supplied PDF annotations','<main class="review-index"><a href="index.html">← Editorial workspace</a><h1>Annotations already present in the supplied PDF</h1><p>These are source-file comments, separate from textbook prose and from the exam annotation layer. Complete metadata for all highlights/comments is retained in chapter.json.</p><table><thead><tr><th>Source page</th><th>Type</th><th>Original comment</th></tr></thead><tbody>'+''.join(comments)+'</tbody></table></main>',prefix=''),'utf-8')
    for page in dataset['pages']:
        cards.append(f'<h2 id="pdf-{page["pdfPage"]:03}">{esc(original_ref(page))} / PDF {page["pdfPage"]}</h2><div class="cards">')
        for r in dataset['regions']:
            if r['pdfPage']!=page['pdfPage']:continue
            caption=(r.get('caption') or {}).get('text','')
            cards.append(f'<article id="{r["id"]}"><h3>{esc(r["id"])} · {esc(r["kind"])}</h3><a href="{r["asset"]["path"]}" target="_blank" rel="noopener"><img src="{r["asset"]["path"]}" alt="{esc(caption or r["description"])}" width="{r["asset"]["width"]}" height="{r["asset"]["height"]}" loading="lazy"></a><p>{esc(caption or r["description"])}</p><p>PDF points: {r["bbox"]}</p><p class="review-tag">{esc(", ".join(r["reviewFlags"]) or "Boundary retained")}</p><p><a href="compare/pdf-{page["pdfPage"]:03}.html">Compare source placement</a></p></article>')
        cards.append('</div>')
    (output/'assets.html').write_text(shell('Original source asset library','<main class="review-index"><a href="index.html">← Editorial workspace</a><h1>Original source asset library</h1><p>Local reproduced material. No replacement diagrams. Uncertain boundaries/transcriptions are explicitly flagged.</p>'+''.join(cards)+'</main>',prefix=''),'utf-8')
    outline_html=''.join(f'<li><a href="reader/pdf-{h["pdfPage"]:03}.html#{h["blockId"]}">{esc(h["text"].strip())}</a></li>' for h in outline if h['level']<=3)
    (output/'index.html').write_text(shell('Chapter 1 local source conversion',f'<main class="review-index"><p class="review-tag">LOCAL EDITORIAL PREVIEW · PUBLICATION NOT AUTHORIZED</p><h1>Chapter 1 · Hardware<br>Faithful source conversion</h1><p>{esc(dataset["source"]["title"])} · {esc(dataset["source"]["volume"])} · {esc(dataset["source"]["edition"])}</p><p>Complete source text remains in the local structured dataset. Source figures, tables and mathematical notation are retained from original renderings where semantic decoding is uncertain. No summarization or replacement illustrations are used.</p><p><a href="reader/pdf-018.html">Start at printed page 13 →</a></p><p><a data-editorial-resume hidden>Resume local source reading →</a></p><p><a href="compare/pdf-018.html">Side-by-side PDF/digital comparison</a> · <a href="assets.html">Original asset library</a> · <a href="validation.html">Validation and review flags</a></p><h2>Original source structure</h2><ol>{outline_html}</ol><p>The existing public practice screens and account system stay separate. This local edition is not included in Cloudflare output.</p></main>',prefix=''),'utf-8')
    (output/'editorial.css').write_text(CSS,'utf-8')
    (output/'editorial.js').write_text(JS,'utf-8')
    write_json(output/'chapter.json',dataset)
    write_json(output/'page-manifest.json',[{k:p[k] for k in ('pdfPage','printedPage','sourceTextSha256','sourceLineCount','sourceGlyphCount','originalPage')} for p in dataset['pages']])
    write_json(output/'figure-manifest.json',dataset['regions'])
    write_json(output/'outline.json',outline)
    write_json(output/'annotations.json',{'annotations':dataset['annotations'],'unanchored':dataset['unanchoredConcepts']})
    print(f'Local responsive reader and 100 side-by-side comparisons: {output / "index.html"}',flush=True)
