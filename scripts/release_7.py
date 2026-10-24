"""Exact Release 7 authorization transition; uses the existing approval and publisher.

The reviewed preparation package is immutable. This receipt validates the allowed
approval-only transition and the resulting public payload without rebasing old
preparation snapshots. No academic, extraction, or mapping edit is permitted.
"""
import argparse
import copy
import json
import shutil
import subprocess
from contextlib import contextmanager
from unittest.mock import patch
from pathlib import Path
import fitz
import historical_questions as h
import academic_qa as qa
import approval_candidates as c
import approval_batch07 as f
from release_36 import checksum, unchanged_reviews

BASELINE='fdc4b4698434804ab5fb794f5f60b86a94965f67'
PRODUCTION='1f179640110a374b2329664567eca63218bce344'
MANIFEST_SHA='5357a9fcb55554b2620a03d1333a6ced1e6d9740b63ad5fa419641df52eca2d8'
SET_FP='c2a48d56ec7a0e0474e96c8da2e2bb132bf27a28033e8dae2560b0e8d93fb2a6'
FOLDER=h.ROOT/'.local/releases/historical-31-batch07'
RECEIPT=h.ROOT/'docs/development/evidence/historical-release-7.json'
SCOPE='Release 7: exact 31 Batch 7 Hardware questions and zero new highlights; eight existing highlights reused'
PUBLIC_MUTATIONS={'public/data/questions.json','public/data/import-manifest.json','src/content/concepts.json','src/content/explanations.json','src/content/hardware-toc.json'}


def freeze(authorization):
    if FOLDER.exists():raise ValueError('Never overwrite the frozen release baseline')
    if subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()!=BASELINE:raise ValueError('Wrong reviewed commit')
    if subprocess.check_output(['git','status','--porcelain'],text=True).strip().splitlines() not in [[],['?? scripts/release_7.py']]:raise ValueError('Unrelated working-tree changes before release freeze')
    if subprocess.check_output(['git','rev-parse','origin/main'],text=True).strip()!=PRODUCTION:raise ValueError('Remote main advanced')
    m=c.check(batch=7)
    if h.digest((f.folder()/'manifest.json').read_bytes())!=MANIFEST_SHA or m['candidateSetFingerprint']!=SET_FP:raise ValueError('Wrong authorized package')
    if len(m['candidates'])!=31 or len(m['conceptDefinitions'])!=8 or m['highlightIntegration'] or any(d['newConcept'] for d in m['conceptDefinitions']):raise ValueError('Exact thirty-one candidates and zero new highlights required')
    if any(not e['technicalEligibility'] or e['review'].get('ownerAdjudication') for e in m['candidates']):raise ValueError('Ineligible candidate')
    if any(e['remainingBlockers']!=['final-owner-publication-approval-absent'] for e in m['candidates']):raise ValueError('A substantive publication blocker remains')
    with fitz.open(h.SOURCE) as pdf:qa.validate_source_images([e['record'] for e in m['candidates']],pdf)
    auth=Path(authorization)
    if not auth.is_file():raise ValueError('Explicit owner authorization required')
    FOLDER.mkdir(parents=True);shutil.copyfile(auth,FOLDER/'owner-authorization.txt')
    for name in ['reviews.json','manifest.json']:shutil.copyfile(h.WORK/name,FOLDER/('before-'+name))
    for name,p in [('questions','public/data/questions.json'),('concepts','src/content/concepts.json'),('explanations','src/content/explanations.json')]:shutil.copyfile(h.ROOT/p,FOLDER/f'before-public-{name}.json')
    previous=h.read_json(h.ROOT/'.local/release07-preflight/pages-current.json')
    if previous['canonical']['commit']!=PRODUCTION or previous['canonical']['status']!='success' or previous['canonical']['id']!='31e8863f-6f92-497c-bc59-78211a759af3':raise ValueError('Production predecessor is not healthy')
    h.write_json(FOLDER/'pages-previous.json',previous)
    import hardware_batch02 as b
    state={'baselineCommit':BASELINE,'productionBaseline':PRODUCTION,'expectedPreviousDeployment':'31e8863f-6f92-497c-bc59-78211a759af3','authorizationSha256':h.digest(auth.read_bytes()),'candidateManifestSha256':MANIFEST_SHA,
        'candidateSetFingerprint':SET_FP,'questionIds':m['questionIds'],'releasedQuestionIds':h.read_json(f.folder()/'preparation-inputs.json')['releasedQuestionIds'],
        'implementationByteRepresentations':reviewed_implementation(m),
        'nativeQuestionsSha256':h.digest((h.WORK/'questions.json').read_bytes()),'sourceSha256':m['sourceSha256'],'textbookSha256':m['textbookSha256'],
        'protectedFiles':b.public_fingerprints(),'packageFiles':{str(p.relative_to(f.folder())):h.digest(p.read_bytes()) for p in f.folder().rglob('*') if p.is_file()},
        'preparationFiles':{str(p.relative_to(f.b.WORK)):h.digest(p.read_bytes()) for p in f.b.WORK.rglob('*') if p.is_file()},
        'operationalRisk':'Release 6: 55 unexplained HTML hash differences; live HTML/UI transport blocked; no confirmed regression; no automatic rollback.',
        'nativeImages':{str(h.WORK/im['path']):im['sha256'] for r in h.read_json(h.WORK/'questions.json') for im in r['images']}}
    h.write_json(FOLDER/'state.json',state)
    print('Frozen exact authorization, package, original images, native reviews and 656-question baseline; zero new approvals.')


def reviewed_implementation(manifest):
    result={}
    for name,sha in manifest['implementation'].items():
        try:raw=subprocess.check_output(['git','show',BASELINE+':'+name],cwd=h.ROOT,stderr=subprocess.PIPE)
        except subprocess.CalledProcessError as error:raise ValueError('Missing reviewed implementation: '+name) from error
        if h.digest(raw)==sha:mode='exact-git-bytes'
        elif b'\r' not in raw and h.digest(raw.replace(b'\n',b'\r\n'))==sha:mode='exact-reviewed-crlf-checkout'
        else:raise ValueError('Reviewed implementation binding changed: '+name)
        result[name]={'gitSha256':h.digest(raw),'reviewedSha256':sha,'representation':mode}
    return result


def context():
    state=h.read_json(FOLDER/'state.json');m=h.read_json(f.folder()/'manifest.json')
    if not state or state['baselineCommit']!=BASELINE or state['candidateManifestSha256']!=MANIFEST_SHA or state['candidateSetFingerprint']!=SET_FP:raise ValueError('Missing exact release baseline')
    if h.digest((FOLDER/'owner-authorization.txt').read_bytes())!=state['authorizationSha256'] or h.digest((f.folder()/'manifest.json').read_bytes())!=MANIFEST_SHA:raise ValueError('Authorization or reviewed package changed')
    if m['questionIds']!=state['questionIds'] or m['candidateSetFingerprint']!=SET_FP or len(set(m['questionIds']))!=31 or set(m['questionIds'])&set(state['releasedQuestionIds']):raise ValueError('Release scope changed')
    for name,sha in state['packageFiles'].items():
        if h.digest((f.folder()/name).read_bytes())!=sha:raise ValueError('Frozen approval package artifact changed: '+name)
    for name,sha in state['preparationFiles'].items():
        if h.digest((f.b.WORK/name).read_bytes())!=sha:raise ValueError('Frozen preparation artifact changed: '+name)
    frozen=h.read_json(f.folder()/'preparation-inputs.json')
    for name in ['reviews.json','manifest.json']:
        if h.digest((FOLDER/('before-'+name)).read_bytes())!=frozen['nativeFiles'][name]:raise ValueError('Release native baseline differs from reviewed preparation')
    for name,source in [('questions','public/data/questions.json'),('concepts','src/content/concepts.json'),('explanations','src/content/explanations.json')]:
        if h.digest((FOLDER/f'before-public-{name}.json').read_bytes())!=state['protectedFiles'][source]:raise ValueError('Release public baseline changed')
    # Preparation implementation is checked against its immutable Git commit,
    # rather than silently rewriting its fingerprint after adding release gates.
    if reviewed_implementation(m)!=state['implementationByteRepresentations']:raise ValueError('Reviewed implementation binding changed')
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
    if len(records)!=333 or len(state['releasedQuestionIds'])!=236 or len(set(state['questionIds']))!=31:raise ValueError('Historical scope changed')
    for e in m['candidates']:
        v=reviews[e['id']]
        if h.publication_fingerprint(e['record'],v)!=e['publicationFingerprint'] or not h.valid_verification(e['record'],v) or v.get('ownerAdjudication'):raise ValueError('Candidate answer/source content changed')
        if require_approved:
            if not h.valid_approval(e['record'],v) or any(v['approval'].get(k)!=value for k,value in authorization_fields(state,e).items()):raise ValueError('Missing exact owner authorization')
        elif v['approval']!=before[e['id']]['approval']:raise ValueError('Refuse to refresh an existing approval')
    excluded=set(reviews)-set(state['questionIds'])-set(state['releasedQuestionIds'])
    if len(excluded)!=66 or any(reviews[qid]['approval']['status']!='unapproved' for qid in excluded):raise ValueError('Excluded question approved')
    return state,m,records,reviews


def validate_package():
    state,m=context();frozen=h.read_json(f.folder()/'preparation-inputs.json')
    records=h.read_json(h.WORK/'questions.json');reviews=h.read_json(FOLDER/'before-reviews.json')
    for name,sha in frozen['files'].items():
        if h.digest((f.folder()/'before/batch'/name).read_bytes())!=sha:raise ValueError('Stale original Batch 7 input')
    concepts=m['conceptDefinitions']
    old_concepts={d['id']:d for d in h.read_json(FOLDER/'before-public-concepts.json')}
    if len(concepts)!=8 or sum(d['newConcept'] for d in concepts)!=0:raise ValueError('Wrong final concept scope')
    for d in concepts:
        if not d['newConcept'] and c.concept_view(d)!=c.concept_view(old_concepts[d['id']]):raise ValueError('Reused highlight changed')
    links=f.associations(frozen,records,reviews,concepts)
    rows,highlights=c.validate_batch03_reviews(frozen,records,reviews,concepts,links,root=f.folder(),expected_highlights=0,review_schema='itpec-batch07-final-source-review-v1',existing_concepts=FOLDER/'before-public-concepts.json')
    entries=f.entries(frozen,records,reviews,concepts,links,rows,highlights)
    c.validate_final_package(m,entries,concepts,highlights,frozen,batch=7,expected_count=31)
    if len(highlights)!=0 or any(r['status']!='source-validated-pending-owner-editorial-approval' for r in highlights):raise ValueError('Unvalidated source highlight')
    if m['previewEquality']!={'questions':31,'conceptDefinitionsEqual':8,'allStudentVisibleFieldsEqual':True,'fields':list(entries[0]['studentVisible']),'academicChanges':0} or m['finalVisualReview']!=rows or (f.folder()/'index.html').read_text('utf8')!=f.gallery(m,concepts):raise ValueError('Frozen visible payload changed')
    return m


def publisher_check():
    """Exact owner-authorized prepublication gate; public baseline cannot change."""
    state,m,records,reviews=verify_native()
    import hardware_batch02 as b
    if b.public_fingerprints()!=state['protectedFiles']:raise ValueError('Prepublication 656-question source/public snapshot changed')
    validate_package()
    return m


def publication_gate():
    state,m= context();publisher_check()
    dry=h.read_json(FOLDER/'publisher-dry-run.json')
    if not dry or dry.get('dryRun') is not True or dry.get('approvedInputs')!=267 or len(dry.get('additions',[]))!=31 or set(dry['additions'])!=set(state['questionIds']) or dry.get('updates') or dry.get('conflicts'):raise ValueError('Exact successful Release 7 dry run required before publication')
    expected={'reviewsSha256':h.digest((h.WORK/'reviews.json').read_bytes()),'publisherSha256':h.digest((h.ROOT/'scripts/publish-historical-questions.ts').read_bytes()),'resultSha256':checksum(dry),'manifestSha256':MANIFEST_SHA}
    if h.read_json(FOLDER/'dry-run-evidence.json')!=expected:raise ValueError('Stale Release 7 dry run binding')


def archived_inputs():
    """Validate original read-only evidence without pretending live approvals are absent."""
    state,m=context();validate_package()
    frozen=h.read_json(f.folder()/'preparation-inputs.json')
    records=h.read_json(h.WORK/'questions.json');reviews=h.read_json(FOLDER/'before-reviews.json')
    if h.digest((h.WORK/'questions.json').read_bytes())!=state['nativeQuestionsSha256']:raise ValueError('Immutable source catalog changed')
    for name,sha in frozen['nativeFiles'].items():
        if h.digest((f.folder()/'before/native'/name).read_bytes())!=sha:raise ValueError('Original native preparation snapshot changed')
    for name,sha in state['protectedFiles'].items():
        if name not in PUBLIC_MUTATIONS and h.digest((h.ROOT/name).read_bytes())!=sha:raise ValueError('Protected source/application changed')
    return frozen,records,reviews,reviews


def archived_preview():
    import hardware_batch07 as b
    state,m=context();manifest=h.read_json(b.WORK/'preview/manifest.json')
    frozen=h.read_json(f.folder()/'preparation-inputs.json')
    if h.digest((b.WORK/'preview/manifest.json').read_bytes())!=frozen['files']['preview/manifest.json']:raise ValueError('Reviewed preview binding changed')
    for name,sha in manifest['appSources'].items():
        if h.digest((b.APP/name).read_bytes())!=sha:raise ValueError('Private preview source changed')
    for asset in manifest['assets'].values():
        file=Path(asset['path']).resolve()
        if not (file.is_relative_to((b.APP/'dist').resolve()) or file.is_relative_to((h.WORK/'images').resolve())) or h.digest(file.read_bytes())!=asset['sha256']:raise ValueError('Private preview asset changed')
    # Recompute equality with frozen unapproved reviews, independent of live approval status.
    archived_inputs()
    return manifest


@contextmanager
def preparation_fixture():
    """Run unchanged preparation assertions against their explicit frozen baseline.

    Only test/archival reads are redirected. Live publication gates always inspect
    the real catalog and never enter this context.
    """
    import hardware_batch07 as b
    context,records,current,_=archived_inputs()
    ledger=h.read_json(b.WORK/'decisions.json');before=h.read_json(b.WORK/'before/reviews.json')
    published=h.read_json(FOLDER/'before-public-questions.json')
    nodes=json.loads(subprocess.check_output(['git','show',PRODUCTION+':src/content/hardware-toc.json'],cwd=h.ROOT))['nodes']
    entries=b.core.validate_decisions(records,before,ledger,b.core.book_pages(),published,ledger['concepts'],nodes,spec=b.SPEC)
    expected=b.core.reconcile(records,before,entries,h.digest((b.WORK/'decisions.json').read_bytes()),draft_history=ledger.get('draftHistory'),milestone='technology01-hardware-batch07')
    b.core.validate_transition(records,before,current,expected,set(context['questionIds']),approved_count=236)
    original_read=h.read_json;original_snapshot=qa.snapshot_hashes
    paths={h.ROOT/'public/data/questions.json':published,h.ROOT/'src/content/concepts.json':h.read_json(FOLDER/'before-public-concepts.json'),h.ROOT/'src/content/explanations.json':h.read_json(FOLDER/'before-public-explanations.json')}
    def read(path,*args):return copy.deepcopy(paths[Path(path)]) if Path(path) in paths else original_read(path,*args)
    # The preparation checker also hashes the exact public catalog bytes. Its
    # archived fixture must read its frozen catalog for that byte-level check,
    # just as read_json above reads its frozen objects. Never write the live
    # catalog or redirect any production approval/publication validation.
    original_bytes=Path.read_bytes
    public_path=h.ROOT/'public/data/questions.json'
    public_bytes=(FOLDER/'before-public-questions.json').read_bytes()
    def read_bytes(path):return public_bytes if path==public_path else original_bytes(path)
    def snapshot(path):return context['snapshot'] if Path(path)==h.WORK else original_snapshot(path)
    receipt={'implementation':h.read_json(b.WORK/'preview/manifest.json')['implementation']}
    m=h.read_json(f.folder()/'manifest.json')
    def source_reviews(ctx,rs,vs,cs,ls,**kwargs):
        return c.validate_batch03_reviews(ctx,rs,vs,cs,ls,root=f.folder(),expected_highlights=0,review_schema='itpec-batch07-final-source-review-v1',existing_concepts=FOLDER/'before-public-concepts.json',**kwargs)
    with patch.object(Path,'read_bytes',read_bytes),patch.object(h,'read_json',side_effect=read),patch.object(qa,'snapshot_hashes',side_effect=snapshot),patch.object(b,'load_context',return_value=(ledger,records,before,current,expected,published)),patch.object(b,'implementation',return_value=receipt['implementation']),patch.object(f,'inputs',return_value=(context,records,current)),patch.object(f,'implementation',return_value=m['implementation']),patch.object(f,'source_reviews',side_effect=source_reviews):
        yield


def approve():
    state,m,records,reviews=verify_native(False)
    # Validate every candidate and highlight before the first mutation.
    import hardware_batch02 as b
    if b.public_fingerprints()!=state['protectedFiles']:raise ValueError('Public baseline changed before approval')
    validate_package()
    old=h.read_json(h.WORK/'manifest.json')
    for e in m['candidates']:
        h.approve(records,e['id'],'Project owner — explicit Release 7 authorization '+state['authorizationSha256'])
        live=h.read_json(h.WORK/'reviews.json');live[e['id']]['approval'].update(authorization_fields(state,e));h.write_json(h.WORK/'reviews.json',live)
    # Approval must not rewrite frozen summaries for earlier editorial repairs.
    # Generic gallery regeneration recomputes extraction totals; retain the exact
    # reviewed manifest and change only its authorized approval count.
    updated=copy.deepcopy(old);live_reviews=h.read_json(h.WORK/'reviews.json');updated['approvedQuestions']=sum(h.valid_approval(r,live_reviews[r['id']]) for r in records)
    h.write_json(h.WORK/'manifest.json',updated)
    publisher_check()
    h.write_json(FOLDER/'approvals.json',{'scope':SCOPE,'authorizationSha256':state['authorizationSha256'],'candidateManifestSha256':MANIFEST_SHA,'records':[{'id':qid,**h.read_json(h.WORK/'reviews.json')[qid]['approval']} for qid in state['questionIds']]})
    print('Exactly 31 new approvals; 236 existing approvals unchanged; 66 remain unapproved.')


def verify_public():
    state,m,records,reviews=verify_native();bank=h.read_json(h.ROOT/'public/data/questions.json');answers=h.read_json(h.ROOT/'src/content/explanations.json');concepts=h.read_json(h.ROOT/'src/content/concepts.json')
    previous=h.read_json(FOLDER/'before-public-questions.json');old_answers=h.read_json(FOLDER/'before-public-explanations.json');old_concepts=h.read_json(FOLDER/'before-public-concepts.json')
    index={q['id']:q for q in bank};explanations={e['questionId']:e for e in answers};ids=set(state['questionIds']);all_ids=ids|set(state['releasedQuestionIds'])
    if len(bank)!=687 or len(index)!=687 or len(previous)!=656 or {q['id'] for q in bank if q['format']=='historical'}!=all_ids:raise ValueError('Wrong public release scope')
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
    if len(new_concepts)!=0 or len(concepts)!=45 or len(list((h.ROOT/'public/questions').iterdir()))!=687:raise ValueError('Image/highlight scope mismatch')
    # All public files added by promotion must be the thirty-one original images.
    import hardware_batch02 as b
    if set(b.public_fingerprints())-set(state['protectedFiles'])!={'public'+index[qid]['image']['src'] for qid in ids}:raise ValueError('Unexpected public assets added')
    return {'schema':'itpec-historical-release-7-v1','preparationCommit':BASELINE,'candidateManifestSha256':MANIFEST_SHA,'candidateSetFingerprint':SET_FP,'authorizationSha256':state['authorizationSha256'],
        'scope':SCOPE,'authorizedCount':31,'excludedUnapproved':66,'practiceCount':420,'previousHistoricalCount':236,'historicalCount':267,'total':687,'images':687,'conceptCounts':m['conceptCounts'],
        'previousRecordsSha256':checksum({q['id']:q for q in previous}),'previousExplanationsSha256':checksum(old_answers),'previousConceptsSha256':checksum(old_concepts),'records':entries,'newHighlights':[{'id':d['id'],'definitionSha256':checksum(c.concept_view(d)),'sourceHighlight':d['sourceHighlight']} for d in m['conceptDefinitions'] if d['newConcept']]}


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('command',choices=['freeze','approve','verify','receipt','publication-gate','archive-candidates','archive-preview']);parser.add_argument('--authorization',type=Path);args=parser.parse_args()
    if args.command=='freeze':freeze(args.authorization)
    elif args.command=='approve':approve()
    elif args.command=='publication-gate':publication_gate();print('Exact owner authorization and prepublication dry run validated')
    elif args.command=='archive-candidates':
        state,m=context();archived_inputs();print(json.dumps({'candidates':31,'directory':str(f.folder()),'galleryAssets':m['galleryAssets']}))
    elif args.command=='archive-preview':print(json.dumps(archived_preview()))
    else:
        report=verify_public()
        if args.command=='receipt':
            if RECEIPT.exists() and h.read_json(RECEIPT)!=report:raise ValueError('Never renew a published approval receipt silently')
            h.write_json(RECEIPT,report)
        elif h.read_json(RECEIPT)!=report:raise ValueError('Stale publication receipt')
        print(json.dumps({'approved':31,'existingApprovalsUnchanged':236,'remainingPrivate':66,'total':687,'highlights':0,'receiptFingerprint':checksum(report)}))
