"""Private Hardware Batch 4, reusing native reconciliation and student-preview gates.

The private source-reviewed ledger is required. This module cannot approve,
publish, merge or deploy. Its publisher entry point supports dry runs only.
"""
import argparse
from collections import Counter
from copy import deepcopy
import json
from pathlib import Path
import subprocess
import fitz
import hardware_batch02 as core
import hardware_batch03 as preview
import historical_questions as h
import academic_qa as qa
import catalog_audit as audit
import private_student_preview as pilot

BASELINE='7debddd041e73ee943e4e83d0a39b299338fbf09'
BRANCH='feature/technology01-hardware-batch04'
WORK=h.ROOT/'.local/historical-batches/technology01-hardware-batch04'
APP=WORK/'preview/app'
PREFIX='itpecTextbook:privateHardwareBatch04:'
PAGES={6,25,26,40,48,50,58,65,83,88,91,97,111,115,116,117,127,131,135,138,141,147,176,194,195,196,205,216,217,218,222,251,265,283,287,289,297,323,329,333}
SPEC={'schema':'itpec-hardware-batch04-preparation-v1','baseline':BASELINE,'pages':PAGES}


def implementation():
    files=[Path(__file__),Path(core.__file__),Path(preview.__file__),Path(pilot.__file__),
           h.ROOT/'scripts/private-student-preview-server.mjs',h.ROOT/'scripts/historical-highlight.ts',
           h.ROOT/'scripts/publish-historical-questions.ts',h.ROOT/'package.json',h.ROOT/'package-lock.json',*pilot.TEMPLATES.rglob('*')]
    return {p.relative_to(h.ROOT).as_posix():h.digest(p.read_bytes()) for p in files if p.is_file()}


def preservation_files():
    folders=['.local/historical/approval-candidates','.local/releases',
             '.local/historical-batches/technology01-hardware-batch02',
             '.local/historical-batches/technology01-hardware-batch03']
    return {p.relative_to(h.ROOT).as_posix():h.digest(p.read_bytes()) for folder in folders for p in (h.ROOT/folder).rglob('*') if p.is_file()}


def initialize_guard():
    if (WORK/'baseline-guard.json').exists():return
    from release_3 import verify_public
    verify_public()
    if qa.snapshot_hashes(h.WORK)!=qa.snapshot_hashes(WORK/'before'):raise ValueError('Released native snapshot required')
    pilot.save(WORK/'baseline-guard.json',{'baseline':BASELINE,'publicFiles':core.public_fingerprints(),
        'priorReleaseFiles':preservation_files(),'beforeSnapshot':qa.snapshot_hashes(WORK/'before'),
        'decisionLedgerSha256':h.digest((WORK/'decisions.json').read_bytes())})


def load_context():
    if core.git('branch','--show-current')!=BRANCH or subprocess.run(['git','merge-base','--is-ancestor',BASELINE,'HEAD'],cwd=h.ROOT,capture_output=True).returncode:
        raise ValueError('Authorized Batch 4 branch and released ancestor required')
    guard=h.read_json(WORK/'baseline-guard.json');ledger=h.read_json(WORK/'decisions.json')
    before=h.read_json(WORK/'before/reviews.json');records=h.read_json(WORK/'before/questions.json')
    if not all([guard,ledger,before,records]):raise ValueError('Frozen baseline and source-reviewed ledger required')
    snapshot=qa.snapshot_hashes(WORK/'before')
    if ledger['beforeSnapshot']!=snapshot or guard['beforeSnapshot']!=snapshot or guard['decisionLedgerSha256']!=h.digest((WORK/'decisions.json').read_bytes()):raise ValueError('Stale decisions or snapshot; never automatically rebind')
    if guard['publicFiles']!=core.public_fingerprints() or guard['priorReleaseFiles']!=preservation_files():raise ValueError('Published content or prior release evidence changed')
    if records!=h.read_json(h.WORK/'questions.json') or snapshot['manifestFileSha256']!=qa.snapshot_hashes(h.WORK)['manifestFileSha256']:raise ValueError('Immutable source catalog/manifest changed')
    h.verify_source();h.verify_assets(records);pages=core.book_pages()
    frozen=h.ROOT/'.local/historical-metadata/technology-01/before'
    audit.validate_ledger(h.read_json(frozen/'questions.json'),h.read_json(frozen/'reviews.json'),h.read_json(audit.FOLDER/'decisions.json'),qa.snapshot_hashes(frozen),pages,audit.SOURCE_SHA,audit.BOOK_SHA)
    published=h.read_json(h.ROOT/'public/data/questions.json');nodes=h.read_json(h.ROOT/'src/content/hardware-toc.json')['nodes']
    if len(published)!=536 or sum(q['id'].startswith('HIST-') for q in published)!=116:raise ValueError('Released 420 + 116 catalog required')
    entries=core.validate_decisions(records,before,ledger,pages,published,ledger['concepts'],nodes,spec=SPEC)
    original=h.read_json(h.ROOT/'src/content/concepts.json');new=ledger['concepts'][len(original):]
    if ledger['concepts'][:len(original)]!=original or {c['id'] for c in new}!=set(ledger['newHighlights']) or any(not any(e['mapping']['conceptId']==c['id'] for e in entries) for c in new):raise ValueError('Existing or new highlight scope changed')
    expected=core.reconcile(records,before,entries,guard['decisionLedgerSha256'],milestone='technology01-hardware-batch04')
    current=h.read_json(h.WORK/'reviews.json');core.validate_transition(records,before,current,expected,{e['id'] for e in entries},approved_count=116)
    for e in entries:core.source_association({'id':e['id'],'currentMapping':e['mapping'],'auditClassification':e['classification']},next(c for c in ledger['concepts'] if c['id']==e['mapping']['conceptId']))
    return ledger,records,before,current,expected,published


def payload(ledger,records,reviews,published):
    return preview.payload(ledger,records,reviews,published,collection='batch04')


def candidates(ledger,records,reviews,links):
    return preview.candidates(ledger,records,reviews,links)


def gallery(ledger,records,reviews,links):
    # Reuse the read-only gallery payload and group navigation by concept.
    rows=candidates(ledger,records,reviews,links)['questions']
    for q in rows:
        q['newHighlight']=q['mapping']['conceptId'] in ledger['newHighlights']
        q['publicationBlockers']=['Final fingerprint-bound owner approval has not been granted.']
    pilot.save(APP/'src/content/owner-review.json',rows)
    page=APP/'src/pages/review.astro'
    text=page.read_text('utf8')
    text=text.replace('<ol>{candidates.map(q=><li>', '<nav aria-label="Review concepts"><ul>{[...new Set(candidates.map(q=>q.mapping.conceptId))].map(id=><li><a href={`#group-${id}`}>{id}</a></li>)}</ul></nav><ol>{candidates.map(q=><li>')
    text=text.replace('{candidates.map(q=><article id={q.id}>','{[...new Set(candidates.map(q=>q.mapping.conceptId))].map(id=><section id={`group-${id}`}><h2>{id}</h2>{candidates.filter(q=>q.mapping.conceptId===id).map(q=><article id={q.id}>')
    text=text.replace('</p></article>)}','</p><p>{q.newHighlight?"New source-bound highlight":"Existing highlight reused"}</p><blockquote aria-label="Exact source highlight"><p>Highlight: printed p.{q.association.highlightPrintedPage}, physical PDF p.{q.association.highlightPhysicalPdfPage}</p><p>{q.association.paragraphText}</p></blockquote><p>{q.publicationBlockers.join(" ")}</p></article>)}</section>)}')
    page.write_text(text,encoding='utf8')


def prepare():
    initialize_guard();ledger,records,before,current,expected,published=load_context()
    pilot.save(WORK/'decisions-concepts.json',ledger['concepts'])
    # Released concepts carry their old newConcept marker; only this batch's new
    # definitions belong to the current highlight-validation scope.
    plan=[{**c,'newConcept':c['id'] in ledger['newHighlights']} for c in ledger['concepts']]
    pilot.save(WORK/'highlight-plan.json',plan)
    highlights=json.loads(subprocess.check_output(['node',str(h.ROOT/'node_modules/tsx/dist/cli.mjs'),'scripts/historical-highlight.ts',str(WORK/'highlight-plan.json')],cwd=h.ROOT,text=True))
    if {r['conceptId'] for r in highlights}!=set(ledger['newHighlights']) or any(r['status']!='source-validated-pending-owner-editorial-approval' for r in highlights):raise ValueError(f'Highlight validation failed: {highlights}')
    pilot.save(WORK/'highlight-validation.json',highlights)
    with fitz.open(h.SOURCE) as source:qa.validate_source_images([r for r in records if r['regions'][0]['pdfPage'] in PAGES],source)
    if current!=expected:h.write_json(h.WORK/'reviews.json',expected);h.write_review_gallery(records)
    bank,answers,concepts,links=payload(ledger,records,expected,published)
    preview.preview_overlay(bank,concepts,published,app=APP,prefix=PREFIX,collection='batch04',label='Batch 4')
    for name,value in [('pilot-bank',bank),('explanations',answers),('concepts',concepts)]:pilot.save(APP/f'src/content/{name}.json',value)
    gallery(ledger,records,expected,links)
    for command in ['check','build']:
        if subprocess.run(['node',str(h.ROOT/'node_modules/astro/bin/astro.mjs'),command],cwd=APP,env=pilot.environment()).returncode:raise ValueError('Private check/build failed')
    pilot.save(WORK/'candidate-recommendation.json',candidates(ledger,records,expected,links))
    pilot.save(WORK/'review-diff.json',[{'id':e['id'],'beforeReviewSha256':qa.object_hash(before[e['id']]),'afterReviewSha256':qa.object_hash(expected[e['id']]),'before':{k:before[e['id']].get(k) for k in core.DIMENSIONS},'after':{k:expected[e['id']][k] for k in core.DIMENSIONS}} for e in ledger['entries']])
    manifest={'schema':'itpec-hardware-batch04-preview-v1','privateOnly':True,'approvalGranted':False,'baseline':BASELINE,
        'snapshot':qa.snapshot_hashes(h.WORK),'implementation':implementation(),'decisionLedgerSha256':h.digest((WORK/'decisions.json').read_bytes()),
        'questionIds':[e['id'] for e in ledger['entries']],'referenceIds':[q['id'] for q in bank if q['previewCollection']=='published'],
        'sourceImagesCompared':40,'associations':links,'assets':preview.assets_for(bank,app=APP),'progressPrefix':PREFIX,
        'appSources':{p.relative_to(APP).as_posix():h.digest(p.read_bytes()) for p in (APP/'src').rglob('*') if p.is_file()}}
    pilot.save(WORK/'preview/manifest.json',manifest);check()


def check():
    ledger,records,before,current,expected,published=load_context()
    if current!=expected:raise ValueError('Selected repairs have not been applied')
    m=h.read_json(WORK/'preview/manifest.json')
    if not m or m.get('schema')!='itpec-hardware-batch04-preview-v1' or m.get('privateOnly') is not True or m.get('approvalGranted') is not False or m.get('snapshot')!=qa.snapshot_hashes(h.WORK) or m.get('implementation')!=implementation() or m.get('decisionLedgerSha256')!=h.digest((WORK/'decisions.json').read_bytes()) or m.get('progressPrefix')!=PREFIX:raise ValueError('Private preview stale or not isolated')
    bank,answers,concepts,links=payload(ledger,records,current,published)
    if m['questionIds']!=[e['id'] for e in ledger['entries']] or m['referenceIds']!=[q['id'] for q in bank if q['previewCollection']=='published'] or m['associations']!=links:raise ValueError('Preview scope or association changed')
    for name,value in [('pilot-bank',bank),('explanations',answers),('concepts',concepts)]:
        if h.read_json(APP/f'src/content/{name}.json')!=value:raise ValueError('Candidate-to-preview equality failed')
    expected_gallery=deepcopy(candidates(ledger,records,current,links)['questions'])
    for q in expected_gallery:
        q['newHighlight']=q['mapping']['conceptId'] in ledger['newHighlights'];q['publicationBlockers']=['Final fingerprint-bound owner approval has not been granted.']
    if h.read_json(APP/'src/content/owner-review.json')!=expected_gallery:raise ValueError('Gallery differs from reviewed candidates')
    if m['assets']!=preview.assets_for(bank,app=APP) or m['appSources']!={p.relative_to(APP).as_posix():h.digest(p.read_bytes()) for p in (APP/'src').rglob('*') if p.is_file()}:raise ValueError('Preview sources/assets changed')
    for asset in m['assets'].values():
        file=Path(asset['path']).resolve()
        if not (file.is_relative_to((APP/'dist').resolve()) or file.is_relative_to((h.WORK/'images').resolve())) or h.digest(file.read_bytes())!=asset['sha256']:raise ValueError('Private asset root/hash changed')
    for file in (APP/'dist').rglob('*'):
        if file.suffix in ['.html','.js','.json']:
            text=file.read_text('utf8')
            if any(marker in text for marker in ['firestore.googleapis.com','identitytoolkit.googleapis.com','itpec-textbook.firebaseapp.com','AIzaSyBE9','preparationHistory','beforeReviewSha256','Printed key:','editorial-review-pending']):raise ValueError('Cloud runtime or QA history leaked')
    recommendation=candidates(ledger,records,current,links)
    if h.read_json(WORK/'candidate-recommendation.json')!=recommendation or any(not q['technicallyReadyForOwnerReview'] or q['approval']['status']!='unapproved' for q in recommendation['questions']):raise ValueError('Recommendation stale, blocked or approved')
    return m


def publisher_check():
    m=check();ledger,_,_,_,_,published=load_context()
    return {'questionIds':m['questionIds'],'releasedQuestionIds':[q['id'] for q in published if q['id'].startswith('HIST-')],
        'conceptDefinitions':ledger['concepts'],'preparationOnly':True,'ownerApprovalGranted':False}


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('command',choices=['prepare','check','publisher-check']);args=p.parse_args()
    if args.command=='prepare':prepare()
    elif args.command=='publisher-check':print(json.dumps(publisher_check()))
    else:check();print('Batch 4: 40 private/unapproved; 536 public pairs and 116 approvals preserved.')
