"""Private final-66 audit adapter for the existing review/preview/approval pipeline.

No approval transition, public writer or new question store is provided.
"""
import argparse
import copy
from collections import Counter
import html
import json
from pathlib import Path
import re
import shutil
import subprocess
import fitz
import historical_questions as h
import academic_qa as qa
import catalog_audit as audit
import hardware_batch02 as core
import hardware_batch03 as preview
import private_student_preview as pilot
import approval_candidates as candidates

BASELINE='5800c9e0ca0069649aa6404f672a827eb8c192db'
BRANCH='feature/technology01-phase08-other-chapters'
WORK=h.ROOT/'.local/historical-batches/technology01-phase08'
APP=WORK/'preview/app'
PREFIX='itpecTextbook:privatePhase08:'
COUNTS={'ch1':25,'other-vol1':29,'uncertain':9,'outside-vol1':3}
INPUTS=['audit.json','editorial-overlays.json','highlight-plan.json','other-chapter-inventory.json','hardware-recovery.json','classification-triage.json','duplicate-check.json','source-review/pixel-check.json','full-volume-search.json','independent-calculations.json']
REPORTS=['FINAL-66-AUDIT.md','OTHER-CHAPTER-INTEGRATION.md','HARDWARE-RECOVERY.md','UNCERTAIN-OUTSIDE-TRIAGE.md','ROADMAP.md','classification-inventory.csv']
CHAPTERS={1:'Hardware',2:'Information Processing System',3:'Software',4:'Database',5:'Network',6:'Security',7:'Data Structure and Algorithm'}


def freeze():
    if (WORK/'baseline.json').exists():return verify_baseline()
    if core.git('branch','--show-current')!=BRANCH or core.git('rev-parse','HEAD')!=BASELINE or core.git('rev-parse','origin/main')!=BASELINE:
        raise ValueError('Fresh authorized main baseline and Phase 8 branch required')
    from release_7 import verify_public
    verify_public()
    records=h.read_json(h.WORK/'questions.json');reviews=h.read_json(h.WORK/'reviews.json')
    public=h.read_json(h.ROOT/'public/data/questions.json');published={r['id'] for r in public}
    original={r['id']:r for r in h.read_json(audit.FOLDER/'decisions.json')['entries']}
    private=[r for r in records if r['id'] not in published]
    if len(public)!=687 or len(private)!=66 or Counter(original[r['id']]['classification']['category'] for r in private)!=COUNTS:
        raise ValueError('Actual final-66 categories differ; reconcile before freezing')
    if sum(h.valid_approval(r,reviews[r['id']]) for r in records)!=267 or any(reviews[r['id']]['approval']['status']!='unapproved' for r in private):
        raise ValueError('Expected 267 prior approvals and 66 unapproved records')
    protected={r['id'] for r in private if reviews[r['id']].get('ownerAdjudication')}
    if len(protected)!=7 or {r['regions'][0]['pdfPage'] for r in private if r['id'] in protected}!=core.PROTECTED or any(original[q]['classification']['category']!='ch1' for q in protected):
        raise ValueError('Seven qualified cases must remain within the 25 Hardware deferrals')
    WORK.mkdir(parents=True,exist_ok=True)
    for name in ['questions.json','reviews.json','manifest.json','index.html']:
        target=WORK/'before'/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(h.WORK/name,target)
    prior={p.relative_to(h.ROOT).as_posix():h.digest(p.read_bytes()) for folder in [h.ROOT/'.local/releases',h.ROOT/'.local/historical-batches/technology01-hardware-batch07'] for p in folder.rglob('*') if p.is_file()}
    pilot.save(WORK/'baseline.json',{'schema':'itpec-phase08-baseline-v1','baseline':BASELINE,'snapshot':qa.snapshot_hashes(h.WORK),'nativeFiles':{n:h.digest((h.WORK/n).read_bytes()) for n in ['questions.json','reviews.json','manifest.json','index.html']},
        'publicFiles':core.public_fingerprints(),'priorEvidenceFiles':prior,'privateIds':[r['id'] for r in private],
        'groups':{category:[r['id'] for r in private if original[r['id']]['classification']['category']==category] for category in COUNTS},
        'protectedIds':sorted(protected),'originalAuditSha256':h.digest((audit.FOLDER/'decisions.json').read_bytes()),
        'sourceSha256':audit.SOURCE_SHA,'textbookSha256':audit.BOOK_SHA,'approvals':267,'publicQuestions':687})
    print('Frozen exact 66 private records, 267 approvals, 687 public pairs and previous evidence; no review object changed.')


def verify_baseline():
    state=h.read_json(WORK/'baseline.json')
    if not state or state.get('baseline')!=BASELINE or state.get('schema')!='itpec-phase08-baseline-v1':raise ValueError('Missing Phase 8 baseline')
    if qa.snapshot_hashes(h.WORK)!=state['snapshot'] or core.public_fingerprints()!=state['publicFiles']:raise ValueError('Native reviews/approvals or public application changed')
    for name,sha in state['nativeFiles'].items():
        if h.digest((h.WORK/name).read_bytes())!=sha or h.digest((WORK/'before'/name).read_bytes())!=sha:raise ValueError('Native history or frozen snapshot changed')
    for name,sha in state['priorEvidenceFiles'].items():
        if h.digest((h.ROOT/name).read_bytes())!=sha:raise ValueError('Earlier release evidence changed: '+name)
    if h.digest(h.SOURCE.read_bytes())!=state['sourceSha256'] or h.digest(qa.TEXTBOOK.read_bytes())!=state['textbookSha256'] or h.digest((audit.FOLDER/'decisions.json').read_bytes())!=state['originalAuditSha256']:
        raise ValueError('Source or classification history changed')
    return state


def validate_evidence(evidence,pages):
    for ev in evidence:
        n=ev.get('pdfPage')
        if not isinstance(n,int) or not 1<=n<=487:raise ValueError('Invalid textbook page')
        page=pages[n-1];text=ev.get('checkedExcerpt','')
        if ev.get('kind')!='textbook-source' or ev.get('sourceSha256')!=audit.BOOK_SHA or ev.get('textSha256')!=page['textSha256'] or ev.get('printedPage')!=page['printedPage'] or not text or text not in h.norm(page['text']) or ev.get('role') not in ['direct','context','secondary']:
            raise ValueError('Stale or invented source passage/page reference')


def actual_heading(chapter,number,title,pages):
    number_pattern=r'\s*-\s*'.join(re.escape(part) for part in number.split('-'))
    pattern=re.compile(r'(?<![\d-])'+number_pattern+r'\s+'+re.escape(title),re.I)
    found=[p for p in pages if audit.chapter_at(p['pdfPage'])==chapter and pattern.search(h.norm(p['text']))]
    if len(found)!=1:raise ValueError('Missing or ambiguous actual textbook heading: '+str((chapter,number,title)))
    return {'pdfPage':found[0]['pdfPage'],'printedPage':found[0]['printedPage'],'number':number,'title':title}


def validate_inventory(report,state,records,reviews,pages,overlays,duplicates):
    """Independent source binding and scope gate; a report cannot grant authority."""
    if report.get('schema')!='itpec-phase08-audit-v1' or report.get('baseline')!=BASELINE or report.get('snapshot')!=state['snapshot'] or report.get('sourceSha256')!=audit.SOURCE_SHA or report.get('textbookSha256')!=audit.BOOK_SHA or report.get('publicationApprovalGranted') is not False:
        raise ValueError('Stale Phase 8 audit baseline')
    rows=report.get('questions',[]);ids=[r['id'] for r in rows]
    if len(ids)!=66 or len(set(ids))!=66 or set(ids)!=set(state['privateIds']) or Counter(r['originalCategory'] for r in rows)!=COUNTS or report.get('counts')!=COUNTS:
        raise ValueError('Exact 66/29/25/9/3 scope required')
    index={r['id']:r for r in records};repairs=overlays.get('repairs',[])
    if overlays.get('schema')!='itpec-phase08-editorial-overlays-v1' or overlays.get('nativeApplied') is not False or len({r['id'] for r in repairs})!=len(repairs):raise ValueError('Invalid private editorial overlays')
    for repair in repairs:
        qid=repair['id'];r=index[qid];v=reviews[qid]
        if qid not in state['privateIds'] or qid in state['protectedIds'] or repair.get('sourceBinding')!=qa.extraction_binding(r) or repair.get('beforeReviewSha256')!=qa.object_hash(v) or repair.get('pdfPage')!=r['regions'][0]['pdfPage']:
            raise ValueError('Protected, stale or out-of-scope editorial overlay')
        if repair.get('before')!={k:v['extraction'].get(k) for k in ['imageDescription','optionText']} or set(repair.get('after',{}))!={'imageDescription','optionText'} or repair.get('status')!='source-validated' or repair.get('nativeApplied') is not False or repair.get('academicChanged') is not False or not repair.get('reason') or repair.get('validationMethod')!='original-pdf-image-visual-review-and-pixel-matched-crop':
            raise ValueError('Unvalidated overlay or change beyond accessible fields')
        after=repair['after']
        if not after['imageDescription'] or set(after['optionText'])!=set('abcd') or not all(after['optionText'].values()):raise ValueError('Incomplete reviewed source transcription')
    dup={r['id']:r for r in duplicates.get('questions',[])}
    if set(dup)!=set(ids):raise ValueError('Duplicate authority check scope changed')
    for row in rows:
        qid=row['id'];r=index[qid];v=reviews[qid];category=row['originalCategory']
        if qid not in state['groups'][category] or row.get('sourceBinding')!=qa.extraction_binding(r) or row.get('beforeReviewSha256')!=qa.object_hash(v) or row.get('pdfPage')!=r['regions'][0]['pdfPage'] or row.get('sourceImageIntegrity')!='pixel-matched' or row.get('academicVerified')!=h.valid_verification(r,v) or row.get('protected')!=(qid in state['protectedIds']):
            raise ValueError('Source, image, review or original classification binding changed')
        if row.get('exam')!={'type':'FE','paper':'AM','subject':'A','year':r['year'],'season':r['season'],'number':r['number']} or any(v.get('metadata',{}).get(k)!=val for k,val in [('examType','FE'),('paper','AM'),('subject','A'),('status','verified')]):raise ValueError('Original examination metadata changed or is unverified')
        if not row.get('primaryDisposition') or not row.get('blockers') or not row.get('nextAction') or row.get('approval')!='unapproved' or row.get('selected') is not False or row.get('publicationEligible') is not False or row.get('academicAnswerUnchanged') is not True or row.get('workedExplanationUnchanged') is not True:
            raise ValueError('Missing unique disposition or unauthorized eligibility/approval')
        if row.get('websiteRoute') is not None or row.get('websiteAnchor') is not None:raise ValueError('No student route or anchor may be invented')
        validate_evidence(row.get('textbookEvidence',[]),pages)
        if row.get('accessibleReview'):
            repair=next((e for e in repairs if e['id']==qid),None)
            expected=repair['after'] if repair else {k:v['extraction'].get(k) for k in ['imageDescription','optionText']}
            status='source-validated-private-overlay' if repair else 'source-validated-native-review'
            if row['accessibleReview']!={'status':status,'content':expected,'sha256':qa.object_hash(expected)}:raise ValueError('Missing or unvalidated accessible editorial overlay')
        proposal=row.get('privateMappingProposal')
        if proposal:
            if category!='ch1' or row['protected'] or proposal.get('primaryChapter')!=1 or proposal.get('status')!='source-evidence-bound-future-hardware-only':raise ValueError('Future Hardware evidence cannot expand the candidate scope')
            validate_evidence(proposal['evidence'],pages)
            if any(audit.chapter_at(e['pdfPage'])!=1 and e['role']!='secondary' for e in proposal['evidence']):raise ValueError('Other-chapter support must remain separately typed secondary evidence')
            if proposal.get('sourceFigureBinding'):
                region=next(r for r in h.read_json(h.ROOT/'src/content/hardware-spatial-crops.json')['regions'] if r['id']==proposal['sourceFigureBinding'].get('regionId'))
                expected={'kind':'existing-complete-spatial-crop','sourceSha256':audit.BOOK_SHA,'regionId':region['id'],'pdfPage':region['pdfPage'],'printedPage':region['printedPage'],'bbox':region['bbox'],'url':region['url'],'asset':region['asset']}
                if proposal['sourceFigureBinding']!=expected or h.digest((h.ROOT/'public'/region['asset']['path']).read_bytes())!=region['asset']['sha256']:raise ValueError('Complete source topology crop binding changed')
        if dup[qid].get('sourceBinding')!=qa.extraction_binding(r) or dup[qid]['result']['status']!='distinct':raise ValueError('Duplicate needs separate Practice-authority review')
        if category=='other-vol1':
            chapter=row.get('chapter')
            if chapter not in [2,3,5,7] or row.get('chapterTitle')!=CHAPTERS[chapter] or not row.get('textbookEvidence') or not any(audit.chapter_at(e['pdfPage'])==chapter and e['role']!='secondary' for e in row['textbookEvidence']):raise ValueError('Question mapped to an unsupported chapter')
            actual_heading(chapter,row['headingNumber'],row['headingTitle'],pages)
            x=row.get('accessibleReview',{});content=x.get('content',{})
            repair=next((e for e in repairs if e['id']==qid),None)
            expected=repair['after'] if repair else {k:v['extraction'].get(k) for k in ['imageDescription','optionText']}
            if content!=expected or x.get('sha256')!=qa.object_hash(expected) or not content.get('imageDescription') or set(content.get('optionText',{}))!=set('abcd') or not all(content['optionText'].values()) or re.search('[\u0b00-\u0b7f\ue000-\uf8ff]',json.dumps(content,ensure_ascii=False)):
                raise ValueError('Incomplete, stale or corrupted accessible source text')
            if row['duplicateAuthority']['status']!='distinct' or not row.get('singleAnswerGrading') or 'textbook-chapter-not-implemented' not in row['blockers']:raise ValueError('Missing academic/routing independence')
            if row.get('academicAnswerFingerprint')!=qa.object_hash(v['verification']) or row.get('workedExplanationFingerprint')!=qa.object_hash(v['explanation']) or row.get('examMetadataFingerprint')!=qa.object_hash(v['metadata']):raise ValueError('Academic or examination dossier fingerprint changed')
            fields=['id','sourceBinding','beforeReviewSha256','accessibleReview','academicAnswerFingerprint','workedExplanationFingerprint','examMetadataFingerprint','chapter','headingNumber','headingTitle','concept','textbookEvidence']
            if row.get('reviewDossierFingerprint')!=qa.object_hash({k:row[k] for k in fields}):raise ValueError('Student-visible/source dossier binding changed')
            # This milestone has no converted chapters or legitimate student anchors.
            # A future real chapter implementation needs a new reviewed baseline.
            if row['classificationHistory']['placement']=='context-only' and row['classificationConfidence']!='context-only':raise ValueError('Context cannot be silently promoted to direct teaching')
    if report.get('selectedIds')!=[]:raise ValueError('No source-backed implemented other-chapter route exists in this baseline')
    if {r['id'] for r in rows if r['protected']}!=set(state['protectedIds']):raise ValueError('Seven protected records must remain excluded')
    return rows


def inputs():
    state=verify_baseline();records=h.read_json(WORK/'before/questions.json');reviews=h.read_json(WORK/'before/reviews.json');pages=core.book_pages()
    report=h.read_json(WORK/'audit.json');overlays=h.read_json(WORK/'editorial-overlays.json');duplicates=h.read_json(WORK/'duplicate-check.json')
    rows=validate_inventory(report,state,records,reviews,pages,overlays,duplicates)
    for name,category in [('other-chapter-inventory.json','other-vol1'),('hardware-recovery.json','ch1')]:
        if h.read_json(WORK/name)!=[r for r in rows if r['originalCategory']==category]:raise ValueError('Companion inventory disagrees')
    if h.read_json(WORK/'classification-triage.json')!=[r for r in rows if r['originalCategory'] in ['uncertain','outside-vol1']]:raise ValueError('Classification triage scope differs')
    pixel=h.read_json(WORK/'source-review/pixel-check.json')
    if pixel.get('records')!=66 or pixel.get('allPixelMatched') is not True or pixel.get('ids')!=state['privateIds'] or pixel.get('sourceSha256')!=audit.SOURCE_SHA or pixel.get('originalImagesReplaced') is not False:raise ValueError('Complete original-image pixel comparison is required')
    h.verify_assets(records)
    highlights=h.read_json(WORK/'highlight-plan.json')
    for proposal in highlights:
        if proposal.get('publicationApprovalGranted') is not False or proposal.get('websiteRoute') is not None or proposal.get('websiteAnchor') is not None or proposal.get('htmlFragmentFingerprint') is not None or not proposal.get('status','').startswith('deferred-') or not proposal['questionIds'] or not set(proposal['questionIds'])<=set(state['groups']['other-vol1']):raise ValueError('Unsupported highlight cannot become an integrated student binding')
        validate_evidence(proposal['sourceEvidence'],pages)
    if set(q for p in highlights for q in p['questionIds'])!=set(state['groups']['other-vol1']):raise ValueError('All 29 highlight needs must be accounted for')
    calculations=h.read_json(WORK/'independent-calculations.json')
    computed=calculations.get('computedQuestions',[]);byid={r['id']:r for r in records}
    if calculations.get('sourceSha256')!=audit.SOURCE_SHA or len(computed)!=15 or len({r['id'] for r in computed})!=15 or calculations.get('protectedCasesSolved')!=0 or calculations.get('academicObjectsModified')!=0:raise ValueError('Missing separate source-bound calculation checks')
    for result in computed:
        qid=result['id']
        if qid not in state['groups']['other-vol1'] or result.get('sourceBinding')!=qa.extraction_binding(byid[qid]) or result.get('academicVerificationFingerprint')!=qa.object_hash(reviews[qid]['verification']) or result.get('sourceChoice')!=reviews[qid]['verification']['independentAnswer'] or result.get('answerChanged') is not False or result.get('textbookMappingGranted') is not False:raise ValueError('Calculation check altered academic or mapping authority')
    return state,report,records,reviews,rows


def implementation():
    files=[Path(__file__),Path(preview.__file__),Path(pilot.__file__),h.ROOT/'scripts/approval_candidates.py',h.ROOT/'scripts/phase08_report.py',h.ROOT/'scripts/private-student-preview-server.mjs',h.ROOT/'scripts/question-review-server.mjs',h.ROOT/'scripts/publish-historical-questions.ts',h.ROOT/'src/lib/question-policy.ts',h.ROOT/'package.json',h.ROOT/'package-lock.json',*pilot.TEMPLATES.rglob('*')]
    return {p.relative_to(h.ROOT).as_posix():h.digest(p.read_bytes()) for p in files if p.is_file()}


def preview_payload():
    state,report,records,reviews,rows=inputs()
    public=h.read_json(h.ROOT/'public/data/questions.json');concepts=h.read_json(h.ROOT/'src/content/concepts.json')
    bank,answers,definitions,links=preview.payload({'entries':[],'concepts':concepts},records,reviews,public,collection='phase08',selection_count=0)
    if len(bank)!=290 or links or any(q['id'] in state['privateIds'] for q in bank):raise ValueError('Preview must contain only the 290 existing Hardware references and zero private additions')
    return bank,answers,definitions,public


def prepare_preview():
    if (WORK/'preview/manifest.json').exists():return check_preview()
    bank,answers,definitions,public=preview_payload()
    preview.preview_overlay(bank,definitions,public,app=APP,prefix=PREFIX,collection='phase08',label='Phase 8',selection_count=0)
    index=APP/'src/pages/index.astro'
    pilot.replace_checked(index,'<h2>All 0 Phase 8 questions</h2>','<p>Published sitewide catalog: 687 questions. This isolated preview has 290 unchanged Chapter 1 Hardware references and zero new private candidates. Chapters 2, 3, 5 and 7 have no available reading collections here.</p><h2>No new Phase 8 questions available</h2>')
    for name,value in [('pilot-bank',bank),('explanations',answers),('concepts',definitions)]:pilot.save(APP/f'src/content/{name}.json',value)
    pilot.save(APP/'src/content/owner-review.json',[])
    # An empty eligible scope has no question properties to render. Do not cast
    # an empty JSON array to fake candidate types or show deferred audit material.
    (APP/'src/pages/review.astro').write_bytes(b'''---
import SiteLayout from '../layouts/SiteLayout.astro';
---
<SiteLayout title="Phase 8 review" description="Local preparation status" companion={false} noindex>
<section class="chapter-overview"><h1>Phase 8 review</h1><p>No new questions are available in this preview.</p><p>Existing Hardware reference collections remain available with disposable local progress.</p><a href="/">Return to preview collections</a></section>
</SiteLayout>
''')
    for command in ['check','build']:
        subprocess.run(['node',str(h.ROOT/'node_modules/astro/bin/astro.mjs'),command],cwd=APP,env=pilot.environment(),check=True)
    pilot.save(WORK/'preview/manifest.json',{'schema':'itpec-phase08-private-preview-v1','privateOnly':True,'publicationApprovalGranted':False,'questionIds':[],'referenceIds':[q['id'] for q in bank],'assets':preview.assets_for(bank,app=APP),'progressPrefix':PREFIX,'sitewidePublished':687,'hardwareReferences':290,'privateCandidates':0,'appSources':{p.relative_to(APP).as_posix():h.digest(p.read_bytes()) for p in (APP/'src').rglob('*') if p.is_file()}})
    return check_preview()


def check_preview():
    m=h.read_json(WORK/'preview/manifest.json');bank,answers,definitions,_=preview_payload()
    if not m or m.get('schema')!='itpec-phase08-private-preview-v1' or m.get('privateOnly') is not True or m.get('publicationApprovalGranted') is not False or m.get('questionIds')!=[] or m.get('referenceIds')!=[q['id'] for q in bank] or m.get('progressPrefix')!=PREFIX or m.get('sitewidePublished')!=687 or m.get('hardwareReferences')!=290 or m.get('privateCandidates')!=0:raise ValueError('Stale or mixed private preview scope')
    for name,value in [('pilot-bank',bank),('explanations',answers),('concepts',definitions)]:
        if h.read_json(APP/f'src/content/{name}.json')!=value:raise ValueError('Preview payload changed')
    if h.read_json(APP/'src/content/owner-review.json')!=[]:raise ValueError('Ineligible audit material entered the student preview')
    if m['assets']!=preview.assets_for(bank,app=APP) or m['appSources']!={p.relative_to(APP).as_posix():h.digest(p.read_bytes()) for p in (APP/'src').rglob('*') if p.is_file()}:raise ValueError('Private preview sources/assets changed')
    private=inputs()[0]['privateIds']
    for name,asset in m['assets'].items():
        file=Path(asset['path']).resolve()
        if not (file.is_relative_to((APP/'dist').resolve()) or file.is_relative_to((h.WORK/'images').resolve())) or h.digest(file.read_bytes())!=asset['sha256']:raise ValueError('Private preview asset root/hash changed')
        if file.suffix in ['.html','.js','.json']:
            text=file.read_text('utf8')
            if any(s in text for s in ['firestore.googleapis.com','identitytoolkit.googleapis.com','itpec-textbook.firebaseapp.com','AIzaSyBE9',*private]):raise ValueError('Cloud runtime or ineligible private material leaked to student preview')
    return m


def prepare():
    root=WORK/'final-approval'
    if (root/'manifest.json').exists():return check()
    state,report,records,reviews,rows=inputs();m=prepare_preview()
    from phase08_report import write_reports,owner_gallery
    write_reports(rows)
    root.mkdir(parents=True,exist_ok=True)
    (root/'index.html').write_bytes(owner_gallery(rows).encode())
    public=h.read_json(h.ROOT/'public/data/questions.json')
    context={'schema':'itpec-phase08-final-preparation-v1','baselineCommit':BASELINE,'questionIds':[],'conceptCounts':{},'authorizedOtherChapterIds':state['groups']['other-vol1'],'privateIds':state['privateIds'],'releasedQuestionIds':[q['id'] for q in public if q['id'].startswith('HIST-')],'sourceSha256':audit.SOURCE_SHA,'textbookSha256':audit.BOOK_SHA,'snapshot':state['snapshot'],'files':{name:h.digest((WORK/name).read_bytes()) for name in [*INPUTS,*REPORTS,'preview/manifest.json']},'publicationApprovalGranted':False}
    pilot.save(root/'preparation-inputs.json',context)
    manifest={'schema':'itpec-final-approval-candidates-v1','batch':8,'baselineCommit':BASELINE,'privateOnly':True,'readOnly':True,'publicationApprovalGranted':False,'questionIds':[],'conceptCounts':{},'candidates':[],'conceptDefinitions':[],'highlightIntegration':[],'preparationStatus':'blocked-no-implemented-other-chapter-routes','publicationReady':False,'originalScopeCount':29,'deferredCount':29,'futureApprovalFingerprints':{},'sourceSha256':audit.SOURCE_SHA,'textbookSha256':audit.BOOK_SHA,'implementation':implementation(),'preparationInputsSha256':qa.object_hash(context),'previewEquality':{'candidateQuestions':0,'previewPrivateQuestions':0,'allStudentVisibleFieldsEqual':True,'referenceQuestions':290},'candidateSetFingerprint':qa.object_hash({'ids':[],'candidates':[],'conceptDefinitions':[],'highlightIntegration':[],'sourceSha256':audit.SOURCE_SHA,'textbookSha256':audit.BOOK_SHA}),
        'galleryAssets':{'/':{'path':str(root/'index.html'),'sha256':h.digest((root/'index.html').read_bytes())},**{f'/images/{r["id"]}.webp':{'path':str(h.WORK/r['images'][0]['path']),'sha256':r['images'][0]['sha256']} for r in records if r['id'] in state['privateIds']}}}
    pilot.save(root/'manifest.json',manifest)
    pilot.save(root/'equality-report.json',manifest['previewEquality'])
    pilot.save(root/'owner-review-checklist.json',[{'id':r['id'],'candidate':False,'approval':'unapproved','remainingBlockers':r['blockers']} for r in rows if r['originalCategory']=='other-vol1'])
    return check()


def check(publisher=False):
    state,report,records,reviews,rows=inputs();preview_manifest=check_preview();root=WORK/'final-approval'
    context=h.read_json(root/'preparation-inputs.json');manifest=h.read_json(root/'manifest.json')
    if not context or context.get('schema')!='itpec-phase08-final-preparation-v1' or context.get('baselineCommit')!=BASELINE or context.get('snapshot')!=state['snapshot'] or context.get('authorizedOtherChapterIds')!=state['groups']['other-vol1'] or context.get('privateIds')!=state['privateIds'] or context.get('sourceSha256')!=audit.SOURCE_SHA or context.get('textbookSha256')!=audit.BOOK_SHA or context.get('publicationApprovalGranted') is not False:raise ValueError('Missing or stale exact Phase 8 preparation')
    expected_files=[*INPUTS,*REPORTS,'preview/manifest.json']
    if set(context.get('files',{}))!=set(expected_files) or any(h.digest((WORK/name).read_bytes())!=sha for name,sha in context['files'].items()):raise ValueError('Stale source-reviewed Phase 8 input')
    candidates.validate_final_package(manifest,[],[],[],context,batch=8,expected_count=0)
    if manifest.get('implementation')!=implementation() or manifest.get('preparationInputsSha256')!=qa.object_hash(context) or manifest.get('preparationStatus')!='blocked-no-implemented-other-chapter-routes' or manifest.get('publicationReady') is not False or manifest.get('originalScopeCount')!=29 or manifest.get('deferredCount')!=29 or manifest.get('futureApprovalFingerprints')!={}:raise ValueError('Stale or falsely approval-ready Phase 8 package')
    expected_equality={'candidateQuestions':0,'previewPrivateQuestions':0,'allStudentVisibleFieldsEqual':True,'referenceQuestions':290}
    if manifest.get('previewEquality')!=expected_equality or h.read_json(root/'equality-report.json')!=expected_equality:raise ValueError('Candidate-to-preview scope differs')
    expected_checklist=[{'id':r['id'],'candidate':False,'approval':'unapproved','remainingBlockers':r['blockers']} for r in rows if r['originalCategory']=='other-vol1']
    if h.read_json(root/'owner-review-checklist.json')!=expected_checklist:raise ValueError('Per-question eligibility checklist changed')
    from phase08_report import owner_gallery
    if (root/'index.html').read_text('utf8')!=owner_gallery(rows):raise ValueError('Read-only audit gallery changed')
    expected_assets={'/':{'path':str(root/'index.html'),'sha256':h.digest((root/'index.html').read_bytes())},**{f'/images/{r["id"]}.webp':{'path':str(h.WORK/r['images'][0]['path']),'sha256':r['images'][0]['sha256']} for r in records if r['id'] in state['privateIds']}}
    if manifest['galleryAssets']!=expected_assets:raise ValueError('Owner gallery assets changed')
    public=h.read_json(h.ROOT/'public/data/questions.json')
    if context['releasedQuestionIds']!=[q['id'] for q in public if q['id'].startswith('HIST-')]:raise ValueError('Previous released scope changed')
    return manifest


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('command',choices=['freeze','prepare','check','preview-check']);args=p.parse_args()
    if args.command=='freeze':freeze()
    elif args.command=='prepare':prepare();print('Private Phase 8 audit package prepared; zero eligible additions, zero new approvals.')
    elif args.command=='preview-check':check_preview();print('Phase 8 isolated reference preview validated.')
    else:check();print('Phase 8 full audit, deferred dossiers and exact empty candidate package validated; no publication authorization.')
