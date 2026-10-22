"""Deterministic private reconciliation. Advisory JSON never supplies approval or verification authority."""
import argparse
import copy
import itertools
import json
import csv
import io
import re
from pathlib import Path
import fitz
from PIL import Image
import historical_questions as h

QA=h.WORK/'qa-batch1'
AUDIT='ITPEC_Chapter1_Academic_Audit_Batch01_With_Images.json'
ADDENDUM='ITPEC_Chapter1_Image_QA_Addendum.json'
AUDIT2='ITPEC_Chapter1_Academic_Audit_Batch02.json'
AUDIT3='ITPEC_Chapter1_Academic_Audit_Batch03.json'
PROTECTED_BATCH3_PAGES={110,112,119,180}
TEXTBOOK=Path('D:/ITPEC Old Questions/database/raw/FE Vol 1.pdf')

def object_hash(value):
    return h.digest(json.dumps(value,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode())

def validate_proposals(records,audit,addendum,source_sha):
    batch2=audit.get('schema')=='itpec-academic-audit-proposals-v2' and audit.get('batch') in [2,3]
    if not batch2 and (audit.get('schema')!='itpec-academic-audit-proposals-v1-with-image-addendum' or not addendum or addendum.get('schema')!='itpec-academic-image-audit-addendum-v1'):raise ValueError('Unsupported advisory schema')
    entries=audit.get('entries',[])
    count=audit.get('scope',{}).get('count') if batch2 else audit.get('questionCount')
    if len(entries)!=30 or count!=30 or len({e['questionId'] for e in entries})!=30:raise ValueError('Batch must contain 30 unique canonical IDs')
    index={r['id']:r for r in records}
    for e in entries:
        r=index.get(e['questionId'])
        if not r or e['sourceSha256']!=source_sha or e['questionContentSha256']!=r['contentSha256'] or e['pdfPage'] not in [p['pdfPage'] for p in r['regions']]:raise ValueError(f'Stale or inconsistent proposal: {e["questionId"]}')
        if h.digest(r['rawText'].encode())!=r['contentSha256']:raise ValueError('Original transcript checksum changed')
        if batch2:
            position=e.get('originalRecordIndex',0)
            if not 1<=position<=len(records) or records[position-1]['id']!=r['id']:raise ValueError('Canonical record index changed')
            if e.get('printedAnswer')!=r.get('printedAnswer') or e.get('originalExtractionQuality')!=r.get('extractionQuality'):raise ValueError('Advisory source fields disagree')
            if e.get('reviewSnapshotSha256')!=audit['sourceSnapshot']['reviewFileSha256']:raise ValueError('Inconsistent review snapshot reference')
            if e.get('sourceOriginalImageReferences')!=[a['path'] for a in r['images']]:raise ValueError('Advisory image identity changed')
            if audit['batch']==3:
                if e['pdfPage'] in PROTECTED_BATCH3_PAGES:raise ValueError('Protected unresolved page is outside Batch 3 authorization')
                if e.get('sourceImageSha256')!=[a['sha256'] for a in r['images']]:raise ValueError('Advisory image checksum changed')
    if batch2 and audit['scope'].get('questionIndices')!=[e['originalRecordIndex'] for e in entries]:raise ValueError('Advisory scope indices disagree')
    for e in (addendum or {}).get('visualFindings',[]):
        r=index.get(e['questionId'])
        if not r or e['pdfPage'] not in [p['pdfPage'] for p in r['regions']]:raise ValueError('Visual proposal identity mismatch')
        images=r['images']+[a for history in r.get('imageHistory',[]) for a in history['images']]
        if not any(a['path']==e['imageFile'] and a['sha256']==e['imageSha256'] for a in images):raise ValueError(f'Stale visual image: {e["questionId"]}')
    return index

def validate_companions(audit,csv_text,markdown):
    """Companion documents are consistency checks, never executable instructions."""
    rows=list(csv.DictReader(io.StringIO(csv_text.lstrip('\ufeff'))));entries=audit['entries']
    table=[line.split('|')[1:-1] for line in markdown.splitlines() if re.match(r'^\|\s*\d+\s*\|',line)]
    if len(rows)!=30 or len(table)!=30:raise ValueError('Companion documents must cover all 30 proposals')
    for e,row,md in zip(entries,rows,table,strict=True):
        if audit.get('batch')==3:
            loc=e.get('textbookLocation') or {}
            fields=['PDF page','Canonical ID','Printed answer','Proposed answer','Answer audit','Volume1 classification','Target chapter','Textbook printed page','Textbook PDF page','Textbook section','Mapping proposed status','Flags']
            values=[e['pdfPage'],e['questionId'],e['printedAnswer'].upper(),e['independentProposedAnswer'].upper(),e['answerStatus'],e['classification'],e['targetChapter'],loc.get('printedPage'),loc.get('pdfPage'),loc.get('sectionOrTopic'),e['mappingStatusProposed'],'; '.join(e['flags'])]
            if [row.get(k) for k in fields]!=['' if v is None else str(v) for v in values]:raise ValueError('CSV disagrees with JSON advisory')
            chapter=f'Ch.{e["targetChapter"]}' if e['targetChapter'] else 'Uncertain'
            location=f'{loc["printedPage"]} / {loc["pdfPage"]}' if loc else 'No precise passage'
            if [s.strip(' `*') for s in md[:5]]!=[str(e['pdfPage']),e['questionId'],e['independentProposedAnswer'].upper(),chapter,location]:raise ValueError('Markdown table disagrees with JSON advisory')
            continue
        answer=e['independentProposedAnswer'] or 'UNRESOLVED'
        expected=[str(e['pdfPage']),e['questionId'],answer,f'Vol 1 Chapter {e["targetChapter"]}',str(e['textbookLocation']['pdfPage']),e['answerStatus'],e['sourceVisualReview']['note']]
        if [row.get(k) for k in ['PDF page','Question','Proposed answer','Classification','Textbook PDF page','Review status','Visual / academic note']]!=expected:raise ValueError('CSV disagrees with JSON advisory')
        if md[0].strip()!=str(e['pdfPage']) or md[1].strip(' `')!=e['questionId'] or md[2].strip(' *').lower()!=answer.lower():raise ValueError('Markdown table disagrees with JSON advisory')
        location=re.search(r'Vol 1 Ch\.(\d+), PDF p\.(\d+)',md[3])
        if not location or [int(v) for v in location.groups()]!=[e['targetChapter'],e['textbookLocation']['pdfPage']]:raise ValueError('Markdown textbook location disagrees with JSON advisory')

def snapshot_hashes(folder):
    return {key:h.digest((folder/name).read_bytes()) for key,name in [('questionFileSha256','questions.json'),('reviewFileSha256','reviews.json'),('manifestFileSha256','manifest.json')]}

def validate_batch2_snapshot(folder,audit,source_sha,book_sha,input_hashes):
    batch=audit.get('batch',2)
    expected={k:audit['sourceSnapshot'][k] for k in ['questionFileSha256','reviewFileSha256','manifestFileSha256']}
    if snapshot_hashes(folder/'before')!=expected:raise ValueError(f'Preserved Batch {batch} baseline does not match advisory snapshot')
    if audit['sourceSnapshot']['historicalPdfSha256']!=source_sha or audit['sourceSnapshot']['textbookPdfSha256']!=book_sha:raise ValueError('Advisory source snapshot differs from original PDFs')
    actual=snapshot_hashes(h.WORK);applied=h.read_json(folder/'applied-state.json',{})
    if actual!=expected and (actual!=applied.get('snapshot') or input_hashes!=applied.get('inputs')):raise ValueError(f'Stale Batch {batch} snapshot or changed reconciliation inputs')
    baseline=h.read_json(folder/'before/reviews.json')
    if any(baseline[e['questionId']]['verification']['status']!=e['originalVerificationStatus'] for e in audit['entries']):raise ValueError('Original verification status differs from advisory baseline')
    if batch==3:
        if len(baseline)!=333 or sum(v['verification']['status']=='verified' for v in baseline.values())!=249:raise ValueError('Batch 3 requires the preserved 249-answer baseline')


def validate_batch3_book(audit,decisions,book):
    source_sha=h.digest(Path(book.name).read_bytes())
    for e in audit['entries']:
        loc=e.get('textbookLocation')
        if loc and (loc['sourceSha256']!=source_sha or h.digest(book[loc['pdfPage']-1].get_text().encode())!=loc['textPageSha256']):raise ValueError('Advisory textbook page checksum changed')
    for d in decisions.values():
        if d.get('classification',{}).get('category')=='uncertain':
            if d['classification'].get('chapter') is not None or d.get('mapping',{}).get('status')!='needs-review':raise ValueError('Uncertain classification must remain unassigned')
        for dimension in ['verification','classification','mapping']:
            for ev in d.get(dimension,{}).get('evidence',[]):
                if ev.get('kind')!='textbook-source':continue
                text=book[ev['pdfPage']-1].get_text()
                if ev.get('sourceSha256')!=source_sha or ev.get('textSha256')!=h.digest(text.encode()) or not ev.get('checkedExcerpt') or ev['checkedExcerpt'] not in h.norm(text):raise ValueError('Independent textbook evidence is stale')


def check_dff_trace(proof):
    """First positive-edge DFF; second samples Q1 on the inverted clock edge."""
    q1,q2=proof['initial'];rows=[]
    for edge,d in proof['events']:
        if edge=='rising':q1=d
        elif edge=='falling':q2=q1
        else:raise ValueError('Unknown clock edge')
        rows.append([q1,q2])
    if rows!=proof['expected']:raise ValueError('D flip-flop trace disagrees with source timing')
    return rows


def check_pipeline_schedules(proof):
    results={}
    for key,starts in proof['starts'].items():
        occupied=[(time+i,i) for time in starts for i in range(5)]
        overlaps=any(max(a,b)<min(a+5,b+5) for i,a in enumerate(starts) for b in starts[i+1:])
        results[key]={'stageConflict':len(set(occupied))!=len(occupied),'overlap':overlaps}
    if results!=proof['expected']:raise ValueError('Pipeline schedule interpretation disagrees with source')
    return results

def boolean(expr,values):
    if isinstance(expr,str):return bool(values[expr])
    op,*items=expr;args=[boolean(v,values) for v in items]
    if op=='not' and len(args)==1:return not args[0]
    if op=='and':return all(args)
    if op=='or':return any(args)
    if op=='xor' and len(args)==2:return args[0]!=args[1]
    raise ValueError('Unsupported Boolean proof operation')

def check_proof(proof):
    variables=proof['variables'];expected=proof['expected'];rows=[]
    for bits in itertools.product([0,1],repeat=len(variables)):
        values=dict(zip(variables,bits));rows.append([*bits,int(boolean(proof['expression'],values)),int(boolean(expected,values))])
    if any(r[-2]!=r[-1] for r in rows):raise ValueError('Independent truth table does not establish the claimed equality')
    return rows

def check_choice_proof(proof):
    """Compare every source option, so a matching key cannot hide duplicate answers."""
    variables=proof['variables'];choices=proof['choices'];rows=[]
    if set(choices)!=set('abcd'):raise ValueError('Choice proof must include all four original alternatives')
    for bits in itertools.product([0,1],repeat=len(variables)):
        values=dict(zip(variables,bits))
        rows.append([*bits,int(boolean(proof['expression'],values)),*[int(boolean(choices[k],values)) for k in 'abcd']])
    start=len(variables)
    matches=[k for i,k in enumerate('abcd') if all(row[start]==row[start+1+i] for row in rows)]
    if matches!=proof['expectedMatches']:raise ValueError(f'Source option truth tables disagree with claimed matches: {matches}')
    return {'matches':matches,'rows':rows}

def check_observations(proof):
    variables=proof['variables']
    for row in proof['rows']:
        if len(row)!=len(variables)+1 or any(bit not in [0,1] for bit in row):raise ValueError('Invalid source observation table')
        if int(boolean(proof['expression'],dict(zip(variables,row[:-1]))))!=row[-1]:raise ValueError('Source observation disagrees with independently evaluated expression')
    return proof['rows']

def extraction_binding(record):
    return {'contentSha256':record['contentSha256'],'images':[a['sha256'] for a in record['images']]}

def merge_reviews(records,reviews,entries,decisions,batch_hash,batch=1):
    result=copy.deepcopy(reviews);changes=[];conflicts=[];by_id={e['questionId']:e for e in entries}
    if set(by_id)-set(decisions):raise ValueError('Every proposal requires a separate source-checked decision')
    if batch>=2 and set(decisions)!=set(by_id):raise ValueError(f'Batch {batch} decisions must match exactly the 30 advisory IDs')
    if batch==3 and any(region['pdfPage'] in PROTECTED_BATCH3_PAGES for r in records if r['id'] in decisions for region in r['regions']):raise ValueError('Protected unresolved page is outside Batch 3 authorization')
    for r in records:
        old=copy.deepcopy(result.get(r['id'],{}));v=result.setdefault(r['id'],{})
        if v.get('contentSha256')!=r['contentSha256']:raise ValueError('Existing review content binding is stale')
        if batch==1:
            meta=v.setdefault('metadata',{})
            meta.update(examType='FE',examTypeStatus='owner-confirmed',examTypeEvidence={'kind':'owner-confirmation','reference':'Batch 1 integration request, 2026-10-22, section 7','sourceSha256':r['sourceReferences'][0]['sha256']})
            # FE confirmation is not evidence of paper or subject. Keep the aggregate gate pending.
            if not meta.get('paper') or not meta.get('subject'):meta['status']='needs-review'
        d=decisions.get(r['id'])
        if d:
            if d.get('contentSha256')!=r['contentSha256'] or d.get('sourceChecked') is not True or d.get('imageHashes')!=[a['sha256'] for a in r['images']]:raise ValueError(f'Stale independent decision: {r["id"]}')
            if d.get('classification',{}).get('category','ch1') not in ['ch1','other-vol1','outside-vol1','uncertain']:raise ValueError('Unsupported textbook classification')
            for proof in d.get('booleanProofs',[]):check_proof(proof)
            for proof in d.get('observationProofs',[]):check_observations(proof)
            for proof in d.get('dffProofs',[]):check_dff_trace(proof)
            for proof in d.get('pipelineProofs',[]):check_pipeline_schedules(proof)
            for proof in d.get('choiceProofs',[]):
                matched=check_choice_proof(proof)['matches']
                if d.get('verification',{}).get('status')=='verified' and matched!=[d['verification']['independentAnswer']]:raise ValueError('Verified answer must match exactly one original option')
            for dimension in ['verification','explanation','mapping','classification','extraction']:
                if dimension not in d:continue
                proposed=copy.deepcopy(d[dimension]);existing=v.get(dimension,{})
                answer_conflict=dimension in ['verification','explanation'] and old.get('verification',{}).get('status')=='verified' and old['verification'].get('independentAnswer')!=d.get('verification',old['verification']).get('independentAnswer')
                if answer_conflict:
                    item={'questionId':r['id'],'dimension':dimension,'existing':existing,'proposed':proposed,'status':'needs-owner-review'}
                    conflicts.append(item);v.setdefault('academicConflicts',[])
                    if item not in v['academicConflicts']:v['academicConflicts'].append(item)
                    continue
                # Previously verified answers/explanations remain byte-for-byte unchanged.
                if dimension in ['verification','explanation'] and old.get('verification',{}).get('status')=='verified':continue
                if dimension=='extraction':
                    proposed['sourceBinding']=extraction_binding(r)
                    proposed['reviewedImages']=[a['sha256'] for a in r['images']]
                v[dimension]=proposed
            provenance={'batch':batch,'advisorySha256':batch_hash,'decisionSha256':object_hash(d),'status':'source-reconciled-not-owner-approved'}
            if 'finding' in d:provenance['finding']=d['finding']
            if v.get('verification',{}).get('status')=='verified' and not h.valid_verification(r,v):raise ValueError(f'Incomplete independent verification: {r["id"]}')
            v.setdefault('academicReviews',[])
            if provenance not in v['academicReviews']:v['academicReviews'].append(provenance)
        if v.get('approval',{}).get('status')=='approved' and v['approval'].get('fingerprint')!=h.publication_fingerprint(r,v):
            v['approval']={**v['approval'],'status':'invalidated','reason':'Reviewed source or metadata changed; owner reapproval required'}
        if old!=v:changes.append({'questionId':r['id'],'beforeSha256':object_hash(old),'afterSha256':object_hash(v),'dimensions':[k for k in v if old.get(k)!=v[k]]})
    h.validate_review_statuses(records,result)
    return result,changes,conflicts

def repair_crop(record,page):
    if record['regions'][0]['pdfPage']!=45:raise ValueError('Batch 1 only authorizes the confirmed page 45 recrop')
    if record.get('imageHistory'):return False
    old=copy.deepcopy({'images':record['images'],'regions':record['regions']})
    bounds=h.describe_page(page,45)['bbox'];scale=300/72
    pix=page.get_pixmap(matrix=fitz.Matrix(scale,scale),alpha=False,annots=True)
    full=Image.frombytes('RGB',(pix.width,pix.height),pix.samples);box=list((fitz.Rect(bounds)*fitz.Matrix(scale,scale)).irect);crop=full.crop(box)
    name=f'{record["id"]}-p045-qa1.webp';target=h.WORK/'images'/name
    crop.save(target,'WEBP',lossless=True,method=6)
    with Image.open(target) as decoded:
        if decoded.convert('RGB').tobytes()!=crop.tobytes():raise ValueError('Corrected crop is not source-pixel exact')
    record['imageHistory']=[{**old,'reason':'Batch 1: include complete horizontal output wires; degenerate path bounds were omitted'}]
    record['images']=[{'path':'images/'+name,'sha256':h.digest(target.read_bytes()),'pixelSha256':h.digest(crop.tobytes()),'width':crop.width,'height':crop.height,'bytes':target.stat().st_size,'dpi':300,'pdfPage':45,'pixelBox':box}]
    record['regions'][0]['bbox']=bounds
    return True

def validate_source_images(records,pdf):
    h.verify_assets(records)
    for r in records:
        for a,region in zip(r['images'],r['regions'],strict=True):
            p=pdf[region['pdfPage']-1];desc=h.describe_page(p,region['pdfPage'])
            if h.digest(desc['body'].encode())!=r['contentSha256']:raise ValueError('Raw question differs from source PDF')
            bounds=fitz.Rect(region['bbox'])
            scale=fitz.Matrix(a['dpi']/72,a['dpi']/72)
            if list((bounds*scale).irect)!=a['pixelBox'] or not p.rect.contains(bounds) or a['pdfPage']!=region['pdfPage']:raise ValueError('Image pixel box differs from crop geometry')
            if bounds.y1>=desc['footerY']:raise ValueError('Student image overlaps answer footer')
            for line in desc['lines']:
                if not bounds.contains(fitz.Rect(line['bbox'])):raise ValueError('Question crop cuts source text')
            for item in p.get_image_info():
                b=fitz.Rect(item['bbox'])
                # Some PDF image transforms extend fractions of a point off the page.
                # The source renderer clips that invisible area at the physical page edge.
                if b.y1<desc['footerY']-3 and b.get_area()<p.rect.get_area()*.9 and not bounds.contains(b & p.rect):raise ValueError(f'Question crop cuts an embedded image: PDF {region["pdfPage"]}')
            for d in p.get_drawings():
                b=fitz.Rect(d['rect']);pad=max(float(d.get('width') or 0)/2,.25)
                b=fitz.Rect(b.x0-pad,b.y0-pad,b.x1+pad,b.y1+pad)
                if b.y1<desc['footerY']-3 and b.get_area()<p.rect.get_area()*.9 and not bounds.contains(b):raise ValueError(f'Incomplete vector crop: PDF {region["pdfPage"]}')
            pix=p.get_pixmap(matrix=fitz.Matrix(a['dpi']/72,a['dpi']/72),alpha=False,annots=True)
            original=Image.frombytes('RGB',(pix.width,pix.height),pix.samples).crop(a['pixelBox'])
            with Image.open(h.WORK/a['path']) as decoded:
                if decoded.size!=(a['width'],a['height']) or decoded.convert('RGB').tobytes()!=original.tobytes() or h.digest(original.tobytes())!=a['pixelSha256']:raise ValueError('Source pixels or image metadata differ')
    return len(records)

def reconcile(apply=False,batch=1):
    if batch not in [1,2,3]:raise ValueError('Unsupported academic batch')
    folder=QA if batch==1 else h.WORK/f'qa-batch{batch}'
    records=h.read_json(h.WORK/'questions.json');reviews=h.read_json(h.WORK/'reviews.json');manifest=h.read_json(h.WORK/'manifest.json')
    if manifest.get('qaReconciliation',{}).get('batch',1)>batch:raise ValueError('A later batch is already reconciled; older batch replay is blocked')
    source_sha=h.digest(h.SOURCE.read_bytes())
    if source_sha!=manifest['sourceSha256']:raise ValueError('Historical source changed')
    if manifest.get('recordsSha256') and manifest['recordsSha256']!=h.digest((h.WORK/'questions.json').read_bytes()):raise ValueError('Question snapshot changed since source validation')
    if any(s['sha256']!=source_sha for r in records for s in r['sourceReferences']):raise ValueError('Question source identity differs from authorized PDF')
    audit_file=folder/{1:AUDIT,2:AUDIT2,3:AUDIT3}[batch]
    audit=h.read_json(audit_file);addon=h.read_json(folder/ADDENDUM) if batch==1 else None
    if batch>=2 and audit.get('batch')!=batch:raise ValueError('Advisory batch differs from selected reconciliation')
    validate_proposals(records,audit,addon,source_sha)
    decisions=h.read_json(folder/'decisions.json')
    if decisions is None:raise ValueError('Source-checked decisions must be prepared independently before reconciliation')
    inputs={'advisorySha256':h.digest(audit_file.read_bytes()),'decisionsSha256':object_hash(decisions)}
    if batch>=2:
        h.verify_source()
        companions=[audit_file,audit_file.with_suffix('.md'),audit_file.with_suffix('.csv')]
        inputs['advisoryFiles']={p.name:h.digest(p.read_bytes()) for p in companions}
        validate_companions(audit,companions[2].read_text('utf-8-sig'),companions[1].read_text('utf8'))
        validate_batch2_snapshot(folder,audit,source_sha,h.digest(TEXTBOOK.read_bytes()),inputs)
        if batch==3:
            with fitz.open(TEXTBOOK) as book:validate_batch3_book(audit,decisions,book)
    proposed=copy.deepcopy(records)
    with fitz.open(h.SOURCE) as pdf:
        # Dry-run does not generate or overwrite a crop; use the previously prepared reviewed crop.
        if batch==1:
            target=next(r for r in proposed if r['regions'][0]['pdfPage']==45)
            prepared=h.read_json(folder/'corrected-page45.json')
            if prepared is None:raise ValueError('Prepare and visually review the targeted page 45 crop first')
            if prepared['id']!=target['id'] or prepared['contentSha256']!=target['contentSha256']:raise ValueError('Prepared crop identity changed')
            target.update(images=prepared['images'],regions=prepared['regions'],imageHistory=prepared['imageHistory'])
        checked=validate_source_images(proposed,pdf)
    if batch==1:
        for r in proposed:
            r['examType']='FE';r['examTypeStatus']='owner-confirmed'
            r['examTypeProvenance']={'kind':'owner-confirmation','reference':'Batch 1 integration request, 2026-10-22, section 7'}
    updated,changes,conflicts=merge_reviews(proposed,reviews,audit['entries'],decisions,inputs['advisorySha256'],batch)
    if batch==3:
        baseline=h.read_json(folder/'before/reviews.json')
        scope={e['questionId'] for e in audit['entries']}
        for key,old in baseline.items():
            if key not in scope and updated.get(key)!=old:raise ValueError('Batch 3 changed a review outside its scope')
            if old['verification']['status']=='verified' and any(updated[key].get(k)!=old.get(k) for k in ['verification','explanation']):raise ValueError('Previously verified answer or explanation changed')
    report={'batch':batch,'batchQuestions':30,'sourcePixelComparisons':checked,'regeneratedCrops':sum(old['images']!=new['images'] for old,new in zip(records,proposed,strict=True)),'reviewChanges':len(changes),'academicConflicts':conflicts,**inputs,'changes':changes,'ownerApprovalsGranted':0}
    if apply:
        before={'questions':records,'reviews':reviews,'manifest':manifest};key=object_hash(before)
        history=folder/'history'/key
        if changes or records!=proposed:
            h.write_json(history/'snapshot.json',before);h.write_json(history/'changes.json',report)
            h.write_json(h.WORK/'questions.json',proposed);h.write_json(h.WORK/'reviews.json',updated)
        revised=h.manifest_for(proposed,source_sha,manifest['pdfPages'],manifest)
        revised['sourceHistory']=manifest.get('sourceHistory',[{'sourceSha256':source_sha,'importerFingerprint':manifest['importerFingerprint'],'kind':'original-extraction'}])
        prior=manifest.get('qaReconciliation',{});past=copy.deepcopy(prior.get('previousBatches',[]))
        if prior and prior.get('batch')!=batch:past.append({k:v for k,v in prior.items() if k!='previousBatches'})
        revised['qaReconciliation']={'batch':batch,'kind':'targeted-source-validated-reconciliation',**inputs,'manualSourcePages':37 if batch==1 else 30,'sourcePixelComparisons':checked,'regeneratedCrops':1 if batch==1 else 0,'unchangedCrops':332 if batch==1 else 333}
        if past:revised['qaReconciliation']['previousBatches']=past
        revised['recordsSha256']=h.digest((h.WORK/'questions.json').read_bytes())
        h.write_json(h.WORK/'manifest.json',revised);h.write_review_gallery(proposed)
        if batch>=2:h.write_json(folder/'applied-state.json',{'snapshot':snapshot_hashes(h.WORK),'inputs':inputs})
        stable={k:v for k,v in report.items() if k not in ['changes','reviewChanges','regeneratedCrops']}
        h.write_json(folder/'reconciliation-report.json',stable)
    print(json.dumps({**report,'changes':None,'dryRun':not apply},indent=2));return report

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--apply',action='store_true');parser.add_argument('--batch',type=int,choices=[1,2,3],default=1);args=parser.parse_args();reconcile(args.apply,args.batch)
