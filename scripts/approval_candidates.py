"""Prepare/check the existing pilot's exact native publication payload; never approve."""
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
    return {name:h.digest((h.ROOT/name).read_bytes()) for name in names}


def build_entries(records,reviews,ids,associations,bank,answers):
    index={r['id']:r for r in records};questions={q['id']:q for q in bank};explanations={e['questionId']:e for e in answers}
    if len(ids)!=36 or len(set(ids))!=36 or set(ids)!=set(questions) or set(ids)!=set(explanations):raise ValueError('Approval preparation requires exactly the same 36 preview IDs')
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
    entries=manifest['candidates'];titles={c['id']:c['title'] for c in concepts}
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
            cards.append(f'''<article id="{esc(r['id'])}" tabindex="-1" data-question="{esc(r['id'])}">
<header><p>FE · Morning · Subject A · {r['year']} {'Spring' if r['season']=='S' else 'Autumn'} · Q{r['number']} · historical PDF p.{r['regions'][0]['pdfPage']}</p><h3>{esc(r['id'])}</h3><p class="eligibility">Technically eligible for owner review · Approval: <strong>unapproved</strong> · Publication blocked</p></header>
<div class="review-columns"><div><figure><a href="/images/{esc(r['id'])}.webp" aria-label="Open full-size original {esc(r['id'])}"><img src="/images/{esc(r['id'])}.webp" width="{im['width']}" height="{im['height']}" loading="lazy" alt="{esc(x['imageDescription'])}"></a><figcaption>Unchanged original question crop. Open the image for full-size reading.</figcaption></figure><h4>Accessible question and diagram</h4><p class="transcription">{esc(x['imageDescription'])}</p><ol class="choices">{options}</ol>{editorial_note}</div>
<div><h4>Verified correct answer: {esc(v['verification']['independentAnswer'].upper())}</h4><p class="answer-summary">{esc(v['explanation']['summary'])}</p><ol class="worked-steps">{steps}</ol><p>{esc(v['explanation']['takeaway'])}</p><h4>Exact textbook placement</h4><p>{esc(v['mapping']['sectionId'])} / {esc(v['mapping']['subsectionId'])} · heading {esc(v['mapping']['headingNumber'])} · concept {esc(cid)}</p><p>Existing highlight: printed p.{a['highlightPrintedPage']} / physical PDF p.{a['highlightPhysicalPdfPage']}.</p><blockquote><p>{esc(paragraph)}</p><footer>Website source paragraph {esc(a['sourceParagraphId'])}; exam-count annotation omitted</footer></blockquote>{passages}<details><summary>Integrity and approval binding</summary><dl><dt>Image SHA-256</dt><dd>{esc(im['sha256'])}</dd><dt>Source content SHA-256</dt><dd>{esc(r['contentSha256'])}</dd><dt>Exact publication fingerprint</dt><dd>{esc(e['publicationFingerprint'])}</dd><dt>Candidate equals validated preview</dt><dd>Yes — all student-visible academic fields</dd><dt>Grading</dt><dd>Independently verified, single-answer eligible. No qualified owner-adjudicated cases included.</dd></dl></details></div></div>
<nav aria-label="Question navigation">{prev} <a href="#question-index">All 36 questions</a> {nxt}</nav></article>''')
        groups.append(f'<section id="concept-{esc(cid)}" aria-labelledby="title-{esc(cid)}"><h2 id="title-{esc(cid)}">{esc(titles[cid])} · {len(cards)} questions</h2>'+''.join(cards)+'</section>')
    return '''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><meta name="robots" content="noindex,nofollow"><title>Final 36-question owner review</title><style>
body{font:16px/1.6 system-ui;background:#faf8f1;color:#18232d;max-width:1200px;margin:auto;padding:24px}a{color:#304a63}a:focus-visible,summary:focus-visible{outline:3px solid #be8615;outline-offset:4px}.skip{display:block}article{padding:28px 0;border-bottom:1px solid #aaa;scroll-margin-top:16px}h3,dd,blockquote,p,li{overflow-wrap:anywhere}h2{margin-top:48px}figure{margin:0}img{width:100%;height:auto}figcaption,footer{font-size:.88rem;color:#4b5560}blockquote{margin:12px 0;padding:12px 16px;border-left:3px solid #b4aa91;background:#f0ece2}nav ul,#question-index ol{display:flex;flex-wrap:wrap;gap:8px 24px;padding-left:24px}.review-columns{display:grid;grid-template-columns:minmax(0,1.1fr) minmax(0,1fr);gap:28px}.review-columns>div{min-width:0}.choices{list-style:none;padding:0}.choices li{padding:8px;border:1px solid #aaa;margin:8px 0}.eligibility,.integrity{background:#e9eee6;padding:10px}dd{margin-left:0;font:12px/1.6 monospace}article nav{display:flex;gap:24px;flex-wrap:wrap;margin-top:20px}@media(max-width:780px){body{padding:16px}.review-columns{grid-template-columns:1fr}h3{font-size:1.1rem}}
</style><body><a class="skip" href="#question-index">Skip to all 36 questions</a><header><p>PRIVATE · LOOPBACK ONLY · READ-ONLY</p><h1>Final 36-question owner review</h1><p>36 of 36 candidates exactly match the validated private preview in all student-visible academic content. Both accessibility corrections are now native publication transcriptions. Original images, answers and worked explanations are unchanged.</p><p><strong>Zero publication approvals.</strong> Every question remains unapproved. No approval controls, student-progress writes, authentication or publication actions are available here.</p><nav aria-label="Concept groups"><ul>'''+nav+'</ul></nav></header><section id="question-index"><h2>All 36 questions</h2><ol>'+all_nav+'</ol></section>'+''.join(groups)+'</body></html>'


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


def check(publisher=False):
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


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('command',choices=['prepare','check']);parser.add_argument('--publisher-check',action='store_true');args=parser.parse_args()
    if args.command=='prepare':prepare()
    else:
        manifest=check(args.publisher_check)
        live=h.read_json(h.WORK/'reviews.json')
        print(json.dumps({'questionIds':manifest['questionIds'],'candidates':36,'unapproved':sum(live[qid]['approval']['status']=='unapproved' for qid in manifest['questionIds']),'publicationApprovalGranted':False,
            'galleryAssets':manifest['galleryAssets'] if not args.publisher_check else None,'directory':str(editorial.folder())},ensure_ascii=False))
