"""Validate the exhaustive private audit before the existing editorial pipeline runs.

This is a report/selection gate over native records, not another question store.
Neither recommendations nor this validator change academic or approval objects.
"""
from collections import Counter
import historical_questions as h
import academic_qa as qa
import catalog_audit as audit

DISPOSITIONS={'ready-for-batch07','repairable-for-batch07','deferred-protected','reclassified'}


def validate_inventory(ledger,records,before,pages,published,*,root=None):
    root=root or h.ROOT/'.local/historical-batches/technology01-hardware-batch07'
    report=h.read_json(root/'audit.json');triage=h.read_json(root/'uncertain-triage.json')
    original=h.read_json(audit.FOLDER/'decisions.json')
    categories={r['id']:r['classification']['category'] for r in original['entries']}
    public_ids={q['id'] for q in published};private=[r for r in records if r['id'] not in public_ids]
    counts=Counter(categories[r['id']] for r in private)
    if len(private)!=97 or counts!=Counter({'ch1':56,'other-vol1':29,'outside-vol1':3,'uncertain':9}):
        raise ValueError('Private classification baseline changed')
    expected={r['id'] for r in private if categories[r['id']]=='ch1'}
    if not report or report.get('schema')!='itpec-hardware-batch07-audit-v1' or report.get('beforeSnapshot')!=ledger['beforeSnapshot'] or report.get('sourceSha256')!=audit.SOURCE_SHA or report.get('textbookSha256')!=audit.BOOK_SHA or report.get('approvalGranted') is not False:
        raise ValueError('Missing or stale exhaustive audit')
    if ledger.get('auditSha256')!=h.digest((root/'audit.json').read_bytes()) or ledger.get('triageSha256')!=h.digest((root/'uncertain-triage.json').read_bytes()):raise ValueError('Audit/triage fingerprint changed')
    rows=report.get('questions',[]);ids=[r['id'] for r in rows]
    if len(ids)!=56 or len(set(ids))!=56 or set(ids)!=expected:
        raise ValueError('Exactly all 56 Hardware records require one disposition')
    byid={r['id']:r for r in records};selected={e['id'] for e in ledger['entries']}
    eligible=set()
    for row in rows:
        r=byid[row['id']];v=before[r['id']]
        if row.get('disposition') not in DISPOSITIONS or not row.get('decisionReason') or not row.get('nextAction'):
            raise ValueError('Missing or ambiguous audit disposition')
        if row.get('sourceBinding')!=qa.extraction_binding(r) or row.get('beforeReviewSha256')!=qa.object_hash(v) or row.get('pdfPage')!=r['regions'][0]['pdfPage'] or row.get('sourceImageIntegrity')!='pixel-matched' or row.get('academicVerified')!=h.valid_verification(r,v) or row.get('protected')!=bool(v.get('ownerAdjudication')):
            raise ValueError('Audit source, image, academic or native snapshot changed')
        evidence=row.get('textbookEvidence',[])
        if not evidence:raise ValueError('Every audit row requires actual source context')
        for ev in evidence:
            n=ev.get('pdfPage');excerpt=ev.get('checkedExcerpt','')
            if not isinstance(n,int) or not 1<=n<=len(pages):raise ValueError('Invalid audit source page')
            p=pages[n-1]
            if ev.get('sourceSha256')!=audit.BOOK_SHA or ev.get('textSha256')!=p['textSha256'] or ev.get('printedPage')!=p['printedPage'] or len(excerpt)<50 or excerpt not in h.norm(p['text']):
                raise ValueError('Audit textbook context is stale or invented')
        if row['disposition'] in {'ready-for-batch07','repairable-for-batch07'}:
            if row['protected'] or not row['academicVerified'] or not row.get('eligibleAfterRepairs') or not row.get('singleAnswerGrading') or row.get('blockers'):
                raise ValueError('Protected or blocked record claimed eligible')
            eligible.add(row['id'])
        elif not row.get('blockers'):raise ValueError('Deferred/reclassified record requires an explicit blocker')
    if selected!=eligible or not 1<=len(selected)<=40:
        raise ValueError('Select every eligible record up to 40; no uncertain replacements')
    uncertain={r['id'] for r in private if categories[r['id']]=='uncertain'}
    if not triage or triage.get('readOnly') is not True or triage.get('beforeSnapshot')!=ledger['beforeSnapshot'] or len(triage.get('questions',[]))!=9 or {r['id'] for r in triage['questions']}!=uncertain or uncertain&selected:
        raise ValueError('Exact nine-record read-only uncertain triage required')
    for row in triage['questions']:
        r=byid[row['id']]
        if row.get('beforeReviewSha256')!=qa.object_hash(before[r['id']]) or row.get('sourceBinding')!=qa.extraction_binding(r) or row.get('selected') is not False or not row.get('reason') or not row.get('nextAction'):
            raise ValueError('Uncertain triage changed native bindings or eligibility')
    return Counter(row['disposition'] for row in rows)
