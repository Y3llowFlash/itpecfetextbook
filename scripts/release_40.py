"""Exact Release 2 authorization transition; uses the existing approval and publisher.

The reviewed preparation package is immutable. This receipt validates the allowed
approval-only transition and the resulting public payload without rebasing old
preparation snapshots. No academic, extraction, or mapping edit is permitted.
"""
import argparse
import copy
import json
import shutil
import subprocess
from pathlib import Path
import fitz
import historical_questions as h
import academic_qa as qa
import approval_candidates as c
from release_36 import checksum, unchanged_reviews

BASELINE='c23b7654992268b39e6666b86e47cf2b312e8b57'
PRODUCTION='88577fed721e24ef5db9fbbe07bd7fe1e4910d19'
MANIFEST_SHA='39bcc7b8ca0488bccfe61e5a66ab5ff7e61fa7e7310ff2b3089cc3449b85cea3'
SET_FP='4a887d4730c7c8e4f5a43ff7585bbb0081fa0b4fbb81463e7fb348e1c3853cf0'
FOLDER=h.ROOT/'.local/releases/historical-40'
RECEIPT=h.ROOT/'docs/development/evidence/historical-release-40.json'
SCOPE='Release 2: exact 40 Batch 2 Hardware questions and 15 source highlights'
PUBLIC_MUTATIONS={'public/data/questions.json','public/data/import-manifest.json','src/content/concepts.json','src/content/explanations.json','src/content/hardware-toc.json'}


def freeze(authorization):
    if FOLDER.exists():raise ValueError('Never overwrite the frozen release baseline')
    if subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()!=BASELINE:raise ValueError('Wrong reviewed commit')
    m=c.check(batch=2)
    if h.digest((c.batch02_folder()/'manifest.json').read_bytes())!=MANIFEST_SHA or m['candidateSetFingerprint']!=SET_FP:raise ValueError('Wrong authorized package')
    if any(not e['technicalEligibility'] or e['review'].get('ownerAdjudication') for e in m['candidates']):raise ValueError('Ineligible candidate')
    with fitz.open(h.SOURCE) as pdf:qa.validate_source_images([e['record'] for e in m['candidates']],pdf)
    auth=Path(authorization)
    if not auth.is_file():raise ValueError('Explicit owner authorization required')
    FOLDER.mkdir(parents=True);shutil.copyfile(auth,FOLDER/'owner-authorization.txt')
    for name in ['reviews.json','manifest.json']:shutil.copyfile(h.WORK/name,FOLDER/('before-'+name))
    for name,p in [('questions','public/data/questions.json'),('concepts','src/content/concepts.json'),('explanations','src/content/explanations.json')]:shutil.copyfile(h.ROOT/p,FOLDER/f'before-public-{name}.json')
    previous=h.read_json(h.ROOT/'.local/releases/historical-36/pages-current.json')
    if previous['canonical']['commit']!=PRODUCTION or previous['canonical']['status']!='success':raise ValueError('Production predecessor is not healthy')
    h.write_json(FOLDER/'pages-previous.json',previous)
    import hardware_batch02 as b
    state={'baselineCommit':BASELINE,'productionBaseline':PRODUCTION,'authorizationSha256':h.digest(auth.read_bytes()),'candidateManifestSha256':MANIFEST_SHA,
        'candidateSetFingerprint':SET_FP,'questionIds':m['questionIds'],'releasedQuestionIds':h.read_json(c.batch02_folder()/'preparation-inputs.json')['releasedQuestionIds'],
        'nativeQuestionsSha256':h.digest((h.WORK/'questions.json').read_bytes()),'sourceSha256':m['sourceSha256'],'textbookSha256':m['textbookSha256'],
        'protectedFiles':b.public_fingerprints(),'packageFiles':{str(p.relative_to(c.batch02_folder())):h.digest(p.read_bytes()) for p in c.batch02_folder().rglob('*') if p.is_file()},
        'nativeImages':{str(h.WORK/im['path']):im['sha256'] for r in h.read_json(h.WORK/'questions.json') for im in r['images']}}
    h.write_json(FOLDER/'state.json',state)
    print('Frozen exact authorization, package, original images, native reviews and 456-question baseline; zero new approvals.')


def context():
    state=h.read_json(FOLDER/'state.json');m=h.read_json(c.batch02_folder()/'manifest.json')
    if not state or state['baselineCommit']!=BASELINE or state['candidateManifestSha256']!=MANIFEST_SHA or state['candidateSetFingerprint']!=SET_FP:raise ValueError('Missing exact release baseline')
    if h.digest((FOLDER/'owner-authorization.txt').read_bytes())!=state['authorizationSha256'] or h.digest((c.batch02_folder()/'manifest.json').read_bytes())!=MANIFEST_SHA:raise ValueError('Authorization or reviewed package changed')
    if m['questionIds']!=state['questionIds'] or m['candidateSetFingerprint']!=SET_FP or len(set(m['questionIds']))!=40 or set(m['questionIds'])&set(state['releasedQuestionIds']):raise ValueError('Release scope changed')
    for name,sha in state['packageFiles'].items():
        if h.digest((c.batch02_folder()/name).read_bytes())!=sha:raise ValueError('Frozen approval package artifact changed: '+name)
    # Preparation implementation is checked against its immutable Git commit,
    # rather than silently rewriting its fingerprint after adding release gates.
    for name,sha in m['implementation'].items():
        original=subprocess.check_output(['git','show',BASELINE+':'+name],cwd=h.ROOT)
        if h.digest(original)!=sha:raise ValueError('Reviewed implementation binding changed')
    return state,m


def authorization_fields(state,entry):
    result={'candidateManifestSha256':MANIFEST_SHA,'candidateSetFingerprint':SET_FP,'approvalContextFingerprint':entry['approvalContextFingerprint'],
        'releaseAuthorization':{'instructionsSha256':state['authorizationSha256'],'scope':SCOPE,'contentSha256':entry['record']['contentSha256'],'imageSha256':entry['record']['images'][0]['sha256']}}
    if entry['highlightIntegration']['newConcept']:result['highlightEditorialAuthorization']=entry['highlightIntegration']['previewDefinitionSha256']
    return result


def verify_native(require_approved=True):
    state,m=context();records=h.read_json(h.WORK/'questions.json');reviews=h.read_json(h.WORK/'reviews.json');before=h.read_json(FOLDER/'before-reviews.json')
    unchanged_reviews(before,reviews,state['questionIds']);h.verify_source();h.verify_assets(records)
    if h.digest((h.WORK/'questions.json').read_bytes())!=state['nativeQuestionsSha256'] or h.digest(h.SOURCE.read_bytes())!=state['sourceSha256'] or h.digest(qa.TEXTBOOK.read_bytes())!=state['textbookSha256']:raise ValueError('Original source changed')
    for path,sha in state['nativeImages'].items():
        if h.digest(Path(path).read_bytes())!=sha:raise ValueError('Original image changed')
    c.validate_live_reviews(records,reviews,before,state['questionIds'],True)
    c.validate_batch02_approvals(m,records,reviews,MANIFEST_SHA)
    old=h.read_json(FOLDER/'before-manifest.json');current=h.read_json(h.WORK/'manifest.json')
    expected=copy.deepcopy(old);expected['approvedQuestions']=sum(h.valid_approval(r,reviews[r['id']]) for r in records)
    if current!=expected:raise ValueError('Native source/evidence/summary changed outside approval count')
    for e in m['candidates']:
        v=reviews[e['id']]
        if h.publication_fingerprint(e['record'],v)!=e['publicationFingerprint'] or not h.valid_verification(e['record'],v) or v.get('ownerAdjudication'):raise ValueError('Candidate answer/source content changed')
        if require_approved:
            if not h.valid_approval(e['record'],v) or any(v['approval'].get(k)!=value for k,value in authorization_fields(state,e).items()):raise ValueError('Missing exact owner authorization')
        elif v['approval']!=before[e['id']]['approval']:raise ValueError('Refuse to refresh an existing approval')
    excluded=set(reviews)-set(state['questionIds'])-set(state['releasedQuestionIds'])
    if len(excluded)!=257 or any(reviews[qid]['approval']['status']!='unapproved' for qid in excluded):raise ValueError('Excluded question approved')
    return state,m,records,reviews


def publisher_check():
    """Strict prepublication gate used by the existing Batch 2 publisher."""
    state,m,records,reviews=verify_native()
    import hardware_batch02 as b
    if b.public_fingerprints()!=state['protectedFiles']:raise ValueError('Prepublication 456-question source/public snapshot changed')
    frozen=h.read_json(c.batch02_folder()/'preparation-inputs.json')
    for name,sha in frozen['files'].items():
        if h.digest((b.WORK/name).read_bytes())!=sha:raise ValueError('Stale original Batch 2 input')
    concepts=c.batch02_concepts(frozen);highlights=c.validate_batch02_highlights(concepts)
    entries=c.batch02_entries(frozen,records,reviews,concepts,highlights)
    c.validate_batch02_package(m,entries,concepts,highlights,frozen)
    if len(highlights)!=15 or any(r['status']!='source-validated-pending-owner-editorial-approval' for r in highlights):raise ValueError('Unvalidated source highlight')
    return m


def approve():
    state,m,records,reviews=verify_native(False)
    # Validate every candidate and highlight before the first mutation.
    import hardware_batch02 as b
    if b.public_fingerprints()!=state['protectedFiles']:raise ValueError('Public baseline changed before approval')
    frozen=h.read_json(c.batch02_folder()/'preparation-inputs.json');concepts=c.batch02_concepts(frozen)
    c.validate_batch02_package(m,c.batch02_entries(frozen,records,reviews,concepts,c.validate_batch02_highlights(concepts)),concepts,c.validate_batch02_highlights(concepts),frozen)
    old=h.read_json(h.WORK/'manifest.json')
    for e in m['candidates']:
        h.approve(records,e['id'],'Project owner — explicit Release 2 authorization '+state['authorizationSha256'])
        live=h.read_json(h.WORK/'reviews.json');live[e['id']]['approval'].update(authorization_fields(state,e));h.write_json(h.WORK/'reviews.json',live)
    # Preserve the editorial reconciliation receipt discarded by generic summary regeneration.
    updated=h.read_json(h.WORK/'manifest.json');updated['editorialReconciliation']=old['editorialReconciliation'];h.write_json(h.WORK/'manifest.json',updated)
    publisher_check()
    h.write_json(FOLDER/'approvals.json',{'scope':SCOPE,'authorizationSha256':state['authorizationSha256'],'candidateManifestSha256':MANIFEST_SHA,'records':[{'id':qid,**h.read_json(h.WORK/'reviews.json')[qid]['approval']} for qid in state['questionIds']]})
    print('Exactly 40 new approvals; 36 existing approvals unchanged; 257 remain unapproved.')


def verify_public():
    state,m,records,reviews=verify_native();bank=h.read_json(h.ROOT/'public/data/questions.json');answers=h.read_json(h.ROOT/'src/content/explanations.json');concepts=h.read_json(h.ROOT/'src/content/concepts.json')
    previous=h.read_json(FOLDER/'before-public-questions.json');old_answers=h.read_json(FOLDER/'before-public-explanations.json');old_concepts=h.read_json(FOLDER/'before-public-concepts.json')
    index={q['id']:q for q in bank};explanations={e['questionId']:e for e in answers};ids=set(state['questionIds']);all_ids=ids|set(state['releasedQuestionIds'])
    if len(bank)!=496 or len(index)!=496 or len(previous)!=456 or {q['id'] for q in bank if q['format']=='historical'}!=all_ids:raise ValueError('Wrong public release scope')
    if any(index.get(q['id'])!=q for q in previous) or any(explanations.get(e['questionId'])!=e for e in old_answers):raise ValueError('Previous Practice/historical payload changed')
    for name,sha in state['protectedFiles'].items():
        if name not in PUBLIC_MUTATIONS and h.digest((h.ROOT/name).read_bytes())!=sha:raise ValueError('Unrelated application/source content changed: '+name)
    entries=[]
    for entry in m['candidates']:
        qid=entry['id'];q=index[qid];v=reviews[qid];e=explanations[qid];im=entry['record']['images'][0]
        full=copy.deepcopy(q);full['mapping']=q['review']['mappings'][0]
        if c.preview_visible(full,e)!=entry['studentVisible'] or q['mapping']!={k:v['mapping'][k] for k in ['headingNumber','subsectionId']}:raise ValueError('Published student content differs from exact preview: '+qid)
        if q['review']['approvalFingerprint']!=entry['publicationFingerprint'] or q['review']['mappings']!=[v['mapping']]:raise ValueError('Published approval or mapping differs')
        if q['image']['sha256']!=im['sha256'] or h.digest((h.ROOT/'public'/q['image']['src'].lstrip('/')).read_bytes())!=im['sha256']:raise ValueError('Original published image changed')
        definition=next(d for d in m['conceptDefinitions'] if d['id']==v['mapping']['conceptId']);concept=next(cpt for cpt in concepts if cpt['id']==definition['id'])
        if c.concept_view(concept)!=c.concept_view(definition) or concept['questionIds'].count(qid)!=1:raise ValueError('Reviewed concept/highlight changed')
        entries.append({'id':qid,'approvalFingerprint':entry['publicationFingerprint'],'approvalContextFingerprint':entry['approvalContextFingerprint'],'imageSha256':im['sha256'],'contentSha256':entry['record']['contentSha256'],
            'conceptId':concept['id'],'questionSha256':checksum(q),'explanationSha256':checksum(e),'mappingSha256':checksum(q['review']['mappings'])})
    for old in old_concepts:
        new=copy.deepcopy(next(cpt for cpt in concepts if cpt['id']==old['id']));new['questionIds']=[qid for qid in new['questionIds'] if qid not in ids];new['mappingEvidence']=[edge for edge in new['mappingEvidence'] if edge['questionId'] not in ids]
        if new!=old:raise ValueError('Existing concept or placements changed')
    new_concepts=[cpt for cpt in concepts if cpt['id'] not in {old['id'] for old in old_concepts}]
    if len(new_concepts)!=15 or len(concepts)!=28 or len(list((h.ROOT/'public/questions').iterdir()))!=496:raise ValueError('Image/highlight scope mismatch')
    # All public files added by promotion must be the forty original images.
    import hardware_batch02 as b
    if set(b.public_fingerprints())-set(state['protectedFiles'])!={'public'+index[qid]['image']['src'] for qid in ids}:raise ValueError('Unexpected public assets added')
    return {'schema':'itpec-historical-release-2-v1','preparationCommit':BASELINE,'candidateManifestSha256':MANIFEST_SHA,'candidateSetFingerprint':SET_FP,'authorizationSha256':state['authorizationSha256'],
        'scope':SCOPE,'authorizedCount':40,'excludedUnapproved':257,'practiceCount':420,'previousHistoricalCount':36,'historicalCount':76,'total':496,'images':496,'conceptCounts':m['conceptCounts'],
        'previousRecordsSha256':checksum({q['id']:q for q in previous}),'previousExplanationsSha256':checksum(old_answers),'previousConceptsSha256':checksum(old_concepts),'records':entries,'newHighlights':[{'id':d['id'],'definitionSha256':checksum(c.concept_view(d)),'sourceHighlight':d['sourceHighlight']} for d in m['conceptDefinitions'] if d['newConcept']]}


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('command',choices=['freeze','approve','verify','receipt']);parser.add_argument('--authorization',type=Path);args=parser.parse_args()
    if args.command=='freeze':freeze(args.authorization)
    elif args.command=='approve':approve()
    else:
        report=verify_public()
        if args.command=='receipt':
            if RECEIPT.exists() and h.read_json(RECEIPT)!=report:raise ValueError('Never renew a published approval receipt silently')
            h.write_json(RECEIPT,report)
        elif h.read_json(RECEIPT)!=report:raise ValueError('Stale publication receipt')
        print(json.dumps({'approved':40,'existingApprovalsUnchanged':36,'remainingPrivate':257,'total':496,'highlights':15,'receiptFingerprint':checksum(report)}))
