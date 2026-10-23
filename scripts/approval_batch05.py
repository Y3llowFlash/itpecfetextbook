"""Combined private preparation adapter for the existing approval-candidate system.

No authorization transition is implemented here. Repeated preparation validates the
frozen inputs; it never refreshes fingerprints after a change.
"""
from collections import Counter
from pathlib import Path
import re
import shutil
import fitz
import approval_candidates as c
import hardware_batch05 as b

h=c.h
qa=c.qa
INPUTS=('candidate-recommendation.json','review-diff.json','coverage-analysis.json',
        'excluded-deferred.json','highlight-validation.json','decisions-concepts.json',
        'highlight-plan.json','preview/manifest.json','preview/app/src/content/pilot-bank.json',
        'preview/app/src/content/explanations.json','preview/app/src/content/concepts.json',
        'preview/app/src/content/owner-review.json','decisions.json','baseline-guard.json')


def folder():return b.WORK/'final-approval'


def implementation():
    return {**c.implementation(),**b.implementation(),
            'scripts/approval_batch05.py':h.digest(Path(__file__).read_bytes())}


def freeze():
    root=folder()
    if (root/'preparation-inputs.json').exists():return
    preview=b.check()
    files={name:h.digest((b.WORK/name).read_bytes()) for name in INPUTS}
    for name in INPUTS:
        dest=root/'before/batch'/name;dest.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(b.WORK/name,dest)
    for name in ['questions.json','reviews.json','manifest.json','index.html']:
        dest=root/'before/native'/name;dest.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(h.WORK/name,dest)
    bank=h.read_json(b.APP/'src/content/pilot-bank.json')
    published=h.read_json(h.ROOT/'public/data/questions.json')
    ids=preview['questionIds']
    c.save(root/'preparation-inputs.json',{
        'schema':'itpec-final-candidate-preparation-batch05-v1','baselineCommit':b.BASELINE,
        'productionBaseline':b.BASELINE,'files':files,'snapshot':qa.snapshot_hashes(h.WORK),
        'questionIds':ids,'conceptCounts':dict(sorted(Counter(q['topic'] for q in bank if q['id'] in ids).items())),
        'releasedQuestionIds':[q['id'] for q in published if q['id'].startswith('HIST-')],
        'publicFiles':b.core.public_fingerprints(),
        'nativeFiles':{name:h.digest((h.WORK/name).read_bytes()) for name in ['questions.json','reviews.json','manifest.json','index.html']},
        'sourceSha256':b.audit.SOURCE_SHA,'textbookSha256':b.audit.BOOK_SHA,
        'publicationApprovalGranted':False})


def inputs():
    root=folder();context=h.read_json(root/'preparation-inputs.json')
    if not context or context.get('schema')!='itpec-final-candidate-preparation-batch05-v1' or context.get('baselineCommit')!=b.BASELINE or context.get('productionBaseline')!=b.BASELINE or context.get('publicationApprovalGranted') is not False or set(context.get('files',{}))!=set(INPUTS):
        raise ValueError('Missing exact combined Batch 5 preparation context')
    b.check()
    for name,sha in context['files'].items():
        if h.digest((root/'before/batch'/name).read_bytes())!=sha or h.digest((b.WORK/name).read_bytes())!=sha:
            raise ValueError('Stale frozen Batch 5 input: '+name)
    if qa.snapshot_hashes(root/'before/native')!=context['snapshot'] or qa.snapshot_hashes(h.WORK)!=context['snapshot']:
        raise ValueError('Frozen/live native snapshot changed')
    for name,sha in context['nativeFiles'].items():
        if h.digest((root/'before/native'/name).read_bytes())!=sha or h.digest((h.WORK/name).read_bytes())!=sha:
            raise ValueError('Native history, source or approvals changed')
    records=h.read_json(h.WORK/'questions.json');reviews=h.read_json(h.WORK/'reviews.json')
    c.validate_live_reviews(records,reviews,h.read_json(root/'before/native/reviews.json'),context['questionIds'])
    public=h.read_json(h.ROOT/'public/data/questions.json')
    ids=context['questionIds'];released=[q['id'] for q in public if q['id'].startswith('HIST-')]
    if len(public)!=576 or len(released)!=156 or released!=context['releasedQuestionIds'] or len(ids)!=40 or len(set(ids))!=40 or set(ids)&{q['id'] for q in public}:
        raise ValueError('Exact Batch 5 new/public scope changed')
    if context['publicFiles']!=b.core.public_fingerprints() or h.digest(h.SOURCE.read_bytes())!=context['sourceSha256'] or h.digest(qa.TEXTBOOK.read_bytes())!=context['textbookSha256']:
        raise ValueError('Published or original source content changed')
    return context,records,reviews


def concepts(context):
    original=h.read_json(folder()/'before/batch/preview/app/src/content/concepts.json')
    published={x['id']:x for x in h.read_json(h.ROOT/'src/content/concepts.json')}
    result=[]
    for cid in context['conceptCounts']:
        view=c.concept_view(next(x for x in original if x['id']==cid))
        if cid in published and view!=c.concept_view(published[cid]):raise ValueError('Reused concept changed')
        result.append({**view,'newConcept':cid not in published})
    if len(result)!=16 or {x['id'] for x in result if x['newConcept']}!={'flip-flops'}:
        raise ValueError('Exact sixteen concepts and one new flip-flop highlight required')
    return result


def associations(context,records,reviews,definitions):
    original=h.read_json(folder()/'before/batch/preview/manifest.json');result=[]
    for qid in context['questionIds']:
        v=reviews[qid];definition=next(x for x in definitions if x['id']==v['mapping']['conceptId'])
        link=b.core.source_association({'id':qid,'currentMapping':v['mapping'],'auditClassification':{'evidence':v['mapping']['evidence']}},definition)
        if link!=next(x for x in original['associations'] if x['questionId']==qid):raise ValueError('Question/highlight association changed')
        source=(h.ROOT/link['sourceFile']).read_text('utf8')
        if definition.get('sourceHighlight'):pid=definition['sourceHighlight']['passageId']
        else:
            anchor=re.search(r'<a\b[^>]*data-concept="'+re.escape(definition['id'])+r'"',source)
            start=source.rfind('<p ',0,anchor.start());pid=re.search(r'\bid="([^"]+)"',source[start:source.find('>',start)])[1]
        result.append({**link,'sourceParagraphId':pid})
    return result


def source_reviews(context,records,reviews,definitions,links,*,prepare=False):
    return c.validate_batch03_reviews(context,records,reviews,definitions,links,prepare=prepare,
        root=folder(),expected_highlights=1,review_schema='itpec-batch05-final-source-review-v1')


def entries(context,records,reviews,definitions,links,rows,report):
    result=c.batch03_entries(context,records,reviews,definitions,links,rows,report,root=folder())
    prior={x['id']:x for x in h.read_json(folder()/'before/batch/candidate-recommendation.json')['questions']}
    for entry in result:
        if entry['publicationFingerprint']!=prior[entry['id']]['candidateFingerprint']:raise ValueError('Prepared candidate fingerprint changed')
        entry['dimensionFingerprints']={k:qa.object_hash(entry['review'][k]) for k in ['verification','explanation','extraction','metadata','classification','mapping']}
        entry['sourceTranscription']['literalSourceTypos']=entry['finalSourceReview'].get('literalSourceTypos',[])
        entry['approvalContextFingerprint']=c.approval_context_fingerprint(entry,entry['conceptDefinition'])
    return result


def gallery(manifest,definitions):
    return c.batch03_gallery(manifest,definitions,highlight_count=1).replace('http://127.0.0.1:4332','http://127.0.0.1:4340')


def assets(result):
    root=folder()
    return {'/':{'path':str(root/'index.html'),'sha256':h.digest((root/'index.html').read_bytes())},
        **{f'/images/{e["id"]}.webp':{'path':str(h.WORK/e['record']['images'][0]['path']),'sha256':e['record']['images'][0]['sha256']} for e in result}}


def prepare():
    if (folder()/'manifest.json').exists():check();return
    freeze();context,records,reviews=inputs();definitions=concepts(context)
    links=associations(context,records,reviews,definitions)
    rows,report=source_reviews(context,records,reviews,definitions,links,prepare=True)
    result=entries(context,records,reviews,definitions,links,rows,report)
    with fitz.open(h.SOURCE) as pdf:qa.validate_source_images([e['record'] for e in result],pdf)
    manifest={'schema':'itpec-final-approval-candidates-v1','batch':5,'baselineCommit':b.BASELINE,
        'privateOnly':True,'readOnly':True,'publicationApprovalGranted':False,
        'preparationInputsSha256':qa.object_hash(context),'catalogSnapshot':context['snapshot'],
        'sourceSha256':context['sourceSha256'],'textbookSha256':context['textbookSha256'],
        'questionIds':context['questionIds'],'conceptCounts':context['conceptCounts'],
        'conceptDefinitions':definitions,'highlightIntegration':report,'expectedNewHighlights':1,
        'implementation':implementation(),'sourceReviewSha256':h.digest((folder()/'source-review.json').read_bytes()),
        'publicCatalogSha256':h.digest((h.ROOT/'public/data/questions.json').read_bytes()),
        'previewEquality':{'questions':40,'conceptDefinitionsEqual':16,'allStudentVisibleFieldsEqual':True,'fields':list(result[0]['studentVisible']),'academicChanges':0},
        'finalVisualReview':rows,'candidates':result}
    manifest['candidateSetFingerprint']=c.batch03_fingerprint(context,result,definitions,report)
    (folder()/'index.html').write_text(gallery(manifest,definitions),encoding='utf8')
    manifest['galleryAssets']=assets(result);c.save(folder()/'manifest.json',manifest);check()


def check(publisher=False):
    context,records,reviews=inputs();definitions=concepts(context);links=associations(context,records,reviews,definitions)
    rows,report=source_reviews(context,records,reviews,definitions,links)
    result=entries(context,records,reviews,definitions,links,rows,report)
    manifest=h.read_json(folder()/'manifest.json')
    c.validate_final_package(manifest,result,definitions,report,context,batch=5)
    expected={'questions':40,'conceptDefinitionsEqual':16,'allStudentVisibleFieldsEqual':True,'fields':list(result[0]['studentVisible']),'academicChanges':0}
    if manifest.get('implementation')!=implementation() or manifest.get('baselineCommit')!=b.BASELINE or manifest.get('preparationInputsSha256')!=qa.object_hash(context) or manifest.get('catalogSnapshot')!=context['snapshot'] or manifest.get('sourceSha256')!=context['sourceSha256'] or manifest.get('textbookSha256')!=context['textbookSha256'] or manifest.get('expectedNewHighlights')!=1 or manifest.get('publicCatalogSha256')!=h.digest((h.ROOT/'public/data/questions.json').read_bytes()) or manifest.get('sourceReviewSha256')!=h.digest((folder()/'source-review.json').read_bytes()) or manifest.get('finalVisualReview')!=rows or manifest.get('previewEquality')!=expected:
        raise ValueError('Stale Batch 5 candidate package or source/implementation binding')
    if (folder()/'index.html').read_text('utf8')!=gallery(manifest,definitions) or manifest.get('galleryAssets')!=assets(result):raise ValueError('Owner gallery bytes or allowlist changed')
    return manifest
