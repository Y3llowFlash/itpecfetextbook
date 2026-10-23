"""Build/check a loopback-only student preview. Never promotes or edits reviews."""
import argparse
from collections import Counter
import contextlib
import csv
import io
import json
from pathlib import Path
import re
import shutil
import subprocess
import fitz
import catalog_audit as audit
import academic_qa as qa
import historical_questions as h

ROOT = h.ROOT
WORK = ROOT/'.local/private-student-preview'
APP = WORK/'app'
TEMPLATES = ROOT/'scripts/private-preview'
SHORTLIST = 'ITPEC_Chapter1_36_Private_Pilot_Shortlist.csv'
NOTES = 'ITPEC_Chapter1_36_Pilot_Review_Notes.md'
COUNTS = {'logic-gates':24,'radix-conversion':6,'usb-interface':2,'cpu-registers':1,'cache-memory':1,'disk-access':1,'defragmentation':1}
PREFIX = 'itpecTextbook:privatePilot36:'
PILOT_BASELINE = '0d28d36f0a206caf899c337c4d26d059bfdf7e4a'
REPAIR_SCOPE = {'HIST-TECH01-2019A-Q012':22, 'HIST-TECH01-2019S-Q023':28}


def save(path, value):
    data = (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2)+'\n').encode()
    if not path.exists() or path.read_bytes() != data:
        path.parent.mkdir(parents=True, exist_ok=True); path.write_bytes(data)


def fingerprint():
    files = [Path(__file__), ROOT/'scripts/historical_metadata.py', ROOT/'scripts/metadata_integration.py', ROOT/'scripts/private-student-preview-server.mjs', ROOT/'astro.config.mjs', ROOT/'package.json', ROOT/'package-lock.json']
    files += [p for folder in [ROOT/'src', ROOT/'public', TEMPLATES] for p in folder.rglob('*') if p.is_file()]
    return {str(p.relative_to(ROOT)).replace('\\','/'):h.digest(p.read_bytes()) for p in sorted(files)}


def select_questions(inventory, records, reviews, csv_rows):
    selected = [r for r in inventory if r.get('priorityAfterMandatoryRepairs') is True]
    ids = [r['id'] for r in selected]
    if len(ids)!=36 or len(set(ids))!=36 or len(csv_rows)!=36 or len({r['canonical_id'] for r in csv_rows})!=36 or set(ids)!={r['canonical_id'] for r in csv_rows}:
        raise ValueError('The exact 36 unique pilot IDs must agree with the attached shortlist')
    source={r['id']:r for r in records}; advisory={r['canonical_id']:r for r in csv_rows}
    for q in selected:
        r=source[q['id']];v=reviews[q['id']];c=q['auditClassification'];m=v['mapping'];row=advisory[q['id']]
        if q['contentSha256']!=r['contentSha256'] or q['reviewSha256']!=qa.object_hash(v) or q['images']!=r['images']:
            raise ValueError('Stale pilot question/review/image snapshot')
        if c['category']!='ch1' or c['chapter']!=1 or c['placement']!='exact' or not h.valid_verification(r,v) or v.get('ownerAdjudication') or h.effective_extraction(r,v)!='complete' or not q['extraction']['accessibleReviewComplete'] or m.get('status')!='verified' or q['mapping']['issues'] or not q['mapping']['existingConceptReusableInPrinciple']:
            raise ValueError('Pilot requires independent answers, complete accessibility and issue-free existing concept mappings')
        meta=v.get('metadata',{})
        if v['approval']['status']!='unapproved' or meta.get('status')!='verified' or meta.get('examType')!='FE' or meta.get('paper')!='AM' or meta.get('subject')!='A' or not meta.get('evidence'):
            raise ValueError('Pilot requires owner-confirmed Morning/Subject A metadata and no publication approval')
        expected = {'historical_pdf_page':r['regions'][0]['pdfPage'],'exam_year':r['year'],'exam_season':r['season'],'exam_question_number':r['number'],
            'book_heading':m['headingNumber'],'concept_id':m['conceptId'],'book_printed_page':c['evidence'][0]['printedPage'],'book_physical_page':c['evidence'][0]['pdfPage'],
            'existing_section_id':m['sectionId'],'existing_subsection_id':m['subsectionId'],'priority_status':'private-pilot-candidate-only',
            'publication_approval':'unapproved','paper_metadata':'unknown','subject_metadata':'unknown'}
        if any(row.get(k)!=str(value) for k,value in expected.items()):
            raise ValueError(f'Shortlist metadata/placement disagrees with the live source-bound audit: {q["id"]}')
    if dict(Counter(reviews[q['id']]['mapping']['conceptId'] for q in selected))!=COUNTS:
        raise ValueError('Pilot must retain the exact seven-concept distribution')
    return selected


def validated_inputs():
    if subprocess.run(['git','merge-base','--is-ancestor',PILOT_BASELINE,'HEAD'],cwd=ROOT,capture_output=True).returncode:
        raise ValueError('The completed audit commit must be an ancestor; do not compare it to the older input baseline')
    with contextlib.redirect_stdout(io.StringIO()):audit.run(check=True)
    records=h.read_json(h.WORK/'questions.json');reviews=h.read_json(h.WORK/'reviews.json')
    inventory=h.read_json(audit.report_folder()/'classification-inventory.json')['questions']
    candidates=h.read_json(audit.report_folder()/'chapter1-candidates.json')['questions']
    queue=h.read_json(audit.report_folder()/'mapping-extraction-repair-queue.json')['repairs']
    # These companion audit artifacts must describe the same live snapshot.
    if [r for r in inventory if r['chapter1Candidate']]!=candidates or len({r['id'] for r in queue})!=len(queue):
        raise ValueError('Audit companion inventories disagree')
    with (audit.report_folder()/'classification-inventory.csv').open(encoding='utf-8',newline='') as f:
        if [r['id'] for r in csv.DictReader(f)]!=[r['id'] for r in inventory]:raise ValueError('Audit CSV scope differs')
    with (WORK/'inputs'/SHORTLIST).open(encoding='utf-8-sig',newline='') as f:rows=list(csv.DictReader(f))
    selected=select_questions(inventory,records,reviews,rows)
    return records,reviews,selected


def validated_repairs(records, reviews, ledger=None):
    """Read an editorial overlay, never rewrite the preserved academic reviews."""
    ledger=h.read_json(WORK/'accessibility-repairs.json') if ledger is None else ledger
    if not isinstance(ledger,dict) or ledger.get('schema')!='itpec-accessibility-repairs-v1' or ledger.get('sourceSha256')!=audit.SOURCE_SHA:
        raise ValueError('Source-bound accessibility repair ledger is required')
    repairs=ledger.get('repairs',[]);source={r['id']:r for r in records}
    if len(repairs)!=2 or {r['questionId'] for r in repairs}!=set(REPAIR_SCOPE):
        raise ValueError('Accessibility repair scope must be exactly historical pages 22 and 28')
    for repair in repairs:
        r=source.get(repair['questionId']);v=reviews.get(repair['questionId'])
        if not r or not v or repair.get('contentSha256')!=r['contentSha256'] or repair.get('reviewSha256')!=qa.object_hash(v) or repair.get('imageSha256')!=r['images'][0]['sha256'] or repair.get('pdfPage')!=REPAIR_SCOPE[r['id']] or r['regions'][0]['pdfPage']!=repair['pdfPage']:
            raise ValueError('Stale accessibility source/review/image/page binding')
        if v['extraction'].get('editorialProvenance'):
            from approval_editorial import validate_rebound_repair
            validate_rebound_repair(r,v,repair)
            continue
        before={key:v['extraction'][key] for key in ['imageDescription','optionText']}
        after=repair.get('after',{})
        if repair.get('before')!=before or set(after)!=set(before) or not isinstance(after['imageDescription'],str) or not after['imageDescription'].strip() or after['imageDescription']==before['imageDescription']:
            raise ValueError('Accessibility repair must bind original text and change only accessible fields')
        expected_options=dict(before['optionText'])
        if repair['pdfPage']==28:expected_options['d']='B AND (A OR B)'
        if after['optionText']!=expected_options:
            raise ValueError('Accessibility repair changed an unrelated answer choice')
        if repair.get('status')!='source-validated' or not repair.get('sourceDiagramEvidence') or repair.get('validationMethod')!='visual-comparison-with-original-pdf-and-pixel-matched-crop':
            raise ValueError('Accessibility repair needs completed original-diagram validation')
    return repairs


def validated_findings(selected, records, reviews, findings=None, repairs=()):
    findings=h.read_json(WORK/'review-findings.json') if findings is None else findings
    if findings is None:raise ValueError('Preserved private editorial findings input is required; findings must not silently disappear')
    source={r['id']:r for r in records};ids={q['id'] for q in selected}
    if not isinstance(findings,list) or len({f['questionId'] for f in findings})!=len(findings):raise ValueError('Editorial findings must be unique per selected question')
    for f in findings:
        r=source.get(f['questionId'])
        if f['questionId'] not in ids or f.get('contentSha256')!=r['contentSha256'] or f.get('reviewSha256')!=qa.object_hash(reviews[r['id']]) or f.get('imageSha256')!=r['images'][0]['sha256']:
            raise ValueError('Editorial finding has an unselected or stale source/review binding')
        if not f.get('finding'):raise ValueError('Editorial findings must retain their original issue')
        if f.get('status')=='resolved-accessibility':
            repair=next((x for x in repairs if x['questionId']==f['questionId']),None)
            if not repair or f.get('resolutionSha256')!=qa.object_hash(repair):
                raise ValueError('Cannot clear an editorial finding without its validated accessibility repair')
        elif f.get('status')!='editorial-review-pending':
            raise ValueError('Editorial finding has an unknown review status')
    if repairs and {r['questionId'] for r in repairs}!={f['questionId'] for f in findings if f['status']=='resolved-accessibility'}:
        raise ValueError('Each validated accessibility repair needs its preserved resolved finding')
    return findings


def association(q, concept):
    mapping=q['currentMapping'];node=next(n for n in h.read_json(ROOT/'src/content/hardware-toc.json')['nodes'] if n['id']==mapping['subsectionId'])
    if mapping['conceptId'] not in node['conceptIds'] or node['number']!=mapping['headingNumber'] or node['sectionId']!=concept['sectionId'] or node['path']!=concept['sectionUrl']:
        raise ValueError('Existing concept/section/subsection relationship cannot be established')
    file=ROOT/'src/content/source-hardware'/f'{concept["sectionUrl"].strip("/").split("/")[-1]}.html'
    html=file.read_text('utf-8')
    matches=list(re.finditer(r'<a\b(?=[^>]*\bdata-concept="'+re.escape(concept['id'])+r'")[^>]*>([\s\S]*?)</a>',html))
    if len(matches)!=1 or f'id="{node["id"]}"' not in html:
        raise ValueError('Reuse requires one actual existing reviewed source highlight, not a heading-name match')
    match=matches[0];start=html.rfind('<p ',0,match.start());end=html.find('</p>',match.end())+4
    paragraph=html[start:end];body=re.sub('<[^>]+>',' ',paragraph)
    # Retain the already-reviewed shared subsection for the disk-access question.
    reason={
      'logic-gates':'Truth tables, gates, Boolean laws and NAND/XOR networks belong to 3-4-1; the existing Logic circuit entry introduces this same subsection.',
      'radix-conversion':'Positional radix weights, integer/fraction conversion and base relationships are taught under the existing 2-2 entry.',
      'usb-interface':'The original USB definition and device-limit characteristics are taught in 5-5-2 (physical pp.113-114).',
      'cpu-registers':'The actual register definitions on physical p.52 distinguish instruction storage and next-instruction address.',
      'cache-memory':'The cache passage on physical p.75 explicitly describes loading a missing block from main memory.',
      'disk-access':'This question tests why defragmentation improves disk-file access. Keep the existing access-time entry in 4-1-3, with explicit defragmentation support on physical p.91; do not describe it as a numeric seek/latency calculation.',
      'defragmentation':'The existing defragmentation highlight and explanation on physical p.91 directly teach rearrangement to improve disk access.',
    }[concept['id']]
    section=html[html.rfind('<section ',0,match.start()):match.start()]
    physical=int(re.search(r'data-pdf-page="(\d+)"',section)[1]);printed=int(re.search(r'data-printed-page="(\d+)"',section)[1])
    paragraph_id=re.search(r'<p\b[^>]*\bid="([^"]+)"',paragraph)
    return {'questionId':q['id'],'conceptId':concept['id'],'chapter':1,'sectionId':node['sectionId'],'subsectionId':node['id'],
        'heading':node['number'],'route':node['path'],'highlightId':f'concept-{concept["id"]}',
        'highlightPrintedPage':printed,'highlightPhysicalPdfPage':physical,'sourceParagraphId':paragraph_id[1] if paragraph_id else None,
        'highlightSourceSha256':h.digest(match[0].encode()),'paragraphSha256':h.digest(paragraph.encode()),'sourceFile':str(file.relative_to(ROOT)),
        'paragraphText':h.norm(body),'bookEvidence':q['auditClassification']['evidence'],
        'additionalSupportingPhysicalPages':{'disk-access':[91],'usb-interface':[114],'radix-conversion':[29,30,31,32,33]}.get(concept['id'],[]),
        'status':'private-preview-association-reviewed-not-publication-approved','reason':reason}


def project(selected,records,reviews,concepts,repairs=()):
    index={r['id']:r for r in records};bank=[];explanations=[];links=[]
    for q in selected:
        r=index[q['id']];v=reviews[r['id']];m=v['mapping'];c=next(c for c in concepts if c['id']==m['conceptId'])
        links.append(association(q,c));im=r['images'][0]
        bank.append({'id':r['id'],'examId':f'private-{r["year"]}{r["season"]}-FE-{v["metadata"]["paper"]}','number':r['number'],'year':r['year'],'season':r['season'],
          'subject':v['metadata']['subject'],'paper':v['metadata']['paper'],'privatePreview':True,'is_published':False,'sourceKind':'past_paper','format':'multiple-choice','examLabel':'FE (owner-confirmed)',
          'correctAnswer':v['verification']['independentAnswer'],'options':list('abcd'),'chapter':'Hardware','section':m['sectionId'],'topic':m['conceptId'],'mapping':m,
          'image':{'src':f'/__pilot/images/{im["sha256"]}.webp','width':im['width'],'height':im['height'],'sha256':im['sha256']},
          'source':{'dataset':'private-technology-01','questionPdf':'Technology-01.pdf','pageStart':r['regions'][0]['pdfPage'],'pageEnd':r['regions'][-1]['pdfPage'],
                    'originalImagePath':im['path'],'documentPath':'Technology-01.pdf'},
          'review':{'examType':'FE','sources':[{'kind':'historical-pdf','filename':'Technology-01.pdf','sha256':audit.SOURCE_SHA,'pages':[p['pdfPage'] for p in r['regions']]}],
                    'answerVerification':'verified','mappingStatus':'verified','extractionQuality':'complete','reviewStatus':'needs-review','publicationStatus':'unapproved','mappings':[m]}})
        e=v['explanation'];x=next((repair['after'] for repair in repairs if repair['questionId']==r['id']),v['extraction'])
        # Metadata-only rebinding must not change the academic revision of saved attempts.
        prior_meta=v['metadata'].get('history',[v['metadata']])[0]
        academic_view={**v,'metadata':prior_meta}
        if v['extraction'].get('editorialProvenance'):
            original=next(repair['before'] for repair in repairs if repair['questionId']==r['id'])
            academic_view['extraction']={**v['extraction'],**original}
            academic_view['extraction'].pop('editorialProvenance')
        academic_revision=qa.object_hash(academic_view)
        explanations.append({'questionId':r['id'],'revision':f'private-{academic_revision[:16]}','answer':v['verification']['independentAnswer'],
          'summary':e['summary'],'steps':e['steps'],'takeaway':e['takeaway'],'optionText':x['optionText'],'imageDescription':x['imageDescription'],
          'reviewedAgainst':['Existing immutable independently verified private review',academic_revision]})
    scoped=[]
    for c in concepts:
        if c['id'] not in COUNTS:continue
        value=dict(c);value['questionIds']=[q['id'] for q in bank if q['topic']==c['id']];value['videos']=[];scoped.append(value)
    return bank,explanations,scoped,links


def replace_checked(file, before, after):
    text=file.read_text('utf-8')
    if before not in text:raise ValueError(f'Preview overlay target changed: {file.name}: {before[:60]}')
    file.write_text(text.replace(before,after),encoding='utf-8')


def overlay():
    # Copy the approved application, then adapt only this ignored private copy.
    shutil.copytree(ROOT/'src',APP/'src',dirs_exist_ok=True)
    for src in (ROOT/'public').rglob('*'):
        rel=src.relative_to(ROOT/'public')
        if src.is_file() and rel.parts[0] not in ['questions','data'] and src.suffix.lower()!='.pdf':
            dst=APP/'public'/rel;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dst)
    for rel in ['package.json','tsconfig.json']:
        shutil.copyfile(ROOT/rel,APP/rel)
    (APP/'astro.config.mjs').write_text("import {defineConfig} from 'astro/config';import react from '@astrojs/react';export default defineConfig({site:'http://127.0.0.1:4324',output:'static',trailingSlash:'always',integrations:[react()],devToolbar:{enabled:false}});\n",encoding='utf-8')
    targets={'catalog.ts':'lib/catalog.ts','account.ts':'lib/account.ts','firebase.ts':'lib/firebase.ts',
             'AccountControls.tsx':'components/AccountControls.tsx','GuestNotice.tsx':'components/GuestNotice.tsx','index.astro':'pages/index.astro'}
    for source,target in targets.items():shutil.copyfile(TEMPLATES/(source+'.template'),APP/'src'/target)
    # Namespacing applies to filters, account caches, reading returns and guest keys.
    for p in (APP/'src').rglob('*'):
        if p.suffix in ['.ts','.tsx','.astro']:
            text=p.read_text('utf-8');p.write_text(re.sub(r'itpecTextbook:(?!privatePilot36:)',PREFIX,text),encoding='utf-8')
    for name in ['firestore-sync.ts','account-session.ts','sync-controller.ts']:
        (APP/'src/lib'/name).unlink(missing_ok=True)
    models=APP/'src/lib/models.ts'
    replace_checked(models,'is_published: true;','is_published: false; privatePreview: true;')
    policy=APP/'src/lib/question-policy.ts'
    replace_checked(policy,'q.is_published === true','q.privatePreview === true && q.is_published === false')
    text=policy.read_text('utf-8');start=text.index('export function questionLabel(');end=text.index('\nexport interface MatchCandidate',start)
    policy.write_text(text[:start]+"export function questionLabel(q: Question) { return `FE · ${q.paper === 'AM' || q.paper === 'A' ? 'Morning' : q.paper === 'B' ? 'Evening' : q.paper} · Subject ${q.subject} · ${q.year} ${q.season === 'S' ? 'Spring' : 'Autumn'}`; }\n"+text[end:],encoding='utf-8')
    replace_checked(APP/'src/lib/question-highlights.ts','q.is_published===true','q.privatePreview===true&&q.is_published===false')
    replace_checked(APP/'src/lib/question-highlights.ts','published questions','private preview questions')
    # Remove only unavailable exam-link overlays, preserving their native wording.
    high=APP/'src/lib/question-highlights.ts'
    replace_checked(high,'  return html;',"""  return html.replace(/<a\\b([^>]*data-concept=\"([^\"]+)\"[^>]*)>([\\s\\S]*?)<\\/a>/g,(whole,_attrs,id,body)=>concepts.some(c=>c.id===id)?whole:body.replace(/<span class=\"concept-count\"[^>]*>[\\s\\S]*?<\\/span>/g,''));""")
    replace_checked(APP/'src/components/Practice.tsx','related published questions','related private preview questions')
    replace_checked(APP/'src/components/Practice.tsx','complete published question set','complete private preview question set')
    layout=APP/'src/layouts/SiteLayout.astro'
    replace_checked(layout,'noindex = false','noindex = true')
    replace_checked(layout,'<body>','<body><p class="source-note" role="note">Private student preview · Not approved for publication · Disposable local progress</p>')
    progress=APP/'src/components/ProgressDashboard.tsx'
    replace_checked(progress,'Optional Google sign-in backs up submitted attempts, incorrect-answer history, bookmarks, completed sections and periodic reading checkpoints. Offline changes are kept locally for the same account and retried when the connection returns.','This private preview uses disposable local progress only. Google sign-in, migration and cloud synchronization are disabled.')
    (APP/'public/robots.txt').write_text('User-agent: *\nDisallow: /\n',encoding='utf-8')


def prepare():
    WORK.mkdir(parents=True,exist_ok=True);(WORK/'inputs').mkdir(exist_ok=True)
    for name in [SHORTLIST,NOTES]:
        destination=WORK/'inputs'/name
        if not destination.exists():shutil.copyfile(Path('C:/Users/lenovo/Downloads')/name,destination)
    records,reviews,selected=validated_inputs()
    concepts=h.read_json(ROOT/'src/content/concepts.json')
    repairs=validated_repairs(records,reviews)
    findings=validated_findings(selected,records,reviews,repairs=repairs)
    bank,answers,scoped,links=project(selected,records,reviews,concepts,repairs)
    # Independently compare all 36 active crops to the original PDF at recorded DPI.
    with fitz.open(h.SOURCE) as source:
        qa.validate_source_images([r for r in records if r['id'] in {q['id'] for q in selected}],source)
    APP.mkdir(parents=True,exist_ok=True);overlay()
    save(APP/'src/content/pilot-bank.json',bank);save(APP/'src/content/concepts.json',scoped);save(APP/'src/content/explanations.json',answers)
    # Astro always writes to this ignored root, never the production dist/public.
    result=subprocess.run(['node',str(ROOT/'node_modules/astro/bin/astro.mjs'),'check'],cwd=APP,env=environment())
    if result.returncode:raise ValueError('Private Astro/TypeScript validation failed')
    result=subprocess.run(['node',str(ROOT/'node_modules/astro/bin/astro.mjs'),'build'],cwd=APP,env=environment())
    if result.returncode:raise ValueError('Private preview build failed')
    assets={}
    for p in (APP/'dist').rglob('*'):
        if p.is_file():assets['/'+p.relative_to(APP/'dist').as_posix()]={'path':str(p),'sha256':h.digest(p.read_bytes())}
    for q in bank:
        r=next(r for r in records if r['id']==q['id']);assets[q['image']['src']]={'path':str(h.WORK/r['images'][0]['path']),'sha256':q['image']['sha256']}
    if any('/questions/' in name or '/data/' in name or name.endswith('.pdf') for name in assets):raise ValueError('Private delivery accidentally included a public bank or PDF')
    manifest={'schema':'itpec-private-student-preview-v1','privateOnly':True,'publicationApprovalGranted':False,'snapshot':qa.snapshot_hashes(h.WORK),
      'implementation':fingerprint(),'inputHashes':{name:h.digest((WORK/'inputs'/name).read_bytes()) for name in [SHORTLIST,NOTES]},
      'sourceSha256':audit.SOURCE_SHA,'bookSha256':audit.BOOK_SHA,'auditBaseline':audit.BASELINE,'completedAuditCommit':PILOT_BASELINE,
      'questionIds':[q['id'] for q in bank],'counts':COUNTS,'associations':links,'assets':assets,
      'imagesComparedToOriginalPixels':36,'excludedAssociations':[],'editorialFindings':findings,'accessibilityRepairs':repairs,'progressPrefix':PREFIX,'paper':'AM','subject':'A'}
    save(WORK/'manifest.json',manifest)
    save(WORK/'walkthrough.json',[{'conceptId':c['id'],'questionId':c['questionIds'][0],'readingUrl':f'{c["sectionUrl"]}#concept-{c["id"]}',
        'practiceUrl':f'/practice/{c["id"]}/?question={c["questionIds"][0]}'} for c in scoped])
    check()
    print('Prepared 36 unapproved private questions; serve with npm run questions:pilot')


def environment():
    import os
    return {**os.environ,'ASTRO_TELEMETRY_DISABLED':'1'}


def check():
    records,reviews,selected=validated_inputs();manifest=h.read_json(WORK/'manifest.json')
    if not manifest or manifest.get('schema')!='itpec-private-student-preview-v1' or manifest.get('privateOnly') is not True or manifest.get('publicationApprovalGranted') is not False:
        raise ValueError('Prepare the private preview first; approval is never supplied by preview generation')
    if manifest['snapshot']!=qa.snapshot_hashes(h.WORK) or manifest['implementation']!=fingerprint() or manifest['questionIds']!=[q['id'] for q in selected]:
        raise ValueError('Private preview is stale; rebuild without editing the original review objects')
    if manifest['inputHashes']!={name:h.digest((WORK/'inputs'/name).read_bytes()) for name in [SHORTLIST,NOTES]}:
        raise ValueError('Private shortlist/review-note inputs changed')
    repairs=validated_repairs(records,reviews)
    findings=validated_findings(selected,records,reviews,repairs=repairs)
    bank,answers,concepts,links=project(selected,records,reviews,h.read_json(ROOT/'src/content/concepts.json'),repairs)
    if manifest.get('editorialFindings')!=findings or manifest.get('accessibilityRepairs')!=repairs:raise ValueError('Private editorial evidence changed; rebuild from validated corrections')
    if links!=manifest['associations'] or h.read_json(APP/'src/content/pilot-bank.json')!=bank or h.read_json(APP/'src/content/explanations.json')!=answers or h.read_json(APP/'src/content/concepts.json')!=concepts:
        raise ValueError('Generated private data or source associations changed')
    expected_assets={'/'+p.relative_to(APP/'dist').as_posix():{'path':str(p),'sha256':h.digest(p.read_bytes())} for p in (APP/'dist').rglob('*') if p.is_file()}
    originals={r['id']:r for r in records}
    for q in bank:expected_assets[q['image']['src']]={'path':str(h.WORK/originals[q['id']]['images'][0]['path']),'sha256':q['image']['sha256']}
    if manifest['assets']!=expected_assets:
        raise ValueError('Private delivery must contain the exact built site and 36 selected source images only')
    for name,asset in manifest['assets'].items():
        path=Path(asset['path']).resolve()
        if not (path.is_relative_to((APP/'dist').resolve()) or path.is_relative_to((h.WORK/'images').resolve())) or not path.is_file() or h.digest(path.read_bytes())!=asset['sha256']:
            raise ValueError('Private image/build asset identity changed')
    for p in (APP/'dist').rglob('*.js'):
        text=p.read_text('utf-8')
        if any(marker in text for marker in ['firestore.googleapis.com','identitytoolkit.googleapis.com','itpec-textbook.firebaseapp.com','AIzaSyBE9']):
            raise ValueError('Private preview must not include production Firebase runtime/configuration')
    # QA history stays in the private editorial manifest, never in student props/UI.
    for p in (APP/'dist').rglob('*'):
        if p.is_file() and p.suffix in ['.html','.js','.json']:
            text=p.read_text('utf-8')
            if any(marker in text for marker in ['previewNotices','Private editorial review','editorial-review-pending','resolved-accessibility']+[f['finding'] for f in findings]+[f['studentNotice'] for f in findings if f.get('studentNotice')]):
                raise ValueError('Internal editorial notices leaked into the student build')
    print('Private preview integrity: 36 questions, 7 existing concepts, 0 approvals, 0 public catalog changes.')
    return manifest


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('command',choices=['prepare','check'])
    args=parser.parse_args()
    if args.command=='prepare':prepare()
    else:check()
