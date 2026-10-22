"""Deterministic private reconciliation. Advisory JSON never supplies approval or verification authority."""
import argparse
import copy
import itertools
import json
import fitz
from PIL import Image
import historical_questions as h

QA=h.WORK/'qa-batch1'
AUDIT='ITPEC_Chapter1_Academic_Audit_Batch01_With_Images.json'
ADDENDUM='ITPEC_Chapter1_Image_QA_Addendum.json'

def object_hash(value):
    return h.digest(json.dumps(value,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode())

def validate_proposals(records,audit,addendum,source_sha):
    if audit.get('schema')!='itpec-academic-audit-proposals-v1-with-image-addendum' or addendum.get('schema')!='itpec-academic-image-audit-addendum-v1':raise ValueError('Unsupported advisory schema')
    entries=audit.get('entries',[])
    if len(entries)!=30 or audit.get('questionCount')!=30 or len({e['questionId'] for e in entries})!=30:raise ValueError('Batch must contain 30 unique canonical IDs')
    index={r['id']:r for r in records}
    for e in entries:
        r=index.get(e['questionId'])
        if not r or e['sourceSha256']!=source_sha or e['questionContentSha256']!=r['contentSha256'] or e['pdfPage'] not in [p['pdfPage'] for p in r['regions']]:raise ValueError(f'Stale or inconsistent proposal: {e["questionId"]}')
        if h.digest(r['rawText'].encode())!=r['contentSha256']:raise ValueError('Original transcript checksum changed')
    for e in addendum['visualFindings']:
        r=index.get(e['questionId'])
        if not r or e['pdfPage'] not in [p['pdfPage'] for p in r['regions']]:raise ValueError('Visual proposal identity mismatch')
        images=r['images']+[a for history in r.get('imageHistory',[]) for a in history['images']]
        if not any(a['path']==e['imageFile'] and a['sha256']==e['imageSha256'] for a in images):raise ValueError(f'Stale visual image: {e["questionId"]}')
    return index

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

def extraction_binding(record):
    return {'contentSha256':record['contentSha256'],'images':[a['sha256'] for a in record['images']]}

def merge_reviews(records,reviews,entries,decisions,batch_hash):
    result=copy.deepcopy(reviews);changes=[];conflicts=[];by_id={e['questionId']:e for e in entries}
    if set(by_id)-set(decisions):raise ValueError('Every Batch 1 proposal requires a separate source-checked decision')
    for r in records:
        old=copy.deepcopy(result.get(r['id'],{}));v=result.setdefault(r['id'],{})
        if v.get('contentSha256')!=r['contentSha256']:raise ValueError('Existing review content binding is stale')
        meta=v.setdefault('metadata',{})
        meta.update(examType='FE',examTypeStatus='owner-confirmed',examTypeEvidence={'kind':'owner-confirmation','reference':'Batch 1 integration request, 2026-10-22, section 7','sourceSha256':r['sourceReferences'][0]['sha256']})
        # FE confirmation is not evidence of paper or subject. Keep the aggregate gate pending.
        if not meta.get('paper') or not meta.get('subject'):meta['status']='needs-review'
        d=decisions.get(r['id'])
        if d:
            if d.get('contentSha256')!=r['contentSha256'] or d.get('sourceChecked') is not True or d.get('imageHashes')!=[a['sha256'] for a in r['images']]:raise ValueError(f'Stale independent decision: {r["id"]}')
            if d.get('classification',{}).get('category','ch1') not in ['ch1','other-vol1','outside-vol1','uncertain']:raise ValueError('Unsupported textbook classification')
            for proof in d.get('booleanProofs',[]):check_proof(proof)
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
            provenance={'batch':1,'advisorySha256':batch_hash,'decisionSha256':object_hash(d),'status':'source-reconciled-not-owner-approved'}
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

def reconcile(apply=False):
    records=h.read_json(h.WORK/'questions.json');reviews=h.read_json(h.WORK/'reviews.json');manifest=h.read_json(h.WORK/'manifest.json')
    source_sha=h.digest(h.SOURCE.read_bytes())
    if source_sha!=manifest['sourceSha256']:raise ValueError('Historical source changed')
    if manifest.get('recordsSha256') and manifest['recordsSha256']!=h.digest((h.WORK/'questions.json').read_bytes()):raise ValueError('Question snapshot changed since source validation')
    if any(s['sha256']!=source_sha for r in records for s in r['sourceReferences']):raise ValueError('Question source identity differs from authorized PDF')
    audit=h.read_json(QA/AUDIT);addon=h.read_json(QA/ADDENDUM);validate_proposals(records,audit,addon,source_sha)
    decisions=h.read_json(QA/'decisions.json')
    if decisions is None:raise ValueError('Source-checked decisions must be prepared independently before reconciliation')
    proposed=copy.deepcopy(records)
    with fitz.open(h.SOURCE) as pdf:
        # Dry-run does not generate or overwrite a crop; use the previously prepared reviewed crop.
        target=next(r for r in proposed if r['regions'][0]['pdfPage']==45)
        prepared=h.read_json(QA/'corrected-page45.json')
        if prepared is None:raise ValueError('Prepare and visually review the targeted page 45 crop first')
        if prepared['id']!=target['id'] or prepared['contentSha256']!=target['contentSha256']:raise ValueError('Prepared crop identity changed')
        target.update(images=prepared['images'],regions=prepared['regions'],imageHistory=prepared['imageHistory'])
        checked=validate_source_images(proposed,pdf)
    for r in proposed:
        r['examType']='FE';r['examTypeStatus']='owner-confirmed'
        r['examTypeProvenance']={'kind':'owner-confirmation','reference':'Batch 1 integration request, 2026-10-22, section 7'}
    updated,changes,conflicts=merge_reviews(proposed,reviews,audit['entries'],decisions,h.digest((QA/AUDIT).read_bytes()))
    report={'batchQuestions':30,'sourcePixelComparisons':checked,'regeneratedCrops':sum(old['images']!=new['images'] for old,new in zip(records,proposed,strict=True)),'reviewChanges':len(changes),'academicConflicts':conflicts,'advisorySha256':h.digest((QA/AUDIT).read_bytes()),'decisionsSha256':object_hash(decisions),'changes':changes,'ownerApprovalsGranted':0}
    if apply:
        before={'questions':records,'reviews':reviews,'manifest':manifest};key=object_hash(before)
        history=QA/'history'/key
        if changes or records!=proposed:
            h.write_json(history/'snapshot.json',before);h.write_json(history/'changes.json',report)
            h.write_json(h.WORK/'questions.json',proposed);h.write_json(h.WORK/'reviews.json',updated)
        revised=h.manifest_for(proposed,source_sha,manifest['pdfPages'],manifest)
        revised['sourceHistory']=manifest.get('sourceHistory',[{'sourceSha256':source_sha,'importerFingerprint':manifest['importerFingerprint'],'kind':'original-extraction'}])
        revised['qaReconciliation']={'batch':1,'kind':'targeted-source-validated-reconciliation','advisorySha256':report['advisorySha256'],'decisionsSha256':report['decisionsSha256'],'manualSourcePages':37,'sourcePixelComparisons':checked,'regeneratedCrops':1,'unchangedCrops':332}
        revised['recordsSha256']=h.digest((h.WORK/'questions.json').read_bytes())
        h.write_json(h.WORK/'manifest.json',revised);h.write_review_gallery(proposed)
        stable={k:v for k,v in report.items() if k not in ['changes','reviewChanges','regeneratedCrops']}
        h.write_json(QA/'reconciliation-report.json',stable)
    print(json.dumps({**report,'changes':None,'dryRun':not apply},indent=2));return report

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--apply',action='store_true');args=parser.parse_args();reconcile(args.apply)
