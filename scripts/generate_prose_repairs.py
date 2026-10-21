"""Generate reviewed paragraph layout metadata, never rewrite source words/assets.

The unnumbered PDF insertion encodes prose as individual word objects. Its five
paragraphs were visually checked against PDF 83. Other pages (including tables
and diagram labels) are deliberately excluded from this repair.
"""
import argparse
import json
from pathlib import Path

import fitz
from editorial_convert import OUT, ROOT, digest, get_lines, write_json
from figures import checked_source

TARGET = ROOT / 'src/content/hardware-prose-repairs.json'


def paragraph_groups(blocks):
    """Join adjacent word objects by their physical rows and paragraph gaps."""
    groups = []
    for block in blocks:
        if block['kind'] != 'paragraph':
            raise ValueError('A visual, heading or table must never enter a prose run')
        if len(block['sourceText'].split()) != 1:
            raise ValueError('This reviewed repair expects individual word objects')
        if groups:
            previous = groups[-1][-1]
            x0, y0, _, y1 = block['bbox']
            px0, py0, px1, _ = previous['bbox']
            if abs(y0-py0) < 2:
                if not 0 <= x0-px1 < 12:
                    raise ValueError('Words do not form adjacent same-row prose')
            elif 0 < y0-py0 <= 1.5*(y1-y0):
                if abs(x0-groups[-1][0]['bbox'][0]) > 2:
                    raise ValueError('A prose continuation must return to its left edge')
            elif y0 > py0:
                groups.append([])
            else:
                raise ValueError('Source reading order changed')
        else:
            groups.append([])
        groups[-1].append(block)
    return groups


def generate(source):
    evidence = checked_source(source)
    release = json.loads((ROOT/'src/content/hardware-source-release.json').read_text('utf-8'))
    data = json.loads((OUT/'chapter.json').read_text('utf-8'))
    if evidence['sha256'] != release['sourceSha256'] or evidence['sha256'] != data['source']['sha256']:
        raise ValueError('Incorrect source edition')
    page = next(p for p in data['pages'] if p['pdfPage'] == 83)
    with fitz.open(source) as pdf:
        fresh = {line['id']:line for line in get_lines(pdf[82],83)}
    fragments = [b for b in page['blocks'] if b['kind'] == 'paragraph']
    for block in fragments:
        if len(block['lineRanges']) != 1:
            raise ValueError('Unexpected multi-line source object')
        line_id, start, end = block['lineRanges'][0]
        if fresh[line_id]['text'][start:end] != block['sourceText'] or fresh[line_id]['bbox'] != block['bbox']:
            raise ValueError('Source words or physical coordinates changed')
    groups = paragraph_groups(fragments)
    if [len(group) for group in groups] != [50,56,48,57,24]:
        raise ValueError('Reviewed five-paragraph layout changed; inspect the source again')
    prefix = release['releaseId']+'-'
    records = []
    for index, group in enumerate(groups,1):
        records.append({
            'id':f'pdf-083-prose-{index:03}',
            'firstId':prefix+group[0]['id'], 'lastId':prefix+group[-1]['id'],
            'fragmentCount':len(group),
            'bbox':[min(b['bbox'][0] for b in group),min(b['bbox'][1] for b in group),
                    max(b['bbox'][2] for b in group),max(b['bbox'][3] for b in group)],
            'textSha256':digest(' '.join(b['sourceText'] for b in group).encode()),
        })
    return {'schemaVersion':1,'releaseId':release['releaseId'],'sourceSha256':release['sourceSha256'],
            'pdfPage':83,'printedPage':None,
            'review':'Five prose paragraphs visually verified against the original PDF; original word IDs and text remain unchanged.',
            'paragraphs':records}


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source',type=Path,default=Path(r'D:\ITPEC Old Questions\database\raw\FE Vol 1.pdf'))
    parser.add_argument('--check',action='store_true')
    args=parser.parse_args()
    result=generate(args.source)
    if args.check:
        if json.loads(TARGET.read_text('utf-8')) != result:
            raise ValueError('Prose repair metadata drifted from the reviewed source geometry')
    else:
        write_json(TARGET,result)
    print('Verified PDF 83: 235 original word objects form 5 source paragraphs; no text or assets changed.')
