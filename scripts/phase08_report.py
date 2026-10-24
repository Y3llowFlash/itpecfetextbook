"""Read-only views of the final-66 audit; no native or public writes."""
from collections import Counter
import csv
import html
import io
import json
import phase08 as p


def write_reports(rows):
    columns=['id','pdfPage','originalCategory','primaryDisposition','chapterTitle','headingNumber','concept','academicVerified','protected','publicationEligible','blockers','nextAction']
    stream=io.StringIO(newline='');writer=csv.DictWriter(stream,fieldnames=columns);writer.writeheader()
    for row in rows:writer.writerow({k:json.dumps(row[k],ensure_ascii=False) if isinstance(row.get(k),list) else row.get(k,'') for k in columns})
    (p.WORK/'classification-inventory.csv').write_bytes(stream.getvalue().encode('utf8'))
    header=['# Phase 8 final-66 private audit','',
        'All 66 records have one primary disposition. All 687 public question/image pairs, 267 previous approvals and 333 native academic histories are unchanged. No private record is approved or published.','',
        '**Final publication-candidate count: zero.** All 29 other-chapter records require Chapters 2, 3, 5 or 7, which are absent from the website. Adding source conversion, precise TOCs/anchors, navigation and chapter-aware publication is substantive chapter work; it is not a safe route alias. The owner expressly requires deferral rather than invented routes or substantial chapter implementation in this milestone.','',
        'The empty final package is an explicit blocked preparation result, not an authorization-ready release. It does not certify the 29 audit dossiers as final candidates. Twenty-two have direct source-topic evidence, while seven still have only contextual teaching for the tested method. All 29 have readable, original-image-bound private accessible dossiers after ten corrections; their academic objects remain unchanged.','',
        '| Category | Count |','|---|---:|','| Deferred Hardware | 25 |','| Other Volume 1 | 29 |','| Uncertain | 9 |','| Provisionally outside | 3 |','| Final eligible candidates | 0 |','',
        '| ID | Technology physical page | Original category | Current primary disposition | Actual chapter / heading | Secondary blockers | Next action |','|---|---:|---|---|---|---|---|']
    for r in rows:header.append(f"| {r['id']} | {r['pdfPage']} | {r['originalCategory']} | {r['primaryDisposition']} | {r['chapterTitle']} / {r.get('headingNumber','unassigned')} | {', '.join(r['blockers'])} | {r['nextAction']} |")
    (p.WORK/'FINAL-66-AUDIT.md').write_bytes(('\n'.join(header)+'\n').encode())
    subsets=[('OTHER-CHAPTER-INTEGRATION.md',[r for r in rows if r['originalCategory']=='other-vol1']),('HARDWARE-RECOVERY.md',[r for r in rows if r['originalCategory']=='ch1']),('UNCERTAIN-OUTSIDE-TRIAGE.md',[r for r in rows if r['originalCategory'] in ['uncertain','outside-vol1']])]
    for name,subset in subsets:
        lines=['# '+name.removesuffix('.md').replace('-',' ').title(),'',
            'This report preserves original classification and academic history. Source-supported recommendations and private accessible overlays do not grant mapping or publication approval. No unsupported student URL or anchor is assigned.','']
        for r in subset:
            lines += [f"## {r['id']} — Technology physical p.{r['pdfPage']}",'',f"FE / Morning / Subject A / {r['exam']['year']} {r['exam']['season']} Q{r['exam']['number']}. Native independently verified: {r['academicVerified']}; protected qualification: {r['protected']}; selected: false; approval: unapproved.",'',
                f"Primary disposition: **{r['primaryDisposition']}**. {r['classificationReason']}",'',
                f"Chapter: {r['chapterTitle']}; source heading {r.get('headingNumber','not assigned')} / {r.get('headingTitle','not assigned')}; concept {r.get('concept','not assigned')}. Website route/anchor: absent; no placeholder link is presented as a real lesson.",'',
                'Blockers: '+', '.join(r['blockers'])+'.','',r['nextAction'],'']
            if r.get('phase08Finding'):lines += ['Fresh source finding: '+r['phase08Finding'],'']
            if r.get('batch07Disposition'):lines += ['Original Batch 7 disposition: '+r['batch07Disposition']+'.','Private repairs: '+('; '.join(r.get('completedPrivateRepairs',[])) or 'None; source/academic/owner dependency persists.')+'.','Engineering/editorial scope: '+r['engineeringScope']+'.','']
            for ev in r.get('textbookEvidence',[]):lines += [f"Supporting source ({ev['role']}): FE Volume 1 printed p.{ev['printedPage']}, physical p.{ev['pdfPage']}; page-text SHA-256 `{ev['textSha256']}`.",'',ev['checkedExcerpt'],'']
            if r.get('privateMappingProposal'):lines += ['Future Hardware-only evidence proposal (not a Phase 8 release candidate):','',json.dumps(r['privateMappingProposal'],ensure_ascii=False,indent=2),'']
            if r.get('accessibleReview'):lines += ['Accessible review: '+r['accessibleReview']['status']+'; content hash `'+r['accessibleReview']['sha256']+'`.','']
        (p.WORK/name).write_bytes(('\n'.join(lines)+'\n').encode())
    roadmap=['# Remaining 66: implementation roadmap','',
        '1. Convert and verify the real Chapter 2 Information Processing System source, TOC, source-page labels, precise anchors and spatial figures. Its eleven questions all have direct topic evidence. Preserve the exact numeric MIPS example as teaching material; do not add answer-specific annotations to the general highlight. This is the largest clean first follow-up group.','',
        '2. Extend the existing typed chapter mapping, native publication eligibility and publisher only after real chapter identities and routes exist. Current native approval_errors and historical publisher explicitly enforce Chapter 1. The Phase 8 dry-run adapter is read-only and does not pretend those gates already support other chapters.','',
        '3. Implement Software teaching for the eight directly supported Chapter 3 records. Keep four contextual cases separate: TLB lookup latency, two distinct LOOK occurrences and the combined cache/main/disk average require precise teaching evidence, not just OS I/O or DAT terminology.','',
        '4. Network has two directly supported records and three with additional SECDED/redundancy teaching dependencies. The Algorithm chapter has one directly supported decision-table record. These require genuine chapter source conversion before release preparation.','',
        '5. Hardware remains 25: seven protected owner qualifications; two worked-explanation defects; two literal source-header defects; two figure-highlight capability dependencies; one cross-chapter secondary-evidence dependency; one unnumbered insert; ten direct-teaching/placement gaps. Five source-bound private accessible repairs are available, and two topology plus one secondary-evidence proposals are documented separately. None is silently added to the other-chapter package.','',
        '6. Nine uncertain set/count/rate/factorization questions remain unassigned; three outside records retain provisional lack-of-direct-coverage dispositions. Do not import another volume or infer absence of all context: the electrical-energy record has a real watts reference in Hardware, but lacks the required VI/time teaching.','',
        '7. After those dependencies are resolved, reprepare an exact nonempty candidate package through the existing framework. No approval fingerprint or source mapping from this empty result authorizes a future changed question set. Separate explicit owner publication authorization remains mandatory.','',
        'Release 7 operational risk remains open: 55 unexplained provider/local HTML hash differences, no new mismatch paths in Release 7, and transport-blocked live HTML/UI. This phase makes no production probes, rollback, cloud settings/data writes or deployment.','']
    (p.WORK/'ROADMAP.md').write_bytes('\n'.join(roadmap).encode())


def owner_gallery(rows):
    esc=lambda s:html.escape(str(s),quote=True)
    records={r['id']:r for r in p.h.read_json(p.WORK/'before/questions.json')};reviews=p.h.read_json(p.WORK/'before/reviews.json')
    groups={}
    for r in rows:
        key=('Chapter '+str(r['chapter'])+' — '+r['chapterTitle']) if r.get('chapter') else r['chapterTitle']
        groups.setdefault(key,[]).append(r)
    out=['<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="robots" content="noindex,nofollow"><title>Phase 8 — private final-66 owner audit</title><style>body{font:18px/1.6 system-ui;background:#faf8f1;color:#17212b;margin:auto;max-width:1050px;padding:24px}a{color:#175f7e}a:focus,summary:focus{outline:3px solid #b97800;outline-offset:4px}article{border-top:2px solid #cbc7ba;margin:36px 0;padding-top:24px}img{max-width:100%;height:auto;background:white}code{overflow-wrap:anywhere}blockquote{border-left:3px solid #b8b5aa;margin:16px 0;padding:8px 16px;background:#fff}dt{font-weight:bold}dd{margin:0 0 12px}nav ul{columns:2}h2,h3{scroll-margin-top:16px}@media(max-width:650px){body{padding:16px;font-size:16px}nav ul{columns:1}}</style><body><a href="#main">Skip to audit</a><main id="main"><h1>Phase 8 — read-only owner audit</h1><p>66 private records: 29 other-chapter, 25 Hardware, nine uncertain and three outside. <strong>Zero final eligible candidates and zero new approvals.</strong> All 29 other-chapter records are deferred because their real textbook chapters are not implemented; seven also lack exact teaching for the tested method. This is an audit gallery, not a release candidate claim.</p><p>Existing site: 687 published questions/images; existing approvals: 267. The separate isolated student preview contains only 290 unchanged Hardware references and zero new additions. No protected record appears in student grading.</p><h2 id="final-candidates">Final approval candidates: 0</h2><p>The exact empty manifest is fingerprint-bound to this audit and its original 29-record scope. It grants no publication authority. Audit and dossier hashes below are integrity receipts, not new owner approvals.</p><nav aria-label="Textbook chapter groups"><ul>']
    for i,(group,items) in enumerate(groups.items()):out.append(f'<li><a href="#group-{i}">{esc(group)} ({len(items)})</a></li>')
    out.append('</ul></nav><style>nav li{overflow-wrap:anywhere;break-inside:avoid;padding-right:.75rem}</style>')
    for i,(group,items) in enumerate(groups.items()):
        out.append(f'<section id="group-{i}"><h2>{esc(group)} ({len(items)})</h2><nav aria-label="{esc(group)} question navigation"><ul>')
        for row in items:out.append(f'<li><a href="#{esc(row["id"])}">{esc(row["id"])} · p.{row["pdfPage"]} · {esc(row.get("headingNumber","unassigned"))} / {esc(row.get("concept","follow-up"))}</a></li>')
        out.append('</ul></nav>')
        for row in items:
            qid=row['id'];r=records[qid];v=reviews[qid];x=row.get('accessibleReview',{}).get('content',v.get('extraction',{}));desc=x.get('imageDescription') or r['questionText'];opts=x.get('optionText',{})
            out += [f'<article id="{esc(qid)}" data-question-id="{esc(qid)}" data-eligible="false"><h3>{esc(qid)}</h3><p>FE · Morning · Subject A · {r["year"]} {esc(r["season"])} · Q{r["number"]} · Technology-01 physical p.{row["pdfPage"]}</p>',f'<p>Disposition: {esc(row["primaryDisposition"])} · Approval: unapproved · Technical publication eligibility: false.</p>',f'<a href="/images/{esc(qid)}.webp" target="_blank" rel="noopener" aria-label="Enlarge original {esc(qid)}"><img src="/images/{esc(qid)}.webp" alt="{esc(desc)}" loading="lazy" width="{r["images"][0]["width"]}" height="{r["images"][0]["height"]}"></a>',f'<details><summary>Accessible source description and original choices</summary><p>{esc(desc)}</p><dl>']
            for key in 'abcd':out.append(f'<dt>{key.upper()}</dt><dd>{esc(opts.get(key,"Incomplete or image-only source choice; preserve original image and review qualification."))}</dd>')
            answer=v.get('verification',{}).get('independentAnswer') if row['academicVerified'] else v.get('ownerAdjudication',{}).get('selectedAnswer')
            out.append(f'</dl></details><details><summary>Preserved academic answer and worked explanation</summary><p>{"Independently verified" if row["academicVerified"] else "Qualified owner-adjudicated; protected"} answer: {esc(str(answer).upper())}.</p><p>{esc(v["explanation"]["summary"])}</p><ol>')
            out.extend('<li>'+esc(step)+'</li>' for step in v['explanation']['steps'])
            out.append('</ol><p>'+esc(v['explanation']['takeaway'])+'</p>')
            if row['protected']:out.append('<p>Protected qualification and grading restriction preserved:</p><pre style="white-space:pre-wrap">'+esc(json.dumps(v.get('ownerAdjudication'),ensure_ascii=False,indent=2))+'</pre>')
            out += ['</details>',f'<p>Source heading: {esc(row.get("headingNumber","unassigned"))} / {esc(row.get("headingTitle","not established"))}; concept: {esc(row.get("concept","not mapped"))}. Approved student question placement: absent.</p>',f'<p>{esc(row["classificationReason"])}</p>']
            if row.get('availableSourceContext'):
                location=row['availableSourceContext'];url='http://127.0.0.1:4352'+location['path']+'#'+location['anchor']
                out.append(f'<p><a href="{esc(url)}" target="_blank" rel="noopener">Open existing Hardware source context in the isolated reference preview</a>. This is contextual teaching, not approval of the deferred question mapping.</p>')
            for ev in row.get('textbookEvidence',[]):out.append(f'<blockquote><p>FE Volume 1 printed p.{ev["printedPage"]}, physical p.{ev["pdfPage"]}; {esc(ev["role"])} support.</p><p>{esc(ev["checkedExcerpt"])}</p><p>Page SHA-256: <code>{esc(ev["textSha256"])}</code></p></blockquote>')
            if row.get('phase08Finding'):out.append('<p>Fresh source finding: '+esc(row['phase08Finding'])+'</p>')
            out += ['<p>Blockers: '+esc(', '.join(row['blockers']))+'</p>','<p>Next action: '+esc(row['nextAction'])+'</p>',f'<p>Original image SHA-256: <code>{r["images"][0]["sha256"]}</code><br>Native review integrity hash: <code>{row["beforeReviewSha256"]}</code></p>','<p><a href="#main">Back to chapter navigation</a></p></article>']
        out.append('</section>')
    out.append('</main></body></html>')
    return ''.join(out)
