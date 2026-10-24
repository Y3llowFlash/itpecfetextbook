"""Prepare exactly forty private Hardware additions using the established review/preview gates.

Requires the local source-reviewed decisions and immutable baseline snapshot. No
approval, publication, merge or deployment operation is provided.
"""
import argparse
from collections import Counter
from copy import deepcopy
import csv
import io
import json
from pathlib import Path
import subprocess
import fitz
import hardware_batch02 as core
import historical_questions as h
import academic_qa as qa
import catalog_audit as audit
import private_student_preview as pilot

BASELINE='540ddf145cc60fbf223a7bc960d89012a06f4cb6'
BRANCH='feature/technology01-hardware-batch03'
WORK=h.ROOT/'.local/historical-batches/technology01-hardware-batch03'
APP=WORK/'preview/app'
PREFIX='itpecTextbook:privateHardwareBatch03:'
PAGES={9,12,42,44,51,59,62,75,78,82,84,89,90,108,132,149,155,157,161,165,168,182,184,185,204,207,215,225,238,245,260,262,263,284,299,305,306,317,325,330}
SPEC={'schema':'itpec-hardware-batch03-preparation-v1','baseline':BASELINE,'pages':PAGES}


def implementation():
    files=[Path(__file__),Path(core.__file__),Path(pilot.__file__),h.ROOT/'scripts/private-student-preview-server.mjs',
        h.ROOT/'scripts/historical-highlight.ts',h.ROOT/'scripts/publish-historical-questions.ts',
        h.ROOT/'package.json',h.ROOT/'package-lock.json',*pilot.TEMPLATES.rglob('*')]
    return {p.relative_to(h.ROOT).as_posix():h.digest(p.read_bytes()) for p in files if p.is_file()}


def preservation_files():
    folders=[h.ROOT/'.local/historical/approval-candidates',h.ROOT/'.local/releases']
    return {p.relative_to(h.ROOT).as_posix():h.digest(p.read_bytes()) for folder in folders for p in folder.rglob('*') if p.is_file()}


def initialize_guard():
    if (WORK/'baseline-guard.json').exists():return
    from release_40 import verify_public
    verify_public()
    if qa.snapshot_hashes(h.WORK)!=qa.snapshot_hashes(WORK/'before'):raise ValueError('Released native snapshot required')
    pilot.save(WORK/'baseline-guard.json',{'baseline':BASELINE,'publicFiles':core.public_fingerprints(),
        'priorPrivateReleaseFiles':preservation_files(),'beforeSnapshot':qa.snapshot_hashes(WORK/'before'),
        'decisionLedgerSha256':h.digest((WORK/'decisions.json').read_bytes())})


def load_context():
    if core.git('branch','--show-current')!=BRANCH or subprocess.run(['git','merge-base','--is-ancestor',BASELINE,'HEAD'],cwd=h.ROOT,capture_output=True).returncode:
        raise ValueError('Authorized fresh feature branch and released ancestor required')
    guard=h.read_json(WORK/'baseline-guard.json');ledger=h.read_json(WORK/'decisions.json')
    before=h.read_json(WORK/'before/reviews.json');records=h.read_json(WORK/'before/questions.json')
    if not all([guard,ledger,before,records]):raise ValueError('Private reviewed decisions and frozen baseline required')
    snapshot=qa.snapshot_hashes(WORK/'before')
    if ledger['beforeSnapshot']!=snapshot or guard['beforeSnapshot']!=snapshot or guard['decisionLedgerSha256']!=h.digest((WORK/'decisions.json').read_bytes()):raise ValueError('Stale baseline or decisions; do not rebind')
    if ledger.get('draftHistory',{}).get('draftLedgerSha256')!=h.digest((WORK/'draft-01/decisions.json').read_bytes()):raise ValueError('Superseded draft evidence changed')
    if guard['publicFiles']!=core.public_fingerprints() or guard['priorPrivateReleaseFiles']!=preservation_files():raise ValueError('Protected production or previous release evidence changed')
    if records!=h.read_json(h.WORK/'questions.json') or snapshot['manifestFileSha256']!=qa.snapshot_hashes(h.WORK)['manifestFileSha256']:raise ValueError('Immutable source catalog/manifest changed')
    h.verify_source();h.verify_assets(records);pages=core.book_pages()
    frozen=h.ROOT/'.local/historical-metadata/technology-01/before'
    audit.validate_ledger(h.read_json(frozen/'questions.json'),h.read_json(frozen/'reviews.json'),h.read_json(audit.FOLDER/'decisions.json'),qa.snapshot_hashes(frozen),pages,audit.SOURCE_SHA,audit.BOOK_SHA)
    published=h.read_json(h.ROOT/'public/data/questions.json');nodes=h.read_json(h.ROOT/'src/content/hardware-toc.json')['nodes']
    if len(published)!=496 or sum(q['id'].startswith('HIST-') for q in published)!=76:raise ValueError('Released 420 + 76 catalog required')
    entries=core.validate_decisions(records,before,ledger,pages,published,ledger['concepts'],nodes,spec=SPEC)
    # No unused definitions, duplicate paragraphs or arbitrary alterations to existing concepts.
    original=h.read_json(h.ROOT/'src/content/concepts.json');new=[c for c in ledger['concepts'] if c['id'] not in {c['id'] for c in original}]
    if ledger['concepts'][:len(original)]!=original or {c['id'] for c in new}!=set(ledger['newHighlights']) or any(not any(e['mapping']['conceptId']==c['id'] for e in entries) for c in new):raise ValueError('Existing or proposed highlight scope changed')
    expected=core.reconcile(records,before,entries,guard['decisionLedgerSha256'],milestone='technology01-hardware-batch03')
    current=h.read_json(h.WORK/'reviews.json');core.validate_transition(records,before,current,expected,{e['id'] for e in entries},approved_count=76)
    for e in entries:
        c=next(c for c in ledger['concepts'] if c['id']==e['mapping']['conceptId'])
        core.source_association({'id':e['id'],'currentMapping':e['mapping'],'auditClassification':e['classification']},c)
    return ledger,records,before,current,expected,published


def payload(ledger,records,reviews,published,*,collection='batch03',selection_count=40):
    selected=[{'id':e['id'],'currentMapping':e['mapping'],'auditClassification':e['classification']} for e in ledger['entries']]
    counts=Counter(e['mapping']['conceptId'] for e in ledger['entries'])
    bank,answers,_,links=pilot.project(selected,records,reviews,ledger['concepts'],associate=core.source_association,counts=counts)
    for q in bank:q['previewCollection']=collection
    original_concepts=h.read_json(h.ROOT/'src/content/concepts.json');reference_ids={i for c in original_concepts for i in c['questionIds']}
    originals={r['id']:r for r in records};live_answers={e['questionId']:e for e in h.read_json(h.ROOT/'src/content/explanations.json')}
    for q in published:
        if q['id'] not in reference_ids:continue
        reference=deepcopy(q);reference.update(is_published=False,privatePreview=True,previewCollection='published')
        if q['id'] in originals:reference['image']['src']=f"/__pilot/images/{q['image']['sha256']}.webp"
        else:reference['image']['src']=f"/__pilot/published-images/{q['image']['sha256']}.webp"
        bank.append(reference);answers.append(deepcopy(live_answers[q['id']]))
    concepts=deepcopy(ledger['concepts'])
    for c in concepts:c.update(questionIds=[q['id'] for q in bank if q['id'] in c['questionIds'] or (q['previewCollection']==collection and q['topic']==c['id'])],videos=[])
    if len(bank)!=len({q['id'] for q in bank}) or any(q['id'] in reference_ids for q in bank[:selection_count]):raise ValueError('Duplicate private/published occurrence')
    return bank,answers,concepts,links


def preview_overlay(bank,concepts,published,*,app=None,prefix=None,collection='batch03',label='Batch 3',selection_count=40):
    APP=app or globals()['APP']
    PREFIX=prefix or globals()['PREFIX']
    APP.mkdir(parents=True,exist_ok=True);pilot.overlay(APP,PREFIX)
    pilot.replace_checked(APP/'src/lib/models.ts','privatePreview: true;','privatePreview: true; previewCollection: "batch03" | "published";')
    practice=APP/'src/components/Practice.tsx'
    pilot.replace_checked(practice,'questions: bank, explanations','questions: fullBank, explanations')
    pilot.replace_checked(practice,'  const { progress } = useProgress();','  const [collection,setCollection] = useState("all");\n  const bank=fullBank.filter(q=>collection==="all" || q.previewCollection===collection);\n  const { progress } = useProgress();')
    pilot.replace_checked(practice,'<legend>Filter questions</legend>','<legend>Filter questions</legend><label>Preview collection<select value={collection} onChange={e=>{setFeedbackId(undefined);setCollection(e.target.value);}}><option value="all">All preview questions</option><option value="batch03">Batch 3 · Private additions</option><option value="published">Published references</option></select></label>')
    pilot.replace_checked(practice,'{bank.length > 0 && controls}','{controls}')
    pilot.replace_checked(practice,'<p aria-live="polite">{questions.length} of {bank.length} questions match.</p>','<p aria-live="polite">{fullBank.filter(q=>q.previewCollection==="published").length} published in this concept · {fullBank.filter(q=>q.previewCollection==="batch03").length} new private Batch 3 · {questions.length} match active filters.</p>')
    pilot.replace_checked(practice,'<div className="question-meta">','<p className="source-note" data-preview-collection={question.previewCollection}>{question.previewCollection==="batch03"?"Batch 3 · Private addition · Unapproved":"Published reference"}</p><div className="question-meta">')
    high=APP/'src/lib/question-highlights.ts'
    pilot.replace_checked(high,'  return html.replace(','''  for(const c of concepts){
    const added=bank.filter(q=>q.previewCollection==='batch03'&&c.questionIds.includes(q.id)).length;
    const released=bank.filter(q=>q.previewCollection==='published'&&c.questionIds.includes(q.id)).length;
    html=html.replace(new RegExp('(<a\\\\b[^>]*data-concept="'+c.id+'"[^>]*>)([\\\\s\\\\S]*?)(<\\\\/a>)','g'),(_,open,body,close)=>open+body.replace(/<span class="concept-count"[^>]*>[\\s\\S]*?<\\/span>/g,`<span class="concept-count"> · ${released} published + ${added} new private</span>`)+close);
  }
  return html.replace(''')
    toc=h.read_json(APP/'src/content/hardware-toc.json')
    for node in toc['nodes']:
        for c in concepts:
            if c.get('sourceHighlight',{}).get('headingNumber')==node['number'] and c['id'] not in node['conceptIds']:node['conceptIds'].append(c['id'])
    pilot.save(APP/'src/content/hardware-toc.json',toc)
    for q in bank:
        if q['previewCollection']!='published' or q['id'].startswith('HIST-'):continue
        original=next(r for r in published if r['id']==q['id']);file=h.ROOT/'public'/original['image']['src'].lstrip('/');target=APP/'public'/q['image']['src'].lstrip('/')
        if h.digest(file.read_bytes())!=q['image']['sha256']:raise ValueError('Published reference image changed')
        target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(file.read_bytes())
    index=APP/'src/pages/index.astro'
    pilot.replace_checked(index,'36-question local review; no publication approval.','Batch 3 local review; no publication approval.')
    pilot.replace_checked(index,'{bank.length} historical questions across seven existing concepts.','40 new private questions plus {bank.length-40} unchanged published references across {concepts.length} concepts.')
    pilot.replace_checked(index,'Seven-concept walkthrough','Concept walkthrough')
    pilot.replace_checked(index,'{questionsForConcept(c,bank).length} private questions','{questionsForConcept(c,bank).filter(q=>q.previewCollection==="published").length} published · {questionsForConcept(c,bank).filter(q=>q.previewCollection==="batch03").length} new private')
    pilot.replace_checked(index,' <h2>Concept walkthrough',' <p><a href="/review/">Open read-only owner gallery →</a></p><h2>All 40 Batch 3 questions</h2><ol>{bank.filter(q=>q.previewCollection==="batch03").map(q=><li><a href={`/practice/${q.topic}/?question=${q.id}`}>{q.id} · {q.year} {q.season} Q{q.number}</a></li>)}</ol>\n <h2>Concept walkthrough')
    gallery='''---
import SiteLayout from '../layouts/SiteLayout.astro';
import candidates from '../content/owner-review.json';
---
<SiteLayout title="Batch 3 owner review" description="Read-only local review" companion={false} noindex>
<section class="chapter-overview"><h1>Batch 3 — read-only owner gallery</h1><a href="/">Student preview index</a><p>40 technically prepared candidates; no publication approval. Source images and academic explanations are preserved.</p>
<ol>{candidates.map(q=><li><a href={`#${q.id}`}>{q.id} · {q.mapping.conceptId}</a></li>)}</ol>
{candidates.map(q=><article id={q.id}><h2>{q.id}</h2><p>FE · Morning · Subject A · {q.year} {q.season} · Q{q.number} · Technology-01 physical page {q.pdfPage}</p>
<a href={q.previewImage} target="_blank"><img src={q.previewImage} width={q.image.width} height={q.image.height} alt={q.accessibleTranscription.imageDescription} loading="lazy" style="max-width:100%;height:auto" /></a>
<p>{q.accessibleTranscription.imageDescription}</p><dl>{Object.entries(q.accessibleTranscription.optionText).map(([key,value])=><><dt>{key.toUpperCase()}</dt><dd>{value}</dd></>)}</dl>
<p>Verified answer: {q.correctAnswer.toUpperCase()} · Approval: unapproved · Grading: eligible after separate publication authorization.</p><p>{q.explanation.summary}</p><ol>{q.explanation.steps.map(step=><li>{step}</li>)}</ol><p>{q.explanation.takeaway}</p>
<p>Exact placement: {q.mapping.headingNumber} · {q.mapping.conceptId}. {q.editorialRepair}</p>
{q.mapping.evidence.map(ev=><blockquote><p>FE Volume 1 printed p.{ev.printedPage}, physical PDF p.{ev.pdfPage} · {ev.role}</p><p>{ev.checkedExcerpt}</p></blockquote>)}
<p><a href={`/practice/${q.mapping.conceptId}/?question=${q.id}`}>Try in student preview</a> · <a href="#top">Back to navigation</a></p></article>)}
</section></SiteLayout>
'''
    (APP/'src/pages/review.astro').write_text(gallery,encoding='utf8')
    # Later batches reuse exactly this disposable application adapter. Only the
    # private generated files receive collection labels; production is untouched.
    if collection!='batch03' or label!='Batch 3':
        for relative in ['src/lib/models.ts','src/components/Practice.tsx','src/lib/question-highlights.ts','src/pages/index.astro','src/pages/review.astro']:
            file=APP/relative
            file.write_text(file.read_text('utf8').replace('batch03',collection).replace('Batch 3',label),encoding='utf8')
    if selection_count!=40:
        for relative in ['src/pages/index.astro','src/pages/review.astro']:
            file=APP/relative
            text=file.read_text('utf8')
            for old,new in [('40 new private',f'{selection_count} new private'),('bank.length-40',f'bank.length-{selection_count}'),('All 40 ',f'All {selection_count} '),('40 technically',f'{selection_count} technically')]:text=text.replace(old,new)
            file.write_text(text,encoding='utf8')


def assets_for(bank,*,app=None):
    APP=app or globals()['APP']
    assets={'/'+p.relative_to(APP/'dist').as_posix():{'path':str(p),'sha256':h.digest(p.read_bytes())} for p in (APP/'dist').rglob('*') if p.is_file()}
    originals={r['id']:r for r in h.read_json(h.WORK/'questions.json')}
    for q in bank:
        if q['id'] in originals:assets[q['image']['src']]={'path':str(h.WORK/originals[q['id']]['images'][0]['path']),'sha256':q['image']['sha256']}
    if any('/questions/' in key or '/data/' in key or key.endswith('.pdf') for key in assets):raise ValueError('Private bank or raw PDF escaped delivery isolation')
    return assets


def candidates(ledger,records,reviews,links):
    result=core.recommendation(ledger,records,reviews,links)
    for q in result['questions']:q['previewImage']=f"/__pilot/images/{q['image']['sha256']}.webp"
    return result


def write_reports(ledger,records,before,reviews,links,bank):
    candidate=candidates(ledger,records,reviews,links);pilot.save(WORK/'candidate-recommendation.json',candidate)
    pilot.save(WORK/'review-diff.json',[{'id':e['id'],'beforeReviewSha256':e['beforeReviewSha256'],'afterReviewSha256':qa.object_hash(reviews[e['id']]),'previous':{k:before[e['id']].get(k) for k in core.DIMENSIONS},'revised':{k:reviews[e['id']][k] for k in core.DIMENSIONS}} for e in ledger['entries']])
    counts=Counter(e['mapping']['conceptId'] for e in ledger['entries'])
    preservation={'publicQuestionImagePairs':496,'practiceRecords':420,'releasedHistorical':76,'privateHistorical':257,'independentAnswers':326,'qualifiedCases':7,'selectedUnapproved':40,
      'allAcademicMetadataApprovalHistoryUnchanged':True,'other293ReviewsUnchanged':True,'originalImagesPixelCompared':40,'publicFileHashes':h.read_json(WORK/'baseline-guard.json')['publicFiles'],
      'mappings':dict(Counter(v['mapping']['status'] for v in reviews.values())),'extractions':dict(Counter(h.effective_extraction(r,reviews[r['id']]) for r in records)),
      'distribution':dict(counts),'newHighlights':ledger['newHighlights'],'existingSelectedConcepts':sorted(set(counts)-set(ledger['newHighlights']))}
    pilot.save(WORK/'preservation-report.json',preservation)
    out=io.StringIO();w=csv.writer(out);w.writerow(['id','historical_pdf_page','year','season','question','concept','heading','book_printed_pages','book_physical_pages','technical_ready','approval'])
    lines=['# Technology-01 Hardware Batch 3 — private preparation','',
      f'40 source-reviewed additions across {len(counts)} concepts: {len(ledger["newHighlights"])} proposed new highlights and {len(set(counts)-set(ledger["newHighlights"]))} existing selected concepts. All 40 are unapproved.',
      f'The private preview also contains {len(bank)-40} unchanged published Hardware references. Published, private and filtered counts are separate.',
      '496 public question/image pairs (420 Practice + 76 historical), all source HTML, Firebase/progress code, prior approval fingerprints and release evidence are byte-preserved.',
      '326 independently verified academic answers/explanations and all seven qualified owner adjudications remain unchanged. The other 293 native review objects are unchanged. There are still 257 private historical records: 40 prepared here and 217 outside this selection.',
      '', '| Source PDF page | Canonical ID / examination | Concept / exact heading | Book printed (physical) | Repair | Status |','|---|---|---|---|---|---|']
    for q in candidate['questions']:
        evidence=q['mapping']['evidence'];pages=', '.join(f"{p['printedPage']} ({p['pdfPage']})" for p in evidence)
        lines.append(f"| {q['pdfPage']} | {q['id']} · {q['year']}{q['season']} Q{q['number']} | {q['mapping']['conceptId']} / {q['mapping']['headingNumber']} | {pages} | {q['editorialRepair']} | Academically verified; accessible; exact mapping; FE/AM/A confirmed; grading eligible; unapproved |")
        w.writerow([q['id'],q['pdfPage'],q['year'],q['season'],q['number'],q['mapping']['conceptId'],q['mapping']['headingNumber'],','.join(str(p['printedPage']) for p in evidence),','.join(str(p['pdfPage']) for p in evidence),q['technicallyReadyForOwnerReview'],'unapproved'])
    lines+=['','## Distribution and highlight inventory','']+[f'- {id}: {n} private additions; '+('new source-bound proposal' if id in ledger['newHighlights'] else 'existing highlight reused') for id,n in sorted(counts.items())]
    lines+=['','## Source interpretation and deferrals','',
      'Original images are not edited or regenerated. Accessibility repairs supply missing stems/options, diagram connections, table-column order, signed exponents, fractions and units. They do not contain solved outputs or reviewer instructions. The original option b typo “cash memory” on physical page 75 is retained; the verified explanation is unchanged.',
      'Physical page 62 uses the explicit mechanical-contact definition in the 5-1-1 keyboard note (book physical p.98); its warning that key-repeat differs from chattering is retained. The 5-3 definition on physical p.110 corroborates it. The digitizer highlight fragment retains its adjacent original figure and continuation paragraph. The memory hierarchy entry spans book physical pp.77–78, including the original hierarchy figure.',
      'CD-R uses the actual write-once paragraph on book physical p.93. Laser-printer dpi/ppm support on physical p.108 precedes the next numbered subsection and belongs to 5-2-2. Physical question page 245 needs no forced Chapter 3 mapping: Chapter 1 physical pp.87–88 teach block allocation. IEEE mask and memory-line options retain the original exponent/bit layouts.',
      'Published references are copied from the authoritative public question/explanation payload, including Practice answers. No conservative year/season/question or image collision was selected.',
      *[f"- Deferred physical page {e['pdfPage']}: {e['reason']}" for e in ledger['deferred']],
      'The 29 other-Volume-1, three outside-Volume-1 and nine uncertain classifications are not applied or forced into Hardware. The seven qualified cases and the existing 12 partial extractions are outside the batch and unchanged.',
      '',f"Native mapping totals: {preservation['mappings']}. Effective extraction totals: {preservation['extractions']}.",
      '', '## Local owner review and next milestone','',
      '`python scripts/hardware_batch03.py check` validates exact decisions, source pixels/hashes, frozen baseline, private preview equality and preservation.',
      '`node scripts/private-student-preview-server.mjs --batch03` serves http://127.0.0.1:4332/ on loopback only; `/review/` is the read-only visual owner gallery. The home page indexes every new question. All private attempts, bookmarks, filters and reading checkpoints use `itpecTextbook:privateHardwareBatch03:`; no Firebase runtime is included.',
      '`npx tsx scripts/publish-historical-questions.ts --batch 3 --dry-run` uses the current publisher with a read-only preparation gate. Non-dry-run Batch 3 publication is rejected. Expected: 76 existing approved inputs, zero new approvals, zero additions/updates/conflicts.',
      'Future publication remains blocked on a separately authorized final candidate package and owner authorization bound to each exact publication fingerprint and source-highlight definition. Reconcile the exact final payload against this preview through the existing approval-candidate system. Any student-visible change requires revalidation and invalidates prior approval. This preparation creates no owner authorization.',
      'No merge, deployment, production request, rollback, Practice-repository edit, real-progress migration or infrastructure change was performed. Test/build evidence is recorded separately in validation-results.md.']
    (WORK/'completion-report.md').write_text('\n'.join(lines)+'\n',encoding='utf8');(WORK/'inventory.csv').write_text(out.getvalue(),encoding='utf8')


def prepare():
    initialize_guard();ledger,records,before,current,expected,published=load_context()
    pilot.save(WORK/'decisions-concepts.json',ledger['concepts'])
    result=json.loads(subprocess.check_output(['node',str(h.ROOT/'node_modules/tsx/dist/cli.mjs'),'scripts/historical-highlight.ts',str(WORK/'decisions-concepts.json')],cwd=h.ROOT,text=True))
    if {r['conceptId'] for r in result}!=set(ledger['newHighlights']) or any(r['status']!='source-validated-pending-owner-editorial-approval' for r in result):raise ValueError(f'Highlight validation failed: {result}')
    pilot.save(WORK/'highlight-validation.json',result)
    with fitz.open(h.SOURCE) as source:qa.validate_source_images([r for r in records if r['regions'][0]['pdfPage'] in PAGES],source)
    if current!=expected:h.write_json(h.WORK/'reviews.json',expected);h.write_review_gallery(records)
    bank,answers,concepts,links=payload(ledger,records,expected,published);preview_overlay(bank,concepts,published)
    for name,value in [('pilot-bank',bank),('explanations',answers),('concepts',concepts),('owner-review',candidates(ledger,records,expected,links)['questions'])]:pilot.save(APP/f'src/content/{name}.json',value)
    for command in ['check','build']:
        if subprocess.run(['node',str(h.ROOT/'node_modules/astro/bin/astro.mjs'),command],cwd=APP,env=pilot.environment()).returncode:raise ValueError('Private check/build failed')
    manifest={'schema':'itpec-hardware-batch03-preview-v1','privateOnly':True,'approvalGranted':False,'baseline':BASELINE,'snapshot':qa.snapshot_hashes(h.WORK),'implementation':implementation(),
      'decisionLedgerSha256':h.digest((WORK/'decisions.json').read_bytes()),'questionIds':[e['id'] for e in ledger['entries']],
      'referenceIds':[q['id'] for q in bank if q['previewCollection']=='published'],'sourceImagesCompared':40,'associations':links,'assets':assets_for(bank),'progressPrefix':PREFIX,
      'appSources':{p.relative_to(APP).as_posix():h.digest(p.read_bytes()) for p in (APP/'src').rglob('*') if p.is_file()}}
    pilot.save(WORK/'preview/manifest.json',manifest);write_reports(ledger,records,before,expected,links,bank);check()


def check():
    ledger,records,before,current,expected,published=load_context()
    if current!=expected:raise ValueError('Private repairs not yet applied')
    manifest=h.read_json(WORK/'preview/manifest.json')
    if not manifest or manifest.get('schema')!='itpec-hardware-batch03-preview-v1' or manifest.get('privateOnly') is not True or manifest.get('approvalGranted') is not False or manifest.get('snapshot')!=qa.snapshot_hashes(h.WORK) or manifest.get('implementation')!=implementation() or manifest.get('decisionLedgerSha256')!=h.digest((WORK/'decisions.json').read_bytes()) or manifest.get('progressPrefix')!=PREFIX:raise ValueError('Private preview stale or not isolated')
    bank,answers,concepts,links=payload(ledger,records,current,published)
    if manifest['questionIds']!=[e['id'] for e in ledger['entries']] or manifest['referenceIds']!=[q['id'] for q in bank if q['previewCollection']=='published'] or manifest['associations']!=links:raise ValueError('Preview scope/association changed')
    for name,value in [('pilot-bank',bank),('explanations',answers),('concepts',concepts),('owner-review',candidates(ledger,records,current,links)['questions'])]:
        if h.read_json(APP/f'src/content/{name}.json')!=value:raise ValueError('Candidate-to-preview equality failed')
    if manifest['assets']!=assets_for(bank) or manifest['appSources']!={p.relative_to(APP).as_posix():h.digest(p.read_bytes()) for p in (APP/'src').rglob('*') if p.is_file()}:raise ValueError('Preview sources/assets changed')
    for asset in manifest['assets'].values():
        file=Path(asset['path']).resolve()
        if not (file.is_relative_to((APP/'dist').resolve()) or file.is_relative_to((h.WORK/'images').resolve())) or h.digest(file.read_bytes())!=asset['sha256']:raise ValueError('Private asset root/hash changed')
    for file in (APP/'dist').rglob('*'):
        if file.suffix in ['.html','.js','.json']:
            text=file.read_text('utf8')
            if any(marker in text for marker in ['firestore.googleapis.com','identitytoolkit.googleapis.com','itpec-textbook.firebaseapp.com','AIzaSyBE9','preparationHistory','beforeReviewSha256','Printed key:','editorial-review-pending']):raise ValueError('Cloud runtime or QA history leaked')
    if h.read_json(WORK/'candidate-recommendation.json')!=candidates(ledger,records,current,links):raise ValueError('Recommendation stale')
    return manifest


def publisher_check():
    manifest=check();ledger,_,_,_,_,published=load_context()
    return {'questionIds':manifest['questionIds'],'releasedQuestionIds':[q['id'] for q in published if q['id'].startswith('HIST-')],
      'conceptDefinitions':ledger['concepts'],'preparationOnly':True,'ownerApprovalGranted':False}


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('command',choices=['prepare','check','publisher-check']);args=parser.parse_args()
    if args.command=='prepare':prepare()
    elif args.command=='publisher-check':print(json.dumps(publisher_check()))
    else:check();print('Batch 3 integrity: 40 prepared/unapproved; 496 public pairs and 76 approvals unchanged; 326 independent answers preserved.')
