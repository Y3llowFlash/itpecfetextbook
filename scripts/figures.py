"""Local PDF figure review; requires PyMuPDF and Pillow. Never writes public/ or dist/."""
import argparse
import hashlib
import html
import json
from pathlib import Path

import fitz
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / '.local' / 'figures'
EVIDENCE = ROOT / 'docs/development/evidence/hardware-printed-pages.json'
DEFAULT_MANIFEST = ROOT / 'docs/development/figures/chapter1-inventory.json'


def render(pdf, number, target, dpi=150, crop=None):
    page = pdf[number - 1]
    rect = fitz.Rect(crop) if crop else page.rect
    if not page.rect.contains(rect) or rect.is_empty:
        raise ValueError(f'Invalid PDF-point crop on PDF page {number}: {crop}')
    target.parent.mkdir(parents=True, exist_ok=True)
    pix = page.get_pixmap(matrix=fitz.Matrix(dpi / 72, dpi / 72), clip=rect, alpha=False)
    im = Image.frombytes('RGB', (pix.width, pix.height), pix.samples)
    if target.suffix == '.webp':
        im.save(target, 'WEBP', quality=94, method=6)
    else:
        im.save(target, 'PNG', optimize=True)
    return im


def checked_source(path):
    evidence = json.loads(EVIDENCE.read_text('utf-8'))
    if hashlib.sha256(path.read_bytes()).hexdigest() != evidence['sha256']:
        raise ValueError('Source fingerprint differs from the verified 2015 edition')
    return evidence


def load_manifest(path, evidence, pdf):
    manifest = json.loads(path.read_text('utf-8'))
    mapping = {p['pdfPage']: p['printedPage'] for p in evidence['pages']}
    seen = set()
    for figure in manifest['regions']:
        if figure['id'] in seen:
            raise ValueError('Duplicate figure ID')
        seen.add(figure['id'])
        if mapping.get(figure['pdfPage'], 'missing') != figure['printedPage']:
            raise ValueError(f"Incorrect printed/PDF page pair: {figure['id']}")
        page = pdf[figure['pdfPage'] - 1]
        rect = fitz.Rect(figure['crop'])
        if not page.rect.contains(rect) or rect.is_empty:
            raise ValueError(f"Crop outside source page: {figure['id']}")
        if figure['disposition'] not in ('recreated', 'existing-equivalent', 'editorial-only'):
            raise ValueError('Unapproved disposition; source crops cannot be published by this tool')
    expected = set(range(13, 112))
    covered = {p['printedPage'] for p in manifest['pageReview']}
    if covered != expected:
        raise ValueError('Every printed page 13–111 must have an explicit review record')
    return manifest


def boundary_findings(page, crop):
    """Find severed word/image boxes, including images used as vector-like connectors."""
    rect = fitz.Rect(crop)
    objects = [(fitz.Rect(w[:4]), 'label') for w in page.get_text('words')]
    objects += [(fitz.Rect(im['bbox']), 'image/connector') for im in page.get_image_info()]
    return [(bounds, kind) for bounds, kind in objects
            if (rect & bounds).get_area() > 0 and not rect.contains(bounds)]


def snap_bounds(page, crop):
    """Conservative proposal, not automatic detection of the figure's semantics.

    Expands a manually selected region to retain intersecting labels and raster
    fragments. A human must still check arrows, vector paths, captions and context.
    """
    rect = fitz.Rect(crop)
    for _ in range(100):
        findings = boundary_findings(page, rect)
        if not findings:
            return [round(v, 2) for v in rect]
        for bounds, _ in findings:
            rect |= bounds + (-0.5, -0.5, 0.5, 0.5)
        rect &= page.rect
    raise ValueError('Boundary expansion did not converge; inspect manually')


def survey(pdf, evidence):
    pages = [p for p in evidence['pages'] if p['printedPage'] is None or 13 <= p['printedPage'] <= 111]
    for batch in range(0, len(pages), 8):
        sheet = Image.new('RGB', (2000, 1450), '#dedbd5')
        draw = ImageDraw.Draw(sheet)
        for slot, item in enumerate(pages[batch:batch + 8]):
            n = item['pdfPage']
            im = render(pdf, n, WORK / 'pages' / f'pdf-{n:03}.webp', 100)
            im.thumbnail((490, 690))
            x, y = (slot % 4) * 500, (slot // 4) * 725
            sheet.paste(im, (x, y + 26))
            draw.text((x + 8, y + 5), f"Printed {item['printedPage']} / PDF {n}", fill='black')
            (WORK / 'pages' / f'pdf-{n:03}.txt').write_text(pdf[n - 1].get_text(), 'utf-8')
        sheet.save(WORK / f'survey-{batch // 8 + 1:02}.jpg', quality=90)
    print(f'Rendered {len(pages)} pages and 13 survey sheets under {WORK}')


def review(pdf, manifest, dpi):
    cards = []
    for figure in manifest['regions']:
        name = figure['id']
        target = WORK / 'crops' / f'{name}.webp'
        render(pdf, figure['pdfPage'], target, dpi, figure['crop'])
        page = pdf[figure['pdfPage'] - 1]
        # A contextual page preview draws the exact crop boundary; retain it beside the crop.
        pix = page.get_pixmap(matrix=fitz.Matrix(1, 1), alpha=False)
        context = Image.frombytes('RGB', (pix.width, pix.height), pix.samples)
        ImageDraw.Draw(context).rectangle(figure['crop'], outline='#bc2929', width=2)
        context.save(WORK / 'crops' / f'{name}-context.webp', quality=85)
        label = html.escape(figure['description'])
        findings = boundary_findings(page, figure['crop'])
        if findings:
            raise ValueError(f'{name}: {len(findings)} severed labels/images; inspect or propose snapped bounds')
        ref = f"Printed {figure['printedPage']} · PDF {figure['pdfPage']} · {figure['kind']}"
        equivalent = html.escape(figure.get('equivalent', ''))
        if figure['disposition'] == 'recreated':
            destination = f'<a href="originals.html#{equivalent}">{equivalent}</a>'
        elif figure['disposition'] == 'existing-equivalent':
            slug = 'memory-and-cache' if equivalent == 'memory-hierarchy' else figure['section']
            destination = f'<a href="https://itpecfetextbook.pages.dev/chapters/hardware/{slug}/#{equivalent}">Existing lesson equivalent: {equivalent}</a>'
        else:
            destination = 'Editorial only; no source reuse approved'
        cards.append(f'<article id="{name}"><h2>{name}: {label}</h2><p>{ref}</p><p>{html.escape(figure["section"])} / {html.escape(figure["anchor"])}</p><p>{html.escape(figure["disposition"])} → {destination}</p><p>{html.escape(figure.get("review", ""))}</p><div><img src="crops/{name}.webp" alt="Local source review: {label}" loading="lazy"><a href="crops/{name}-context.webp">Full-page boundary context</a></div></article>')
    template = '<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Local Chapter 1 figure review — not for publication</title><style>body{font:16px/1.5 system-ui;background:#f4f1eb;margin:24px}main{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,420px),1fr));gap:24px}article{background:white;padding:20px;border:1px solid #bbb}h2{font-size:18px}img{display:block;max-width:100%;height:auto}a{display:block}header{max-width:70ch}</style><header><h1>Chapter 1 — private source figure review</h1><p>Copyrighted source crops. Editorial use only. No publication permission established. Red boundaries in contextual previews show the recorded PDF-point crops. Public diagrams are separately authored originals.</p><p>Coordinates: PDF points, top-left origin; 72 points/inch. All exports use full-page rasterization clipped to the selected region, including vector/text objects.</p></header><main>' + ''.join(cards) + '</main></html>'
    (WORK / 'gallery.html').write_text(template, 'utf-8')
    (WORK / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n', 'utf-8')
    originals = json.loads((ROOT / 'src/content/hardware-figures.json').read_text('utf-8'))
    original_cards = []
    for figure in originals:
        svg = (ROOT / 'src/assets/hardware' / figure['asset']).read_text('utf-8')
        links = ' '.join(f'<a href="gallery.html#{region}">{region}</a>' for region in figure['sourceRegions'])
        original_cards.append(f'<article id="{figure["id"]}"><h2>{html.escape(figure["title"])}</h2>{svg}<p>{html.escape(figure["caption"])}</p><p>New original; no source artwork. Printed pages {figure["sourcePages"]}.</p>{links}</article>')
    (WORK / 'originals.html').write_text('<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Original Chapter 1 artwork review</title><style>body{font:16px/1.5 system-ui;background:#f4f1eb;margin:16px}main{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,320px),1fr));gap:20px}article{padding:12px;background:white;border:1px solid #bbb}h2{font-size:18px}svg{width:100%;max-width:400px;height:auto}a{display:block}</style><h1>New original artwork: review beside source evidence</h1><p><a href="gallery.html">Private source gallery</a>. Do not publish this editorial gallery with its linked source crops.</p><main>' + ''.join(original_cards) + '</main></html>', 'utf-8')
    print(f'Rendered {len(cards)} complete regions at {dpi} DPI; gallery: {WORK / "gallery.html"}')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, default=Path(r'D:\ITPEC Old Questions\database\raw\FE Vol 1.pdf'))
    parser.add_argument('--manifest', type=Path, default=DEFAULT_MANIFEST)
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('survey')
    sub.add_parser('validate')
    sub.add_parser('suggest-bounds', help='Write local candidate bounds; review before updating editorial manifest')
    r = sub.add_parser('render')
    r.add_argument('--pdf-page', type=int, required=True)
    r.add_argument('--dpi', type=int, default=150)
    r.add_argument('--crop', type=float, nargs=4, help='x0 y0 x1 y1 in PDF points')
    r.add_argument('--format', choices=('webp', 'png'), default='webp')
    g = sub.add_parser('review')
    g.add_argument('--dpi', type=int, default=180)
    args = parser.parse_args()
    if not 72 <= getattr(args, 'dpi', 150) <= 600:
        parser.error('DPI must be between 72 and 600')
    evidence = checked_source(args.source)
    pdf = fitz.open(args.source)
    WORK.mkdir(parents=True, exist_ok=True)
    if args.command == 'survey':
        survey(pdf, evidence)
    elif args.command == 'render':
        if not 1 <= args.pdf_page <= len(pdf):
            parser.error('PDF page is outside this source')
        out = WORK / f'selected-pdf-{args.pdf_page:03}.{args.format}'
        render(pdf, args.pdf_page, out, args.dpi, args.crop)
        print(out)
    else:
        manifest = load_manifest(args.manifest, evidence, pdf)
        if args.command == 'suggest-bounds':
            for region in manifest['regions']:
                region['crop'] = snap_bounds(pdf[region['pdfPage'] - 1], region['crop'])
            target = WORK / 'suggested-manifest.json'
            target.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + '\n', 'utf-8')
            print(f'Candidate bounds: {target}; inspect contextual previews before adopting')
        elif args.command == 'review':
            review(pdf, manifest, args.dpi)
        else:
            for region in manifest['regions']:
                if boundary_findings(pdf[region['pdfPage'] - 1], region['crop']):
                    raise ValueError(f"Severed label/image at {region['id']}")
            print(f"Verified {len(manifest['regions'])} crop bounds, page pairs and 99 page reviews")


if __name__ == '__main__':
    main()
