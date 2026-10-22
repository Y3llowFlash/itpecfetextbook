"""Local historical-question extraction and review. This milestone opens Technology-01 only.

Raw PDFs, question crops, transcripts and unapproved explanations stay in .local/.
Extraction never approves a question or equates a printed key with verification.
"""
import argparse
import hashlib
import html
import json
import re
from datetime import datetime,timezone
from pathlib import Path
from collections import Counter
import fitz
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'data-sources/historical-pdfs/Technology-01.pdf'
WORK=ROOT/'.local/historical/technology-01'
VERSION='technology-question-v1'
_PRACTICE_SNAPSHOT=None
Q=re.compile(r'^\s*Q\s*(\d+)\.',re.M)
KEY=re.compile(r'Ans\s*:\s*\(?([a-d])\)?',re.I)
DATE=re.compile(r'(20\d\d)\s+(April|October)',re.I)
OPTION=re.compile(r'^\s*([a-d])\)',re.M)
digest=lambda data:hashlib.sha256(data).hexdigest()
norm=lambda text:re.sub(r'\s+',' ',text).strip()

def read_json(path,default=None):
    return json.loads(path.read_text('utf8')) if path.exists() else default

def write_json(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    text=json.dumps(value,indent=2,ensure_ascii=False)+'\n'
    if not path.exists() or path.read_text('utf8')!=text:path.write_text(text,'utf8')

def processing_fingerprint():
    return digest(VERSION.encode()+Path(__file__).read_bytes().replace(b'\r\n',b'\n'))

def publication_fingerprint(record,review):
    # Approval is invalidated by any source, crop, metadata, mapping or explanation change.
    return digest(json.dumps({'question':record,'review':{k:v for k,v in review.items() if k!='approval'}},sort_keys=True,ensure_ascii=False).encode())

def describe_page(page,number):
    raw=page.get_text('dict');lines=[]
    for block in raw['blocks']:
        for line in block.get('lines',[]):
            lines.append({'bbox':list(line['bbox']),'text':''.join(s['text'] for s in line['spans']),
                          'spans':[{'text':s['text'],'font':s['font'],'bbox':list(s['bbox'])} for s in line['spans']]})
    text=page.get_text();starts=[l for l in lines if Q.match(l['text'])]
    if len(starts)>1:raise ValueError(f'PDF {number}: multiple questions on one page require an explicit layout adapter; no guess was made')
    keys=[l for l in lines if KEY.search(l['text'])];dates=[l for l in lines if DATE.search(l['text'])]
    footer=min([l['bbox'][1] for l in keys+dates if l['bbox'][1]>page.rect.height*.65],default=page.rect.height)
    body=[l for l in lines if l['bbox'][1]<footer-3 and not KEY.search(l['text']) and not DATE.fullmatch(l['text'].strip())]
    rect=fitz.Rect()
    for line in body:rect|=fitz.Rect(line['bbox'])
    for image in page.get_image_info():
        bounds=fitz.Rect(image['bbox'])
        if bounds.y1<footer-3 and bounds.get_area()<page.rect.get_area()*.9:rect|=bounds
    for drawing in page.get_drawings():
        bounds=fitz.Rect(drawing['rect'])
        if bounds.y1<footer-3 and bounds.get_area()<page.rect.get_area()*.9:rect|=bounds
    if rect.is_empty:raise ValueError(f'No readable question region on PDF {number}')
    rect=fitz.Rect(rect.x0-5,rect.y0-5,rect.x1+5,rect.y1+5)&page.rect
    if rect.y1>=footer:raise ValueError('Question crop overlaps its answer key')
    for line in body:
        if not rect.contains(fitz.Rect(line['bbox'])):raise ValueError('Question crop cuts a source line')
    return {'pdfPage':number,'questionNumber':int(Q.match(starts[0]['text']).group(1)) if starts else None,
            'body':'\n'.join(l['text'] for l in body),'lines':body,'bbox':list(rect),
            'answerKeys':KEY.findall(text),'dates':DATE.findall(text),'footerY':footer,
            'privateGlyphs':sorted(set(c for l in body for c in l['text'] if 0xe000<=ord(c)<=0xf8ff))}

def assemble_questions(pages,source_sha):
    groups=[]
    for page in pages:
        if page['questionNumber'] is not None:groups.append([page])
        elif groups:groups[-1].append(page)
        else:raise ValueError('Continuation page has no preceding question')
    records=[];seen={}
    for group in groups:
        dates=list(dict.fromkeys((int(y),m.lower()) for p in group for y,m in p['dates']))
        keys=list(dict.fromkeys(k.lower() for p in group for k in p['answerKeys']))
        year,month=dates[0] if len(dates)==1 else (None,None);season={'april':'S','october':'A'}.get(month)
        number=group[0]['questionNumber'];body='\n'.join(p['body'] for p in group);matches=list(OPTION.finditer(body));labels=[m.group(1) for m in matches]
        options={m.group(1):body[m.end():matches[i+1].start() if i+1<len(matches) else len(body)].strip() for i,m in enumerate(matches)}
        identity=f'HIST-TECH01-{year}{season}-Q{number:03}' if year and season else f'HIST-TECH01-P{group[0]["pdfPage"]:04}'
        content_hash=digest(body.encode());issues=[]
        if labels!=list('abcd'):issues.append('option-layout-needs-review')
        if any(not options.get(k) for k in 'abcd'):issues.append('image-only-or-empty-option-text')
        if matches and Q.search(body) and Q.search(body).start()>matches[0].start():issues.append('reading-order-needs-review')
        if len(keys)!=1:issues.append('missing-or-conflicting-answer-key')
        if len(dates)!=1:issues.append('missing-or-conflicting-exam-date')
        if any(p['privateGlyphs'] for p in group):issues.append('private-font-symbols-in-transcript')
        if identity in seen:
            if seen[identity]['contentSha256']==content_hash:
                previous=seen[identity]
                previous['sourceReferences'].append({'kind':'historical-pdf','sourceId':'technology-01','filename':'Technology-01.pdf','sha256':source_sha,'pages':[p['pdfPage'] for p in group],'printedAnswer':keys[0] if len(keys)==1 else None})
                if len(keys)!=1 or previous['printedAnswer']!=keys[0]:
                    previous['issues'].append('duplicate-answer-key-conflict');previous['extractionQuality']='partial'
                continue
            issues.append('ambiguous-examination-occurrence');seen[identity]['issues'].append('ambiguous-examination-occurrence');seen[identity]['extractionQuality']='partial';identity+='-'+content_hash[:8]
        r={'id':identity,'contentSha256':content_hash,'examType':None,'examTypeStatus':'needs-review',
           'year':year,'season':season,'number':number,'subject':None,'paper':None,
           'questionText':body[:matches[0].start()].strip() if matches else body,'options':options,'rawText':body,
           'printedAnswer':keys[0] if len(keys)==1 else None,'extractionQuality':'partial' if issues else 'complete','issues':issues,
           'sourceReferences':[{'kind':'historical-pdf','sourceId':'technology-01','filename':'Technology-01.pdf','sha256':source_sha,'pages':[p['pdfPage'] for p in group],'printedAnswer':keys[0] if len(keys)==1 else None}],
           'regions':[{'pdfPage':p['pdfPage'],'bbox':p['bbox'],'lineCount':len(p['lines'])} for p in group],
           'preliminaryMapping':propose_mapping(body),'images':[]}
        seen[identity]=r;records.append(r)
    return records

def propose_mapping(text):
    # Proposals are editorial hints only. They never create public highlights.
    rules=[('cache-memory','3-5-1',r'cache'),('interrupts','3-3-4',r'interrupt'),('cpu-registers','3-1',r'program counter|instruction register|accumulator'),
           ('disk-access','4-1-3',r'average access time|average seek|rotational latency'),('logic-gates','3-4-1',r'logic circuit|logical circuit|truth table|logic gate|NAND|NOR|flip-flop'),
           ('processor-speed','3-5-2',r'pipeline|superscalar|RISC|VLIW|CISC|MIMD|SIMD|SISD|multicore'),('memory-devices','3-2-1',r'DRAM|SRAM|flash memory|non.?volatile|EEPROM|memory cell'),
           ('floating-point','2-3-2',r'floating.point|IEEE 754|mantissa'),('signed-shifts','2-3-4',r'shift|rotation operation'),
           ('radix-conversion','2-2',r'hexadecimal|binary number|decimal number|octal'),('usb-interface','5-5-2',r'USB|IEEE 1394|Bluetooth|daisy.chain|SCSI'),
           ('display-memory','5-2-1',r'VRAM|pixel|display|colour|color'),('printer','5-2-2',r'printer|printing'),('input-devices','5-1',r'sensor|scanner|OCR|OMR|bar.?code|mouse|touch panel'),
           ('io-control','5-4',r'DMA|direct memory access|input/output control'),('instruction-execution','3-3-2',r'instruction|processor|CPU'),('storage-media','4',r'disk|DVD|CD-ROM|SSD|RAID')]
    return [{'conceptId':concept,'headingNumber':heading,'status':'proposed','method':'keyword-triage-not-verification'} for concept,heading,pattern in rules if re.search(pattern,text,re.I)][:3]

def render_crops(pdf,records):
    folder=WORK/'images';folder.mkdir(exist_ok=True)
    for index,r in enumerate(records):
        for region in r['regions']:
            page=pdf[region['pdfPage']-1];scale=300/72;pix=page.get_pixmap(matrix=fitz.Matrix(scale,scale),alpha=False,annots=True)
            image=Image.frombytes('RGB',(pix.width,pix.height),pix.samples);box=list((fitz.Rect(region['bbox'])*fitz.Matrix(scale,scale)).irect);crop=image.crop(box)
            target=folder/f'{r["id"]}-p{region["pdfPage"]:03}.webp';crop.save(target,'WEBP',lossless=True,method=6)
            with Image.open(target) as decoded:
                if decoded.convert('RGB').tobytes()!=crop.tobytes():raise ValueError('Lossless question crop differs from source pixels')
            r['images'].append({'path':'images/'+target.name,'sha256':digest(target.read_bytes()),'pixelSha256':digest(crop.tobytes()),'width':crop.width,'height':crop.height,'bytes':target.stat().st_size,'dpi':300,'pdfPage':region['pdfPage'],'pixelBox':box})
        if index%20==0:print(f'Rendered {index+1}/{len(records)} original questions',flush=True)

def manifest_for(records,source_sha,page_count,previous=None):
    reviews=read_json(WORK/'reviews.json',{})
    verified=sum(valid_verification(r,reviews.get(r['id'],{})) for r in records)
    approved=sum(valid_approval(r,reviews.get(r['id'],{})) for r in records)
    return {'schemaVersion':1,'sourceFilename':'Technology-01.pdf','sourceSha256':source_sha,'importerFingerprint':processing_fingerprint(),
            'importedAt':(previous or {}).get('importedAt') or datetime.now(timezone.utc).isoformat(),'processingStatus':'review-in-progress' if verified else 'extracted-awaiting-review',
            'pdfPages':page_count,'totalExtracted':sum(len(r['sourceReferences']) for r in records),'duplicateQuestions':sum(len(r['sourceReferences'])-1 for r in records),'uniqueQuestions':len(records),
            'verifiedAnswers':verified,'approvedQuestions':approved,'unresolvedQuestions':len(records)-verified,'imageExtractionFailures':0,
            'successfulImageCrops':sum(len(r['images']) for r in records),'extractionQuality':dict(Counter(r['extractionQuality'] for r in records)),
            'answerStatuses':dict(Counter(reviews.get(r['id'],{}).get('verification',{}).get('status','unverified') for r in records)),
            'mappingStatuses':dict(Counter(reviews.get(r['id'],{}).get('mapping',{}).get('status','needs-review') for r in records)),
            'completedExplanations':sum(valid_verification(r,reviews.get(r['id'],{})) and bool(reviews.get(r['id'],{}).get('explanation')) for r in records),
            'publicationPolicy':'Only a separate, fingerprint-bound owner approval can publish independently verified Chapter 1 records.'}

def valid_verification(record,review):
    v=review.get('verification',{});ex=review.get('explanation',{})
    return bool('duplicate-answer-key-conflict' not in record.get('issues',[]) and review.get('contentSha256')==record['contentSha256'] and v.get('status')=='verified' and
                v.get('independentAnswer') in list('abcd') and v.get('independentAnswer')==record.get('printedAnswer') and
                v.get('method') in ['textbook-source','calculation','truth-table'] and v.get('evidence') and
                v.get('reasoning') and ex.get('steps') and ex.get('summary') and ex.get('takeaway'))

def approval_errors(record,review):
    errors=[]
    if not authoritative_duplicate(record,review) and not valid_verification(record,review):errors.append('Independent answer evidence and worked explanation are incomplete or conflict with the printed key')
    mapping=review.get('mapping',{});quality=review.get('extraction',{});meta=review.get('metadata',{})
    if mapping.get('status')!='verified' or mapping.get('chapterId')!='fe-v1-ch01' or not all(mapping.get(k) for k in ['conceptId','headingNumber','sectionId','subsectionId','evidence']):errors.append('Precise Chapter 1 mapping has not been verified')
    if quality.get('status')!='complete' or quality.get('reviewedImages')!=[a['sha256'] for a in record.get('images',[])] or not quality.get('imageDescription') or set(quality.get('optionText',{}))!=set('abcd') or not all(quality.get('optionText',{}).values()):errors.append('Complete image, option and accessible transcript review is required')
    if meta.get('status')!='verified' or meta.get('examType')!='FE' or meta.get('subject') not in ['A','B'] or not meta.get('paper') or not meta.get('evidence'):errors.append('Examination type/paper is not printed on these pages and needs owner-confirmed evidence')
    return errors

def authoritative_duplicate(record,review):
    """Only a reliable published Practice occurrence can bypass novel-answer verification.
    Preserve its answer and explanation even if the PDF key or new reasoning disagrees.
    """
    global _PRACTICE_SNAPSHOT
    meta=review.get('metadata',{})
    if meta.get('status')!='verified' or meta.get('examType')!='FE' or not record.get('year') or not record.get('images'):return None
    if _PRACTICE_SNAPSHOT is None:_PRACTICE_SNAPSHOT=read_json(ROOT/'public/data/questions.json',[])
    candidates=[q for q in _PRACTICE_SNAPSHOT if q.get('is_published') is True and
                (not q.get('review') or any(s['kind']=='itpec-practice' for s in q['review']['sources'])) and
                q.get('year')==record.get('year') and q.get('season')==record.get('season') and q.get('number')==record.get('number') and
                q.get('paper')==meta.get('paper') and q.get('image',{}).get('sha256')==record['images'][0]['sha256']]
    return candidates[0] if len(candidates)==1 else None

def valid_approval(record,review):
    a=review.get('approval',{})
    return bool(not approval_errors(record,review) and a.get('status')=='approved' and a.get('reviewer') and a.get('fingerprint')==publication_fingerprint(record,review))

def refresh_review(records):
    previous=read_json(WORK/'manifest.json');write_json(WORK/'manifest.json',manifest_for(records,previous['sourceSha256'],previous['pdfPages'],previous));write_review_gallery(records)

def approve(records,identity,reviewer):
    if not identity or not reviewer:raise ValueError('Explicit --id and --reviewer are required for owner approval')
    record=next((r for r in records if r['id']==identity),None)
    if record is None:raise ValueError('Unknown historical record')
    reviews=read_json(WORK/'reviews.json',{});review=reviews.get(identity,{})
    errors=approval_errors(record,review)
    if errors:raise ValueError('; '.join(errors))
    review['approval']={'status':'approved','reviewer':reviewer,'at':datetime.now(timezone.utc).isoformat(),'fingerprint':publication_fingerprint(record,review)}
    reviews[identity]=review;write_json(WORK/'reviews.json',reviews);refresh_review(records)

def extract(source=SOURCE,force=False):
    source=Path(source)
    if source.name!='Technology-01.pdf':raise ValueError('Only Technology-01.pdf is authorized in this milestone')
    if not source.is_file():raise FileNotFoundError(f'Missing authorized source: {source}')
    sha=digest(source.read_bytes());previous=read_json(WORK/'manifest.json',{})
    if not force and previous.get('sourceSha256')==sha and previous.get('importerFingerprint')==processing_fingerprint() and (WORK/'questions.json').exists():
        records=read_json(WORK/'questions.json');verify_assets(records);print('Unchanged previously processed source: no records or files duplicated.');return previous
    WORK.mkdir(parents=True,exist_ok=True)
    with fitz.open(source) as pdf:
        if pdf.is_encrypted:raise ValueError('The authorized PDF cannot be read')
        pages=[describe_page(page,i+1) for i,page in enumerate(pdf)]
        records=assemble_questions(pages,sha);render_crops(pdf,records)
        write_json(WORK/'pages.json',pages);write_json(WORK/'questions.json',records)
        manifest=manifest_for(records,sha,len(pdf),previous if previous.get('sourceSha256')==sha else None);write_json(WORK/'manifest.json',manifest)
    write_review_gallery(records);print(json.dumps(manifest,indent=2));return manifest

def verify_assets(records):
    for r in records:
        for image in r['images']:
            file=(WORK/image['path']).resolve()
            if not file.is_relative_to((WORK/'images').resolve()) or not file.is_file() or digest(file.read_bytes())!=image['sha256']:raise ValueError('Historical question asset changed or missing')

def verify_source():
    manifest=read_json(WORK/'manifest.json',{})
    if digest(SOURCE.read_bytes())!=manifest.get('sourceSha256'):raise ValueError('Source changed: re-extraction and review are required')
    if manifest.get('importerFingerprint')!=processing_fingerprint():raise ValueError('Importer changed: rerun extract before review or promotion')

def write_review_gallery(records):
    reviews=read_json(WORK/'reviews.json',{});cards=[]
    for r in records:
        review=reviews.get(r['id'],{});status=review.get('verification',{}).get('status','unverified')
        images=''.join(f'<a href="{a["path"]}"><img loading="lazy" src="{a["path"]}" alt="Original complete question, PDF page {a["pdfPage"]}"></a>' for a in r['images'])
        publication='approved' if valid_approval(r,review) else 'unapproved'
        cards.append(f'<article id="{r["id"]}"><h2>{r["id"]}</h2><p>PDF pages {r["sourceReferences"][0]["pages"]} · Printed key: {r["printedAnswer"]} · Verification: {status} · Publication: {publication}</p>{images}<details><summary>Extracted text and layout flags</summary><pre>{html.escape(r["rawText"])}</pre><p>{html.escape(str(r["issues"]))}</p></details><h3>Independent review</h3><pre>{html.escape(json.dumps(review,indent=2,ensure_ascii=False))}</pre><p>Approval blockers: {html.escape("; ".join(approval_errors(r,review)))}</p></article>')
    page='<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Technology-01 local review</title><style>body{font:16px/1.6 system-ui;background:#faf8f1;max-width:1100px;margin:auto;padding:24px}article{padding:32px 0;border-bottom:1px solid #aaa}img{width:100%;height:auto}pre{white-space:pre-wrap;overflow-wrap:anywhere}h2{font-size:20px}</style><h1>Technology-01 · private question review</h1><p>Original question crops omit the answer-key footer. The printed answer, independent reasoning, source mapping and owner approval are separate review dimensions. These records are not public.</p>'+''.join(cards)+'</html>'
    (WORK/'index.html').write_text(page,'utf8')

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('command',choices=['extract','verify','gallery','approve','export']);parser.add_argument('--source',type=Path,default=SOURCE);parser.add_argument('--force',action='store_true');parser.add_argument('--id');parser.add_argument('--reviewer');args=parser.parse_args()
    if args.command=='extract':extract(args.source,args.force)
    else:
        records=read_json(WORK/'questions.json')
        if records is None:raise ValueError('Run extraction first')
        verify_source()
        verify_assets(records)
        if args.command=='gallery':refresh_review(records)
        if args.command=='approve':approve(records,args.id,args.reviewer)
        if args.command=='export':
            reviews=read_json(WORK/'reviews.json',{});print(json.dumps([{'record':r,'review':reviews[r['id']]} for r in records if valid_approval(r,reviews.get(r['id'],{}))],ensure_ascii=False))
        else:print(f'Verified {len(records)} local historical records and their complete source crops.')
