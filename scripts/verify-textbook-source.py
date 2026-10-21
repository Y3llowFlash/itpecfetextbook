"""Read-only verification of printed page labels, never a public prose extractor."""
import argparse
import hashlib
import json
import re
from pathlib import Path
import fitz

parser = argparse.ArgumentParser()
parser.add_argument('--source', default=r'D:\ITPEC Old Questions\database\raw\FE Vol 1.pdf')
args = parser.parse_args()
source = Path(args.source)
pdf = fitz.open(source)
pages = []
for index in range(17, 118):
    page = pdf[index]
    labels = [word[4] for word in page.get_text('words')
              if word[1] > page.rect.height - 70 and re.fullmatch(r'\d{1,3}', word[4])]
    pages.append({'pdfPage': index + 1, 'printedPage': int(labels[0]) if len(labels) == 1 else None})
colophon = pdf[-1].get_text()
assert 'First Edition: April, 2015' in colophon
assert [p['printedPage'] for p in pages if p['printedPage'] is not None] == list(range(13, 113))
evidence = {
    'editionId': 'new-fe-vol1-2015-04', 'title': 'New FE Textbook Vol.1',
    'volume': 'IT Fundamentals', 'edition': 'First Edition, April 2015',
    'sourceFile': 'FE Vol 1.pdf', 'sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
    'contentsPdfPage': 2, 'colophonPdfPage': len(pdf), 'pages': pages,
    'notes': ['PDF page 83 is an unnumbered inserted I2C page. No printed-page badge is assigned to that insertion.'],
}
target = Path('docs/development/evidence/hardware-printed-pages.json')
target.parent.mkdir(parents=True, exist_ok=True)
target.write_text(json.dumps(evidence, indent=2) + '\n', encoding='utf-8')
print('Verified 100 printed labels (13–112), one unnumbered insertion, and the 2015 edition colophon.')
