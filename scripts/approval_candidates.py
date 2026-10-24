"""Prepare/check exact native publication candidates; never grant approval."""
import argparse
from collections import Counter
import contextlib
import copy
import html
import io
import json
import re
from pathlib import Path
import shutil
import subprocess
import fitz
import historical_questions as h
import academic_qa as qa
import approval_editorial as editorial
import metadata_integration as metadata
import private_student_preview as pilot


def save(path,value):pilot.save(path,value)


def integrate_native():
    root=editorial.folder();context=editorial.inputs();old=h.read_json(root/'before/reviews.json')
    records=h.read_json(h.WORK/'questions.json');source=h.digest(h.SOURCE.read_bytes())
    if source!=context['sourceSha256'] or h.digest(qa.TEXTBOOK.read_bytes())!=context['bookSha256'] or h.digest((h.WORK/'questions.json').read_bytes())!=context['snapshot']['questionFileSha256']:
        raise ValueError('Source PDF, textbook or immutable records changed')
    repairs=h.read_json(root/'before/repairs.json')
    pilot.validated_repairs(records,old,repairs)
    expected=editorial.merge_native(records,old,repairs['repairs'])
    state=h.read_json(metadata.FOLDER/'applied-state.json');manifest=h.read_json(h.WORK/'manifest.json')
    if state.get('editorialReconciliation'):
        metadata.validate_transition()
        if h.read_json(h.WORK/'reviews.json')!=expected:raise ValueError('Stale native editorial output')
        return
    if qa.snapshot_hashes(h.WORK)!=context['snapshot'] or state!=h.read_json(root/'before/metadata-state.json'):
        raise ValueError('Stale candidate preparation snapshot')
    # Validate all affected pixels against the original, without writing images.
    with fitz.open(h.SOURCE) as pdf:qa.validate_source_images([r for r in records if r['id'] in editorial.SCOPE],pdf)
    if sum(h.valid_verification(r,expected[r['id']]) for r in records)!=326 or sum(h.valid_adjudication(r,expected[r['id']]) for r in records)!=7 or any(v['approval']['status']!='unapproved' for v in expected.values()):
        raise ValueError('Native transfer changed academic evidence or publication authority')
    archive=root/'before/audit-metadata-reports'
    if not archive.exists():shutil.copytree(pilot.audit.report_folder(),archive)
    _,binding=metadata.inputs();receipt=editorial.marker()
    manifest['metadataReconciliation']=binding;manifest['editorialReconciliation']=receipt
    h.write_json(h.WORK/'reviews.json',expected);h.write_json(h.WORK/'manifest.json',manifest);h.write_review_gallery(records)
    rebound,findings=metadata.rebind_preview(expected)
    save(pilot.WORK/'accessibility-repairs.json',rebound);save(pilot.WORK/'review-findings.json',findings)
    state.update(inputs=binding,snapshot=qa.snapshot_hashes(h.WORK),editorialReconciliation=receipt)
    state['changedFiles']={name:{'sha256':h.digest((h.WORK/name).read_bytes()),'mtimeNs':(h.WORK/name).stat().st_mtime_ns} for name in ['reviews.json','manifest.json','index.html']}
    h.write_json(metadata.FOLDER/'applied-state.json',state)
    save(root/'editorial-reconciliation.json',{'receipt':receipt,'beforeSnapshot':context['snapshot'],'afterSnapshot':state['snapshot'],
        'changes':[{'id':qid,'beforeReviewSha256':qa.object_hash(old[qid]),'afterReviewSha256':qa.object_hash(expected[qid]),
            'fields':['extraction.imageDescription']+(['extraction.optionText.d'] if page==28 else [])+['extraction.editorialProvenance']} for qid,page in editorial.SCOPE.items()],
        'academicEvidenceChanged':False,'rawQuestionsOrImagesChanged':False,'approvalsGranted':0})
    metadata.validate_transition()


def without_approval(review):return {k:v for k,v in review.items() if k!='approval'}


def visible(record,review):
    x=review['extraction'];e=review['explanation'];m=review['metadata'];im=record['images'][0]
    return {'id':record['id'],'examType':m['examType'],'paper':m['paper'],'subject':m['subject'],
        'year':record['year'],'season':record['season'],'number':record['number'],
        'image':{key:im[key] for key in ['sha256','width','height']},'imageDescription':x['imageDescription'],'optionText':x['optionText'],
        'correctAnswer':review['verification']['independentAnswer'],'summary':e['summary'],'steps':e['steps'],'takeaway':e['takeaway'],'mapping':review['mapping']}


def preview_visible(question,explanation):
    return {'id':question['id'],'examType':'FE','paper':question['paper'],'subject':question['subject'],
        'year':question['year'],'season':question['season'],'number':question['number'],
        'image':{key:question['image'][key] for key in ['sha256','width','height']},
        **{key:explanation[key] for key in ['imageDescription','optionText','summary','steps','takeaway']},
        'correctAnswer':question['correctAnswer'],'mapping':question['mapping']}


def implementation():
    names=['scripts/approval_candidates.py','scripts/approval_editorial.py','scripts/question-review-server.mjs','scripts/publish-historical-questions.ts']
    names+=['scripts/historical-highlight.ts']
    return {name:h.digest((h.ROOT/name).read_bytes()) for name in names}


def build_entries(records,reviews,ids,associations,bank,answers,*,expected_count=36):
    index={r['id']:r for r in records};questions={q['id']:q for q in bank};explanations={e['questionId']:e for e in answers}
    if len(ids)!=expected_count or len(set(ids))!=expected_count or set(ids)!=set(questions) or set(ids)!=set(explanations):raise ValueError(f'Approval preparation requires exactly the same {expected_count} preview IDs')
    entries=[]
    for qid in ids:
        r=index[qid];v=reviews[qid];content=visible(r,v)
        if v.get('ownerAdjudication') or not h.valid_verification(r,v) or v['approval']['status']!='unapproved':raise ValueError('Candidate is not independently verified and unapproved')
        if content!=preview_visible(questions[qid],explanations[qid]):raise ValueError('Native publication payload differs from validated private preview')
        errors=h.approval_errors(r,v)
        if errors:raise ValueError(f'Candidate is not technically eligible: {qid}: {errors}')
        association=next(a for a in associations if a['questionId']==qid)
        entries.append({'id':qid,'record':r,'review':v,'publicationFingerprint':h.publication_fingerprint(r,v),
            'nativeReviewSha256':qa.object_hash(without_approval(v)),'studentVisible':content,'studentVisibleSha256':qa.object_hash(content),
            'textbookSupport':association,'grading':{'status':'eligible','basis':'existing independent verification','singleAnswer':True},
            'technicalEligibility':True,'remainingBlockers':['final-owner-publication-approval-absent'],'publicationApprovalGranted':False})
    return entries


def render_gallery(manifest,concepts):
    esc=lambda value:html.escape(str(value),quote=True)
    entries=manifest['candidates'];titles={c['id']:c['title'] for c in concepts};count=len(entries)
    nav=''.join(f'<li><a href="#concept-{esc(cid)}">{esc(titles[cid])} ({count})</a></li>' for cid,count in manifest['conceptCounts'].items())
    all_nav=''.join(f'<li><a href="#{esc(e["id"])}">{esc(e["id"])} · PDF {e["record"]["regions"][0]["pdfPage"]}</a></li>' for e in entries)
    groups=[]
    for cid in manifest['conceptCounts']:
        cards=[]
        for e in entries:
            if e['review']['mapping']['conceptId']!=cid:continue
            r=e['record'];v=e['review'];x=v['extraction'];a=e['textbookSupport'];i=entries.index(e);im=r['images'][0]
            options=''.join(f'<li><strong>{key.upper()}.</strong> {esc(value)}</li>' for key,value in x['optionText'].items())
            steps=''.join(f'<li>{esc(step)}</li>' for step in v['explanation']['steps'])
            passages=''.join(f'<blockquote><p>{esc(ev["checkedExcerpt"])}</p><footer>FE Volume 1 · printed p.{ev["printedPage"]} / physical PDF p.{ev["pdfPage"]} · {esc(ev["role"])} support</footer></blockquote>' for ev in a['bookEvidence'])
            paragraph=re.sub(r'\s+·\s+\d+\s+questions?\b','',a['paragraphText'])
            prev=f'<a href="#{esc(entries[i-1]["id"])}">Previous question</a>' if i else ''
            nxt=f'<a href="#{esc(entries[i+1]["id"])}">Next question</a>' if i+1<len(entries) else ''
            editorial_note='<p class="integrity">Validated accessibility correction is integrated into the native publication review; original image and academic evidence are unchanged.</p>' if r['id'] in editorial.SCOPE else ''
            eligibility='Technically eligible for owner review' if e['technicalEligibility'] else 'Technical correction required before approval'
            blockers=''.join(f'<li>{esc(value)}</li>' for value in e['remainingBlockers'])
            highlight_label=('New source highlight · source validated; owner editorial approval pending' if e['highlightIntegration']['status']=='source-validated-pending-owner-editorial-approval' else 'New source highlight · correction required; owner editorial approval absent') if e.get('highlightIntegration',{}).get('newConcept') else 'Existing reviewed highlight'
            context_binding=f'<dt>Concept and passage context fingerprint</dt><dd>{esc(e["approvalContextFingerprint"])}</dd>' if e.get('approvalContextFingerprint') else ''
            cards.append(f'''<article id="{esc(r['id'])}" tabindex="-1" data-question="{esc(r['id'])}">
<header><p>FE · Morning · Subject A · {r['year']} {'Spring' if r['season']=='S' else 'Autumn'} · Q{r['number']} · historical PDF p.{r['regions'][0]['pdfPage']}</p><h3>{esc(r['id'])}</h3><p class="eligibility">{eligibility} · Approval: <strong>unapproved</strong> · Publication blocked</p><details class="blockers"><summary>Remaining blockers</summary><ul>{blockers}</ul></details></header>
<div class="review-columns"><div><figure><a href="/images/{esc(r['id'])}.webp" aria-label="Open full-size original {esc(r['id'])}"><img src="/images/{esc(r['id'])}.webp" width="{im['width']}" height="{im['height']}" loading="lazy" alt="{esc(x['imageDescription'])}"></a><figcaption>Unchanged original question crop. Open the image for full-size reading.</figcaption></figure><h4>Accessible question and diagram</h4><p class="transcription">{esc(x['imageDescription'])}</p><ol class="choices">{options}</ol>{editorial_note}</div>
<div><h4>Verified correct answer: {esc(v['verification']['independentAnswer'].upper())}</h4><p class="answer-summary">{esc(v['explanation']['summary'])}</p><ol class="worked-steps">{steps}</ol><p>{esc(v['explanation']['takeaway'])}</p><h4>Exact textbook placement</h4><p>{esc(v['mapping']['sectionId'])} / {esc(v['mapping']['subsectionId'])} · heading {esc(v['mapping']['headingNumber'])} · concept {esc(cid)}</p><p class="highlight-status">{highlight_label}: printed p.{a['highlightPrintedPage']} / physical PDF p.{a['highlightPhysicalPdfPage']}.</p><blockquote class="highlight-preview"><p>{esc(paragraph)}</p><footer>Website source paragraph {esc(a['sourceParagraphId'])}; exam-count annotation omitted</footer></blockquote>{passages}<details><summary>Integrity and approval binding</summary><dl><dt>Image SHA-256</dt><dd>{esc(im['sha256'])}</dd><dt>Source content SHA-256</dt><dd>{esc(r['contentSha256'])}</dd><dt>Exact publication fingerprint</dt><dd>{esc(e['publicationFingerprint'])}</dd>{context_binding}<dt>Candidate equals validated preview</dt><dd>Yes — all student-visible academic fields</dd><dt>Grading</dt><dd>Independently verified, single-answer eligible. No qualified owner-adjudicated cases included.</dd></dl></details></div></div>
<nav aria-label="Question navigation">{prev} <a href="#question-index">All {count} questions</a> {nxt}</nav></article>''')
        groups.append(f'<section id="concept-{esc(cid)}" aria-labelledby="title-{esc(cid)}"><h2 id="title-{esc(cid)}">{esc(titles[cid])} · {len(cards)} questions</h2>'+''.join(cards)+'</section>')
    page='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><meta name="robots" content="noindex,nofollow"><title>Final 36-question owner review</title><style>
body{font:16px/1.6 system-ui;background:#faf8f1;color:#18232d;max-width:1200px;margin:auto;padding:24px}a{color:#304a63}a:focus-visible,summary:focus-visible{outline:3px solid #be8615;outline-offset:4px}.skip{display:block}article{padding:28px 0;border-bottom:1px solid #aaa;scroll-margin-top:16px}h3,dd,blockquote,p,li{overflow-wrap:anywhere}h2{margin-top:48px}figure{margin:0}img{width:100%;height:auto}figcaption,footer{font-size:.88rem;color:#4b5560}blockquote{margin:12px 0;padding:12px 16px;border-left:3px solid #b4aa91;background:#f0ece2}nav ul,#question-index ol{display:flex;flex-wrap:wrap;gap:8px 24px;padding-left:24px}.review-columns{display:grid;grid-template-columns:minmax(0,1.1fr) minmax(0,1fr);gap:28px}.review-columns>div{min-width:0}.choices{list-style:none;padding:0}.choices li{padding:8px;border:1px solid #aaa;margin:8px 0}.eligibility,.integrity{background:#e9eee6;padding:10px}dd{margin-left:0;font:12px/1.6 monospace}article nav{display:flex;gap:24px;flex-wrap:wrap;margin-top:20px}@media(max-width:780px){body{padding:16px}.review-columns{grid-template-columns:1fr}h3{font-size:1.1rem}}
</style><body><a class="skip" href="#question-index">Skip to all 36 questions</a><header><p>PRIVATE · LOOPBACK ONLY · READ-ONLY</p><h1>Final 36-question owner review</h1><p>36 of 36 candidates exactly match the validated private preview in all student-visible academic content. Both accessibility corrections are now native publication transcriptions. Original images, answers and worked explanations are unchanged.</p><p><strong>Zero publication approvals.</strong> Every question remains unapproved. No approval controls, student-progress writes, authentication or publication actions are available here.</p><nav aria-label="Concept groups"><ul>'''+nav+'</ul></nav></header><section id="question-index"><h2>All 36 questions</h2><ol>'+all_nav+'</ol></section>'+''.join(groups)+'</body></html>'
    if count!=36:
        valid=sum(r['status']=='source-validated-pending-owner-editorial-approval' for r in manifest.get('highlightIntegration',[]))
        page=page.replace('36-question',f'{count}-question').replace('36 questions',f'{count} questions').replace('36 of 36',f'{count} of {count}').replace('Both accessibility corrections are now native publication transcriptions.',f'{valid} of {manifest.get("expectedNewHighlights",15)} new source highlights are source validated; individual correction blockers, if present, are listed below. Final owner editorial approval remains pending.')
        checklist='<section id="review-checklist"><h2>Complete owner-review checklist</h2><p>Read-only technical checklist; no owner decisions have been recorded.</p><ol>'
        for e in entries:checklist+=f'<li data-checklist="{esc(e["id"])}"><a href="#{esc(e["id"])}">{esc(e["id"])}</a> · Image, accessible choices, verified answer, explanation, FE/Morning/Subject A metadata, exact mapping and preview equality checked · {"Technically ready" if e["technicalEligibility"] else "Correction required"} · Owner decision pending</li>'
        page=page.replace('</header><section id="question-index">','</header>'+checklist+'</ol></section><section id="question-index">')
    return page


def prepare():
    branch=subprocess.check_output(['git','branch','--show-current'],cwd=h.ROOT,text=True).strip()
    if branch!=pilot.audit.BRANCH or subprocess.run(['git','merge-base','--is-ancestor',editorial.BASELINE,'HEAD'],cwd=h.ROOT,capture_output=True).returncode:raise ValueError('Wrong feature branch or preparation baseline')
    integrate_native()
    with contextlib.redirect_stdout(io.StringIO()):pilot.audit.run(check=False)
    try:
        with contextlib.redirect_stdout(io.StringIO()):pilot.check()
    except ValueError:
        pilot.prepare()
    root=editorial.folder();context=editorial.inputs();records,reviews,selected=pilot.validated_inputs();pm=h.read_json(pilot.WORK/'manifest.json')
    bank=h.read_json(pilot.APP/'src/content/pilot-bank.json');answers=h.read_json(pilot.APP/'src/content/explanations.json')
    old_bank=h.read_json(root/'before/pilot-bank.json');old_answers=h.read_json(root/'before/pilot-explanations.json')
    if bank!=old_bank or answers!=old_answers:raise ValueError('Preparation changed validated preview content, academic revisions or progress identities')
    entries=build_entries(records,reviews,context['questionIds'],pm['associations'],bank,answers)
    with fitz.open(h.SOURCE) as pdf:qa.validate_source_images([e['record'] for e in entries],pdf)
    manifest={'schema':'itpec-final-approval-candidates-v1','baselineCommit':editorial.BASELINE,'privateOnly':True,'readOnly':True,'publicationApprovalGranted':False,
        'preparationInputsSha256':qa.object_hash(context),'catalogSnapshot':qa.snapshot_hashes(h.WORK),'editorialReconciliation':editorial.marker(),
        'sourceSha256':context['sourceSha256'],'textbookSha256':context['bookSha256'],'questionIds':context['questionIds'],'conceptCounts':context['conceptCounts'],
        'implementation':implementation(),'previewEquality':{'originalPilot':True,'currentPilot':True,'questions':36,'fields':list(entries[0]['studentVisible']),'academicRevisionAndProgressCompatibility':True},
        'publicCatalogSha256':h.digest((h.ROOT/'public/data/questions.json').read_bytes()),'candidates':entries}
    text=render_gallery(manifest,h.read_json(h.ROOT/'src/content/concepts.json'))
    page=root/'index.html'
    if not page.exists() or page.read_text('utf-8')!=text:page.write_text(text,encoding='utf-8')
    assets={'/':{'path':str(page),'sha256':h.digest(page.read_bytes())}}
    for e in entries:
        image=e['record']['images'][0];assets[f'/images/{e["id"]}.webp']={'path':str(h.WORK/image['path']),'sha256':image['sha256']}
    manifest['galleryAssets']=assets;save(root/'manifest.json',manifest)
    check();write_report(manifest)
    print('Prepared exactly 36 native publication candidates; all remain unapproved. Owner gallery: node scripts/question-review-server.mjs --approval-candidates')


def check(publisher=False,batch=1):
    if batch==2:return check_batch02(publisher)
    if batch==3:return check_batch03(publisher)
    if batch==5:
        if publisher:
            import release_5
            if (release_5.FOLDER/'state.json').exists():return release_5.publisher_check()
        from approval_batch05 import check
        return check(publisher)
    if batch==4:return check_batch04(publisher)
    root=editorial.folder();context=editorial.inputs();manifest=h.read_json(root/'manifest.json')
    if not manifest or manifest.get('schema')!='itpec-final-approval-candidates-v1' or manifest.get('questionIds')!=context['questionIds'] or manifest.get('conceptCounts')!=context['conceptCounts'] or len(manifest.get('candidates',[]))!=36 or manifest.get('privateOnly') is not True or manifest.get('readOnly') is not True or manifest.get('publicationApprovalGranted') is not False:
        raise ValueError('Missing, expanded or unapproved-scope candidate package')
    if manifest.get('implementation')!=implementation() or manifest.get('preparationInputsSha256')!=qa.object_hash(context) or manifest.get('editorialReconciliation')!=editorial.marker():raise ValueError('Stale candidate implementation or source/overlay binding')
    h.verify_source();records=h.read_json(h.WORK/'questions.json');reviews=h.read_json(h.WORK/'reviews.json');index={r['id']:r for r in records}
    expected=editorial.merge_native(h.read_json(root/'before/questions.json'),h.read_json(root/'before/reviews.json'),h.read_json(root/'before/repairs.json')['repairs'])
    frozen_entries=build_entries(h.read_json(root/'before/questions.json'),expected,context['questionIds'],
        h.read_json(root/'before/pilot-manifest.json')['associations'],h.read_json(root/'before/pilot-bank.json'),h.read_json(root/'before/pilot-explanations.json'))
    if manifest['candidates']!=frozen_entries:raise ValueError('Final candidate evidence or textbook context differs from the frozen reviewed payload')
    equality={'originalPilot':True,'currentPilot':True,'questions':36,'fields':list(frozen_entries[0]['studentVisible']),'academicRevisionAndProgressCompatibility':True}
    if manifest.get('previewEquality')!=equality:raise ValueError('Candidate equality evidence changed')
    if h.digest(h.SOURCE.read_bytes())!=manifest['sourceSha256'] or h.digest(qa.TEXTBOOK.read_bytes())!=manifest['textbookSha256'] or h.digest((h.ROOT/'public/data/questions.json').read_bytes())!=manifest['publicCatalogSha256']:
        raise ValueError('Source/textbook/public Practice snapshot changed')
    for e in manifest['candidates']:
        qid=e['id'];r=index[qid];v=reviews[qid]
        if r!=e['record'] or without_approval(v)!=without_approval(expected[qid]) or qa.object_hash(without_approval(v))!=e['nativeReviewSha256'] or h.publication_fingerprint(r,v)!=e['publicationFingerprint'] or visible(r,v)!=e['studentVisible'] or qa.object_hash(e['studentVisible'])!=e['studentVisibleSha256']:
            raise ValueError('Candidate payload or approval fingerprint is stale')
        if e['review']!=expected[qid] or e['remainingBlockers']!=['final-owner-publication-approval-absent'] or e.get('publicationApprovalGranted') is not False or not e.get('technicalEligibility') or h.approval_errors(r,v):raise ValueError('Candidate grading, placement, accessibility or approval status changed')
        if not publisher and v['approval']['status']!='unapproved':raise ValueError('Read-only owner preparation must retain unapproved status')
    if Counter(e['review']['mapping']['conceptId'] for e in manifest['candidates'])!=context['conceptCounts'] or [e['id'] for e in manifest['candidates']]!=context['questionIds']:
        raise ValueError('Candidate IDs or seven-concept distribution changed')
    h.verify_assets([e['record'] for e in manifest['candidates']])
    if not publisher:
        with contextlib.redirect_stdout(io.StringIO()):pilot.check()
        if qa.snapshot_hashes(h.WORK)!=manifest['catalogSnapshot']:raise ValueError('Read-only candidate snapshot changed')
        entries=build_entries(records,reviews,context['questionIds'],h.read_json(pilot.WORK/'manifest.json')['associations'],h.read_json(pilot.APP/'src/content/pilot-bank.json'),h.read_json(pilot.APP/'src/content/explanations.json'))
        if entries!=manifest['candidates']:raise ValueError('Candidate-to-preview equality changed')
    expected_page=render_gallery(manifest,h.read_json(h.ROOT/'src/content/concepts.json'))
    if (root/'index.html').read_text('utf-8')!=expected_page:raise ValueError('Owner gallery no longer matches exact reviewed payload')
    expected_assets={'/':{'path':str(root/'index.html'),'sha256':h.digest((root/'index.html').read_bytes())}}
    for e in manifest['candidates']:
        im=e['record']['images'][0];expected_assets[f'/images/{e["id"]}.webp']={'path':str(h.WORK/im['path']),'sha256':im['sha256']}
    if manifest['galleryAssets']!=expected_assets:raise ValueError('Owner gallery asset allowlist changed')
    return manifest


def write_report(manifest):
    root=editorial.folder();lines=['# Final 36-question owner approval preparation','',
        'Both source-validated accessibility overlays are integrated into native extraction reviews. The existing publisher reads the corrected native descriptions and options; no preview-only merge is required. All academic answers, explanations, verification evidence, metadata, source images, raw transcripts, classifications and mappings are unchanged. Only the two extraction reviews and editorial provenance changed.','',
        'All 36 final payloads exactly equal the original and current validated private preview in student-visible academic fields. Canonical IDs, storage keys and academic revisions remain compatible. No owner-adjudicated question or other historical question was added.','',
        '| ID | Historical PDF | Concept / heading | Native correction | Technically eligible | Approval | Remaining blocker | Publication fingerprint |',
        '|---|---:|---|---|---|---|---|---|']
    for e in manifest['candidates']:
        r=e['record'];m=e['review']['mapping']
        lines.append(f'| {e["id"]} | {r["regions"][0]["pdfPage"]} | {m["conceptId"]} / {m["headingNumber"]} | {"integrated" if e["id"] in editorial.SCOPE else "original reviewed transcription"} | yes | unapproved | final owner publication approval | {e["publicationFingerprint"]} |')
    lines+=['','The gallery is read-only and serves only its generated page and 36 original allowlisted images. No raw PDF, other 297 historical images, JSON catalog/review files or authentication/progress endpoint is exposed.','',
        'The existing publication validator remains authoritative. Each fingerprint is the existing `publication_fingerprint(record, review)`, binding the complete question, answer, explanation, metadata, mapping and corrected extraction, excluding only the mutable approval object. Any content change invalidates an old approval. The publisher also checks this exact candidate package before native export; missing/stale corrections or manifest block promotion.','',
        'Launch: `node scripts/question-review-server.mjs --approval-candidates`, then http://127.0.0.1:4319/ . Student preview remains separately available at http://127.0.0.1:4324/ . Future approval procedure and regression/build results are in the tracked development report. No approval, publication, merge or deployment occurred.']
    path=root/'completion-report.md';text='\n'.join(lines)+'\n'
    if not path.exists() or path.read_text('utf-8')!=text:path.write_text(text,encoding='utf-8')
    save(root/'equality-report.json',{'originalPilot':36,'currentPilot':36,'nativeCorrectedPayloads':2,'academicChanges':0,'otherHistoricalQuestionsAdded':0,
        'candidateStudentHashes':{e['id']:e['studentVisibleSha256'] for e in manifest['candidates']},'ownerApprovals':0})


# Batch 2 uses the same entries, visible-content comparator, gallery and approval
# fingerprints. Its already validated native reviews need no editorial transfer.
BATCH02_BASELINE='3e6c959c6941e68b61d29becbb79ffac0e26c23f'
BATCH02_INPUTS=('completion-report.md','candidate-recommendation.json','review-diff.json','inventory.csv',
    'completion-integrity.json','preview/manifest.json','preview/app/src/content/pilot-bank.json',
    'preview/app/src/content/explanations.json','preview/app/src/content/concepts.json','decisions.json','baseline-guard.json')
CONCEPT_FIELDS=('id','title','summary','sectionId','sectionUrl','anchor','sourceHighlight')


def batch02_folder():return h.WORK.parent/'approval-candidates'/f'{h.WORK.name}-batch02'


def concept_view(concept):return {k:copy.deepcopy(concept[k]) for k in CONCEPT_FIELDS if k in concept}


def freeze_batch02():
    import hardware_batch02 as batch
    root=batch02_folder()
    if (root/'preparation-inputs.json').exists():return
    if batch.git('branch','--show-current')!=batch.BRANCH or subprocess.run(['git','merge-base','--is-ancestor',BATCH02_BASELINE,'HEAD'],cwd=h.ROOT,capture_output=True).returncode:
        raise ValueError('Wrong Batch 2 branch/baseline')
    with contextlib.redirect_stdout(io.StringIO()):pm=batch.check()
    integrity=h.read_json(batch.WORK/'completion-integrity.json')
    if integrity['commit']!=BATCH02_BASELINE or integrity['nativeSnapshot']!=qa.snapshot_hashes(h.WORK):raise ValueError('Prepared Batch 2 integrity receipt is stale')
    files={name:h.digest((batch.WORK/name).read_bytes()) for name in BATCH02_INPUTS}
    for name in BATCH02_INPUTS:
        target=root/'before/batch'/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(batch.WORK/name,target)
    for name in ['questions.json','reviews.json','manifest.json','index.html']:
        target=root/'before/native'/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(h.WORK/name,target)
    bank=h.read_json(batch.APP/'src/content/pilot-bank.json');ids=pm['questionIds'];published=h.read_json(h.ROOT/'public/data/questions.json')
    published_ids=[q['id'] for q in published if q['id'].startswith('HIST-')]
    if len(ids)!=40 or len(set(ids))!=40 or len(published_ids)!=36 or set(ids)&set(published_ids):raise ValueError('Batch 2 and released scopes overlap or changed')
    save(root/'preparation-inputs.json',{'schema':'itpec-final-candidate-preparation-batch02-v1','baselineCommit':BATCH02_BASELINE,
        'productionBaseline':batch.BASELINE,'files':files,'snapshot':qa.snapshot_hashes(h.WORK),'questionIds':ids,
        'conceptCounts':dict(sorted(Counter(q['topic'] for q in bank if q['id'] in ids).items())),
        'releasedQuestionIds':published_ids,'publicFiles':batch.public_fingerprints(),
        'nativeFiles':{name:h.digest((h.WORK/name).read_bytes()) for name in ['questions.json','reviews.json','manifest.json','index.html']},
        'sourceSha256':batch.audit.SOURCE_SHA,'textbookSha256':batch.audit.BOOK_SHA,'publicationApprovalGranted':False})


def batch02_inputs(publisher=False):
    import hardware_batch02 as batch
    root=batch02_folder();context=h.read_json(root/'preparation-inputs.json')
    if not context or context.get('schema')!='itpec-final-candidate-preparation-batch02-v1' or context.get('baselineCommit')!=BATCH02_BASELINE or context.get('publicationApprovalGranted') is not False or set(context.get('files',{}))!=set(BATCH02_INPUTS):raise ValueError('Missing exact Batch 2 preparation context')
    if batch.git('branch','--show-current')!=batch.BRANCH or subprocess.run(['git','merge-base','--is-ancestor',BATCH02_BASELINE,'HEAD'],cwd=h.ROOT,capture_output=True).returncode:raise ValueError('Wrong Batch 2 feature branch')
    for name,sha in context['files'].items():
        if h.digest((root/'before/batch'/name).read_bytes())!=sha or h.digest((batch.WORK/name).read_bytes())!=sha:raise ValueError('Stale original Batch 2 input: '+name)
    original=h.read_json(root/'before/batch/preview/manifest.json');integrity=h.read_json(root/'before/batch/completion-integrity.json')
    bank=h.read_json(root/'before/batch/preview/app/src/content/pilot-bank.json')
    counts=dict(sorted(Counter(q['topic'] for q in bank if q['id'] in original['questionIds']).items()))
    if context['questionIds']!=original['questionIds'] or context['conceptCounts']!=counts or integrity['commit']!=BATCH02_BASELINE or context['snapshot']!=integrity['nativeSnapshot'] or context['sourceSha256']!=integrity['sourceSha256'] or context['textbookSha256']!=integrity['bookSha256']:
        raise ValueError('Preparation context differs from the completed exact Batch 2 receipt')
    if qa.snapshot_hashes(root/'before/native')!=context['snapshot'] or any(h.digest((root/'before/native'/name).read_bytes())!=sha for name,sha in context['nativeFiles'].items()):raise ValueError('Frozen native preparation input changed')
    if not publisher and any(h.digest((h.WORK/name).read_bytes())!=sha for name,sha in context['nativeFiles'].items()):raise ValueError('Live read-only native snapshot changed')
    if context['publicFiles']!=batch.public_fingerprints():raise ValueError('Published questions, images or application source changed')
    h.verify_source();records=h.read_json(h.WORK/'questions.json');reviews=h.read_json(h.WORK/'reviews.json');frozen=h.read_json(root/'before/native/reviews.json')
    if records!=h.read_json(root/'before/native/questions.json') or h.digest(h.SOURCE.read_bytes())!=context['sourceSha256'] or h.digest(qa.TEXTBOOK.read_bytes())!=context['textbookSha256'] or h.digest((h.WORK/'manifest.json').read_bytes())!=context['snapshot']['manifestFileSha256']:raise ValueError('Native/source/textbook bindings changed')
    ids=context['questionIds'];published=h.read_json(h.ROOT/'public/data/questions.json')
    if len(ids)!=40 or len(set(ids))!=40 or set(ids)&set(context['releasedQuestionIds']) or len(context['releasedQuestionIds'])!=36 or set(context['releasedQuestionIds'])!={q['id'] for q in published if q['id'].startswith('HIST-')}:raise ValueError('Exact 40-question scope or released scope changed')
    validate_live_reviews(records,reviews,frozen,ids,publisher)
    for q in published:
        if q['id'] in context['releasedQuestionIds']:
            r=next(r for r in records if r['id']==q['id']);v=reviews[q['id']]
            if not h.valid_approval(r,v) or q['review']['approvalFingerprint']!=v['approval']['fingerprint']:raise ValueError('Existing historical approval/public fingerprint changed')
    if not publisher:
        with contextlib.redirect_stdout(io.StringIO()):batch.check()
    h.verify_assets(records)
    return context,records,reviews,frozen


def validate_live_reviews(records,reviews,frozen,ids,publisher=False):
    if len(records)!=333 or set(reviews)!=set(frozen) or set(reviews)!={r['id'] for r in records}:raise ValueError('Complete native catalog scope changed')
    for r in records:
        v=reviews[r['id']];old=frozen[r['id']]
        if r['id'] not in ids:
            if v!=old:raise ValueError('Noncandidate or released native review changed')
        elif without_approval(v)!=without_approval(old) or (not publisher and v!=old):raise ValueError('Candidate content/approval changed during read-only preparation')
        elif v['approval']['status'] not in ['unapproved','approved']:raise ValueError('Unexpected approval status')


def batch02_concepts(context):
    root=batch02_folder();concepts=h.read_json(root/'before/batch/preview/app/src/content/concepts.json')
    public=h.read_json(h.ROOT/'src/content/concepts.json');known={c['id']:c for c in public};scoped=[]
    for cid in context['conceptCounts']:
        concept=next(c for c in concepts if c['id']==cid);view=concept_view(concept)
        if cid in known and view!=concept_view(known[cid]):raise ValueError('Existing concept definition changed in preview')
        scoped.append({**view,'newConcept':cid not in known})
    if len(scoped)!=21 or sum(c['newConcept'] for c in scoped)!=15:raise ValueError('Exact 21 concepts / 15 new highlights required')
    return scoped


def validate_batch02_highlights(concepts,prepare=False):
    root=batch02_folder()
    if prepare:save(root/'concept-plan.json',concepts)
    elif h.read_json(root/'concept-plan.json')!=concepts:raise ValueError('Prepared concept plan changed; reject stale output')
    run=subprocess.run(['node',str(h.ROOT/'node_modules/tsx/dist/cli.mjs'),str(h.ROOT/'scripts/historical-highlight.ts'),str(root/'concept-plan.json')],cwd=h.ROOT,capture_output=True,text=True,encoding='utf8')
    if run.returncode:raise ValueError('Existing publisher highlight gate rejected the preparation plan: '+run.stderr)
    report=json.loads(run.stdout)
    if len(report)!=15 or {r['conceptId'] for r in report}!={c['id'] for c in concepts if c['newConcept']}:raise ValueError('Highlight integration review scope changed')
    return report


def batch02_associations(context,records,reviews,concepts):
    import hardware_batch02 as batch
    root=batch02_folder();pm=h.read_json(root/'before/batch/preview/manifest.json');associations=[]
    for qid in context['questionIds']:
        a=copy.deepcopy(next(a for a in pm['associations'] if a['questionId']==qid));v=reviews[qid];c=next(c for c in concepts if c['id']==v['mapping']['conceptId'])
        current=batch.source_association({'id':qid,'currentMapping':v['mapping'],'auditClassification':{'evidence':v['mapping']['evidence']}},c)
        if current!=a:raise ValueError('Prepared question/highlight association changed')
        text=(h.ROOT/a['sourceFile']).read_text('utf8')
        if c.get('sourceHighlight'):pid=c['sourceHighlight']['passageId']
        else:
            anchor=re.search(r'<a\b[^>]*data-concept="'+re.escape(c['id'])+r'"',text)
            p=text.rfind('<p ',0,anchor.start());pid=re.search(r'\bid="([^"]+)"',text[p:text.find('>',p)])[1]
        a['sourceParagraphId']=pid;associations.append(a)
    return associations


def approval_context_fingerprint(entry,concept):
    binding={'publicationFingerprint':entry['publicationFingerprint'],'studentVisibleSha256':entry['studentVisibleSha256'],
        'conceptDefinition':concept,'textbookSupport':entry['textbookSupport']}
    for key in ['finalSourceReview','sourceTranscription','finalHighlightReview']:
        if key in entry:binding[key]=entry[key]
    return qa.object_hash(binding)


def batch02_entries(context,records,reviews,concepts,highlight_report):
    root=batch02_folder();ids=context['questionIds'];frozen=h.read_json(root/'before/native/reviews.json')
    bank=[q for q in h.read_json(root/'before/batch/preview/app/src/content/pilot-bank.json') if q['id'] in ids]
    answers=[e for e in h.read_json(root/'before/batch/preview/app/src/content/explanations.json') if e['questionId'] in ids]
    associations=batch02_associations(context,records,reviews,concepts)
    entries=build_entries(records,frozen,ids,associations,bank,answers,expected_count=40)
    for e in entries:
        c=next(c for c in concepts if c['id']==e['review']['mapping']['conceptId'])
        e['conceptDefinition']=c;e['approvalContextFingerprint']=approval_context_fingerprint(e,c)
        e['highlightIntegration']={'newConcept':c['newConcept'],'status':'existing-reviewed-highlight' if not c['newConcept'] else next(r['status'] for r in highlight_report if r['conceptId']==c['id']),
            'ownerEditorialApprovalGranted':False,'wordingChanged':False,'previewDefinitionSha256':qa.object_hash(concept_view(c))}
        if c['newConcept']:
            e['remainingBlockers'].append('final-owner-editorial-highlight-approval-absent')
            if e['highlightIntegration']['status']!='source-validated-pending-owner-editorial-approval':
                e['technicalEligibility']=False;e['remainingBlockers'].append('source-highlight-correction-required')
    return entries


def prepare_batch02():
    freeze_batch02();context,records,reviews,frozen=batch02_inputs();root=batch02_folder()
    concepts=batch02_concepts(context);highlight_report=validate_batch02_highlights(concepts,prepare=True)
    entries=batch02_entries(context,records,reviews,concepts,highlight_report)
    with fitz.open(h.SOURCE) as pdf:qa.validate_source_images([e['record'] for e in entries],pdf)
    special={3,32,137,186,221,300,311}
    visual_review=[{'id':e['id'],'pdfPage':e['record']['regions'][0]['pdfPage'],'imageSha256':e['record']['images'][0]['sha256'],
        'accessibleFieldsSha256':qa.object_hash({k:e['review']['extraction'][k] for k in ['imageDescription','optionText']}),
        'status':'visually-rechecked-against-original-image-and-pixel-matched-pdf','newContentCorrection':False}
        for e in entries if e['record']['regions'][0]['pdfPage'] in special]
    manifest={'schema':'itpec-final-approval-candidates-v1','batch':2,'baselineCommit':BATCH02_BASELINE,'privateOnly':True,'readOnly':True,
        'publicationApprovalGranted':False,'preparationInputsSha256':qa.object_hash(context),'catalogSnapshot':context['snapshot'],
        'sourceSha256':context['sourceSha256'],'textbookSha256':context['textbookSha256'],'questionIds':context['questionIds'],
        'conceptCounts':context['conceptCounts'],'conceptDefinitions':concepts,'highlightIntegration':highlight_report,'finalVisualReview':visual_review,
        'implementation':implementation(),'previewEquality':{'questions':40,'allStudentVisibleFieldsEqual':True,'conceptDefinitionsEqual':21,
            'fields':list(entries[0]['studentVisible']),'academicChanges':0,'newContentCorrections':0,'imagesComparedToOriginalPixels':40},
        'publicCatalogSha256':h.digest((h.ROOT/'public/data/questions.json').read_bytes()),'candidates':entries}
    manifest['candidateSetFingerprint']=qa.object_hash({'ids':manifest['questionIds'],'candidates':entries,'conceptDefinitions':concepts,'highlightIntegration':highlight_report,'sourceSha256':manifest['sourceSha256'],'textbookSha256':manifest['textbookSha256']})
    page=render_gallery(manifest,concepts);target=root/'index.html'
    if not target.exists() or target.read_text('utf8')!=page:target.write_text(page,encoding='utf8')
    manifest['galleryAssets']={'/':{'path':str(target),'sha256':h.digest(target.read_bytes())},**{f'/images/{e["id"]}.webp':{'path':str(h.WORK/e['record']['images'][0]['path']),'sha256':e['record']['images'][0]['sha256']} for e in entries}}
    save(root/'manifest.json',manifest);check_batch02();write_batch02_report(manifest)
    print('Prepared exact 40-question Batch 2 owner package; zero approvals. node scripts/question-review-server.mjs --approval-candidates --batch2')


def validate_final_package(manifest,expected_entries,concepts,highlight_report,context,*,batch=2):
    if not manifest or manifest.get('schema')!='itpec-final-approval-candidates-v1' or manifest.get('batch')!=batch or manifest.get('privateOnly') is not True or manifest.get('readOnly') is not True or manifest.get('publicationApprovalGranted') is not False or manifest.get('questionIds')!=context['questionIds'] or manifest.get('conceptCounts')!=context['conceptCounts'] or len(manifest.get('candidates',[]))!=40:
        raise ValueError(f'Missing or expanded exact Batch {batch} owner package')
    if manifest['candidates']!=expected_entries or manifest.get('conceptDefinitions')!=concepts or manifest.get('highlightIntegration')!=highlight_report:raise ValueError('Candidate content, context or highlight definition is stale')
    fingerprint=qa.object_hash({'ids':manifest['questionIds'],'candidates':expected_entries,'conceptDefinitions':concepts,'highlightIntegration':highlight_report,'sourceSha256':context['sourceSha256'],'textbookSha256':context['textbookSha256']})
    if manifest.get('candidateSetFingerprint')!=fingerprint:raise ValueError('Candidate set fingerprint changed')


def validate_batch02_package(manifest,expected_entries,concepts,highlight_report,context):
    return validate_final_package(manifest,expected_entries,concepts,highlight_report,context)


def validate_batch02_approvals(manifest,records,reviews,manifest_sha):
    for entry in manifest['candidates']:
        v=reviews[entry['id']];r=next(r for r in records if r['id']==entry['id'])
        if v['approval']['status']=='unapproved':continue
        approval=v['approval']
        if not entry['technicalEligibility'] or not h.valid_approval(r,v) or approval.get('candidateManifestSha256')!=manifest_sha or approval.get('candidateSetFingerprint')!=manifest['candidateSetFingerprint'] or approval.get('approvalContextFingerprint')!=entry['approvalContextFingerprint'] or (entry['highlightIntegration']['newConcept'] and approval.get('highlightEditorialAuthorization')!=entry['highlightIntegration']['previewDefinitionSha256']):
            raise ValueError('Owner authorization is not bound to the exact package and concept context')


def check_batch02(publisher=False):
    # A later explicit owner authorization permits only the frozen approval
    # transition. Keep the original read-only preparation gate unchanged.
    if publisher and (h.ROOT/'.local/releases/historical-40/state.json').exists():
        import release_40
        return release_40.publisher_check()
    root=batch02_folder();context,records,reviews,frozen=batch02_inputs(publisher);manifest=h.read_json(root/'manifest.json')
    concepts=batch02_concepts(context);highlight_report=validate_batch02_highlights(concepts)
    entries=batch02_entries(context,records,reviews,concepts,highlight_report)
    validate_batch02_package(manifest,entries,concepts,highlight_report,context)
    if manifest.get('implementation')!=implementation() or manifest.get('preparationInputsSha256')!=qa.object_hash(context) or manifest.get('catalogSnapshot')!=context['snapshot'] or manifest.get('sourceSha256')!=context['sourceSha256'] or manifest.get('textbookSha256')!=context['textbookSha256'] or manifest.get('publicCatalogSha256')!=h.digest((h.ROOT/'public/data/questions.json').read_bytes()):raise ValueError('Candidate implementation/source/public snapshot is stale')
    equality={'questions':40,'allStudentVisibleFieldsEqual':True,'conceptDefinitionsEqual':21,'fields':list(entries[0]['studentVisible']),'academicChanges':0,'newContentCorrections':0,'imagesComparedToOriginalPixels':40}
    if manifest.get('previewEquality')!=equality:raise ValueError('Candidate-to-preview equality evidence changed')
    cases=[{'id':e['id'],'pdfPage':e['record']['regions'][0]['pdfPage'],'imageSha256':e['record']['images'][0]['sha256'],
        'accessibleFieldsSha256':qa.object_hash({k:e['review']['extraction'][k] for k in ['imageDescription','optionText']}),
        'status':'visually-rechecked-against-original-image-and-pixel-matched-pdf','newContentCorrection':False} for e in entries if e['record']['regions'][0]['pdfPage'] in {3,32,137,186,221,300,311}]
    if manifest.get('finalVisualReview')!=cases:raise ValueError('Final image/accessible review receipt changed')
    if (root/'index.html').read_text('utf8')!=render_gallery(manifest,concepts):raise ValueError('Read-only gallery differs from frozen candidates')
    expected={'/':{'path':str(root/'index.html'),'sha256':h.digest((root/'index.html').read_bytes())},**{f'/images/{e["id"]}.webp':{'path':str(h.WORK/e['record']['images'][0]['path']),'sha256':e['record']['images'][0]['sha256']} for e in entries}}
    if manifest.get('galleryAssets')!=expected:raise ValueError('Owner gallery allowlist changed')
    if publisher:validate_batch02_approvals(manifest,records,reviews,h.digest((root/'manifest.json').read_bytes()))
    return manifest


def write_batch02_report(manifest):
    root=batch02_folder();entries=manifest['candidates']
    valid=sum(r['status']=='source-validated-pending-owner-editorial-approval' for r in manifest['highlightIntegration'])
    save(root/'equality-report.json',manifest['previewEquality']|{'candidateStudentHashes':{e['id']:e['studentVisibleSha256'] for e in entries},'approvalContextFingerprints':{e['id']:e['approvalContextFingerprint'] for e in entries}})
    save(root/'highlight-integration-report.json',manifest['highlightIntegration'])
    save(root/'owner-review-checklist.json',[{'id':e['id'],'pdfPage':e['record']['regions'][0]['pdfPage'],'conceptId':e['review']['mapping']['conceptId'],
        'technicallyEligible':e['technicalEligibility'],'approval':'unapproved','remainingBlockers':e['remainingBlockers'],'publicationFingerprint':e['publicationFingerprint'],'approvalContextFingerprint':e['approvalContextFingerprint']} for e in entries])
    lines=['# Batch 2 final owner-approval preparation','',
        'Exactly 40 previously prepared questions, grouped by all 21 concepts. All remain unapproved. No native review, academic answer, explanation, original image, existing approval, published record, progress record or textbook wording was changed.',
        'All 40 student-visible payloads and all 21 concept definitions equal the validated private preview. All 40 image crops were pixel-compared to the original Technology-01 PDF. The seven requested source cases were visually rechecked; no new transcription correction was required.',
        f'{valid} of 15 new highlights are source validated and match the private preview. Any correction-required highlight blocks technical eligibility for its affected candidates. Final owner editorial approval remains absent. Ordinary textbook definitions remain unchanged teaching text; no option selection, answer-key annotation or question-specific worked result was added before student submission.',
        '', '| Canonical ID | PDF | Concept / heading | Technical eligibility | Remaining blockers | Publication fingerprint | Context fingerprint |',
        '|---|---:|---|---|---|---|---|']
    for e in entries:lines.append(f'| {e["id"]} | {e["record"]["regions"][0]["pdfPage"]} | {e["review"]["mapping"]["conceptId"]} / {e["review"]["mapping"]["headingNumber"]} | {"yes" if e["technicalEligibility"] else "correction required"} | {", ".join(e["remainingBlockers"])} | {e["publicationFingerprint"]} | {e["approvalContextFingerprint"]} |')
    lines+=['','## Highlight integration','',
        'The publisher consumes the exact concept plan from this checked candidate package. Original paragraph hashes, actual numbered subsection ownership, stable IDs and lack of duplicate/nested highlights are validated by the same gate used by publisher promotion. Unnumbered child labels such as “(2) Pipeline control” are permitted within their enclosing numbered subsection; crossing another numbered subsection is rejected.',
        'Device-driver wording continues across printed pages 110–111; both source passages are included. Display, signed-integer and memory-addressing highlights are subsection entry points, with decisive bounded support passages separately supplied. No exact formula was invented from those introductory paragraphs.',
        '', '## Future owner authorization procedure','',
        '1. Run `python scripts/approval_candidates.py check --batch 2` and review every checklist entry, its original image, explanation, source passages and highlight context.',
        '2. In a separately explicitly authorized milestone, bind the owner decision to the exact SHA-256 of `manifest.json`, its candidate-set fingerprint, all 40 publication fingerprints and all 40 approval-context fingerprints. Explicitly review the 15 new concept definitions/highlights; their definition hashes are part of the context.',
        '3. Use the existing native approval mechanism only for these exact records. The future authorization receipt must also record `candidateManifestSha256`, `candidateSetFingerprint`, and the per-record `approvalContextFingerprint`; new-highlight records additionally require `highlightEditorialAuthorization` equal to the reviewed definition hash. No command in this milestone grants those fields or approval.',
        '4. Run the existing publisher with `--dry-run --batch 2`. Any altered question, answer, explanation, metadata, mapping, accessible description, source binding, concept definition, package or source passage must invalidate the authorization. Re-review and obtain fresh explicit authorization after any such change.',
        '5. Actual publication, merge and deployment each require later authorization; none is performed here. ITPEC Practice remains authoritative for reliably matched published occurrences.',
        '', '## Local owner review','',
        'Launch `node scripts/question-review-server.mjs --approval-candidates --batch2`; open http://127.0.0.1:4330/. The existing gallery server serves only the read-only HTML and these 40 original images. It blocks mutation, foreign Host/Origin headers, raw PDFs, native catalogs, package JSON and all other question images. There are no approval controls, scripts, authentication or progress writes.',
        'Full payload: `manifest.json`. Highlight review: `highlight-integration-report.json`. Equality: `equality-report.json`. Complete individual blocker checklist: `owner-review-checklist.json`. Source/native/input snapshots: `preparation-inputs.json` and `before/`.',
        '', 'Expected new approvals: zero. Expected publisher dry-run additions and updates: zero. Test, build, commit and dry-run receipts are recorded separately after validation.']
    text='\n'.join(lines)+'\n';target=root/'completion-report.md'
    if not target.exists() or target.read_text('utf8')!=text:target.write_text(text,encoding='utf8')


BATCH03_BASELINE='e08aaa20a72996d6bb57aa8641488c2f674a4bc9'
BATCH03_INPUTS=('completion-report.md','completion-receipt.json','candidate-recommendation.json','review-diff.json','inventory.csv',
    'preservation-report.json','idempotency-evidence.json','highlight-validation.json','decisions-concepts.json',
    'preview/manifest.json','preview/app/src/content/pilot-bank.json','preview/app/src/content/explanations.json',
    'preview/app/src/content/concepts.json','decisions.json','baseline-guard.json')


def batch03_folder():
    # The preparation guard freezes all earlier approval workspaces. Keep this new
    # package in its own batch workspace, using the same manifest/gallery system.
    import hardware_batch03 as batch
    return batch.WORK/'final-approval'


def freeze_batch03():
    """Archive the completed preparation before changing any publisher integration."""
    import hardware_batch03 as batch
    root=batch03_folder()
    if (root/'preparation-inputs.json').exists():return
    if batch.core.git('branch','--show-current')!=batch.BRANCH or subprocess.run(['git','merge-base','--is-ancestor',BATCH03_BASELINE,'HEAD'],cwd=h.ROOT,capture_output=True).returncode:
        raise ValueError('Wrong Batch 3 branch/baseline')
    pm=batch.check();receipt=h.read_json(batch.WORK/'completion-receipt.json')
    if receipt.get('commit')!=BATCH03_BASELINE or receipt.get('newApprovals')!=0 or receipt.get('newPublications')!=0:raise ValueError('Completed Batch 3 receipt differs')
    files={name:h.digest((batch.WORK/name).read_bytes()) for name in BATCH03_INPUTS}
    for name in BATCH03_INPUTS:
        target=root/'before/batch'/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(batch.WORK/name,target)
    for name in ['questions.json','reviews.json','manifest.json','index.html']:
        target=root/'before/native'/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(h.WORK/name,target)
    published=h.read_json(h.ROOT/'public/data/questions.json');bank=h.read_json(batch.APP/'src/content/pilot-bank.json');ids=pm['questionIds']
    released=[q['id'] for q in published if q['id'].startswith('HIST-')]
    counts=dict(sorted(Counter(q['topic'] for q in bank if q['id'] in ids).items()))
    if len(published)!=496 or len(released)!=76 or len(ids)!=40 or len(set(ids))!=40 or set(ids)&set(released) or len(counts)!=28:raise ValueError('Completed Batch 3 scope changed')
    save(root/'preparation-inputs.json',{'schema':'itpec-final-candidate-preparation-batch03-v1','baselineCommit':BATCH03_BASELINE,
        'productionBaseline':batch.BASELINE,'files':files,'snapshot':qa.snapshot_hashes(h.WORK),'questionIds':ids,'conceptCounts':counts,
        'releasedQuestionIds':released,'publicFiles':batch.core.public_fingerprints(),
        'nativeFiles':{name:h.digest((h.WORK/name).read_bytes()) for name in ['questions.json','reviews.json','manifest.json','index.html']},
        'sourceSha256':batch.audit.SOURCE_SHA,'textbookSha256':batch.audit.BOOK_SHA,'publicationApprovalGranted':False})


def refresh_batch03_preview():
    """Rebuild after publisher integration, proving every delivered preview byte equal.

    The original manifest and completion artifacts remain archived. This never
    updates a stale receipt or weakens the preparation engine's own checks.
    """
    import hardware_batch03 as batch
    root=batch03_folder();context=h.read_json(root/'preparation-inputs.json')
    original=h.read_json(root/'before/batch/preview/manifest.json');current=h.read_json(batch.WORK/'preview/manifest.json')
    if (root/'preview-revalidation.json').exists():return
    if qa.snapshot_hashes(h.WORK)!=context['snapshot'] or current!=original:raise ValueError('Preview revalidation requires the exact completed original snapshot')
    for name,sha in original['implementation'].items():
        data=subprocess.check_output(['git','show',f'{BATCH03_BASELINE}:{name}'],cwd=h.ROOT)
        # The frozen Windows lockfile has CRLF while Git stores LF. JSON whitespace
        # is the sole permitted checkout normalization; source code stays exact.
        lockfile_checkout=name=='package-lock.json' and h.digest(data.replace(b'\r\n',b'\n').replace(b'\n',b'\r\n'))==sha
        if h.digest(data)!=sha and not lockfile_checkout:raise ValueError('Original preparation implementation differs from its commit')
    if current['implementation']!=batch.implementation():batch.prepare()
    updated=h.read_json(batch.WORK/'preview/manifest.json')
    if {k:v for k,v in updated.items() if k!='implementation'}!={k:v for k,v in original.items() if k!='implementation'} or qa.snapshot_hashes(h.WORK)!=context['snapshot']:
        raise ValueError('Revalidation changed preview bytes, IDs, academic content or native state')
    # The preceding preparation rebuild regenerates its completion report. Restore
    # the original final receipt/report and all editorial artifacts byte for byte.
    for name in BATCH03_INPUTS:
        if name!='preview/manifest.json':shutil.copyfile(root/'before/batch'/name,batch.WORK/name)
    batch.check()
    save(root/'preview-revalidation.json',{'originalManifestSha256':context['files']['preview/manifest.json'],
        'currentManifestSha256':h.digest((batch.WORK/'preview/manifest.json').read_bytes()),'implementation':batch.implementation(),
        'nativeSnapshot':context['snapshot'],'studentAndOwnerPreviewBytesEqual':True,'reason':'Existing publisher now checks the exact final candidate package; original preview content and all served bytes unchanged.'})


def batch03_inputs():
    import hardware_batch03 as batch
    root=batch03_folder();context=h.read_json(root/'preparation-inputs.json')
    if not context or context.get('schema')!='itpec-final-candidate-preparation-batch03-v1' or context.get('baselineCommit')!=BATCH03_BASELINE or context.get('publicationApprovalGranted') is not False or set(context.get('files',{}))!=set(BATCH03_INPUTS):raise ValueError('Missing exact Batch 3 preparation context')
    if batch.core.git('branch','--show-current')!=batch.BRANCH or subprocess.run(['git','merge-base','--is-ancestor',BATCH03_BASELINE,'HEAD'],cwd=h.ROOT,capture_output=True).returncode:raise ValueError('Wrong Batch 3 branch/baseline')
    for name,sha in context['files'].items():
        if h.digest((root/'before/batch'/name).read_bytes())!=sha or (name!='preview/manifest.json' and h.digest((batch.WORK/name).read_bytes())!=sha):raise ValueError('Stale completed Batch 3 input: '+name)
    if qa.snapshot_hashes(root/'before/native')!=context['snapshot'] or qa.snapshot_hashes(h.WORK)!=context['snapshot']:raise ValueError('Frozen/live native snapshot changed')
    for name,sha in context['nativeFiles'].items():
        if h.digest((root/'before/native'/name).read_bytes())!=sha or h.digest((h.WORK/name).read_bytes())!=sha:raise ValueError('Read-only native catalog/history changed')
    original=h.read_json(root/'before/batch/preview/manifest.json');current=batch.check();receipt=h.read_json(root/'preview-revalidation.json')
    if not receipt or receipt.get('originalManifestSha256')!=context['files']['preview/manifest.json'] or receipt.get('currentManifestSha256')!=h.digest((batch.WORK/'preview/manifest.json').read_bytes()) or receipt.get('implementation')!=batch.implementation() or receipt.get('nativeSnapshot')!=context['snapshot'] or receipt.get('studentAndOwnerPreviewBytesEqual') is not True:raise ValueError('Stale or missing preview revalidation receipt')
    if {k:v for k,v in current.items() if k!='implementation'}!={k:v for k,v in original.items() if k!='implementation'}:raise ValueError('Final preparation changed the previously reviewed preview')
    records=h.read_json(h.WORK/'questions.json');reviews=h.read_json(h.WORK/'reviews.json');frozen=h.read_json(root/'before/native/reviews.json')
    validate_live_reviews(records,reviews,frozen,context['questionIds'])
    published=h.read_json(h.ROOT/'public/data/questions.json');released=[q for q in published if q['id'].startswith('HIST-')]
    if len(published)!=496 or len(released)!=76 or context['releasedQuestionIds']!=[q['id'] for q in released] or len(context['questionIds'])!=40 or len(set(context['questionIds']))!=40 or set(context['questionIds'])&{q['id'] for q in published}:raise ValueError('Exact new/public scopes changed')
    if context['publicFiles']!=batch.core.public_fingerprints() or h.digest(h.SOURCE.read_bytes())!=context['sourceSha256'] or h.digest(qa.TEXTBOOK.read_bytes())!=context['textbookSha256']:raise ValueError('Protected published or original source content changed')
    index={r['id']:r for r in records}
    for q in released:
        if not h.valid_approval(index[q['id']],reviews[q['id']]) or q['review']['approvalFingerprint']!=reviews[q['id']]['approval']['fingerprint']:raise ValueError('Existing owner approval changed')
    return context,records,reviews,frozen


def batch03_concepts(context):
    root=batch03_folder();all_concepts=h.read_json(root/'before/batch/preview/app/src/content/concepts.json')
    public={c['id']:c for c in h.read_json(h.ROOT/'src/content/concepts.json')};result=[]
    for cid in context['conceptCounts']:
        view=concept_view(next(c for c in all_concepts if c['id']==cid))
        if cid in public and view!=concept_view(public[cid]):raise ValueError('Existing public concept differs from private preview')
        result.append({**view,'newConcept':cid not in public})
    if len(result)!=28 or sum(c['newConcept'] for c in result)!=14:raise ValueError('Exact 28 concepts / 14 proposed highlights required')
    return result


def batch03_associations(context,records,reviews,concepts):
    import hardware_batch02 as shared
    original=h.read_json(batch03_folder()/'before/batch/preview/manifest.json');result=[]
    for qid in context['questionIds']:
        v=reviews[qid];c=next(c for c in concepts if c['id']==v['mapping']['conceptId'])
        current=shared.source_association({'id':qid,'currentMapping':v['mapping'],'auditClassification':{'evidence':v['mapping']['evidence']}},c)
        if current!=next(a for a in original['associations'] if a['questionId']==qid):raise ValueError('Original source highlight association changed')
        source=(h.ROOT/current['sourceFile']).read_text('utf8')
        if c.get('sourceHighlight'):pid=c['sourceHighlight']['passageId']
        else:
            anchor=re.search(r'<a\b[^>]*data-concept="'+re.escape(c['id'])+r'"',source)
            start=source.rfind('<p ',0,anchor.start());pid=re.search(r'\bid="([^"]+)"',source[start:source.find('>',start)])[1]
        result.append({**current,'sourceParagraphId':pid})
    return result


def validate_batch03_reviews(context,records,reviews,concepts,associations,*,prepare=False,existing_concepts=None,root=None,expected_highlights=14,review_schema='itpec-batch03-final-source-review-v1'):
    """Combine the existing structural highlight gate with explicit source review.

    Missing/stale review evidence fails closed. A genuine recorded source finding
    blocks the affected candidate; it is never relabeled as owner approval.
    """
    root=root or batch03_folder();plan=root/'concept-plan.json'
    if prepare:save(plan,concepts)
    elif h.read_json(plan)!=concepts:raise ValueError('Final concept plan changed')
    run=subprocess.run(['node',str(h.ROOT/'node_modules/tsx/dist/cli.mjs'),'scripts/historical-highlight.ts',str(plan),*([str(existing_concepts)] if existing_concepts else [])],cwd=h.ROOT,capture_output=True,text=True,encoding='utf8')
    if run.returncode:raise ValueError('Existing highlight gate failed: '+run.stderr)
    structural=json.loads(run.stdout);new=[c for c in concepts if c['newConcept']]
    if len(structural)!=expected_highlights or {r['conceptId'] for r in structural}!={c['id'] for c in new}:raise ValueError(f'Exact {expected_highlights} highlight gate results required')
    ledger=h.read_json(root/'source-review.json')
    if not ledger or ledger.get('schema')!=review_schema or ledger.get('sourceSha256')!=context['sourceSha256'] or ledger.get('textbookSha256')!=context['textbookSha256'] or ledger.get('nativeSnapshot')!=context['snapshot'] or ledger.get('ownerApprovalGranted') is not False:raise ValueError('Missing or stale independent final source review')
    source={r['id']:r for r in records};rows=ledger.get('questions',[]);editorial=ledger.get('highlights',[])
    if [r['id'] for r in rows]!=context['questionIds'] or len(editorial)!=expected_highlights or {r['conceptId'] for r in editorial}!={c['id'] for c in new}:raise ValueError('Final source-review scope changed')
    for row in rows:
        r=source[row['id']];v=reviews[r['id']]
        if row.get('sourceBinding')!=qa.extraction_binding(r) or row.get('reviewSha256')!=qa.object_hash(v) or row.get('visibleSha256')!=qa.object_hash(visible(r,v)) or row.get('rawTranscriptSha256')!=r['contentSha256'] or set(row.get('literalOptionWording',{}))!=set('abcd') or row.get('status') not in ['source-rechecked','correction-required'] or row.get('ownerApprovalGranted') is not False:raise ValueError('Stale image, transcription, answer or final review evidence')
        if row['status']=='source-rechecked' and (row.get('issues') or not all(row.get('checks',{}).get(k) is True for k in ['image','literalOptions','mathematics','diagramLayout','units','answerNeutrality'])):raise ValueError('Unvalidated accessible review cannot be cleared')
    report=[]
    for c in new:
        row=next(r for r in editorial if r['conceptId']==c['id']);linked=[a for a in associations if a['conceptId']==c['id']]
        binding=qa.object_hash({'concept':c,'associations':linked})
        if row.get('bindingSha256')!=binding or row.get('questionIds')!=[a['questionId'] for a in linked] or row.get('status') not in ['source-rechecked','correction-required'] or row.get('ownerApprovalGranted') is not False or not row.get('teachingJustification') or not row.get('continuationContext') or not row.get('answerNeutralityRationale'):raise ValueError('Stale or incomplete per-highlight editorial review')
        if row['status']=='source-rechecked' and (row.get('issues') or not all(row.get('checks',{}).get(k) is True for k in ['teachesConcept','exactSubsection','pageLabels','stableId','noDuplicate','allAssociations','answerNeutrality','unchangedWording','previewEquality'])):raise ValueError('Highlight lacks required review evidence')
        gate=next(r for r in structural if r['conceptId']==c['id'])
        report.append({**gate,'editorialReview':row,'status':gate['status'] if row['status']=='source-rechecked' else 'correction-required','ownerEditorialApprovalGranted':False,
            'printedPage':linked[0]['highlightPrintedPage'],'physicalPdfPage':linked[0]['highlightPhysicalPdfPage'],'sourceParagraph':linked[0]['paragraphText'],'sourceParagraphId':linked[0]['sourceParagraphId']})
    return rows,report


def batch03_entries(context,records,reviews,concepts,associations,source_rows,report,*,root=None):
    root=root or batch03_folder();ids=context['questionIds']
    bank=[q for q in h.read_json(root/'before/batch/preview/app/src/content/pilot-bank.json') if q['id'] in ids]
    answers=[e for e in h.read_json(root/'before/batch/preview/app/src/content/explanations.json') if e['questionId'] in ids]
    entries=build_entries(records,reviews,ids,associations,bank,answers,expected_count=40)
    for e in entries:
        c=next(c for c in concepts if c['id']==e['review']['mapping']['conceptId']);row=next(r for r in source_rows if r['id']==e['id'])
        highlight=next((r for r in report if r['conceptId']==c['id']),None)
        e['conceptDefinition']=c;e['finalSourceReview']=row;e['finalHighlightReview']=highlight
        e['sourceTranscription']={'immutableRawTranscript':e['record']['rawText'],'rawTranscriptSha256':row['rawTranscriptSha256'],
            'literalOptionWording':row['literalOptionWording'],'editorialClarifications':row['editorialClarifications'],
            'note':'Immutable PDF text extraction is retained separately; original image is typographic authority. Reviewed notation and neutral diagram descriptions equal the validated preview.'}
        e['highlightIntegration']={'newConcept':c['newConcept'],'status':highlight['status'] if highlight else 'existing-reviewed-highlight','ownerEditorialApprovalGranted':False,'wordingChanged':False,'previewDefinitionSha256':qa.object_hash(concept_view(c))}
        if c['newConcept']:e['remainingBlockers'].append('final-owner-editorial-highlight-approval-absent')
        if row['status']!='source-rechecked':e['technicalEligibility']=False;e['remainingBlockers'].append('source-transcription-correction-required')
        if highlight and highlight['status']!='source-validated-pending-owner-editorial-approval':e['technicalEligibility']=False;e['remainingBlockers'].append('source-highlight-correction-required')
        e['approvalContextFingerprint']=approval_context_fingerprint(e,c)
        e['readiness']={'academic':'independently-verified','sourceImage':'immutable-pixel-matched','accessibility':row['status'],'metadata':'owner-confirmed-FE-AM-A',
            'classification':e['review']['classification']['status'],'mapping':e['review']['mapping']['status'],'placement':e['review']['classification']['placement'],
            'highlight':e['highlightIntegration']['status'],'grading':'independent-single-answer','duplicateConflicts':[],'ownerApproval':'unapproved'}
    return entries


def batch03_fingerprint(context,entries,concepts,report):
    return qa.object_hash({'ids':context['questionIds'],'candidates':entries,'conceptDefinitions':concepts,'highlightIntegration':report,'sourceSha256':context['sourceSha256'],'textbookSha256':context['textbookSha256']})


def batch03_gallery(manifest,concepts,*,highlight_count=14):
    page=render_gallery(manifest,concepts);esc=lambda x:html.escape(str(x),quote=True)
    for e in manifest['candidates']:
        transcription=e['sourceTranscription']
        literal=''.join(f'<li>{esc(k.upper())}: {esc(v)}</li>' for k,v in transcription['literalOptionWording'].items())
        notes=''.join(f'<li>{esc(note)}</li>' for note in transcription['editorialClarifications'])
        details=f'<details class="literal-source"><summary>Literal source wording and editorial clarifications</summary><p>{esc(transcription["note"])}</p><h4>Literal source options</h4><ol>{literal}</ol><h4>Editorial clarifications in the unchanged preview</h4><ul>{notes}</ul><details><summary>Preserved raw PDF text extraction</summary><pre style="white-space:pre-wrap;overflow-wrap:anywhere">{esc(transcription["immutableRawTranscript"])}</pre></details></details>'
        pattern=r'(<article\b[^>]*data-question="'+re.escape(e['id'])+r'"[\s\S]*?)(<nav aria-label="Question navigation">)'
        page=re.sub(pattern,lambda m:m[1]+details+m[2],page,count=1)
    links=f'<section id="highlight-index"><h2>All {highlight_count} proposed highlights</h2><ol>'+''.join(f'<li><a href="#highlight-{esc(r["conceptId"])}">{esc(r["conceptId"])}</a></li>' for r in manifest['highlightIntegration'])+'</ol></section>'
    cards=[]
    for row in manifest['highlightIntegration']:
        review=row['editorialReview'];ids=' · '.join(f'<a href="#{esc(i)}">{esc(i)}</a>' for i in review['questionIds'])
        cards.append(f'<section class="highlight-review" id="highlight-{esc(row["conceptId"])}"><h2>{esc(row["conceptId"])}</h2><p>{esc(row["status"])} · Owner editorial approval absent</p><p>Printed p.{row["printedPage"]} / physical PDF p.{row["physicalPdfPage"]} · {esc(row["sourceParagraphId"])}</p><blockquote>{esc(row["sourceParagraph"])}</blockquote><p>{esc(review["teachingJustification"])}</p><p>{esc(review["continuationContext"])}</p><p>{esc(review["answerNeutralityRationale"])}</p><p>Associated questions: {ids}</p><a href="#highlight-index">All highlights</a></section>')
    return page.replace('<nav aria-label="Concept groups">', f'<p><a href="#highlight-index">Inspect all {highlight_count} proposed highlights</a> · Candidate-set fingerprint: <code>'+esc(manifest['candidateSetFingerprint'])+'</code></p><nav aria-label="Concept groups">').replace('</body>',links+''.join(cards)+'</body>')


def prepare_batch03():
    freeze_batch03();refresh_batch03_preview();context,records,reviews,_=batch03_inputs();root=batch03_folder()
    concepts=batch03_concepts(context);associations=batch03_associations(context,records,reviews,concepts)
    rows,report=validate_batch03_reviews(context,records,reviews,concepts,associations,prepare=True)
    entries=batch03_entries(context,records,reviews,concepts,associations,rows,report)
    with fitz.open(h.SOURCE) as pdf:qa.validate_source_images([e['record'] for e in entries],pdf)
    manifest={'schema':'itpec-final-approval-candidates-v1','batch':3,'baselineCommit':BATCH03_BASELINE,'featureCommit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=h.ROOT,text=True).strip(),'privateOnly':True,'readOnly':True,'publicationApprovalGranted':False,
        'preparationInputsSha256':qa.object_hash(context),'catalogSnapshot':context['snapshot'],'sourceSha256':context['sourceSha256'],'textbookSha256':context['textbookSha256'],
        'questionIds':context['questionIds'],'conceptCounts':context['conceptCounts'],'conceptDefinitions':concepts,'highlightIntegration':report,'expectedNewHighlights':14,
        'implementation':implementation(),'sourceReviewSha256':h.digest((root/'source-review.json').read_bytes()),'previewRevalidationSha256':h.digest((root/'preview-revalidation.json').read_bytes()),
        'previewEquality':{'questions':40,'conceptDefinitionsEqual':28,'allStudentVisibleFieldsEqual':True,'fields':list(entries[0]['studentVisible']),'academicChanges':0,'newContentCorrections':0,'imagesComparedToOriginalPixels':40,'originalPreviewAssetBytesEqual':True},
        'publicCatalogSha256':h.digest((h.ROOT/'public/data/questions.json').read_bytes()),'finalVisualReview':rows,'candidates':entries}
    manifest['candidateSetFingerprint']=batch03_fingerprint(context,entries,concepts,report)
    page=batch03_gallery(manifest,concepts);target=root/'index.html'
    if not target.exists() or target.read_text('utf8')!=page:target.write_text(page,encoding='utf8')
    manifest['galleryAssets']={'/':{'path':str(target),'sha256':h.digest(target.read_bytes())},**{f'/images/{e["id"]}.webp':{'path':str(h.WORK/e['record']['images'][0]['path']),'sha256':e['record']['images'][0]['sha256']} for e in entries}}
    save(root/'manifest.json',manifest);check_batch03();write_batch03_report(manifest)
    print('Prepared exact Batch 3 candidate package: 40 unapproved questions, 28 concepts, 14 proposed highlights; no publication authorization.')


def check_batch03(publisher=False):
    if publisher:
        import release_3
        if (release_3.FOLDER/'state.json').exists():return release_3.publisher_check()
    # Preparation checks remain strict; a release never rewrites this snapshot.
    root=batch03_folder();context,records,reviews,_=batch03_inputs();manifest=h.read_json(root/'manifest.json')
    concepts=batch03_concepts(context);associations=batch03_associations(context,records,reviews,concepts)
    rows,report=validate_batch03_reviews(context,records,reviews,concepts,associations)
    entries=batch03_entries(context,records,reviews,concepts,associations,rows,report)
    validate_final_package(manifest,entries,concepts,report,context,batch=3)
    feature=manifest.get('featureCommit','')
    if not re.fullmatch('[0-9a-f]{40}',feature) or subprocess.run(['git','merge-base','--is-ancestor',BATCH03_BASELINE,feature],cwd=h.ROOT,capture_output=True).returncode or subprocess.run(['git','merge-base','--is-ancestor',feature,'HEAD'],cwd=h.ROOT,capture_output=True).returncode:raise ValueError('Candidate feature commit is outside its reviewed preparation ancestry')
    if manifest.get('implementation')!=implementation() or manifest.get('baselineCommit')!=BATCH03_BASELINE or manifest.get('expectedNewHighlights')!=14 or manifest.get('preparationInputsSha256')!=qa.object_hash(context) or manifest.get('catalogSnapshot')!=context['snapshot'] or manifest.get('sourceSha256')!=context['sourceSha256'] or manifest.get('textbookSha256')!=context['textbookSha256'] or manifest.get('publicCatalogSha256')!=h.digest((h.ROOT/'public/data/questions.json').read_bytes()) or manifest.get('sourceReviewSha256')!=h.digest((root/'source-review.json').read_bytes()) or manifest.get('previewRevalidationSha256')!=h.digest((root/'preview-revalidation.json').read_bytes()):raise ValueError('Stale final candidate implementation/source/review snapshot')
    equality={'questions':40,'conceptDefinitionsEqual':28,'allStudentVisibleFieldsEqual':True,'fields':list(entries[0]['studentVisible']),'academicChanges':0,'newContentCorrections':0,'imagesComparedToOriginalPixels':40,'originalPreviewAssetBytesEqual':True}
    if manifest.get('previewEquality')!=equality or manifest.get('finalVisualReview')!=rows:raise ValueError('Candidate-to-preview or final source review changed')
    if (root/'index.html').read_text('utf8')!=batch03_gallery(manifest,concepts):raise ValueError('Owner gallery differs from exact candidates')
    expected={'/':{'path':str(root/'index.html'),'sha256':h.digest((root/'index.html').read_bytes())},**{f'/images/{e["id"]}.webp':{'path':str(h.WORK/e['record']['images'][0]['path']),'sha256':e['record']['images'][0]['sha256']} for e in entries}}
    if manifest.get('galleryAssets')!=expected:raise ValueError('Final owner gallery allowlist changed')
    return manifest


def write_batch03_report(manifest):
    root=batch03_folder();entries=manifest['candidates'];eligible=sum(e['technicalEligibility'] for e in entries)
    save(root/'equality-report.json',manifest['previewEquality']|{'studentHashes':{e['id']:e['studentVisibleSha256'] for e in entries},'contextFingerprints':{e['id']:e['approvalContextFingerprint'] for e in entries}})
    save(root/'highlight-integration-report.json',manifest['highlightIntegration'])
    save(root/'owner-review-checklist.json',[{'id':e['id'],'pdfPage':e['record']['regions'][0]['pdfPage'],'conceptId':e['review']['mapping']['conceptId'],'technicallyEligible':e['technicalEligibility'],'readiness':e['readiness'],'remainingBlockers':e['remainingBlockers'],'publicationFingerprint':e['publicationFingerprint'],'approvalContextFingerprint':e['approvalContextFingerprint']} for e in entries])
    lines=['# Batch 3 final publication candidate package','',f'Exactly 40 frozen candidates across 28 concepts. {eligible} technically eligible for owner review; {40-eligible} need corrections. Every candidate remains unapproved. No native review, source image, answer, explanation, metadata, approval or published file was changed.',
        'All 40 student-visible payloads and all 28 concept definitions equal the original validated private preview. The original preview manifest is preserved. Publisher integration required revalidation of its implementation fingerprint: the full preparation engine rebuilt the preview, and every native object, generated source and delivered asset byte was proven identical. Original completion artifacts were restored byte for byte; no stale-check exception was introduced.',
        'All 40 source images and transcriptions were visually rechecked; all crops were pixel-compared against Technology-01. Literal raw extraction and source option wording are separate from neutral editorial clarifications. On PDF p.155 the source uses full gate names; parenthetic standard abbreviations in the existing preview are retained and explicitly labeled as clarifications. The p.75 “cash memory” typo remains literal. No academic answer or explanation was rewritten.',
        '',f'Candidate-set fingerprint: `{manifest["candidateSetFingerprint"]}`. Exact package: `manifest.json`; per-candidate publication and context fingerprints follow.',
        '', '| Canonical ID | Historical PDF / examination | Concept / heading | Eligible | Approval / blockers | Publication fingerprint | Context fingerprint |','|---|---|---|---|---|---|---|']
    for e in entries:
        r=e['record'];m=e['review']['mapping'];lines.append(f'| {e["id"]} | {r["regions"][0]["pdfPage"]} / {r["year"]}{r["season"]} Q{r["number"]} FE AM A | {m["conceptId"]} / {m["headingNumber"]} | {e["technicalEligibility"]} | unapproved; {", ".join(e["remainingBlockers"])} | {e["publicationFingerprint"]} | {e["approvalContextFingerprint"]} |')
    lines+=['','## Individual proposed-highlight review','', '| Concept | Printed / physical page | Exact heading | Result | Teaching and continuation context |','|---|---|---|---|---|']
    for row in manifest['highlightIntegration']:
        ev=row['editorialReview'];lines.append(f'| {row["conceptId"]} | {row["printedPage"]} / {row["physicalPdfPage"]} | {next(c for c in manifest["conceptDefinitions"] if c["id"]==row["conceptId"])["sourceHighlight"]["headingNumber"]} | {row["status"]}; owner editorial approval absent | {ev["teachingJustification"]} {ev["continuationContext"]} |')
    lines+=['','## Owner review and later authorization','',
        'Launch `node scripts/question-review-server.mjs --approval-candidates --batch3`; open http://127.0.0.1:4334/. The existing loopback server delivers only the read-only gallery and exactly 40 original images. It rejects mutations, foreign Host/Origin, source PDFs, package/review JSON and other questions. Navigation groups all 40 questions into 28 concepts and provides a separate index for all 14 highlights. No authentication or progress code is served.',
        'The ordinary textbook teaching remains unchanged, including definitions that help students learn the concept. No selected option, answer-key label, solved diagram output or question-specific worked result is inserted into a highlight or pre-submission description. The owner-only gallery deliberately displays answers for review.',
        '496 public question/image pairs (420 Practice + 36 Release 1 + 40 Release 2), 76 prior owner approvals, all academic/adjudication objects, and all production source/progress/Firebase/bookmark/filter code are fingerprint-preserved. The qualified seven cases are excluded. Canonical IDs and student-visible revisions are preserved. No real progress or Firebase data is accessed.',
        'Run `python scripts/approval_candidates.py check --batch 3` and the existing publisher with `--batch 3 --dry-run`. Batch 3 without dry-run remains rejected before mutation. Missing/changed package, source review, question, accessible description, explanation, metadata, image, mapping, source paragraph or concept definition invalidates candidate/context/set binding.',
        'A later separately explicit owner authorization must bind the exact manifest SHA-256, candidate-set fingerprint, each publication/context fingerprint and each new-highlight definition hash. Use the existing native approval architecture, with its package/context authorization fields. This read-only milestone accepts no new approval transition and creates no owner authorization. Publication, merge and deployment remain separate future actions.',
        'Validation, publisher dry-run and final commit receipts are recorded in validation-results.md after testing.']
    target=root/'completion-report.md';text='\n'.join(lines)+'\n'
    if not target.exists() or target.read_text('utf8')!=text:target.write_text(text,encoding='utf8')


BATCH04_BASELINE='4bfdd608def68e511aa0a55fa748c575459c1334'
BATCH04_INPUTS=('completion-report.md','completion-receipt.json','candidate-recommendation.json','review-diff.json','inventory.csv',
    'preservation-report.json','eligibility-report.json','coverage-analysis.json','excluded-deferred.json','highlight-inventory.json',
    'highlight-validation.json','decisions-concepts.json','highlight-plan.json','validation/idempotency.json',
    'preview/manifest.json','preview/app/src/content/pilot-bank.json','preview/app/src/content/explanations.json',
    'preview/app/src/content/concepts.json','preview/app/src/content/owner-review.json','decisions.json','baseline-guard.json')
BATCH04_COMPLEX={40,58,97,111,147,195,216,222,265,283,287,289,333}


def batch04_folder():
    import hardware_batch04 as batch
    return batch.WORK/'final-approval'


def freeze_batch04():
    """Freeze the authorized completed preparation, before publisher changes."""
    import hardware_batch04 as batch
    root=batch04_folder()
    if (root/'preparation-inputs.json').exists():return
    if batch.core.git('branch','--show-current')!=batch.BRANCH or batch.core.git('rev-parse','HEAD')!=BATCH04_BASELINE or batch.core.git('rev-parse','origin/main')!=batch.BASELINE:
        raise ValueError('Exact Batch 4 preparation commit, feature branch and production baseline required')
    pm=batch.check();receipt=h.read_json(batch.WORK/'completion-receipt.json')
    if receipt.get('commit')!=BATCH04_BASELINE or receipt.get('nativeSnapshot')!=qa.snapshot_hashes(h.WORK) or receipt.get('previewManifestSha256')!=h.digest((batch.WORK/'preview/manifest.json').read_bytes()) or receipt.get('decisionLedgerSha256')!=h.digest((batch.WORK/'decisions.json').read_bytes()) or receipt.get('newApprovals')!=0 or receipt.get('newPublications')!=0:
        raise ValueError('Completed Batch 4 fingerprints changed; do not refresh the preparation identity')
    files={name:h.digest((batch.WORK/name).read_bytes()) for name in BATCH04_INPUTS}
    for name in BATCH04_INPUTS:
        target=root/'before/batch'/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(batch.WORK/name,target)
    for name in ['questions.json','reviews.json','manifest.json','index.html']:
        target=root/'before/native'/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(h.WORK/name,target)
    published=h.read_json(h.ROOT/'public/data/questions.json');bank=h.read_json(batch.APP/'src/content/pilot-bank.json');ids=pm['questionIds']
    released=[q['id'] for q in published if q['id'].startswith('HIST-')]
    counts=dict(sorted(Counter(q['topic'] for q in bank if q['id'] in ids).items()))
    if len(published)!=536 or len(released)!=116 or len(ids)!=40 or len(set(ids))!=40 or set(ids)&set(released) or len(counts)!=20:raise ValueError('Exact Batch 4 new/public scope changed')
    save(root/'preparation-inputs.json',{'schema':'itpec-final-candidate-preparation-batch04-v1','baselineCommit':BATCH04_BASELINE,
        'productionBaseline':batch.BASELINE,'files':files,'snapshot':qa.snapshot_hashes(h.WORK),'questionIds':ids,'conceptCounts':counts,
        'releasedQuestionIds':released,'publicFiles':batch.core.public_fingerprints(),
        'nativeFiles':{name:h.digest((h.WORK/name).read_bytes()) for name in ['questions.json','reviews.json','manifest.json','index.html']},
        'sourceSha256':batch.audit.SOURCE_SHA,'textbookSha256':batch.audit.BOOK_SHA,'publicationApprovalGranted':False})


def refresh_batch04_preview():
    """Revalidate changed implementation; require byte-identical preview output."""
    import hardware_batch04 as batch
    root=batch04_folder();context=h.read_json(root/'preparation-inputs.json')
    if (root/'preview-revalidation.json').exists():return
    original=h.read_json(root/'before/batch/preview/manifest.json');current=h.read_json(batch.WORK/'preview/manifest.json')
    if qa.snapshot_hashes(h.WORK)!=context['snapshot'] or current!=original:raise ValueError('Exact original preview and native snapshot required; no automatic rebinding')
    for name,sha in original['implementation'].items():
        data=subprocess.check_output(['git','show',f'{BATCH04_BASELINE}:{name}'],cwd=h.ROOT)
        checkout=name=='package-lock.json' and h.digest(data.replace(b'\r\n',b'\n').replace(b'\n',b'\r\n'))==sha
        if h.digest(data)!=sha and not checkout:raise ValueError('Preparation implementation differs from the authorized Git commit')
    if current['implementation']!=batch.implementation():batch.prepare()
    updated=h.read_json(batch.WORK/'preview/manifest.json')
    if {k:v for k,v in updated.items() if k!='implementation'}!={k:v for k,v in original.items() if k!='implementation'} or qa.snapshot_hashes(h.WORK)!=context['snapshot']:
        raise ValueError('Revalidation changed served bytes, native reviews, IDs or student-visible content')
    for name in BATCH04_INPUTS:
        if name!='preview/manifest.json' and h.digest((batch.WORK/name).read_bytes())!=context['files'][name]:raise ValueError('Read-only preparation artifact changed: '+name)
    batch.check()
    save(root/'preview-revalidation.json',{'originalManifestSha256':context['files']['preview/manifest.json'],
        'currentManifestSha256':h.digest((batch.WORK/'preview/manifest.json').read_bytes()),'implementation':batch.implementation(),
        'nativeSnapshot':context['snapshot'],'studentAndOwnerPreviewBytesEqual':True,
        'reason':'Existing publisher now checks the final Batch 4 candidate package; only implementation fingerprint changed, all served preview bytes preserved.'})


def batch04_inputs():
    import hardware_batch04 as batch
    root=batch04_folder();context=h.read_json(root/'preparation-inputs.json')
    if not context or context.get('schema')!='itpec-final-candidate-preparation-batch04-v1' or context.get('baselineCommit')!=BATCH04_BASELINE or context.get('productionBaseline')!=batch.BASELINE or context.get('publicationApprovalGranted') is not False or set(context.get('files',{}))!=set(BATCH04_INPUTS):raise ValueError('Missing exact Batch 4 preparation context')
    if batch.core.git('branch','--show-current')!=batch.BRANCH or subprocess.run(['git','merge-base','--is-ancestor',BATCH04_BASELINE,'HEAD'],cwd=h.ROOT,capture_output=True).returncode:raise ValueError('Wrong Batch 4 feature branch or ancestry')
    for name,sha in context['files'].items():
        if h.digest((root/'before/batch'/name).read_bytes())!=sha or (name!='preview/manifest.json' and h.digest((batch.WORK/name).read_bytes())!=sha):raise ValueError('Stale original Batch 4 input: '+name)
    if qa.snapshot_hashes(root/'before/native')!=context['snapshot'] or qa.snapshot_hashes(h.WORK)!=context['snapshot']:raise ValueError('Frozen/live native snapshot changed')
    for name,sha in context['nativeFiles'].items():
        if h.digest((root/'before/native'/name).read_bytes())!=sha or h.digest((h.WORK/name).read_bytes())!=sha:raise ValueError('Read-only native history or approvals changed')
    original=h.read_json(root/'before/batch/preview/manifest.json');current=batch.check();receipt=h.read_json(root/'preview-revalidation.json')
    if not receipt or receipt.get('originalManifestSha256')!=context['files']['preview/manifest.json'] or receipt.get('currentManifestSha256')!=h.digest((batch.WORK/'preview/manifest.json').read_bytes()) or receipt.get('implementation')!=batch.implementation() or receipt.get('nativeSnapshot')!=context['snapshot'] or receipt.get('studentAndOwnerPreviewBytesEqual') is not True:raise ValueError('Missing or stale preview revalidation')
    if {k:v for k,v in original.items() if k!='implementation'}!={k:v for k,v in current.items() if k!='implementation'}:raise ValueError('Reviewed preview bytes or IDs changed')
    records=h.read_json(h.WORK/'questions.json');reviews=h.read_json(h.WORK/'reviews.json');frozen=h.read_json(root/'before/native/reviews.json')
    validate_live_reviews(records,reviews,frozen,context['questionIds'])
    published=h.read_json(h.ROOT/'public/data/questions.json');released=[q['id'] for q in published if q['id'].startswith('HIST-')]
    if len(published)!=536 or len(released)!=116 or context['releasedQuestionIds']!=released or len(context['questionIds'])!=40 or len(set(context['questionIds']))!=40 or set(context['questionIds'])&{q['id'] for q in published}:raise ValueError('Exact candidate or public scope changed')
    if context['publicFiles']!=batch.core.public_fingerprints() or h.digest(h.SOURCE.read_bytes())!=context['sourceSha256'] or h.digest(qa.TEXTBOOK.read_bytes())!=context['textbookSha256']:raise ValueError('Published or original source content changed')
    index={r['id']:r for r in records}
    for q in published:
        if q['id'] in released and (not h.valid_approval(index[q['id']],reviews[q['id']]) or q['review']['approvalFingerprint']!=reviews[q['id']]['approval']['fingerprint']):raise ValueError('Prior historical approval changed')
    h.verify_assets(records)
    return context,records,reviews,frozen


def batch04_concepts(context):
    original=h.read_json(batch04_folder()/'before/batch/preview/app/src/content/concepts.json')
    known={c['id']:c for c in h.read_json(h.ROOT/'src/content/concepts.json')};result=[]
    for cid in context['conceptCounts']:
        view=concept_view(next(c for c in original if c['id']==cid))
        if cid in known and view!=concept_view(known[cid]):raise ValueError('Reused published highlight changed')
        result.append({**view,'newConcept':cid not in known})
    if len(result)!=20 or {c['id'] for c in result if c['newConcept']}!={'display-memory','cache-write-policies'}:raise ValueError('Exact 20 concepts / two new highlights required')
    return result


def batch04_associations(context,records,reviews,concepts):
    import hardware_batch02 as shared
    original=h.read_json(batch04_folder()/'before/batch/preview/manifest.json');result=[]
    for qid in context['questionIds']:
        v=reviews[qid];c=next(c for c in concepts if c['id']==v['mapping']['conceptId'])
        a=shared.source_association({'id':qid,'currentMapping':v['mapping'],'auditClassification':{'evidence':v['mapping']['evidence']}},c)
        if a!=next(row for row in original['associations'] if row['questionId']==qid):raise ValueError('Prepared question/highlight association changed')
        source=(h.ROOT/a['sourceFile']).read_text('utf8')
        if c.get('sourceHighlight'):pid=c['sourceHighlight']['passageId']
        else:
            anchor=re.search(r'<a\b[^>]*data-concept="'+re.escape(c['id'])+r'"',source);start=source.rfind('<p ',0,anchor.start());pid=re.search(r'\bid="([^"]+)"',source[start:source.find('>',start)])[1]
        result.append({**a,'sourceParagraphId':pid})
    return result


def batch04_reviews(context,records,reviews,concepts,associations,*,prepare=False):
    return validate_batch03_reviews(context,records,reviews,concepts,associations,prepare=prepare,root=batch04_folder(),expected_highlights=2,review_schema='itpec-batch04-final-source-review-v1')


def batch04_entries(context,records,reviews,concepts,associations,rows,report):
    entries=batch03_entries(context,records,reviews,concepts,associations,rows,report,root=batch04_folder())
    recommendation=h.read_json(batch04_folder()/'before/batch/candidate-recommendation.json')
    prior={e['id']:e for e in recommendation['questions']}
    for e in entries:
        if e['publicationFingerprint']!=prior[e['id']]['candidateFingerprint']:raise ValueError('Prepared candidate fingerprint changed: '+e['id'])
        v=e['review'];e['dimensionFingerprints']={key:qa.object_hash(v[key]) for key in ['verification','explanation','extraction','metadata','classification','mapping']}
        e['sourceTranscription']['literalSourceTypos']=e['finalSourceReview'].get('literalSourceTypos',[])
        e['approvalContextFingerprint']=approval_context_fingerprint(e,e['conceptDefinition'])
    return entries


def batch04_gallery(manifest,concepts):
    page=batch03_gallery(manifest,concepts,highlight_count=2);esc=lambda x:html.escape(str(x),quote=True)
    special=[e for e in manifest['candidates'] if e['record']['regions'][0]['pdfPage'] in BATCH04_COMPLEX]
    nav='<section id="complex-index"><h2>Complex source cases</h2><ol>'+''.join(f'<li><a href="#{esc(e["id"])}">PDF p.{e["record"]["regions"][0]["pdfPage"]} · {esc(e["id"])}</a></li>' for e in special)+'</ol></section>'
    for e in manifest['candidates']:
        c=e['conceptDefinition'];marker=f'<h4>Exact textbook placement</h4>'
        # Add only owner-gallery links; the student/source application is untouched.
        pattern=r'(<article\b[^>]*data-question="'+re.escape(e['id'])+r'"[\s\S]*?)(<h4>Exact textbook placement</h4>)'
        link=f'<p><a class="concept-source-link" href="http://127.0.0.1:4336{esc(c["sectionUrl"])}#concept-{esc(c["id"])}">Open exact concept in private textbook preview</a></p>'
        page=re.sub(pattern,lambda m:m[1]+link+m[2],page,count=1)
    return page.replace('<section id="question-index">',nav+'<section id="question-index">')


def batch04_equality(entries):
    return {'questions':40,'conceptDefinitionsEqual':20,'allStudentVisibleFieldsEqual':True,'fields':list(entries[0]['studentVisible']),
        'academicChanges':0,'newContentCorrections':0,'imagesComparedToOriginalPixels':40,'originalPreviewAssetBytesEqual':True}


def prepare_batch04():
    root=batch04_folder()
    if (root/'manifest.json').exists():
        manifest=check_batch04();write_batch04_report(manifest);print('Exact Batch 4 package already prepared; unchanged and unapproved.');return
    freeze_batch04();refresh_batch04_preview();context,records,reviews,_=batch04_inputs()
    concepts=batch04_concepts(context);associations=batch04_associations(context,records,reviews,concepts)
    rows,report=batch04_reviews(context,records,reviews,concepts,associations,prepare=True)
    entries=batch04_entries(context,records,reviews,concepts,associations,rows,report)
    with fitz.open(h.SOURCE) as pdf:qa.validate_source_images([e['record'] for e in entries],pdf)
    manifest={'schema':'itpec-final-approval-candidates-v1','batch':4,'baselineCommit':BATCH04_BASELINE,'featureCommit':BATCH04_BASELINE,
        'privateOnly':True,'readOnly':True,'publicationApprovalGranted':False,'preparationInputsSha256':qa.object_hash(context),
        'catalogSnapshot':context['snapshot'],'sourceSha256':context['sourceSha256'],'textbookSha256':context['textbookSha256'],
        'questionIds':context['questionIds'],'conceptCounts':context['conceptCounts'],'conceptDefinitions':concepts,'highlightIntegration':report,'expectedNewHighlights':2,
        'implementation':implementation(),'sourceReviewSha256':h.digest((root/'source-review.json').read_bytes()),'previewRevalidationSha256':h.digest((root/'preview-revalidation.json').read_bytes()),
        'previewEquality':batch04_equality(entries),'publicCatalogSha256':h.digest((h.ROOT/'public/data/questions.json').read_bytes()),'finalVisualReview':rows,'candidates':entries}
    manifest['candidateSetFingerprint']=batch03_fingerprint(context,entries,concepts,report)
    page=batch04_gallery(manifest,concepts);(root/'index.html').write_text(page,encoding='utf8')
    manifest['galleryAssets']={'/':{'path':str(root/'index.html'),'sha256':h.digest((root/'index.html').read_bytes())},**{f'/images/{e["id"]}.webp':{'path':str(h.WORK/e['record']['images'][0]['path']),'sha256':e['record']['images'][0]['sha256']} for e in entries}}
    save(root/'manifest.json',manifest);check_batch04();write_batch04_report(manifest)
    print('Prepared exact Batch 4 final package: 40 unapproved questions; 20 concepts; two new source-validated highlights.')


def check_batch04(publisher=False):
    if publisher:
        import release_4
        if (release_4.FOLDER/'state.json').exists():return release_4.publisher_check()
    # Keep read-only preparation strict; authorization is a separate transition.
    root=batch04_folder();context,records,reviews,_=batch04_inputs();manifest=h.read_json(root/'manifest.json')
    concepts=batch04_concepts(context);associations=batch04_associations(context,records,reviews,concepts)
    rows,report=batch04_reviews(context,records,reviews,concepts,associations)
    entries=batch04_entries(context,records,reviews,concepts,associations,rows,report)
    validate_final_package(manifest,entries,concepts,report,context,batch=4)
    if manifest.get('implementation')!=implementation() or manifest.get('baselineCommit')!=BATCH04_BASELINE or manifest.get('featureCommit')!=BATCH04_BASELINE or manifest.get('expectedNewHighlights')!=2 or manifest.get('preparationInputsSha256')!=qa.object_hash(context) or manifest.get('catalogSnapshot')!=context['snapshot'] or manifest.get('sourceSha256')!=context['sourceSha256'] or manifest.get('textbookSha256')!=context['textbookSha256'] or manifest.get('publicCatalogSha256')!=h.digest((h.ROOT/'public/data/questions.json').read_bytes()) or manifest.get('sourceReviewSha256')!=h.digest((root/'source-review.json').read_bytes()) or manifest.get('previewRevalidationSha256')!=h.digest((root/'preview-revalidation.json').read_bytes()):raise ValueError('Stale Batch 4 candidate package or implementation/source binding')
    if manifest.get('previewEquality')!=batch04_equality(entries) or manifest.get('finalVisualReview')!=rows:raise ValueError('Final source review or preview equality changed')
    if (root/'index.html').read_text('utf8')!=batch04_gallery(manifest,concepts):raise ValueError('Owner gallery differs from exact candidates')
    assets={'/':{'path':str(root/'index.html'),'sha256':h.digest((root/'index.html').read_bytes())},**{f'/images/{e["id"]}.webp':{'path':str(h.WORK/e['record']['images'][0]['path']),'sha256':e['record']['images'][0]['sha256']} for e in entries}}
    if manifest.get('galleryAssets')!=assets:raise ValueError('Gallery allowlist or original image binding changed')
    return manifest


def write_batch04_report(manifest):
    root=batch04_folder();entries=manifest['candidates']
    save(root/'equality-report.json',manifest['previewEquality']|{'studentHashes':{e['id']:e['studentVisibleSha256'] for e in entries},'contextFingerprints':{e['id']:e['approvalContextFingerprint'] for e in entries}})
    save(root/'highlight-integration-report.json',manifest['highlightIntegration'])
    save(root/'owner-review-checklist.json',[{'id':e['id'],'pdfPage':e['record']['regions'][0]['pdfPage'],'conceptId':e['review']['mapping']['conceptId'],
        'technicallyEligible':e['technicalEligibility'],'readiness':e['readiness'],'remainingBlockers':e['remainingBlockers'],
        'publicationFingerprint':e['publicationFingerprint'],'approvalContextFingerprint':e['approvalContextFingerprint'],'dimensionFingerprints':e['dimensionFingerprints']} for e in entries])
    lines=['# Batch 4 final publication candidate package','',
        'Exactly 40 candidates across 20 Hardware concepts: 18 reused published definitions and two new highlights. All 40 are technically eligible and unapproved; zero required academic/editorial repairs. No native record, source image, answer, explanation, identity, approval or production content changed.',
        'All student-visible question fields, choices, answers, worked explanations, metadata, mappings, images and concepts equal the frozen private preview. Publisher integration was revalidated by rebuilding through the existing preparation engine: only its implementation fingerprint changed, while every native object and served source/build byte remained identical. The original preparation manifest/receipt/reports remain archived and unchanged.',
        f'Candidate-set fingerprint: `{manifest["candidateSetFingerprint"]}`. Exact manifest SHA-256: `{h.digest((root/"manifest.json").read_bytes())}`.',
        '', '| Canonical ID | PDF page / examination | Concept / heading | Eligible | Approval and blockers | Publication fingerprint | Context fingerprint |','|---|---|---|---|---|---|---|']
    for e in entries:
        r=e['record'];m=e['review']['mapping'];lines.append(f'| {e["id"]} | {r["regions"][0]["pdfPage"]} / {r["year"]}{r["season"]} Q{r["number"]} FE AM A | {m["conceptId"]} / {m["headingNumber"]} | {e["technicalEligibility"]} | unapproved; {", ".join(e["remainingBlockers"])} | {e["publicationFingerprint"]} | {e["approvalContextFingerprint"]} |')
    lines+=['','## Highlight review and complex sources','',
        'Display memory: two questions, heading 5-2-1, printed p.98 / physical p.104. Cache write policies: one question, heading 3-5-1, highlighted introductory context printed p.71 / physical p.76; direct write-policy teaching printed p.72 / physical p.77. Both exact fragments, book checksums, page identities and question associations are included in the candidate/context/set fingerprints. No wording, option selection or question-specific answer annotation was added. All 18 reused definitions remain unchanged.',
        'Final complex cases reconfirmed: Technology-01 physical pp.40, 58, 97, 111, 147, 195, 216, 222, 265, 283, 287, 289 and 333. Original diagrams/options are authoritative; neutral diagram/table linearization is labeled separately from literal source wording. The p.111 source typo “bimary” remains in the raw transcript/image; the separately documented accessible correction remains “binary”. Repaired effective extractions on pp.111/283/287 are present in the final native payload. All 40 crops were pixel-compared again against the original PDF. No academic answer was reopened or altered.',
        '', '## Read-only review and future owner authorization','',
        'Launch `node scripts/question-review-server.mjs --approval-candidates --batch4`; open http://127.0.0.1:4338/. Twenty concept groups, two dedicated highlight cards and direct links for all thirteen complex source cases are provided. GET/HEAD only; exact Host/Origin, hash allowlist and loopback root; source PDFs/native JSON/unselected images denied; no scripts, forms, approval action or progress/Firebase runtime is served.',
        '1. Review this exact package and the forty question cards, both proposed highlights, all source/accessible/academic fields and remaining blockers. Technical eligibility does not grant approval.',
        '2. In a separately explicitly authorized milestone, bind owner authorization to the exact manifest SHA-256 above, candidate-set fingerprint, all forty publication fingerprints and context fingerprints. The three records using new highlights additionally require their exact highlight-definition hash as owner editorial authorization.',
        '3. Use the existing native approval architecture only after that authorization. The receipt must include candidateManifestSha256, candidateSetFingerprint and each approvalContextFingerprint; new-highlight records must also bind highlightEditorialAuthorization. This milestone creates none of these owner approval fields.',
        '4. Recheck source/review/preview equality and all fingerprints immediately before approval and again before a publication dry run. Any student-visible question, answer, explanation, image, description, metadata, mapping, highlight, source passage or package change invalidates the old authorization. Re-review changed material; do not refresh authorization silently.',
        '5. Before a later production release, explicitly account for Release 3’s unresolved 52 HTML hash differences and blocked live HTML/UI verification. The prior exhaustive and final bounded investigations remain open operational evidence, not harmless differences or passed live tests. No regression is confirmed and current evidence does not warrant rollback. Do not repeat identical network failures without new evidence.',
        '', '## Preservation and validation','',
        '536 public question/image pairs (420 Practice + 36 + 40 + 40 historical), all 116 prior approvals, all 333 academic histories and seven qualified cases remain unchanged. The 217 unpublished historical questions remain private. Practice authority, source history, guest/account progress, bookmarks, reading checkpoints, filters and landing behavior are preserved; production source and asset fingerprints are unchanged.',
        'The existing publisher `--batch 4 --dry-run` requires this exact package and still exports only the 116 already approved records. Expected additions/updates/conflicts are zero. Non-dry-run Batch 4 publication is rejected before source access or mutation. Tests/build, exact package digest, commit and clean-tree receipts are recorded in validation-results.md and completion-receipt.json. No approval, publication, merge, deployment, rollback, additional historical PDF or student-data mutation occurred.']
    (root/'completion-report.md').write_text('\n'.join(lines)+'\n',encoding='utf8')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('command',choices=['prepare','check']);parser.add_argument('--publisher-check',action='store_true');parser.add_argument('--batch',type=int,choices=[1,2,3,4,5],default=1);args=parser.parse_args()
    if args.command=='prepare' and args.batch==5:
        from approval_batch05 import prepare
        prepare()
    elif args.command=='prepare':prepare_batch04() if args.batch==4 else prepare_batch03() if args.batch==3 else prepare_batch02() if args.batch==2 else prepare()
    else:
        manifest=check(args.publisher_check,args.batch)
        live=h.read_json(h.WORK/'reviews.json')
        folder=__import__('approval_batch05').folder() if args.batch==5 else batch04_folder() if args.batch==4 else batch03_folder() if args.batch==3 else batch02_folder() if args.batch==2 else editorial.folder()
        released=h.read_json(folder/'preparation-inputs.json')['releasedQuestionIds'] if args.batch in [2,3,4,5] else []
        print(json.dumps({'questionIds':manifest['questionIds'],'candidates':len(manifest['candidates']),'unapproved':sum(live[qid]['approval']['status']=='unapproved' for qid in manifest['questionIds']),'publicationApprovalGranted':False,
            'releasedQuestionIds':released,'conceptDefinitions':manifest.get('conceptDefinitions',[]) if args.publisher_check else None,
            'galleryAssets':manifest['galleryAssets'] if not args.publisher_check else None,'directory':str(folder)},ensure_ascii=False))
