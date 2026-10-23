"""Deterministic private reconciliation. Advisory JSON never supplies approval or verification authority."""
import argparse
import copy
import itertools
import json
import csv
import io
import re
from fractions import Fraction
from pathlib import Path
import fitz
from PIL import Image
import historical_questions as h

QA=h.WORK/'qa-batch1'
AUDIT='ITPEC_Chapter1_Academic_Audit_Batch01_With_Images.json'
ADDENDUM='ITPEC_Chapter1_Image_QA_Addendum.json'
AUDIT2='ITPEC_Chapter1_Academic_Audit_Batch02.json'
AUDIT3='ITPEC_Chapter1_Academic_Audit_Batch03.json'
AUDIT4='ITPEC_Chapter1_Academic_Audit_Batch04.json'
AUDIT5='ITPEC_Chapter1_Academic_Audit_Batch05.json'
PROTECTED_BATCH3_PAGES={110,112,119,180}
PROTECTED_BATCH4_PAGES=PROTECTED_BATCH3_PAGES|{152,179,181}
TEXTBOOK=Path('D:/ITPEC Old Questions/database/raw/FE Vol 1.pdf')
OWNER_SCOPE={110:('HIST-TECH01-2012A-Q001','c'),112:('HIST-TECH01-2012A-Q013','b'),
             119:('HIST-TECH01-2012A-Q030','a'),152:('HIST-TECH01-2010S-Q018','a'),
             179:('HIST-TECH01-2008A-Q017','b'),180:('HIST-TECH01-2008A-Q018','b'),181:('HIST-TECH01-2008A-Q020','c')}

def batch_size(batch):
    return 20 if batch==5 else 30

def object_hash(value):
    return h.digest(json.dumps(value,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode())

def validate_proposals(records,audit,addendum,source_sha):
    batch2=audit.get('schema')=='itpec-academic-audit-proposals-v2' and audit.get('batch') in [2,3,4,5]
    if not batch2 and (audit.get('schema')!='itpec-academic-audit-proposals-v1-with-image-addendum' or not addendum or addendum.get('schema')!='itpec-academic-image-audit-addendum-v1'):raise ValueError('Unsupported advisory schema')
    entries=audit.get('entries',[])
    count=audit.get('scope',{}).get('count') if batch2 else audit.get('questionCount')
    expected=batch_size(audit.get('batch',1))
    if len(entries)!=expected or count!=expected or len({e['questionId'] for e in entries})!=expected:raise ValueError(f'Batch must contain {expected} unique canonical IDs')
    if audit.get('batch')==5 and audit['scope'].get('recordIndexConvention')!='zero-based, original JSON array':raise ValueError('Batch 5 scope record-index convention changed')
    index={r['id']:r for r in records}
    for e in entries:
        r=index.get(e['questionId'])
        if not r or e['sourceSha256']!=source_sha or e['questionContentSha256']!=r['contentSha256'] or e['pdfPage'] not in [p['pdfPage'] for p in r['regions']]:raise ValueError(f'Stale or inconsistent proposal: {e["questionId"]}')
        if h.digest(r['rawText'].encode())!=r['contentSha256']:raise ValueError('Original transcript checksum changed')
        if batch2:
            # Batches 4/5 use zero-based record indices; PDF pages stay one-based.
            position=e.get('originalRecordIndex',-1 if audit['batch']>=4 else 0)
            offset=position if audit['batch']>=4 else position-1
            if not 0<=offset<len(records) or records[offset]['id']!=r['id']:raise ValueError('Canonical record index changed')
            if audit['batch']==5 and e.get('originalRecordIndexConvention')!='zero-based':raise ValueError('Batch 5 record-index convention changed')
            if e.get('printedAnswer')!=r.get('printedAnswer') or e.get('originalExtractionQuality')!=r.get('extractionQuality'):raise ValueError('Advisory source fields disagree')
            if e.get('reviewSnapshotSha256')!=audit['sourceSnapshot']['reviewFileSha256']:raise ValueError('Inconsistent review snapshot reference')
            if e.get('sourceOriginalImageReferences')!=[a['path'] for a in r['images']]:raise ValueError('Advisory image identity changed')
            if audit['batch']>=3:
                protected=PROTECTED_BATCH4_PAGES if audit['batch']>=4 else PROTECTED_BATCH3_PAGES
                if e['pdfPage'] in protected:raise ValueError(f'Protected unresolved page is outside Batch {audit["batch"]} authorization')
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
    expected=batch_size(audit.get('batch',2))
    if len(rows)!=expected or len(table)!=expected or len(entries)!=expected:raise ValueError(f'Companion documents must cover all {expected} proposals')
    for e,row,md in zip(entries,rows,table,strict=True):
        if audit.get('batch')==5:
            loc=e.get('textbookLocation') or {}
            fields=['Historical PDF page','Canonical question ID','Printed key','Independent answer proposal','Classification','Target volume','Target chapter','FE Vol 1 printed page','FE Vol 1 physical PDF page','Mapping status proposed','Source-grounded reasoning','Source QA flags']
            values=[e['pdfPage'],e['questionId'],e['printedAnswer'].upper(),e['independentProposedAnswer'].upper(),e['classification'],e['targetVolume'],e['targetChapter'],loc.get('printedPage'),loc.get('pdfPage'),e['mappingStatusProposed'],' '.join(e['reasoning']),'; '.join(e['flags'])]
            if [row.get(k) for k in fields]!=['' if v is None else str(v) for v in values]:raise ValueError('CSV disagrees with JSON advisory')
            location=f'{loc["printedPage"]} / {loc["pdfPage"]}' if loc else 'not established'
            if [s.strip(' `*') for s in md]!=[str(e['pdfPage']),e['questionId'].removeprefix('HIST-TECH01-'),e['independentProposedAnswer'].upper(),e['classification'],location,e['mappingStatusProposed']]:raise ValueError('Markdown table disagrees with JSON advisory')
            continue
        if audit.get('batch')==4:
            loc=e.get('textbookLocation') or {}
            fields=['PDF page','Question ID','Printed key','Answer proposal','Classification','Vol 1 printed p.','Vol 1 PDF p.','Mapping proposal','Answer reasoning / verification evidence','QA flags']
            values=[e['pdfPage'],e['questionId'],e['printedAnswer'].upper(),e['independentProposedAnswer'].upper(),e['classification'],loc.get('printedPage'),loc.get('pdfPage'),e['mappingStatusProposed'],' '.join(e['reasoning']),'; '.join(e['flags'])]
            if [row.get(k) for k in fields]!=['' if v is None else str(v) for v in values]:raise ValueError('CSV disagrees with JSON advisory')
            location=f'{loc["printedPage"]} / {loc["pdfPage"]}' if loc else 'Not established'
            if [s.strip(' `*') for s in md]!=[str(e['pdfPage']),e['questionId'].removeprefix('HIST-TECH01-'),e['independentProposedAnswer'].upper(),e['classification'],location,e['mappingStatusProposed']]:raise ValueError('Markdown table disagrees with JSON advisory')
            continue
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
    if batch>=3:
        count={3:249,4:276,5:306}[batch]
        if len(baseline)!=333 or sum(v['verification']['status']=='verified' for v in baseline.values())!=count:raise ValueError(f'Batch {batch} requires the preserved {count}-answer baseline')


def validate_batch3_book(audit,decisions,book):
    source_sha=h.digest(Path(book.name).read_bytes())
    for e in audit['entries']:
        loc=e.get('textbookLocation')
        if loc and (loc['sourceSha256']!=source_sha or h.digest(book[loc['pdfPage']-1].get_text().encode())!=loc['textPageSha256']):raise ValueError('Advisory textbook page checksum changed')
        if loc and audit.get('batch')==5 and (not loc.get('checkedExcerpt') or h.norm(loc['checkedExcerpt']) not in h.norm(book[loc['pdfPage']-1].get_text())):raise ValueError('Advisory textbook excerpt changed')
    for d in decisions.values():
        if d.get('classification',{}).get('category') in ['uncertain','outside-vol1']:
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
    relation=proof.get('relation','equivalent')
    if relation not in ['equivalent','not-equivalent']:raise ValueError('Unsupported source option relation')
    if relation=='not-equivalent':matches=[k for k in 'abcd' if k not in matches]
    if matches!=proof['expectedMatches']:raise ValueError(f'Source option truth tables disagree with claimed matches: {matches}')
    return {'matches':matches,'rows':rows}


def check_table_choices(proof):
    """Check every cell of a source multi-output truth-table alternative."""
    variables=proof['variables'];outputs=proof['outputs'];rows=[]
    for bits in itertools.product([0,1],repeat=len(variables)):
        values=dict(zip(variables,bits));rows.append([int(boolean(expr,values)) for expr in outputs])
    if set(proof['choices'])!=set('abcd'):raise ValueError('Table proof requires all four source choices')
    matches=[k for k in 'abcd' if proof['choices'][k]==rows]
    if matches!=proof['expectedMatches']:raise ValueError('Source table cells disagree with computed outputs')
    return {'matches':matches,'rows':rows}


def check_latch_choices(proof):
    """Solve cross-coupled gate equations; classify forbidden noncomplementary states separately."""
    if proof['gate'] not in ['nand','nor']:raise ValueError('Unsupported latch gate')
    rows=[]
    for s,r in itertools.product([0,1],repeat=2):
        states=[]
        for q,qbar in itertools.product([0,1],repeat=2):
            top=not (s and qbar) if proof['gate']=='nand' else not (r or qbar)
            bottom=not (r and q) if proof['gate']=='nand' else not (s or q)
            if (q,qbar)==(int(top),int(bottom)):states.append([q,qbar])
        rows.append('hold' if len(states)==2 else states[0] if len(states)==1 and states[0][0]!=states[0][1] else 'invalid')
    if set(proof['choices'])!=set('abcd'):raise ValueError('Latch proof requires all four source tables')
    matches=[k for k in 'abcd' if proof['choices'][k]==rows]
    if matches!=proof['expectedMatches']:raise ValueError('Latch source tables disagree with gate equations')
    return {'matches':matches,'rows':rows}

def check_observations(proof):
    variables=proof['variables']
    for row in proof['rows']:
        if len(row)!=len(variables)+1 or any(bit not in [0,1] for bit in row):raise ValueError('Invalid source observation table')
        if int(boolean(proof['expression'],dict(zip(variables,row[:-1]))))!=row[-1]:raise ValueError('Source observation disagrees with independently evaluated expression')
    return proof['rows']


def rational(expr,values=None):
    """Small exact-arithmetic proof language; no execution of advisory code."""
    if isinstance(expr,(int,str)):return Fraction(expr)
    op,*items=expr
    if op=='var':return Fraction((values or {})[items[0]])
    if op=='radix':
        number,base=items
        if not isinstance(base,int) or not 2<=base<=36 or not re.fullmatch(r'[0-9A-Za-z]+(?:\.[0-9A-Za-z]+)?',number):raise ValueError('Invalid radix literal')
        whole,_,part=number.partition('.')
        if any(int(c,36)>=base for c in whole+part):raise ValueError('Digit exceeds radix')
        return Fraction(int(whole,base))+sum((Fraction(int(c,36),base**i) for i,c in enumerate(part,1)),Fraction(0))
    if op not in ['add','sub','mul','div','pow','floor','ceil','xor']:raise ValueError('Unsupported exact-arithmetic operation')
    args=[rational(item,values) for item in items]
    if op=='add':return sum(args,Fraction(0))
    if op=='sub' and len(args)==2:return args[0]-args[1]
    if op=='mul':
        result=Fraction(1)
        for item in args:result*=item
        return result
    if op=='div' and len(args)==2:return args[0]/args[1]
    if op=='pow' and len(args)==2 and args[1].denominator==1:return args[0]**int(args[1])
    if op=='floor' and len(args)==1:return Fraction(args[0].numerator//args[0].denominator)
    if op=='ceil' and len(args)==1:return Fraction(-(-args[0].numerator//args[0].denominator))
    if op=='xor' and args and all(a.denominator==1 and a>=0 for a in args):
        result=0
        for item in args:result^=int(item)
        return Fraction(result)
    raise ValueError('Unsupported exact-arithmetic operation')


def check_numeric_choices(proof):
    if set(proof['choices'])!=set('abcd'):raise ValueError('Numeric proof requires all four original choices')
    comparison=proof.get('comparison','exact');cases=proof.get('cases',[{}]);rows=[]
    if comparison not in ['exact','nearest'] or not cases:raise ValueError('Invalid numeric comparison or empty cases')
    for values in cases:
        target=rational(proof['expression'],values);options={key:rational(value,values) for key,value in proof['choices'].items()}
        error={key:abs(value-target) for key,value in options.items()}
        matches=[key for key in 'abcd' if error[key]==(0 if comparison=='exact' else min(error.values()))]
        rows.append({'values':values,'result':str(target),'choices':{k:str(v) for k,v in options.items()},'matches':matches})
    matches=[key for key in 'abcd' if all(key in row['matches'] for row in rows)]
    if matches!=proof['expectedMatches']:raise ValueError('Exact calculation disagrees with source choice identity')
    return {'matches':matches,'rows':rows}

def extraction_binding(record):
    return {'contentSha256':record['contentSha256'],'images':[a['sha256'] for a in record['images']]}

def merge_reviews(records,reviews,entries,decisions,batch_hash,batch=1):
    result=copy.deepcopy(reviews);changes=[];conflicts=[];by_id={e['questionId']:e for e in entries}
    if set(by_id)-set(decisions):raise ValueError('Every proposal requires a separate source-checked decision')
    if batch>=2 and set(decisions)!=set(by_id):raise ValueError(f'Batch {batch} decisions must match exactly the {batch_size(batch)} advisory IDs')
    if batch>=3:
        protected=PROTECTED_BATCH4_PAGES if batch>=4 else PROTECTED_BATCH3_PAGES
        if any(region['pdfPage'] in protected for r in records if r['id'] in decisions for region in r['regions']):raise ValueError(f'Protected unresolved page is outside Batch {batch} authorization')
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
            for kind,checker in [('tableProofs',check_table_choices),('latchProofs',check_latch_choices),('numericProofs',check_numeric_choices)]:
                for proof in d.get(kind,[]):
                    matches=checker(proof)['matches']
                    if d.get('verification',{}).get('status')=='verified' and matches!=[d['verification']['independentAnswer']]:raise ValueError('Verified answer must match exactly one original table')
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
    if batch not in [1,2,3,4,5]:raise ValueError('Unsupported academic batch')
    folder=QA if batch==1 else h.WORK/f'qa-batch{batch}'
    records=h.read_json(h.WORK/'questions.json');reviews=h.read_json(h.WORK/'reviews.json');manifest=h.read_json(h.WORK/'manifest.json')
    if manifest.get('ownerAdjudication'):raise ValueError('Owner adjudication is already recorded; academic-batch replay is blocked')
    if manifest.get('qaReconciliation',{}).get('batch',1)>batch:raise ValueError('A later batch is already reconciled; older batch replay is blocked')
    source_sha=h.digest(h.SOURCE.read_bytes())
    if source_sha!=manifest['sourceSha256']:raise ValueError('Historical source changed')
    if manifest.get('recordsSha256') and manifest['recordsSha256']!=h.digest((h.WORK/'questions.json').read_bytes()):raise ValueError('Question snapshot changed since source validation')
    if any(s['sha256']!=source_sha for r in records for s in r['sourceReferences']):raise ValueError('Question source identity differs from authorized PDF')
    audit_file=folder/{1:AUDIT,2:AUDIT2,3:AUDIT3,4:AUDIT4,5:AUDIT5}[batch]
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
        if batch>=3:
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
    if batch>=3:
        baseline=h.read_json(folder/'before/reviews.json')
        scope={e['questionId'] for e in audit['entries']}
        for key,old in baseline.items():
            if key not in scope and updated.get(key)!=old:raise ValueError(f'Batch {batch} changed a review outside its scope')
            if old['verification']['status']=='verified' and any(updated[key].get(k)!=old.get(k) for k in ['verification','explanation']):raise ValueError('Previously verified answer or explanation changed')
    report={'batch':batch,'batchQuestions':batch_size(batch),'sourcePixelComparisons':checked,'regeneratedCrops':sum(old['images']!=new['images'] for old,new in zip(records,proposed,strict=True)),'reviewChanges':len(changes),'academicConflicts':conflicts,**inputs,'changes':changes,'ownerApprovalsGranted':0}
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
        revised['qaReconciliation']={'batch':batch,'kind':'targeted-source-validated-reconciliation',**inputs,'manualSourcePages':37 if batch==1 else batch_size(batch),'sourcePixelComparisons':checked,'regeneratedCrops':1 if batch==1 else 0,'unchangedCrops':332 if batch==1 else 333}
        if past:revised['qaReconciliation']['previousBatches']=past
        revised['recordsSha256']=h.digest((h.WORK/'questions.json').read_bytes())
        h.write_json(h.WORK/'manifest.json',revised);h.write_review_gallery(proposed)
        if batch>=2:h.write_json(folder/'applied-state.json',{'snapshot':snapshot_hashes(h.WORK),'inputs':inputs})
        stable={k:v for k,v in report.items() if k not in ['changes','reviewChanges','regeneratedCrops']}
        h.write_json(folder/'reconciliation-report.json',stable)
    print(json.dumps({**report,'changes':None,'dryRun':not apply},indent=2));return report


def merge_owner_decisions(records,reviews,package,instructions_sha):
    """Apply exactly the explicit seven owner selections; academic verification stays intact."""
    entries=package.get('entries',[]);scope={identity for identity,_ in OWNER_SCOPE.values()}
    if len(entries)!=7 or {e['questionId'] for e in entries}!=scope:raise ValueError('Owner adjudication requires exactly the seven authorized IDs')
    index={r['id']:r for r in records};updated=copy.deepcopy(reviews);changes=[]
    for entry in entries:
        identity=entry['questionId'];r=index[identity];old=reviews[identity]
        page=entry['pdfPage'];a=copy.deepcopy(entry['ownerAdjudication'])
        if OWNER_SCOPE.get(page)!=(identity,a.get('selectedAnswer')) or [p['pdfPage'] for p in r['regions']]!=[page]:raise ValueError('Owner answer or source-page identity differs from authorization')
        provenance=a.get('provenance',{})
        if provenance.get('instructionsSha256')!=instructions_sha or provenance.get('publicationApprovalGranted') is not False:raise ValueError('Owner instruction binding or publication restriction changed')
        if a.get('priorReviewSha256')!=object_hash(old) and old.get('ownerAdjudication')!=a:raise ValueError('Stale prior review fingerprint')
        if old.get('ownerAdjudication'):
            if old['ownerAdjudication']!=a or not h.valid_adjudication(r,old):raise ValueError('Changed or stale applied owner decision')
            continue
        if old.get('verification',{}).get('status')!='needs-review':raise ValueError('Owner scope must retain its unresolved independent-verification state')
        if a.get('gradingEligibility',{}).get('status')!='blocked' or a.get('publicationReadiness',{}).get('status')!='blocked':raise ValueError('This milestone does not enable grading or publication')
        if a.get('originalPrintedAnswer')!=r['printedAnswer']:raise ValueError('Original printed key changed')
        if page==119:
            if a.get('additionalMathematicallyValidAnswers')!=['d'] or a['gradingEligibility'].get('acceptedOptions')!=['a','d']:raise ValueError('Option D equivalence and grading blocker must be retained')
            if check_choice_proof(entry['choiceProof'])['matches']!=['a','d']:raise ValueError('Both A and D must match the source circuit')
        elif a.get('additionalMathematicallyValidAnswers'):raise ValueError('Unexpected additional accepted answer')
        corrections=a.get('editorialReconstructions',[])
        if page==112:
            if entry.get('reviewedOptions')!={'a':'1201','b':'1300','c':'2200','d':'2300'} or not any(c.get('status')=='owner-confirmed' and c.get('kind')=='missing-option-labels' for c in corrections):raise ValueError('Page 112 requires the owner-confirmed editorial option sequence')
        if page==179 and not any(c.get('literalSource')=='Exclusive-' and c.get('proposedText')=='Exclusive-OR' and c.get('status')=='probable-owner-proposal' for c in corrections):raise ValueError('Page 179 reconstruction must remain a probable proposal')
        for proof in entry.get('numericProofs',[]):check_numeric_choices(proof)
        new=updated[identity];new['ownerAdjudication']=a;new['explanation']=copy.deepcopy(a['studentExplanation'])
        if page==112:
            new['extraction']['optionText']=copy.deepcopy(entry['reviewedOptions'])
            new['extraction']['editorialTranscription']={'kind':'owner-confirmed-label-reconstruction','literalSourceLabels':['a'],
                'sourceFormattingNote':'The original PDF prints a) only; B/C/D labels are editorial, confirmed by the owner. The original crop is unchanged.',
                'instructionsSha256':instructions_sha}
        if not h.valid_adjudication(r,new):raise ValueError('Stale source/content/image binding or incomplete owner adjudication')
        # These dimensions are not an implicit grant of authority to owner selections.
        for dimension in ['verification','approval','metadata','classification','mapping','academicReviews']:
            if new.get(dimension)!=old.get(dimension):raise ValueError('Owner adjudication changed a protected review dimension')
        changes.append({'questionId':identity,'beforeSha256':object_hash(old),'afterSha256':object_hash(new)})
    for identity,old in reviews.items():
        if identity not in scope and updated[identity]!=old:raise ValueError('Owner adjudication changed an earlier verified review')
    h.validate_review_statuses(records,updated)
    return updated,changes


def validate_owner_snapshot(folder,package,inputs):
    baseline=snapshot_hashes(folder/'before')
    if baseline!=package.get('baselineSnapshot'):raise ValueError('Owner baseline snapshot checksum changed')
    actual=snapshot_hashes(h.WORK);applied=h.read_json(folder/'applied-state.json',{})
    if actual!=baseline and (actual!=applied.get('snapshot') or inputs!=applied.get('inputs')):raise ValueError('Stale owner-adjudication snapshot or changed inputs')
    before=h.read_json(folder/'before/reviews.json')
    if len(before)!=333 or sum(v['verification']['status']=='verified' for v in before.values())!=326:raise ValueError('Owner adjudication requires the 326-verified baseline')


def reconcile_owner(apply=False):
    folder=h.WORK/'owner-adjudication';package=h.read_json(folder/'decisions.json')
    if not package or package.get('schema')!='itpec-owner-adjudication-v1':raise ValueError('Missing source-checked owner decisions')
    if package.get('baselineCommit')!='b9f8829e7edc19ad8de6ec596e1844dc3f0ee1da':raise ValueError('Owner authorization baseline commit changed')
    instructions_sha=h.digest((folder/'owner-instructions.txt').read_bytes())
    if instructions_sha!=package.get('instructionsSha256'):raise ValueError('Owner instruction checksum changed')
    source_sha=h.digest(h.SOURCE.read_bytes());book_sha=h.digest(TEXTBOOK.read_bytes())
    if source_sha!=package['sourceSha256'] or book_sha!=package['textbookSha256']:raise ValueError('Owner source PDF checksum changed')
    inputs={'instructionsSha256':instructions_sha,'decisionsSha256':object_hash(package),
            'sourceSha256':source_sha,'textbookSha256':book_sha,
            'reviewEngineFingerprint':h.digest(Path(__file__).read_bytes()+Path(h.__file__).read_bytes())}
    validate_owner_snapshot(folder,package,inputs)
    records=h.read_json(h.WORK/'questions.json');reviews=h.read_json(h.WORK/'reviews.json');manifest=h.read_json(h.WORK/'manifest.json')
    baseline_records=h.read_json(folder/'before/questions.json');baseline_reviews=h.read_json(folder/'before/reviews.json')
    if records!=baseline_records or h.digest((h.WORK/'questions.json').read_bytes())!=package['baselineSnapshot']['questionFileSha256']:raise ValueError('Immutable original question snapshot changed')
    with fitz.open(h.SOURCE) as pdf:
        checked=validate_source_images(records,pdf)
        for page,(identity,_) in OWNER_SCOPE.items():
            record=next(r for r in records if r['id']==identity);desc=h.describe_page(pdf[page-1],page)
            if desc['answerKeys']!=[record['printedAnswer']] or desc['questionNumber']!=record['number']:raise ValueError('Owner source key or question number differs from original PDF')
            if (str(record['year']),'October' if record['season']=='A' else 'April') not in desc['dates']:raise ValueError('Owner source examination occurrence changed')
    evidence={e['questionId']:{'verification':{'evidence':e['ownerAdjudication']['supportingEvidence']}} for e in package['entries']}
    with fitz.open(TEXTBOOK) as book:validate_batch3_book({'entries':[]},evidence,book)
    updated,changes=merge_owner_decisions(records,reviews,package,instructions_sha)
    for identity,old in baseline_reviews.items():
        if old['verification']['status']=='verified' and updated[identity]!=old:raise ValueError('One of the 326 prior reviews changed')
    if any(v.get('approval',{}).get('status')!='unapproved' for v in updated.values()):raise ValueError('Publication approval is outside this milestone')
    if sum(h.valid_verification(r,updated[r['id']]) for r in records)!=326 or sum(h.valid_adjudication(r,updated[r['id']]) for r in records)!=7:raise ValueError('Independent and owner counts must remain separate')
    report={'kind':'final-owner-adjudication','scope':7,'reviewChanges':len(changes),'independentlyVerified':326,'newIndependentlyVerified':0,
            'ownerAdjudicated':7,'unadjudicated':0,'academicallyUnresolved':7,'publicationApprovals':0,'gradedPublicationBlocked':7,
            'sourcePixelComparisons':checked,'regeneratedCrops':0,**inputs}
    if apply and changes:
        h.write_json(folder/'history/changes.json',{'changes':changes,'report':report})
        h.write_json(h.WORK/'reviews.json',updated)
        revised=h.manifest_for(records,source_sha,manifest['pdfPages'],manifest)
        for key in ['sourceHistory','qaReconciliation','recordsSha256']:revised[key]=copy.deepcopy(manifest[key])
        # Review-only code changes alter the legacy whole-module importer fingerprint.
        # Revalidate all existing source pixels; record the migration without re-extracting.
        revised['sourceHistory'].append({'kind':'review-only-code-revalidation','sourceSha256':source_sha,
            'previousImporterFingerprint':manifest['importerFingerprint'],'validatedWithFingerprint':h.processing_fingerprint(),
            'existingCropsCompared':checked,'regeneratedCrops':0})
        revised['ownerAdjudication']={'kind':'owner-selected-historical-answers-not-publication-approval',**inputs,'questions':7}
        h.write_json(h.WORK/'manifest.json',revised);h.write_review_gallery(records)
        h.write_json(folder/'applied-state.json',{'snapshot':snapshot_hashes(h.WORK),'inputs':inputs})
        h.write_json(folder/'completion.json',{k:v for k,v in report.items() if k!='reviewChanges'})
    print(json.dumps({**report,'dryRun':not apply},indent=2));return report

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--apply',action='store_true')
    mode=parser.add_mutually_exclusive_group();mode.add_argument('--batch',type=int,choices=[1,2,3,4,5]);mode.add_argument('--owner-adjudication',action='store_true');mode.add_argument('--metadata',action='store_true')
    args=parser.parse_args()
    if args.metadata:
        from metadata_integration import reconcile as reconcile_metadata
        reconcile_metadata(args.apply)
    elif args.owner_adjudication:reconcile_owner(args.apply)
    else:reconcile(args.apply,args.batch or 1)
