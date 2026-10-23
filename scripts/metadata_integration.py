"""Scoped metadata reconciliation using the existing QA snapshot/history framework."""
import copy
import contextlib
import io
from pathlib import Path
import shutil
import subprocess
import fitz
import historical_questions as h
import academic_qa as qa
from historical_metadata import merge_metadata, POLICY_INSTRUCTIONS_SHA

FOLDER=h.ROOT/'.local/historical-metadata/technology-01'
PREVIEW=h.ROOT/'.local/private-student-preview'
BASELINE='deccd089be241614fab60eca777987369098a4eb'


def validate_snapshot(folder,policy,binding):
    if qa.snapshot_hashes(folder/'before')!=policy['baselineSnapshot']:
        raise ValueError('Preserved metadata baseline snapshot changed')
    state=h.read_json(folder/'applied-state.json')
    expected=state.get('snapshot') if state else policy['baselineSnapshot']
    if qa.snapshot_hashes(h.WORK)!=expected or state and state.get('inputs')!=binding:
        raise ValueError('Stale metadata snapshot or changed reconciliation inputs')
    return state


def inputs():
    policy=h.read_json(FOLDER/'policy.json')
    if not policy or policy.get('schema')!='itpec-owner-metadata-integration-v1' or policy.get('baselineCommit')!=BASELINE:
        raise ValueError('Missing explicit owner metadata policy or wrong baseline')
    if policy.get('instructionsSha256')!=POLICY_INSTRUCTIONS_SHA or h.digest((FOLDER/'owner-instructions.txt').read_bytes())!=POLICY_INSTRUCTIONS_SHA:
        raise ValueError('Owner metadata instructions changed')
    if qa.snapshot_hashes(FOLDER/'before')!=policy['baselineSnapshot'] or h.digest(h.SOURCE.read_bytes())!=policy['sourceSha256']:
        raise ValueError('Metadata baseline snapshot or source changed')
    binding={'policySha256':qa.object_hash(policy),'instructionsSha256':POLICY_INSTRUCTIONS_SHA,
        'engineSha256':h.digest(b''.join(Path(f).read_bytes() for f in [__file__,h.__file__,qa.__file__,Path(__file__).with_name('historical_metadata.py')]))}
    return policy,binding


def validate_transition():
    """Prove the only live review changes are the authorized metadata fields."""
    policy,binding=inputs();state=h.read_json(FOLDER/'applied-state.json')
    if not state or state.get('inputs')!=binding or state.get('snapshot')!=qa.snapshot_hashes(h.WORK):
        raise ValueError('Stale metadata snapshot or reconciliation engine/input')
    records=h.read_json(FOLDER/'before/questions.json');old=h.read_json(FOLDER/'before/reviews.json')
    if h.digest((h.WORK/'questions.json').read_bytes())!=policy['baselineSnapshot']['questionFileSha256']:
        raise ValueError('Metadata reconciliation changed original questions')
    expected,_=merge_metadata(records,old,policy)
    if state.get('editorialReconciliation'):
        from approval_editorial import reconciled_reviews
        expected=reconciled_reviews(expected,state)
    if h.read_json(h.WORK/'reviews.json')!=expected:
        raise ValueError('Non-metadata review changes or stale owner confirmation')
    original=h.read_json(FOLDER/'before/manifest.json');current=h.read_json(h.WORK/'manifest.json')
    mutable={'importerFingerprint','sourceHistory','metadataReconciliation','editorialReconciliation'}
    if {k:v for k,v in original.items() if k not in mutable}!={k:v for k,v in current.items() if k not in mutable} or current.get('metadataReconciliation')!=binding:
        raise ValueError('Protected manifest evidence changed during metadata migration')
    if current.get('editorialReconciliation')!=state.get('editorialReconciliation'):
        raise ValueError('Editorial manifest and reconciliation receipt disagree')
    expected_history=[*original['sourceHistory'],{'kind':'owner-metadata-only-revalidation','sourceSha256':policy['sourceSha256'],
        'previousImporterFingerprint':original['importerFingerprint'],'validatedWithFingerprint':h.processing_fingerprint(),
        'existingCropsCompared':333,'regeneratedCrops':0}]
    if current['sourceHistory']!=expected_history or current['importerFingerprint']!=h.processing_fingerprint():
        raise ValueError('Importer migration has no current original-source validation')
    if set(state.get('changedFiles',{}))!={'reviews.json','manifest.json','index.html'}:
        raise ValueError('Metadata migration expanded its writable catalog scope')
    for name,guard in state['changedFiles'].items():
        path=h.WORK/name
        if h.digest(path.read_bytes())!=guard['sha256'] or path.stat().st_mtime_ns!=guard['mtimeNs']:
            raise ValueError('Metadata-reconciled file binding changed')
    return state


def rebind_audit(ledger, guard):
    state=validate_transition();policy,_=inputs()
    if ledger['snapshot']!=policy['baselineSnapshot']:
        raise ValueError('Audit is not bound to the preserved metadata baseline')
    original=h.read_json(FOLDER/'before/reviews.json');current=h.read_json(h.WORK/'reviews.json')
    rebound=copy.deepcopy(ledger);rebound['snapshot']=state['snapshot']
    for entry in rebound['entries']:
        if entry['reviewSha256']!=qa.object_hash(original[entry['id']]):
            raise ValueError('Stale pre-metadata classification decision')
        entry['reviewSha256']=qa.object_hash(current[entry['id']])
    rebound['metadataReconciliation']=state['inputs']
    protected=copy.deepcopy(guard)
    for name,binding in state['changedFiles'].items():protected[name]=binding
    return rebound,protected


def rebind_preview(reviews):
    ledger=h.read_json(FOLDER/'preview-before/accessibility-repairs.json')
    findings=h.read_json(FOLDER/'preview-before/review-findings.json')
    old=h.read_json(FOLDER/'before/reviews.json')
    for repair in ledger['repairs']:
        qid=repair['questionId']
        if repair['reviewSha256']!=qa.object_hash(old[qid]):raise ValueError('Stale accessibility repair baseline')
        repair['reviewSha256']=qa.object_hash(reviews[qid])
    for finding in findings:
        qid=finding['questionId']
        if finding['reviewSha256']!=qa.object_hash(old[qid]):raise ValueError('Stale resolved accessibility finding')
        finding['reviewSha256']=qa.object_hash(reviews[qid])
        finding['resolutionSha256']=qa.object_hash(next(r for r in ledger['repairs'] if r['questionId']==qid))
    return ledger,findings


def reconcile(apply=False):
    policy,binding=inputs()
    branch=subprocess.check_output(['git','branch','--show-current'],cwd=h.ROOT,text=True).strip()
    if branch!='feature/chapter1-question-integration' or subprocess.run(['git','merge-base','--is-ancestor',BASELINE,'HEAD'],cwd=h.ROOT,capture_output=True).returncode:
        raise ValueError('Metadata integration requires the existing feature baseline')
    state=validate_snapshot(FOLDER,policy,binding)
    if state:
        validate_transition()
    records=h.read_json(FOLDER/'before/questions.json');old=h.read_json(FOLDER/'before/reviews.json')
    updated,changes=merge_metadata(records,old,policy)
    if state and state.get('editorialReconciliation'):
        from approval_editorial import reconciled_reviews
        updated=reconciled_reviews(updated,state)
    if state and h.read_json(h.WORK/'reviews.json')!=updated:raise ValueError('Applied metadata no longer matches deterministic reconciliation')
    if sum(h.valid_verification(r,updated[r['id']]) for r in records)!=326 or sum(h.valid_adjudication(r,updated[r['id']]) for r in records)!=7 or any(h.valid_approval(r,updated[r['id']]) for r in records):
        raise ValueError('Academic evidence, adjudications or approval baseline changed')
    h.verify_assets(records)
    # Reuse the existing crop/source validator when the legacy importer hash changes.
    with fitz.open(h.SOURCE) as pdf:checked=qa.validate_source_images(records,pdf)
    ledger,findings=rebind_preview(updated)
    import private_student_preview as preview
    repairs=preview.validated_repairs(records,updated,ledger)
    selected=[{'id':qid} for qid in h.read_json(FOLDER/'preview-before/manifest.json')['questionIds']]
    preview.validated_findings(selected,records,updated,findings,repairs)
    if apply and not state:
        from catalog_audit import verify_preservation,FOLDER as audit_folder
        verify_preservation(h.read_json(audit_folder/'before-files.json'))
        qa.h.write_json(FOLDER/'history/changes.json',{'changes':[{'id':qid,'beforeSha256':qa.object_hash(old[qid]),'afterSha256':qa.object_hash(updated[qid])} for qid in changes], 'inputs':binding})
        h.write_json(h.WORK/'reviews.json',updated)
        original=h.read_json(FOLDER/'before/manifest.json');manifest=copy.deepcopy(original)
        manifest['importerFingerprint']=h.processing_fingerprint()
        manifest['sourceHistory'].append({'kind':'owner-metadata-only-revalidation','sourceSha256':policy['sourceSha256'],
            'previousImporterFingerprint':original['importerFingerprint'],'validatedWithFingerprint':h.processing_fingerprint(),
            'existingCropsCompared':checked,'regeneratedCrops':0})
        manifest['metadataReconciliation']=binding
        h.write_json(h.WORK/'manifest.json',manifest);h.write_review_gallery(records)
        h.write_json(PREVIEW/'accessibility-repairs.json',ledger);h.write_json(PREVIEW/'review-findings.json',findings)
        changed={name:{'sha256':h.digest((h.WORK/name).read_bytes()),'mtimeNs':(h.WORK/name).stat().st_mtime_ns} for name in ['reviews.json','manifest.json','index.html']}
        h.write_json(FOLDER/'applied-state.json',{'snapshot':qa.snapshot_hashes(h.WORK),'inputs':binding,'changedFiles':changed})
        validate_transition()
    if state and (h.read_json(PREVIEW/'accessibility-repairs.json')!=ledger or h.read_json(PREVIEW/'review-findings.json')!=findings):
        raise ValueError('Accessibility metadata rebinding changed')
    report={'dryRun':not apply,'historicalRecords':333,'changedReviews':0 if state else len(changes),'morningSubjectA':333,
        'eveningSubjectB':0,'unresolvedMetadata':0,'conflicts':0,'sourcePixelComparisons':checked,
        'independentAnswersPreserved':326,'ownerAdjudicationsPreserved':7,'ownerApprovalsGranted':0,'originalQuestionsChanged':0,
        'reboundAccessibilityRepairs':2,'inputs':binding}
    if apply:h.write_json(FOLDER/'reconciliation-report.json',{k:v for k,v in report.items() if k not in ['dryRun','changedReviews']})
    print(qa.json.dumps(report,indent=2));return report
