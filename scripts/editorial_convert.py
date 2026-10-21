"""Faithful, local-only PDF conversion. No source content is written into src/public/dist."""
import argparse
import collections
import hashlib
import html
import json
import math
import re
from pathlib import Path

import fitz
from PIL import Image

from figures import checked_source

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / '.local/editorial/chapter-1'
CONFIG = ROOT / 'docs/development/editorial/chapter1-regions.json'
PRIOR = ROOT / 'docs/development/figures/chapter1-inventory.json'
MARKER = 'ITPEC_LOCAL_SOURCE_EDITION_V1'
_FRAME = {}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', 'utf-8')


def rect(box):
    return fitz.Rect(box)


def rounded(box):
    return [round(v, 3) for v in box]


def center_inside(box, area):
    b, r = rect(box), rect(area)
    return r.contains(fitz.Point((b.x0 + b.x1) / 2, (b.y0 + b.y1) / 2))


def overlap(box, area):
    b = rect(box)
    if b.width < .2 or b.height < .2:
        b += (-.1,-.1,.1,.1)
    return (b & rect(area)).get_area() / max(b.get_area(), 0.01)


def boundary_findings(page, crop):
    area=rect(crop)
    boxes=[rect(w[:4]) for w in page.get_text('words')]
    boxes.extend(rect(im['bbox']) for im in page.get_image_info())
    # Some PDF objects extend past the physical paper. Preserve the visible
    # portion without requiring impossible expansion beyond the source page.
    boxes=[b&page.rect for b in boxes]
    return [b for b in boxes if not b.is_empty and (area&b).get_area()>0 and not (area+(-.01,-.01,.01,.01)).contains(b)]


def snap_bounds(page, crop):
    area=rect(crop)&page.rect
    for _ in range(100):
        findings=boundary_findings(page,area)
        if not findings:return rounded(area)
        for box in findings:area|=box+(-.5,-.5,.5,.5)
        area&=page.rect
    raise ValueError(f'Inspect unconverged original boundary on PDF {page.number+1}')


def safe_output(output):
    target = output.resolve()
    allowed = (ROOT / '.local/editorial').resolve()
    if target == allowed or not target.is_relative_to(allowed):
        raise ValueError('Reproduced content may only be written beneath .local/editorial/')
    target.mkdir(parents=True, exist_ok=True)
    return target


def get_lines(page, number):
    """Retain every source character, font, position and original PDF block/line index."""
    raw = page.get_text('rawdict', flags=fitz.TEXTFLAGS_RAWDICT & ~fitz.TEXT_PRESERVE_IMAGES)
    result = []
    for b_index, block in enumerate(raw['blocks']):
        if block['type'] != 0:
            continue
        for l_index, line in enumerate(block['lines']):
            spans, glyphs = [], []
            for span in line['spans']:
                start = len(glyphs)
                for char in span['chars']:
                    glyphs.append({'c': char['c'], 'box': rounded(char['bbox']), 'origin': list(char['origin'])})
                spans.append({'start': start, 'end': len(glyphs), 'font': span['font'], 'size': span['size'],
                              'flags': span['flags'], 'color': span['color'], 'bbox': rounded(span['bbox'])})
            text = ''.join(g['c'] for g in glyphs)
            result.append({'id': f'pdf-{number:03}-b{b_index:03}-l{l_index:02}', 'pdfBlock': b_index,
                           'pdfLine': l_index, 'bbox': rounded(line['bbox']), 'direction': list(line['dir']),
                           'text': text, 'glyphs': glyphs, 'spans': spans})
    sizes=collections.Counter()
    for line in result:
        for span in line['spans']:
            if span['size']>=9:
                sizes[round(span['size'])]+=sum(g['c'].isalpha() for g in line['glyphs'][span['start']:span['end']])
    body_size=sizes.most_common(1)[0][0] if sizes else 12
    for line in result:line['bodySize']=body_size
    return result


def is_furniture(line, page_height):
    text, y = line['text'].strip(), line['bbox'][1]
    if not text:
        return 'layout-whitespace'
    if y < 52 and re.fullmatch(r'Chapter\s+1\s+Hardware', text):
        return 'running-header'
    if y > page_height - 60 and re.fullmatch(r'\d{1,3}', text):
        return 'printed-footer'
    return None


def source_annotations(page):
    """Keep the supplied PDF's comments/highlights separate from textbook prose."""
    return [{'xref':a.xref,'type':list(a.type),'bbox':rounded(a.rect),'info':a.info,
             'vertices':[list(v) for v in a.vertices] if a.vertices else None,'colors':a.colors,'flags':a.flags}
            for a in (page.annots() or [])]


def classify_line(line):
    text = line['text'].strip()
    sizes = [span['size'] for span in line['spans'] if span['end'] > span['start']]
    size = max(sizes, default=12)
    if size >= 15.5 and re.match(r'^[1-5]\s', text):
        return 'heading', 2
    body=line.get('bodySize',12)
    if size >= body+1.5 and re.match(r'^\d\s*-\s*\d', text):
        return 'heading', 3
    if size >= body+.7:
        return 'heading', 4
    if re.match(r'^(?:[•●]|\d+\))\s', text):
        return 'list-item', None
    return 'paragraph', None


def math_risk(line):
    text = line['text']
    if any(0xE000 <= ord(c) <= 0xF8FF or c == '\ufffd' for c in text):
        return 'unmapped-special-font-glyph'
    if any('Symbol' in span['font'] or 'MT-Extra' in span['font'] for span in line['spans']):
        return 'special-math-font'
    # Multi-baseline expressions must not be flattened into an incorrect formula.
    if any(span['flags'] & 1 for span in line['spans']) and re.search(r'[=×÷∧∨−+]', text):
        return 'superscript-expression'
    if re.search(r'[=∧∨⊕¬]', text) and (sum(text.count(c) for c in '=∧∨⊕¬') >= 2 or len(text.strip()) < 70):
        return 'spatial-expression'
    return None


def raster(page, bbox, target, dpi=180):
    target.parent.mkdir(parents=True, exist_ok=True)
    bounds = rect(bbox) & page.rect
    key=(id(page.parent),page.number,dpi)
    if _FRAME.get('key')!=key:
        pix=page.get_pixmap(matrix=fitz.Matrix(dpi/72,dpi/72),alpha=False,annots=True)
        _FRAME.clear();_FRAME.update(key=key,image=Image.frombytes('RGB',(pix.width,pix.height),pix.samples))
    pixel_box=(bounds*fitz.Matrix(dpi/72,dpi/72)).irect
    im=_FRAME['image'].crop(tuple(pixel_box))
    im.save(target, 'PNG', optimize=True, dpi=(dpi, dpi))
    return {'file': target.name, 'width': im.width, 'height': im.height,
            'sha256': digest(target.read_bytes()), 'pixelSha256': digest(im.tobytes()), 'dpi': dpi}


def seed_regions(lines, page, printed, number, config):
    """Reviewed source regions only. The old public equivalents are never conversion inputs."""
    result = []
    for definition in config.get('regions', []):
        if definition['pdfPage'] != number:
            continue
        region = {**definition, 'bbox': definition['bbox'][:], 'origin': 'curated-source-region',
                  'reviewFlags': definition.get('reviewFlags', [])[:]}
        if region.get('caption'):
            region['caption'] = {**region['caption'], 'text': '\n'.join(l['text'] for l in lines if l['id'] in region['caption']['lineIds'])}
        result.append(region)
    if printed is None:
        # Keep the inserted screenshot/commentary as an explicitly unnumbered source item.
        images = page.get_image_info()
        for i, image in enumerate(images):
            result.append({'id': f'pdf-{number:03}-insertion-image-{i+1}', 'kind': 'figure',
                           'bbox': rounded(rect(image['bbox']) & page.rect), 'origin': 'source-insertion',
                           'description': 'Original unnumbered inserted image',
                           'reviewFlags': ['unnumbered-editorial-insertion']})
    return result


def table_regions(page, number, seeds):
    result = []
    for i, table in enumerate(page.find_tables(strategy='lines_strict').tables):
        if table.row_count < 2 or table.col_count < 2:
            continue
        if table.bbox[3] - table.bbox[1] < 30:
            continue
        table_id = f'pdf-{number:03}-table-{i+1:02}'
        boxes = [rounded(cell) for cell in table.cells if cell]
        parent = next((s for s in seeds if overlap(table.bbox, s['bbox']) > .8), None)
        result.append({'id': table_id, 'kind': 'table', 'bbox': rounded(rect(table.bbox) + (-2, -2, 2, 2)),
                       'origin': 'strict-source-grid', 'description': 'Original source table',
                       'rows': table.row_count, 'columns': table.col_count, 'cells': boxes,
                       'rowCells': [[rounded(cell) if cell else None for cell in row.cells] for row in table.rows],
                       'extractedCellText': table.extract(), 'parentRegion': parent['id'] if parent else None,
                       'reviewFlags': ['cell-reading-order-requires-review']})
    return result


def merge_regions(regions):
    """Avoid duplicate display: intersecting visual pieces form one original region.

    Subregions remain individually inventoried; no source text is merged or edited.
    """
    groups = []
    for region in sorted(regions, key=lambda r: (r['bbox'][1], r['bbox'][0])):
        touching = [g for g in groups if overlap(region['bbox'], g['bbox']) > .08 or overlap(g['bbox'], region['bbox']) > .08]
        if not touching:
            groups.append({'bbox': region['bbox'][:], 'parts': [region]})
        else:
            first = touching[0]
            first['bbox'] = rounded(rect(first['bbox']) | rect(region['bbox']))
            first['parts'].append(region)
            for other in touching[1:]:
                first['bbox'] = rounded(rect(first['bbox']) | rect(other['bbox']))
                first['parts'].extend(other['parts'])
                groups.remove(other)
    return groups


def complete_images(page, number, regions):
    """All raster objects are accounted for, including tiny labels and equation pieces."""
    additions = []
    for i, image in enumerate(page.get_image_info()):
        bbox = rounded(rect(image['bbox']) & page.rect)
        if any(overlap(bbox, r['bbox']) >= .97 for r in regions + additions):
            continue
        additions.append({'id': f'pdf-{number:03}-image-{i+1:03}', 'kind': 'source-fragment',
                          'bbox': rounded((rect(bbox) + (-2, -2, 2, 2)) & page.rect),
                          'origin': 'unassigned-source-image', 'description': 'Original image or graphic fragment',
                          'reviewFlags': ['automatic-image-boundary-requires-review']})
    # Spatially adjacent fragments of one drawing must be rendered together.
    for _ in range(8):
        groups = merge_regions([{**r, 'bbox': rounded((rect(r['bbox']) + (-3, -3, 3, 3)) & page.rect)} for r in additions])
        if len(groups) == len(additions):
            break
        additions = [{'id': g['parts'][0]['id'], 'kind': 'source-fragment', 'bbox': g['bbox'],
                      'origin': 'clustered-source-images', 'description': 'Original image/connector assembly',
                      'reviewFlags': ['automatic-image-boundary-requires-review']} for g in groups]
    return additions


def math_regions(lines, page, number, regions):
    result, covered_rows = [], []
    for line in lines:
        reason = math_risk(line)
        if not reason or is_furniture(line, page.rect.height):
            continue
        if any(overlap(line['bbox'], r['bbox']) >= .8 for r in regions):
            continue
        cy=(line['bbox'][1]+line['bbox'][3])/2
        if any(abs(cy-y)<5 for y in covered_rows):
            continue
        covered_rows.append(cy)
        siblings=[other for other in lines if abs((other['bbox'][1]+other['bbox'][3])/2-cy)<6 and other['text'].strip()]
        bbox=rect(line['bbox'])
        for other in siblings:bbox |= rect(other['bbox'])
        bbox += (-3,-4,3,4)
        result.append({'id': f'{line["id"]}-equation', 'kind': 'formula', 'bbox': rounded(bbox & page.rect),
                       'origin': 'original-math-preservation', 'description': 'Original equation / mathematical notation',
                       'reviewFlags': [reason, 'semantic-math-transcription-pending']})
    return result


def vector_regions(page, number, existing):
    """Preserve remaining meaningful black strokes. Background/markup stays in the audit."""
    paths = []
    for drawing in page.get_drawings():
        color = drawing.get('color')
        if not color or max(color[:3]) > .8 or max(color[:3])-min(color[:3])>.15 or drawing['rect'].get_area() < 2:
            continue
        if any(overlap(drawing['rect'], r['bbox']) >= .95 for r in existing):
            continue
        # Page borders, heading rules and text decoration do not carry new content.
        if drawing['rect'].height < 3 or drawing['rect'].width < 2:
            continue
        paths.append(drawing)
    clusters = page.cluster_drawings(drawings=paths, x_tolerance=5, y_tolerance=5) if paths else []
    return [{'id': f'pdf-{number:03}-vector-{i+1:02}', 'kind': 'source-vector',
             'bbox': rounded((r + (-4, -4, 4, 4)) & page.rect), 'origin': 'unassigned-source-vector',
             'description': 'Original vector drawing / notation',
             'reviewFlags': ['automatic-vector-boundary-requires-review']}
            for i, r in enumerate(clusters) if r.width > 8 and r.height > 5]


def reflow_around_prose(regions, lines, page):
    """Separate narrative from adjacent math/graphics without rewriting either.

    Full original regions stay in the asset library. Only the responsive flow is
    segmented; genuine image objects are never cut to make room for prose.
    """
    prose_blocks = {l['pdfBlock'] for l in lines
                    if len(l['text'].split()) >= 7 and l['bbox'][0] < 145
                    and l['bbox'][2]-l['bbox'][0] > 240 and not math_risk(l)
                    and not re.match(r'^\s*Figure\s*1-', l['text'])}
    images = [rect(im['bbox']) for im in page.get_image_info()]
    math_rows=[(l['bbox'][1]+l['bbox'][3])/2 for l in lines if math_risk(l)]
    protected = []
    for line in lines:
        if is_furniture(line,page.rect.height) or math_risk(line):
            continue
        if any(abs((line['bbox'][1]+line['bbox'][3])/2-y)<6 for y in math_rows):
            continue
        narrative=line['pdfBlock'] in prose_blocks and (len(line['text'].split())>=3 or (line['bbox'][0]<145 and re.search(r'[A-Za-z]{3}',line['text'])))
        if narrative or (classify_line(line)[0]=='heading' and line['bbox'][0]<145):
            protected.append(line)
    result = []
    for region in regions:
        bands = [region['bbox'][:]]
        caption_ids=(region.get('caption') or {}).get('lineIds',[])
        caption_bottom=max((l['bbox'][3] for l in lines if l['id'] in caption_ids),default=None)
        for line in protected:
            if line['id'] in caption_ids:
                continue
            if region.get('figureNumber') and caption_bottom and line['bbox'][1] <= caption_bottom:
                # Labels / teaching text belonging to a numbered illustration remain together.
                if overlap(line['bbox'],region['bbox'])>.85:
                    continue
            ly0,ly1=line['bbox'][1]-.4,line['bbox'][3]+.4
            next_bands=[]
            for band in bands:
                if not (rect(band)&rect(line['bbox'])).get_area():
                    next_bands.append(band);continue
                if any((im&rect((band[0],ly0,band[2],ly1))).get_area()>1 for im in images):
                    next_bands.append(band);continue
                if band[1]<ly0 and ly0-band[1]>2:next_bands.append([band[0],band[1],band[2],min(ly0,band[3])])
                if band[3]>ly1 and band[3]-ly1>2:next_bands.append([band[0],max(ly1,band[1]),band[2],band[3]])
            bands=next_bands
        for band in bands:
            # Do not render empty slivers left around paragraph/heading borders.
            has_image=any((im&rect(band)).get_area()>2 for im in images)
            has_text=any(l['text'].strip() and any(center_inside(g['box'],band) and g['c'].strip() for g in l['glyphs']) for l in lines)
            if has_image or has_text:
                result.append({**region,'bbox':rounded(band),'flowSegmentation':'narrative-reflow; original full region retained'})
    return result


def line_runs_html(line, start=0, end=None):
    """Preserve characters verbatim; only PDF layout whitespace is reflowed by HTML."""
    end = len(line['glyphs']) if end is None else end
    result = []
    for span in line['spans']:
        a, b = max(start, span['start']), min(end, span['end'])
        if a >= b:
            continue
        value = html.escape(''.join(g['c'] for g in line['glyphs'][a:b]))
        if span['flags'] & 1:
            value = f'<sup>{value}</sup>'
        if span['flags'] & 2:
            value = f'<em>{value}</em>'
        if span['flags'] & 16:
            value = f'<strong>{value}</strong>'
        if span['color'] not in (0, 16777215):
            value = f'<span style="color:#{span["color"]:06x}">{value}</span>'
        result.append(value)
    return ''.join(result)


def flow_blocks(lines, visual_groups, page, number):
    """Every non-whitespace glyph has exactly one owning digital block."""
    blocks, assignments, pending = [], {}, None
    for i, group in enumerate(visual_groups):
        group['id'] = f'pdf-{number:03}-visual-{i+1:03}'
        group['lineRanges'] = []
    for line in sorted(lines, key=lambda l: (round(l['bbox'][1] / 3) * 3, l['bbox'][0])):
        furniture = is_furniture(line, page.rect.height)
        if furniture:
            block_id = f'{line["id"]}-furniture'
            blocks.append({'id': block_id, 'kind': 'page-furniture', 'role': furniture,
                           'bbox': line['bbox'], 'lineRanges': [[line['id'], 0, len(line['glyphs'])]]})
            assignments[line['id']] = [block_id] * len(line['glyphs'])
            continue
        owners = []
        for glyph in line['glyphs']:
            owner = next((g['id'] for g in visual_groups if center_inside(glyph['box'], g['bbox'])), None)
            owners.append(owner)
        assignments[line['id']] = owners[:]
        a = 0
        while a < len(owners):
            owner, b = owners[a], a + 1
            while b < len(owners) and owners[b] == owner:
                b += 1
            if owner:
                next(g for g in visual_groups if g['id'] == owner)['lineRanges'].append([line['id'], a, b])
                pending = None
            else:
                chunk = ''.join(g['c'] for g in line['glyphs'][a:b])
                if not chunk.strip():
                    # Whitespace still has an explicit owner for exact source auditing.
                    owner = f'{line["id"]}-space-{a}'
                    blocks.append({'id': owner, 'kind': 'page-furniture', 'role': 'layout-whitespace',
                                   'bbox': line['bbox'], 'lineRanges': [[line['id'], a, b]]})
                else:
                    kind, level = classify_line(line)
                    last = pending
                    same_source_block = last and last['pdfBlock'] == line['pdfBlock']
                    full_line_continuation = last and last.get('lastRight',0) > 485 and abs(last['bbox'][0]-line['bbox'][0]) < 6
                    heading_continuation = last and kind == 'heading' and last['kind']=='heading' and last.get('level')==level and same_source_block
                    same_baseline=last and abs(line['bbox'][1]-last['lastY'])<2 and 0<=line['bbox'][0]-last.get('lastRight',0)<25 and same_source_block
                    can_continue = last and ((kind == 'paragraph' and last['kind'] in ('paragraph', 'list-item') and (same_source_block or full_line_continuation)) or heading_continuation) and (0 < line['bbox'][1] - last['lastY'] < 25 or same_baseline) and a == 0
                    if can_continue:
                        block = last
                        block['lineRanges'].append([line['id'], a, b])
                        block['bbox'] = rounded(rect(block['bbox']) | rect(line['bbox']))
                        if not same_source_block:
                            block.setdefault('reflowJoins',[]).append({'lineId':line['id'],'reason':'full-width line continuation at original line spacing'})
                    else:
                        block = {'id': f'{line["id"]}-text-{a}', 'kind': kind, 'level': level,
                                 'pdfBlock': line['pdfBlock'], 'bbox': line['bbox'][:], 'lineRanges': [[line['id'], a, b]]}
                        blocks.append(block)
                    block['lastY'] = line['bbox'][1]
                    block['lastRight'] = line['bbox'][2]
                    pending = block
                    owner = block['id']
                assignments[line['id']][a:b] = [owner] * (b-a)
            a = b
    for group in visual_groups:
        kinds = {r['kind'] for r in group['parts']}
        kind = 'figure' if 'figure' in kinds else 'table' if 'table' in kinds else 'formula' if 'formula' in kinds else 'source-visual'
        blocks.append({'id': group['id'], 'kind': kind, 'bbox': group['bbox'], 'lineRanges': group['lineRanges'],
                       'regionIds': [r['id'] for r in group['parts']], 'reviewFlags': sorted({f for r in group['parts'] for f in r.get('reviewFlags', [])})})
    blocks.sort(key=lambda b: (round(b['bbox'][1]/3)*3, b['bbox'][0]))
    for i, block in enumerate(blocks):
        block['order'] = i
        text_lines = []
        for line_id, a, b in block['lineRanges']:
            source_line = next(l for l in lines if l['id'] == line_id)
            text_lines.append(''.join(g['c'] for g in source_line['glyphs'][a:b]))
        block['sourceText'] = '\n'.join(text_lines)
    return blocks, assignments


def convert(source, output, dpi):
    output = safe_output(output)
    evidence = checked_source(source)
    config = json.loads(CONFIG.read_text('utf-8'))
    pdf = fitz.open(source)
    page_map = [p for p in evidence['pages'] if p['printedPage'] is None or 13 <= p['printedPage'] <= 111]
    dataset = {'schemaVersion': 1, 'marker': MARKER, 'publicationAuthorization': 'not-established',
               'source': {k: evidence[k] for k in ('editionId', 'title', 'volume', 'edition', 'sourceFile', 'sha256')},
               'policy': 'Preserve exact source characters and original visual renderings. No summaries, corrections, invented diagrams or public exports.',
               'pages': [], 'regions': [], 'annotations': []}
    for item in page_map:
        number, printed = item['pdfPage'], item['printedPage']
        page = pdf[number-1]
        lines = get_lines(page, number)
        regions = seed_regions(lines, page, printed, number, config)
        tables = table_regions(page, number, regions)
        regions.extend(t for t in tables if not t['parentRegion'])
        regions.extend(complete_images(page, number, regions))
        regions.extend(math_regions(lines, page, number, regions))
        regions.extend(vector_regions(page, number, regions))
        for region in regions:
            before=region['bbox'][:]
            region['bbox']=snap_bounds(page,before)
            if before!=region['bbox']:region['boundaryExpansion']={'before':before,'reason':'retain complete intersecting source words and image/connector objects'}
        flow_regions = reflow_around_prose(regions, lines, page)
        groups = merge_regions(flow_regions)
        blocks, assignments = flow_blocks(lines, groups, page, number)
        by_id = {b['id']: b for b in blocks}
        for group in groups:
            asset = raster(page, group['bbox'], output / 'assets' / f'{group["id"]}.png', dpi)
            block = by_id[group['id']]
            block['asset'] = {**asset, 'path': f'assets/{asset["file"]}'}
        for region in regions + [t for t in tables if t['parentRegion']]:
            asset = raster(page, region['bbox'], output / 'library' / f'{region["id"]}.png', dpi)
            region.update(pdfPage=number, printedPage=printed, editionId=evidence['editionId'],
                          asset={**asset, 'path': f'library/{asset["file"]}'}, publicationAuthorization='not-established')
            dataset['regions'].append(region)
        for table in tables:
            table['cellAssets']=[]
            for cell_index,cell in enumerate(table['cells']):
                asset=raster(page,cell,output/'cells'/f'{table["id"]}-{cell_index:03}.png',dpi)
                table['cellAssets'].append({'bbox':cell,**asset,'path':f'cells/{asset["file"]}'})
        page_asset = raster(page, page.rect, output / 'pages' / f'pdf-{number:03}.png', dpi)
        source_text = page.get_text(sort=False)
        write_json(output / 'raw' / f'pdf-{number:03}.json', {'pdfPage': number, 'printedPage': printed, 'lines': lines,
                                                         'extractedText': source_text, 'extractedTextSha256': digest(source_text.encode())})
        record = {**item, 'width': page.rect.width, 'height': page.rect.height,
                  'sourceTextSha256': digest(source_text.encode()), 'sourceLineCount': len(lines),
                  'sourceGlyphCount': sum(len(l['glyphs']) for l in lines), 'lines': lines,
                  'pdfAnnotations':source_annotations(page),
                  'blocks': blocks, 'glyphOwners': assignments,
                  'originalPage': {**page_asset, 'path': f'pages/{page_asset["file"]}'},
                  'imageObjects': [{'index': i, 'bbox': rounded(im['bbox']), 'width': im['width'], 'height': im['height'],
                                    'owners': [g['id'] for g in groups if overlap(im['bbox'], g['bbox']) >= .97]}
                                   for i, im in enumerate(page.get_image_info())],
                  'vectorObjects': [{'index': i, 'bbox': rounded(d['rect']), 'type': d['type'],
                                     'fill': d.get('fill'), 'stroke': d.get('color'),
                                     'owners': [g['id'] for g in groups if overlap(d['rect'], g['bbox']) >= .95],
                                     'role': 'original-layout-or-markup' if not any(overlap(d['rect'],g['bbox'])>=.95 for g in groups) else 'preserved-in-visual'}
                                    for i,d in enumerate(page.get_drawings())]}
        dataset['pages'].append(record)
        print(f'PDF {number} / printed {printed}: {len(blocks)} blocks, {len(groups)} original visual assemblies, {len(tables)} table grids', flush=True)
    write_json(output / 'chapter.json', dataset)
    # Repeated conversions must not leave obsolete crops in the review library.
    # Only generated PNG files in these three fixed, local directories are pruned.
    expected={r['asset']['path'] for r in dataset['regions']}
    expected.update(b['asset']['path'] for p in dataset['pages'] for b in p['blocks'] if 'asset' in b)
    expected.update(a['path'] for r in dataset['regions'] for a in r.get('cellAssets',[]))
    for folder in ('assets','library','cells'):
        for old in (output/folder).glob('*.png'):
            if old.relative_to(output).as_posix() not in expected:old.unlink()
    print(f'Complete local source dataset: {output / "chapter.json"}', flush=True)
    return dataset


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('convert', 'validate', 'preview'))
    parser.add_argument('--source', type=Path, default=Path(r'D:\ITPEC Old Questions\database\raw\FE Vol 1.pdf'))
    parser.add_argument('--output', type=Path, default=OUT)
    parser.add_argument('--dpi', type=int, default=180)
    args = parser.parse_args()
    if not 120 <= args.dpi <= 300:
        parser.error('DPI must be 120–300 for this editorial library')
    output = safe_output(args.output)
    if args.command == 'convert':
        dataset = convert(args.source, output, args.dpi)
        from editorial_preview import build_preview
        build_preview(dataset, output)
    elif args.command == 'preview':
        from editorial_preview import build_preview
        build_preview(json.loads((output / 'chapter.json').read_text('utf-8')), output)
    else:
        from editorial_validate import validate
        validate(args.source, output)


if __name__ == '__main__':
    main()
