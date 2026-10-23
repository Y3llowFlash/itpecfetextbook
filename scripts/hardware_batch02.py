"""Prepare reviewed Hardware additions using the existing native reviews and private preview.

Editorial decisions and source material stay in .local. No approval, export or
production-writing command is provided. The original 36-question workflow stays frozen.
"""
import argparse
from collections import Counter
from copy import deepcopy
import csv
import html
import io
from pathlib import Path
import re
import subprocess
import fitz
import academic_qa as qa
import catalog_audit as audit
import historical_questions as h
import private_student_preview as pilot

BASELINE='88577fed721e24ef5db9fbbe07bd7fe1e4910d19'
BRANCH='feature/technology01-hardware-batch02'
WORK=h.ROOT/'.local/historical-batches/technology01-hardware-batch02'
APP=WORK/'preview/app'
PREFIX='itpecTextbook:privateHardwareBatch02:'
PAGES={2,3,7,13,14,15,17,18,19,21,23,27,31,32,38,39,43,52,53,64,100,137,151,156,174,186,192,214,221,244,248,253,256,269,271,286,293,300,304,311}
PROTECTED={110,112,119,152,179,180,181}
DIMENSIONS={'classification','mapping','extraction'}


def git(*args):
    return subprocess.check_output(['git',*args],cwd=h.ROOT,text=True).strip()


def public_fingerprints():
    # Book HTML/assets, public questions, progress code and account code are immutable here.
    return {p.relative_to(h.ROOT).as_posix():h.digest(p.read_bytes())
        for folder in ['src','public'] for p in sorted((h.ROOT/folder).rglob('*')) if p.is_file()}


def implementation():
    files=[Path(__file__),h.ROOT/'scripts/private_student_preview.py',h.ROOT/'scripts/private-student-preview-server.mjs',
        h.ROOT/'package.json',h.ROOT/'package-lock.json',*sorted(pilot.TEMPLATES.rglob('*'))]
    return {p.relative_to(h.ROOT).as_posix():h.digest(p.read_bytes()) for p in files if p.is_file()}


def book_pages():
    if h.digest(qa.TEXTBOOK.read_bytes())!=audit.BOOK_SHA:raise ValueError('Textbook checksum changed')
    pages=[]
    with fitz.open(qa.TEXTBOOK) as book:
        if len(book)!=487:raise ValueError('Complete Volume 1 is required')
        for i,page in enumerate(book):
            text=page.get_text();labels=[int(s.strip()) for s in text.splitlines()[:8] if re.fullmatch(r'\d{1,3}',s.strip())]
            pages.append({'pdfPage':i+1,'text':text,'textSha256':h.digest(text.encode()),'printedPage':labels[0] if labels else None})
    return pages


def validate_passages(evidence,pages):
    if not evidence:raise ValueError('Bounded textbook evidence is required')
    for ev in evidence:
        n=ev.get('pdfPage')
        if not isinstance(n,int) or not 18<=n<=117:raise ValueError('Hardware passage outside Chapter 1')
        page=pages[n-1];excerpt=ev.get('checkedExcerpt','')
        if ev.get('kind')!='textbook-source' or ev.get('sourceSha256')!=audit.BOOK_SHA or ev.get('textSha256')!=page['textSha256'] or ev.get('printedPage')!=page['printedPage'] or len(excerpt)<50 or excerpt not in h.norm(page['text']) or ev.get('role') not in ['direct','context','secondary']:
            raise ValueError('Stale, missing or fabricated textbook passage/page label')
    if not any(ev['role']=='direct' for ev in evidence):raise ValueError('Context alone does not establish an exact teaching placement')


def validate_decisions(records,before,ledger,pages,published,concepts,nodes,*,spec=None):
    # Later private batches reuse the same gates without changing the frozen Batch 2 defaults.
    spec=spec or {'schema':'itpec-hardware-batch02-preparation-v1','baseline':BASELINE,'pages':PAGES}
    if ledger.get('schema')!=spec['schema'] or ledger.get('baseline')!=spec['baseline'] or ledger.get('sourceSha256')!=audit.SOURCE_SHA or ledger.get('bookSha256')!=audit.BOOK_SHA:
        raise ValueError('Unrecognized preparation source/baseline')
    entries=ledger.get('entries',[]);ids=[e['id'] for e in entries];index={r['id']:r for r in records}
    if len(entries)!=40 or len(set(ids))!=40 or {e.get('pdfPage') for e in entries}!=spec['pages']:raise ValueError('Exact 40-question scope required')
    concept_index={c['id']:c for c in concepts};node_index={n['id']:n for n in nodes}
    if len(concept_index)!=len(concepts):raise ValueError('Duplicate concept IDs')
    for e in entries:
        r=index[e['id']];v=before[e['id']];m=e['mapping'];c=e['classification'];x=e['extraction']
        if e['pdfPage']!=r['regions'][0]['pdfPage'] or e['pdfPage'] in PROTECTED or v.get('ownerAdjudication') or v['approval']['status']!='unapproved' or not h.valid_verification(r,v):
            raise ValueError('Selection must exclude published and qualified owner cases')
        if e.get('contentSha256')!=r['contentSha256'] or h.digest(r['rawText'].encode())!=r['contentSha256'] or e.get('imageSha256')!=[i['sha256'] for i in r['images']] or e.get('beforeReviewSha256')!=qa.object_hash(v) or e.get('sourceImageVisuallyChecked') is not True:
            raise ValueError('Stale source/image/review decision binding')
        meta=v.get('metadata',{})
        if not (meta.get('status')=='verified' and meta.get('examType')=='FE' and meta.get('paper')=='AM' and meta.get('subject')=='A' and meta.get('evidence')):
            raise ValueError('Owner-confirmed Morning/Subject A evidence required')
        # Conservative collision guard: ambiguous published identities are deferred too.
        # A reliable Practice match retains its existing authority, never becomes a new record.
        if any(q['id']==r['id'] or (q.get('year'),q.get('season'),q.get('number'))==(r['year'],r['season'],r['number']) or q.get('image',{}).get('sha256') in e['imageSha256'] for q in published):
            raise ValueError('Published occurrence/image collision requires existing Practice reconciliation')
        if c.get('category')!='ch1' or c.get('chapter')!=1 or c.get('status')!='source-reviewed' or c.get('placement')!='exact' or not c.get('reason'):
            raise ValueError('Source-supported exact Chapter 1 classification required')
        validate_passages(c['evidence'],pages)
        node=node_index.get(m.get('subsectionId'));concept=concept_index.get(m.get('conceptId'))
        if not node or not concept or m.get('status')!='verified' or m.get('chapterId')!='fe-v1-ch01' or node['number']!=m.get('headingNumber') or node['number']!=c.get('headingNumber') or node['sectionId']!=m.get('sectionId') or concept['sectionId']!=node['sectionId'] or concept['sectionUrl']!=node['path'] or m.get('evidence')!=c['evidence']:
            raise ValueError('Concept, route, subsection and source proof disagree')
        if x.get('sourceBinding')!=qa.extraction_binding(r) or x.get('reviewedImages')!=e['imageSha256'] or x.get('status')!='complete' or not x.get('imageDescription') or set(x.get('optionText',{}))!=set('abcd') or not all(x['optionText'].values()) or x.get('issues') or x.get('sourceDefects'):
            raise ValueError('Complete, validated accessible transcription required')
        # Validate with the existing publisher/readiness gate, independent of approval.
        proposed={**v,**{k:e[k] for k in DIMENSIONS}}
        if h.approval_errors(r,proposed):raise ValueError('Existing readiness gate rejected candidate')
    return entries


def reconcile(records,before,entries,ledger_sha,draft_history=None,*,milestone='technology01-hardware-batch02'):
    """Bounded editorial update of native review dimensions; no academic or approval edits."""
    result=deepcopy(before)
    for e in entries:
        v=result[e['id']]
        if qa.object_hash(v)!=e['beforeReviewSha256']:raise ValueError('Stale editorial snapshot')
        previous={k:deepcopy(v.get(k)) for k in DIMENSIONS}
        for key in DIMENSIONS:v[key]=deepcopy(e[key])
        history=v.setdefault('preparationHistory',[])
        history.append({'milestone':milestone,'decisionLedgerSha256':ledger_sha,
            'decisionSha256':qa.object_hash(e),'beforeReviewSha256':e['beforeReviewSha256'],
            'sourceBinding':qa.extraction_binding(next(r for r in records if r['id']==e['id'])),
            'before':previous,'after':{k:deepcopy(v[k]) for k in DIMENSIONS},'note':e['editorialNote'],
            'status':'source-reviewed-editorial-preparation-only','ownerPublicationApproval':'unapproved'})
        if draft_history:history[-1]['supersededDraft']=deepcopy(draft_history)
    return result


def validate_transition(records,before,current,expected,selected,*,approved_count=36):
    if current not in [before,expected]:raise ValueError('Live reviews changed: reject stale input; do not rebind automatically')
    for r in records:
        old=before[r['id']];new=expected[r['id']]
        if r['id'] not in selected and new!=old:raise ValueError('Nonselected review changed')
        for key in set(old)|set(new):
            if key not in DIMENSIONS|{'preparationHistory'} and new.get(key)!=old.get(key):raise ValueError('Protected academic, metadata or approval object changed')
        if r['regions'][0]['pdfPage'] in PROTECTED and new!=old:raise ValueError('Protected owner case changed')
    if sum(h.valid_verification(r,expected[r['id']]) for r in records)!=326 or sum(h.valid_approval(r,expected[r['id']]) for r in records)!=approved_count:
        raise ValueError('Existing verification/approval totals changed')
    if any(expected[i]['approval']['status']!='unapproved' for i in selected):raise ValueError('New approval is forbidden')


def source_association(q,concept):
    mapping=q['currentMapping'];file=h.ROOT/'src/content/source-hardware'/f'{concept["sectionUrl"].strip("/").split("/")[-1]}.html'
    source=file.read_text('utf8');overlay=concept.get('sourceHighlight')
    if overlay:
        match=re.search(r'<p\b[^>]*\bid="'+re.escape(overlay['passageId'])+r'"[^>]*>([\s\S]*?)</p>',source)
        if not match or h.digest(match[1].encode())!=overlay['fragmentSha256'] or '<a ' in match[1]:raise ValueError('Private highlight source fragment is stale')
    else:
        matches=list(re.finditer(r'<a\b[^>]*data-concept="'+re.escape(concept['id'])+r'"[^>]*>[\s\S]*?</a>',source))
        if len(matches)!=1:raise ValueError('Existing highlight must be unique')
        match=matches[0]
    section=source[source.rfind('<section ',0,match.start()):match.start()]
    nodes=h.read_json(h.ROOT/'src/content/hardware-toc.json')['nodes']
    preceding=[(source.find('id="'+n['id']+'"'),n) for n in nodes if n['path']==concept['sectionUrl']]
    preceding=[(position,n) for position,n in preceding if 0<=position<match.start()]
    owner=max(preceding,key=lambda pair:pair[0])[1] if preceding else None
    if not owner or owner['id']!=mapping['subsectionId'] or owner['number']!=mapping['headingNumber']:
        raise ValueError('Highlight fragment is outside its claimed numbered textbook subsection')
    return {'questionId':q['id'],'conceptId':concept['id'],'sectionId':mapping['sectionId'],'subsectionId':mapping['subsectionId'],
        'heading':mapping['headingNumber'],'route':concept['sectionUrl'],'highlightId':f'concept-{concept["id"]}',
        'highlightPhysicalPdfPage':int(re.search('data-pdf-page="(\\d+)"',section)[1]),
        'highlightPrintedPage':int(re.search('data-printed-page="(\\d+)"',section)[1]),
        'sourceFile':file.relative_to(h.ROOT).as_posix(),'highlightSourceSha256':h.digest(match[0].encode()),
        'paragraphText':h.norm(html.unescape(re.sub('<[^>]+>',' ',match[0]))),'bookEvidence':q['auditClassification']['evidence'],
        'status':'source-reviewed-private-only','publicationApproval':'unapproved'}


def load_context():
    if git('branch','--show-current')!=BRANCH or subprocess.run(['git','merge-base','--is-ancestor',BASELINE,'HEAD'],cwd=h.ROOT,capture_output=True).returncode:
        raise ValueError('Use the fresh authorized feature branch from the release baseline')
    ledger=h.read_json(WORK/'decisions.json');before=h.read_json(WORK/'before/reviews.json');records=h.read_json(WORK/'before/questions.json')
    if not ledger or not before or not records:raise ValueError('Private reviewed decisions and original baseline snapshot required')
    if ledger['beforeSnapshot']!=qa.snapshot_hashes(WORK/'before'):raise ValueError('Frozen baseline snapshot changed')
    h.verify_source();h.verify_assets(records)
    if h.digest(h.SOURCE.read_bytes())!=audit.SOURCE_SHA or records!=h.read_json(h.WORK/'questions.json'):raise ValueError('Immutable source/records changed')
    pages=book_pages()
    # Old audit is checked against its actual historical snapshot, never rebound to today.
    frozen=h.ROOT/'.local/historical-metadata/technology-01/before'
    audit_ledger=h.read_json(audit.FOLDER/'decisions.json')
    audit.validate_ledger(h.read_json(frozen/'questions.json'),h.read_json(frozen/'reviews.json'),audit_ledger,qa.snapshot_hashes(frozen),pages,audit.SOURCE_SHA,audit.BOOK_SHA)
    published=h.read_json(h.ROOT/'public/data/questions.json');nodes=h.read_json(h.ROOT/'src/content/hardware-toc.json')['nodes']
    if len(published)!=456:raise ValueError('Released catalog must remain 456')
    entries=validate_decisions(records,before,ledger,pages,published,ledger['concepts'],nodes)
    ledger_sha=h.digest((WORK/'decisions.json').read_bytes())
    if ledger.get('draftHistory'):
        receipt=ledger['draftHistory']
        if receipt['supersededDecisionLedgerSha256']!=h.digest((WORK/'draft-01/decisions.json').read_bytes()) or receipt['supersededReviewSha256']!=h.digest((WORK/'draft-01/reviews.json').read_bytes()):raise ValueError('Superseded draft history changed')
    expected=reconcile(records,before,entries,ledger_sha,ledger.get('draftHistory'))
    current=h.read_json(h.WORK/'reviews.json');validate_transition(records,before,current,expected,{e['id'] for e in entries})
    guard=h.read_json(WORK/'baseline-guard.json')
    if not guard or guard['publicFiles']!=public_fingerprints() or guard['questionFileSha256']!=h.digest((h.WORK/'questions.json').read_bytes()) or guard['nativeManifestSha256']!=h.digest((h.WORK/'manifest.json').read_bytes()) or guard['decisionLedgerSha256']!=ledger_sha:
        raise ValueError('Protected public/source/decision snapshot changed')
    for concept in ledger['concepts']:
        relevant=next((e for e in entries if e['mapping']['conceptId']==concept['id']),None)
        if relevant:source_association({'id':relevant['id'],'currentMapping':relevant['mapping'],'auditClassification':relevant['classification']},concept)
    return ledger,records,before,current,expected,published


def initialize_guard():
    if (WORK/'baseline-guard.json').exists():return
    from release_36 import verify_public
    verify_public()
    if qa.snapshot_hashes(h.WORK)!=qa.snapshot_hashes(WORK/'before'):raise ValueError('Initial snapshot must be the released baseline')
    pilot.save(WORK/'baseline-guard.json',{'baseline':BASELINE,'publicFiles':public_fingerprints(),
        'questionFileSha256':h.digest((h.WORK/'questions.json').read_bytes()),'nativeManifestSha256':h.digest((h.WORK/'manifest.json').read_bytes()),
        'decisionLedgerSha256':h.digest((WORK/'decisions.json').read_bytes())})


def payload(ledger,records,reviews,published):
    entries=ledger['entries'];published_ids={q['id'] for q in published if q['id'].startswith('HIST-')}
    if len(published_ids)!=36:raise ValueError('Expected first 36 historical references')
    selected=[{'id':e['id'],'currentMapping':e['mapping'],'auditClassification':e['classification']} for e in entries]
    old_inventory={q['id']:q for q in h.read_json(audit.report_folder()/'classification-inventory.json')['questions']}
    selected += [{**old_inventory[i],'currentMapping':reviews[i]['mapping']} for i in sorted(published_ids)]
    repairs=h.read_json(pilot.WORK/'accessibility-repairs.json')['repairs']
    scope=Counter(reviews[q['id']]['mapping']['conceptId'] for q in selected)
    bank,answers,concepts,links=pilot.project(selected,records,reviews,ledger['concepts'],repairs,associate=source_association,counts=scope)
    for q in bank:
        q['previewCollection']='published36' if q['id'] in published_ids else 'batch02'
        if q['previewCollection']=='published36':q['review'].update(reviewStatus='approved',publicationStatus='published')
    # Student-visible academic fields of the reference collection must equal live production.
    live_answers={e['questionId']:e for e in h.read_json(h.ROOT/'src/content/explanations.json')}
    live={q['id']:q for q in published}
    for q,e in zip(bank,answers):
        if q['id'] not in published_ids:continue
        for key in ['summary','steps','takeaway','optionText','imageDescription','answer']:
            if e[key]!=live_answers[q['id']][key]:raise ValueError('Released reference academic content changed')
        if q['correctAnswer']!=live[q['id']]['correctAnswer'] or q['image']['sha256']!=live[q['id']]['image']['sha256']:raise ValueError('Released answer/image changed')
    return bank,answers,concepts,links


def preview_overlay(bank,concepts):
    APP.mkdir(parents=True,exist_ok=True);pilot.overlay(APP,PREFIX)
    pilot.replace_checked(APP/'src/lib/models.ts','privatePreview: true;','privatePreview: true; previewCollection: "batch02" | "published36";')
    pilot.replace_checked(APP/'src/layouts/SiteLayout.astro','Private student preview · Not approved for publication · Disposable local progress',
        'Private comparison · Batch 2 additions are unapproved · Disposable local progress')
    high=APP/'src/lib/question-highlights.ts'
    pilot.replace_checked(high,'  return html.replace(','''  for(const c of concepts){
    const additions=bank.filter(q=>q.previewCollection==='batch02'&&c.questionIds.includes(q.id)).length;
    const released=bank.filter(q=>q.previewCollection==='published36'&&c.questionIds.includes(q.id)).length;
    html=html.replace(new RegExp('(<a\\\\b[^>]*data-concept="'+c.id+'"[^>]*>)([\\\\s\\\\S]*?)(<\\\\/a>)','g'),(_,open,body,close)=>open+body.replace(/<span class="concept-count"[^>]*>[\\s\\S]*?<\\/span>/g,`<span class="concept-count"> · ${additions} private + ${released} published</span>`)+close);
  }
  return html.replace(''')
    practice=APP/'src/components/Practice.tsx'
    pilot.replace_checked(practice,'questions: bank, explanations','questions: fullBank, explanations')
    pilot.replace_checked(practice,'  const { progress } = useProgress();',
        '  const [collection,setCollection] = useState("all");\n  const bank=fullBank.filter(q=>collection==="all" || q.previewCollection===collection);\n  const { progress } = useProgress();')
    pilot.replace_checked(practice,'<legend>Filter questions</legend>',
        '<legend>Filter questions</legend><label>Preview collection<select value={collection} onChange={e=>{setFeedbackId(undefined);setCollection(e.target.value);}}><option value="all">All preview questions</option><option value="batch02">Batch 2 · Private additions</option><option value="published36">Release 1 · Published reference</option></select></label>')
    pilot.replace_checked(practice,'{bank.length > 0 && controls}','{controls}')
    pilot.replace_checked(practice,'<div className="question-meta">',
        '<p className="source-note" data-preview-collection={question.previewCollection}>{question.previewCollection==="batch02"?"Batch 2 · Private addition · Unapproved":"Release 1 · Published reference"}</p><div className="question-meta">')
    index=APP/'src/pages/index.astro'
    pilot.replace_checked(index,'36-question local review; no publication approval.','40 private additions and 36 published references; local comparison only.')
    pilot.replace_checked(index,'{bank.length} historical questions across seven existing concepts.',
        '{bank.filter(q=>q.previewCollection==="batch02").length} Batch 2 private additions plus {bank.filter(q=>q.previewCollection==="published36").length} published Release 1 references across {concepts.length} concepts.')
    pilot.replace_checked(index,'Seven-concept walkthrough','Concept walkthrough and release comparison')
    pilot.replace_checked(index,'{questionsForConcept(c,bank).length} private questions',
        '{questionsForConcept(c,bank).filter(q=>q.previewCollection==="batch02").length} private additions · {questionsForConcept(c,bank).filter(q=>q.previewCollection==="published36").length} published references')
    # Existing server-side sourceHighlight rendering performs the actual private overlay.
    toc=h.read_json(APP/'src/content/hardware-toc.json')
    for node in toc['nodes']:
        for c in concepts:
            if c.get('sourceHighlight',{}).get('headingNumber')==node['number'] and c['id'] not in node['conceptIds']:node['conceptIds'].append(c['id'])
    pilot.save(APP/'src/content/hardware-toc.json',toc)


def assets_for(bank):
    assets={'/'+p.relative_to(APP/'dist').as_posix():{'path':str(p),'sha256':h.digest(p.read_bytes())} for p in (APP/'dist').rglob('*') if p.is_file()}
    originals={r['id']:r for r in h.read_json(h.WORK/'questions.json')}
    for q in bank:assets[q['image']['src']]={'path':str(h.WORK/originals[q['id']]['images'][0]['path']),'sha256':q['image']['sha256']}
    if any('/questions/' in name or '/data/' in name or name.endswith('.pdf') for name in assets):raise ValueError('Source material/public bank escaped private asset isolation')
    return assets


def recommendation(ledger,records,reviews,links):
    index={r['id']:r for r in records};associations={a['questionId']:a for a in links};rows=[]
    for entry in ledger['entries']:
        r=index[entry['id']];v=reviews[r['id']]
        rows.append({'id':r['id'],'pdfPage':entry['pdfPage'],'year':r['year'],'season':r['season'],'number':r['number'],
            'metadata':v['metadata'],'image':r['images'][0],'contentSha256':r['contentSha256'],
            'candidateFingerprint':h.publication_fingerprint(r,v),'correctAnswer':v['verification']['independentAnswer'],
            'explanation':v['explanation'],'accessibleTranscription':v['extraction'],'mapping':v['mapping'],
            'association':associations[r['id']],'independentlyVerified':h.valid_verification(r,v),
            'accessibleReview':'complete','chapterClassification':'supported','mappingStatus':'exact-verified',
            'sourceHighlight':'reviewed-private-only' if v['mapping']['conceptId'] in ledger['newHighlights'] else 'existing-reviewed',
            'metadataStatus':'owner-confirmed-complete','gradingEligibility':'eligible',
            'technicallyReadyForOwnerReview':not h.approval_errors(r,v),'approval':v['approval'],
            'publicationBlockers':['separate-exact-fingerprint-owner-authorization-required'],
            'editorialRepair':entry['editorialNote']})
    return {'schema':'itpec-future-candidate-recommendation-v1','privateOnly':True,'approvalGranted':False,'questions':rows}


def write_reports(ledger,records,before,reviews,links):
    candidate=recommendation(ledger,records,reviews,links);pilot.save(WORK/'candidate-recommendation.json',candidate)
    pilot.save(WORK/'review-diff.json',[{'id':e['id'],'beforeReviewSha256':e['beforeReviewSha256'],
        'afterReviewSha256':qa.object_hash(reviews[e['id']]),'previous':{k:before[e['id']].get(k) for k in DIMENSIONS},
        'revised':{k:reviews[e['id']][k] for k in DIMENSIONS}} for e in ledger['entries']])
    counts=Counter(e['mapping']['conceptId'] for e in ledger['entries'])
    lines=['# Hardware expansion Batch 2 — private preparation','',
        '40 additions prepared; all remain unapproved. The released 36 and all 456 public questions/images are unchanged.',
        '326 independently verified answers and seven qualified adjudications are preserved. No qualified case was selected.',
        f'40 questions span {len(counts)} concepts, including 15 new source-bound private highlights. No logic-gate additions were selected.',
        'The old 333-question audit was validated against its original pre-metadata snapshot, then the selected 40 were independently re-bound to the released baseline.',
        '', '## Complete preparation inventory','',
        '| PDF page | Canonical ID | Concept / heading | Book printed (physical PDF) pages | Editorial repair | Readiness |',
        '|---|---|---|---|---|---|']
    for q in candidate['questions']:
        pages=', '.join(f"{p['printedPage']} ({p['pdfPage']})" for p in q['mapping']['evidence'])
        lines.append(f"| {q['pdfPage']} | {q['id']} | {q['mapping']['conceptId']} / {q['mapping']['headingNumber']} | {pages} | {q['editorialRepair']} | Owner review ready; unapproved |")
    lines+=['','## Distribution','']+[f'- {key}: {value}' for key,value in sorted(counts.items())]
    lines+=['','## Preserved qualifications and repair queue','',
        'The literal choice D `25.` on physical page 221 is retained; the trailing period is not a changed numeric value. The question explicitly adds track-to-track seek time; the book provides general access-time and half-revolution latency support.',
        'Page 186 exponent groupings and page 311 IEEE exponents were restored in accessible text. Pages 32, 137, 174 and 248 retain original diagrams; descriptions state connections without solving the question. Page 300 retains the four original parameter-table rows.',
        'Device-driver source prose continues across printed pages 110–111. Display technology is entered through the intact Display paragraph and supported decisively by the plasma definition on printed page 99; its original figure remains visible in the lesson.',
        'All 40 academic verification and explanation objects remain exactly equal to the baseline, including existing wording. No academic re-verification or stylistic rewrite was substituted.',
        'The 12 effective partial extractions are outside this selected scope and remain unchanged. All other 257 unpublished historical records, including the seven qualified cases, remain in their existing private queues. Their advisory classifications have not been applied.',
        *[f"Deferred physical page {q['pdfPage']}: {q['reason']}" for q in ledger['deferred']],
        '', '## Final queue totals','',
        f"Native mappings: {dict(Counter(v['mapping']['status'] for v in reviews.values()))}.",
        f"Effective extractions: {dict(Counter(h.effective_extraction(r,reviews[r['id']]) for r in records))}.",
        '36 existing approvals; 297 unapproved records (40 prepared additions + 257 unselected). Zero new approvals or published additions.',
        '', '## Local review and future owner procedure','',
        '`python scripts/hardware_batch02.py check` verifies the exact source, review, public and preview fingerprints.',
        '`node scripts/private-student-preview-server.mjs --batch02` serves http://127.0.0.1:4327/. The established server accepts GET/HEAD on an exact hash allowlist, rejects foreign Host/Origin values, and binds to loopback.',
        'The preview contains 40 private additions and 36 unchanged published references, clearly labeled and filterable. All attempts, filters, bookmarks and reading checkpoints use a disposable private namespace. No Firebase runtime or credentials are included.',
        'Future publication must use the existing approval-candidate and publisher workflow after a separately authorized milestone. Recheck this recommendation against current source/review fingerprints, prepare the exact candidate payload and source highlights, compare it to this preview, and obtain explicit owner authorization bound to each final publication fingerprint. Any content, mapping, explanation or accessible-description change invalidates that authorization. This recommendation itself grants nothing.',
        'No merge, deployment, public catalog update, Practice source edit or approval has occurred.']
    (WORK/'completion-report.md').write_text('\n'.join(lines)+'\n',encoding='utf8')
    out=io.StringIO();writer=csv.writer(out);writer.writerow(['id','historical_pdf_page','concept','heading','book_printed_pages','book_physical_pages','technical_ready','approval'])
    for q in candidate['questions']:writer.writerow([q['id'],q['pdfPage'],q['mapping']['conceptId'],q['mapping']['headingNumber'],','.join(str(p['printedPage']) for p in q['mapping']['evidence']),','.join(str(p['pdfPage']) for p in q['mapping']['evidence']),True,'unapproved'])
    (WORK/'inventory.csv').write_text(out.getvalue(),encoding='utf8')


def prepare():
    initialize_guard();ledger,records,before,current,expected,published=load_context()
    selected={e['id'] for e in ledger['entries']}
    with fitz.open(h.SOURCE) as source:qa.validate_source_images([r for r in records if r['id'] in selected],source)
    if current!=expected:
        h.write_json(h.WORK/'reviews.json',expected);h.write_review_gallery(records)
    bank,answers,concepts,links=payload(ledger,records,expected,published)
    preview_overlay(bank,concepts)
    for name,value in [('pilot-bank',bank),('explanations',answers),('concepts',concepts)]:pilot.save(APP/f'src/content/{name}.json',value)
    for command in ['check','build']:
        if subprocess.run(['node',str(h.ROOT/'node_modules/astro/bin/astro.mjs'),command],cwd=APP,env=pilot.environment()).returncode:raise ValueError('Private application validation/build failed')
    manifest={'schema':'itpec-hardware-batch02-preview-v1','privateOnly':True,'approvalGranted':False,
        'baseline':BASELINE,'snapshot':qa.snapshot_hashes(h.WORK),'decisionLedgerSha256':h.digest((WORK/'decisions.json').read_bytes()),
        'implementation':implementation(),'questionIds':[e['id'] for e in ledger['entries']],
        'referenceIds':[q['id'] for q in bank if q['previewCollection']=='published36'],
        'sourceImagesCompared':40,'associations':links,'assets':assets_for(bank),'progressPrefix':PREFIX,
        'appSources':{p.relative_to(APP).as_posix():h.digest(p.read_bytes()) for p in (APP/'src').rglob('*') if p.is_file()}}
    pilot.save(WORK/'preview/manifest.json',manifest);write_reports(ledger,records,before,expected,links);check()


def check():
    ledger,records,before,current,expected,published=load_context()
    if current!=expected:raise ValueError('Reviewed repairs have not been applied')
    manifest=h.read_json(WORK/'preview/manifest.json')
    if not manifest or manifest.get('schema')!='itpec-hardware-batch02-preview-v1' or manifest.get('privateOnly') is not True or manifest.get('approvalGranted') is not False or manifest.get('snapshot')!=qa.snapshot_hashes(h.WORK) or manifest.get('implementation')!=implementation() or manifest.get('decisionLedgerSha256')!=h.digest((WORK/'decisions.json').read_bytes()) or manifest.get('progressPrefix')!=PREFIX:
        raise ValueError('Private preview is stale or not isolated')
    bank,answers,concepts,links=payload(ledger,records,current,published)
    if manifest.get('questionIds')!=[e['id'] for e in ledger['entries']] or manifest.get('referenceIds')!=[q['id'] for q in bank if q['previewCollection']=='published36'] or len(bank)!=76 or manifest.get('associations')!=links:
        raise ValueError('Exact 40+36 comparison scope changed')
    for name,value in [('pilot-bank',bank),('explanations',answers),('concepts',concepts)]:
        if h.read_json(APP/f'src/content/{name}.json')!=value:raise ValueError('Candidate-to-preview equality failed')
    if manifest.get('assets')!=assets_for(bank) or manifest.get('appSources')!={p.relative_to(APP).as_posix():h.digest(p.read_bytes()) for p in (APP/'src').rglob('*') if p.is_file()}:raise ValueError('Generated preview sources/assets changed')
    for asset in manifest['assets'].values():
        file=Path(asset['path']).resolve()
        if not (file.is_relative_to((APP/'dist').resolve()) or file.is_relative_to((h.WORK/'images').resolve())) or h.digest(file.read_bytes())!=asset['sha256']:raise ValueError('Private asset root/hash changed')
    for file in (APP/'dist').rglob('*'):
        if file.suffix in ['.html','.js','.json']:
            text=file.read_text('utf8')
            if any(s in text for s in ['firestore.googleapis.com','identitytoolkit.googleapis.com','itpec-textbook.firebaseapp.com','AIzaSyBE9','preparationHistory','beforeReviewSha256','Printed key:','editorial-review-pending']):raise ValueError('Cloud runtime or private QA history leaked into student UI')
    candidate=recommendation(ledger,records,current,links)
    if h.read_json(WORK/'candidate-recommendation.json')!=candidate or any(not q['technicallyReadyForOwnerReview'] or q['approval']['status']!='unapproved' for q in candidate['questions']):raise ValueError('Recommendation stale, blocked or approved')
    print('Batch 2 integrity: 40 prepared/unapproved + 36 unchanged published references; 456 public questions untouched; 326 independent answers preserved.')
    return manifest


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('command',choices=['prepare','check']);args=parser.parse_args()
    prepare() if args.command=='prepare' else check()
