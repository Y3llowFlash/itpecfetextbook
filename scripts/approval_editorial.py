"""Strict transfer of two already validated transcriptions into native reviews."""
import copy
from pathlib import Path
import historical_questions as h
import academic_qa as qa

BASELINE='9bf34bf904788f88fe12e1cdc8531d82d27cf4f3'
SCOPE={'HIST-TECH01-2019A-Q012':22,'HIST-TECH01-2019S-Q023':28}


def folder():return h.WORK.parent/'approval-candidates'/h.WORK.name


def inputs():
    root=folder();context=h.read_json(root/'preparation-inputs.json')
    if not context or context.get('schema')!='itpec-final-candidate-preparation-v1' or context.get('baselineCommit')!=BASELINE or context.get('publicationApprovalGranted') is not False:
        raise ValueError('Missing owner-authorized candidate preparation baseline')
    for name,sha in context['files'].items():
        if Path(name).name!=name or h.digest((root/'before'/name).read_bytes())!=sha:
            raise ValueError('Stale preserved candidate preparation input')
    if qa.snapshot_hashes(root/'before')!=context['snapshot'] or len(context['questionIds'])!=36 or len(set(context['questionIds']))!=36:
        raise ValueError('Candidate baseline snapshot or exact scope changed')
    return context


def merge_native(records,reviews,repairs):
    if len(repairs)!=2 or {r['questionId'] for r in repairs}!=set(SCOPE):
        raise ValueError('Native accessibility transfer requires exactly pages 22 and 28')
    result=copy.deepcopy(reviews);source={r['id']:r for r in records}
    for repair in repairs:
        r=source[repair['questionId']];v=reviews[r['id']];before={k:v['extraction'][k] for k in ['imageDescription','optionText']}
        if repair.get('status')!='source-validated' or repair.get('reviewSha256')!=qa.object_hash(v) or repair.get('contentSha256')!=r['contentSha256'] or repair.get('imageSha256')!=r['images'][0]['sha256'] or repair.get('pdfPage')!=SCOPE[r['id']] or r['regions'][0]['pdfPage']!=repair['pdfPage'] or repair.get('before')!=before:
            raise ValueError('Stale or unvalidated accessibility overlay')
        after=repair.get('after',{});options=copy.deepcopy(before['optionText'])
        if repair['pdfPage']==28:options['d']='B AND (A OR B)'
        if set(after)!=set(before) or not isinstance(after.get('imageDescription'),str) or not after['imageDescription'].strip() or after['imageDescription']==before['imageDescription'] or after['optionText']!=options or not repair.get('sourceDiagramEvidence') or repair.get('validationMethod')!='visual-comparison-with-original-pdf-and-pixel-matched-crop':
            raise ValueError('Accessibility transfer changed unauthorized fields or lacks diagram evidence')
        if v.get('ownerAdjudication') or not h.valid_verification(r,v) or v.get('approval',{}).get('status')!='unapproved':
            raise ValueError('Accessibility transfer cannot alter owner cases or publication authority')
        x=result[r['id']]['extraction'];x.update(copy.deepcopy(after))
        x['editorialProvenance']={'kind':'validated-accessibility-overlay-transfer','priorReviewSha256':qa.object_hash(v),
            'overlaySha256':qa.object_hash(repair),'contentSha256':r['contentSha256'],'imageSha256':r['images'][0]['sha256'],'pdfPage':repair['pdfPage']}
    return result


def marker():
    context=inputs()
    return {'kind':'native-accessibility-transfer','baselineCommit':BASELINE,'inputsSha256':qa.object_hash(context),
        'overlayLedgerSha256':context['files']['repairs.json'],'changedQuestionIds':list(SCOPE),
        'engineSha256':h.digest(Path(__file__).read_bytes()),'publicationApprovalGranted':False}


def reconciled_reviews(metadata_only,state):
    if state.get('editorialReconciliation')!=marker():raise ValueError('Stale native editorial reconciliation receipt')
    before=h.read_json(folder()/'before/reviews.json')
    if metadata_only!=before:raise ValueError('Editorial transfer baseline differs from preserved metadata reconciliation')
    return merge_native(h.read_json(folder()/'before/questions.json'),before,h.read_json(folder()/'before/repairs.json')['repairs'])


def validate_rebound_repair(record,review,repair):
    context=inputs();old=h.read_json(folder()/'before/reviews.json');ledger=h.read_json(folder()/'before/repairs.json')
    expected=merge_native(h.read_json(folder()/'before/questions.json'),old,ledger['repairs'])[record['id']]
    original=next(r for r in ledger['repairs'] if r['questionId']==record['id'])
    rebound={**original,'reviewSha256':qa.object_hash(expected)}
    if review!=expected or repair!=rebound or context['sourceSha256']!=ledger['sourceSha256']:
        raise ValueError('Native transcription regressed or rebound overlay differs from validated source evidence')
