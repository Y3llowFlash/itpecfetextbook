"""Receipt and preservation checks for the explicitly authorized first release.

Uses historical_questions.approve and the existing TypeScript publisher. Frozen
preparation/audit snapshots remain historical evidence and are never rebased.
"""
import argparse
import copy
import json
import shutil
import subprocess
from pathlib import Path
import historical_questions as h
import academic_qa as qa
import approval_candidates as candidates
import approval_editorial as editorial

BASELINE='7f5545a58488c09a75779eb2fddbb7a58fc4f414'
MANIFEST_SHA='fdbbeeff0924f75508ca3336c714e8a17aa35bd820af1dfad3137615cf02c147'
FOLDER=h.ROOT/'.local/releases/historical-36'
SCOPE='first 36-question ITPEC Textbook release'
PUBLIC_RECEIPT=h.ROOT/'docs/development/evidence/historical-release-36.json'


def canonical(value):
    return json.dumps(value,sort_keys=True,ensure_ascii=False,separators=(',',':'))


def checksum(value):return h.digest(canonical(value).encode())


def unchanged_reviews(before,after,ids):
    if set(before)!=set(after):raise ValueError('Historical catalog scope changed')
    for qid,old in before.items():
        expected=copy.deepcopy(old)
        if qid in ids:expected['approval']=after[qid].get('approval')
        if expected!=after[qid]:raise ValueError(f'Unauthorized review change: {qid}')


def freeze(authorization):
    if FOLDER.exists():raise ValueError('Release baseline already frozen; never overwrite it')
    if subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()!=BASELINE:raise ValueError('Wrong preparation commit')
    m=candidates.check()
    if h.digest((editorial.folder()/'manifest.json').read_bytes())!=MANIFEST_SHA:raise ValueError('Reviewed package checksum mismatch')
    authorization=Path(authorization)
    if not authorization.is_file():raise ValueError('Explicit owner authorization is required')
    FOLDER.mkdir(parents=True)
    shutil.copyfile(authorization,FOLDER/'owner-authorization.txt')
    for name in ['reviews.json','manifest.json']:
        shutil.copyfile(h.WORK/name,FOLDER/('before-'+name))
    for name,source in [('questions',h.ROOT/'public/data/questions.json'),('concepts',h.ROOT/'src/content/concepts.json'),('explanations',h.ROOT/'src/content/explanations.json')]:
        shutil.copyfile(source,FOLDER/f'before-public-{name}.json')
    state={'schema':'itpec-historical-36-release-v1','baselineCommit':BASELINE,'candidateManifestSha256':MANIFEST_SHA,
        'authorizationSha256':h.digest(authorization.read_bytes()),'questionIds':m['questionIds'],'conceptCounts':m['conceptCounts'],
        'nativeQuestionsSha256':h.digest((h.WORK/'questions.json').read_bytes()),'sourceSha256':m['sourceSha256'],'bookSha256':m['textbookSha256'],
        'protectedFiles':{str(p.relative_to(h.ROOT)).replace('\\','/'):h.digest(p.read_bytes()) for folder in ['src','public'] for p in (h.ROOT/folder).rglob('*') if p.is_file()},
        'nativeImages':{str(h.WORK/im['path']):im['sha256'] for r in h.read_json(h.WORK/'questions.json') for im in r['images']}}
    h.write_json(FOLDER/'state.json',state)
    print('Frozen the exact reviewed package, original Practice catalog, and explicit authorization; no approvals granted.')


def context():
    state=h.read_json(FOLDER/'state.json')
    if not state or state['candidateManifestSha256']!=MANIFEST_SHA:raise ValueError('Missing release baseline')
    if h.digest((FOLDER/'owner-authorization.txt').read_bytes())!=state['authorizationSha256']:raise ValueError('Release authorization changed')
    m=h.read_json(editorial.folder()/'manifest.json')
    if h.digest((editorial.folder()/'manifest.json').read_bytes())!=MANIFEST_SHA or state['questionIds']!=m['questionIds']:raise ValueError('Authorized package changed')
    return state,m


def verify_native(require_approved=True):
    state,m=context();reviews=h.read_json(h.WORK/'reviews.json');before=h.read_json(FOLDER/'before-reviews.json');ids=state['questionIds']
    unchanged_reviews(before,reviews,ids)
    if h.digest((h.WORK/'questions.json').read_bytes())!=state['nativeQuestionsSha256'] or h.digest(h.SOURCE.read_bytes())!=state['sourceSha256'] or h.digest(qa.TEXTBOOK.read_bytes())!=state['bookSha256']:raise ValueError('Original source content changed')
    for path,sha in state['nativeImages'].items():
        if h.digest(Path(path).read_bytes())!=sha:raise ValueError('Original historical image changed')
    manifest=h.read_json(h.WORK/'manifest.json');old=h.read_json(FOLDER/'before-manifest.json')
    for key in ['sourceHistory','sourceSha256','recordsSha256','metadataReconciliation','editorialReconciliation','qaReconciliation','ownerAdjudication']:
        if manifest.get(key)!=old.get(key):raise ValueError(f'Original source/evidence receipt changed: {key}')
    for entry in m['candidates']:
        v=reviews[entry['id']]
        if h.publication_fingerprint(entry['record'],v)!=entry['publicationFingerprint']:raise ValueError('Approved content is stale')
        if require_approved:
            if not h.valid_approval(entry['record'],v) or v['approval'].get('releaseAuthorization')!={'instructionsSha256':state['authorizationSha256'],'candidateManifestSha256':MANIFEST_SHA,'scope':SCOPE,'imageSha256':entry['record']['images'][0]['sha256'],'contentSha256':entry['record']['contentSha256']}:raise ValueError('Missing exact fingerprint-bound release approval')
        elif v['approval']!=before[entry['id']]['approval']:raise ValueError('Already-approved release must not be silently refreshed')
    if any(v.get('approval',{}).get('status')!='unapproved' for qid,v in reviews.items() if qid not in ids):raise ValueError('An excluded historical question was approved')
    return state,m,reviews


def approve():
    candidates.check(publisher=True);state,m,reviews=verify_native(False)
    records=h.read_json(h.WORK/'questions.json');old=h.read_json(h.WORK/'manifest.json')
    for entry in m['candidates']:
        h.approve(records,entry['id'],'Project owner — explicit release authorization '+state['authorizationSha256'])
        # Store authorization inside the existing mutable approval object only.
        live=h.read_json(h.WORK/'reviews.json')
        live[entry['id']]['approval']['releaseAuthorization']={'instructionsSha256':state['authorizationSha256'],'candidateManifestSha256':MANIFEST_SHA,'scope':SCOPE,'imageSha256':entry['record']['images'][0]['sha256'],'contentSha256':entry['record']['contentSha256']}
        h.write_json(h.WORK/'reviews.json',live)
    # refresh_review deliberately rebuilds the native summary. Retain the prior
    # validated editorial receipt rather than replaying or altering its evidence.
    current=h.read_json(h.WORK/'manifest.json');current['editorialReconciliation']=old['editorialReconciliation'];h.write_json(h.WORK/'manifest.json',current)
    state,m,reviews=verify_native();candidates.check(publisher=True)
    h.write_json(FOLDER/'approvals.json',{'authorizationSha256':state['authorizationSha256'],'candidateManifestSha256':MANIFEST_SHA,'scope':SCOPE,
        'records':[{'id':qid,**reviews[qid]['approval']} for qid in state['questionIds']],'excludedUnapproved':297})
    print('Existing approval mechanism: exactly 36 approved, all other 297 unapproved; reviewed content unchanged.')


def verify_public():
    state,m,reviews=verify_native();bank=h.read_json(h.ROOT/'public/data/questions.json');answers=h.read_json(h.ROOT/'src/content/explanations.json');concepts=h.read_json(h.ROOT/'src/content/concepts.json')
    previous=h.read_json(FOLDER/'before-public-questions.json');old_answers=h.read_json(FOLDER/'before-public-explanations.json');old_concepts=h.read_json(FOLDER/'before-public-concepts.json')
    ids=set(state['questionIds']);index={q['id']:q for q in bank};explanations={e['questionId']:e for e in answers}
    if len(bank)!=len(index) or len(bank)!=456 or {q['id'] for q in bank if q['format']=='historical'}!=ids:raise ValueError('Unexpected public release scope')
    if any(index.get(q['id'])!=q for q in previous) or len(previous)!=420:raise ValueError('An authoritative Practice question changed')
    if any(explanations.get(e['questionId'])!=e for e in old_answers):raise ValueError('An authoritative Practice explanation changed')
    allowed={'public/data/questions.json','public/data/import-manifest.json','src/content/concepts.json','src/content/explanations.json'}
    for name,sha in state['protectedFiles'].items():
        if name not in allowed and h.digest((h.ROOT/name).read_bytes())!=sha:raise ValueError(f'Unrelated content changed: {name}')
    entries=[]
    for entry in m['candidates']:
        qid=entry['id'];q=index[qid];v=reviews[qid];e=explanations[qid];im=entry['record']['images'][0]
        if q['correctAnswer']!=v['verification']['independentAnswer'] or q['review']['approvalFingerprint']!=entry['publicationFingerprint'] or (q['paper'],q['subject'],q['review']['examType'])!=('AM','A','FE'):raise ValueError('Published answer, metadata or approval mismatch')
        for field in ['imageDescription','optionText']:
            if e[field]!=v['extraction'][field]:raise ValueError('Published accessible transcription differs from reviewed payload')
        for field in ['summary','steps','takeaway']:
            if e[field]!=v['explanation'][field]:raise ValueError('Published explanation differs from reviewed payload')
        if q['image']['sha256']!=im['sha256'] or h.digest((h.ROOT/'public'/q['image']['src'].lstrip('/')).read_bytes())!=im['sha256']:raise ValueError('Published original image differs')
        concept=next(c for c in concepts if c['id']==v['mapping']['conceptId'])
        if concept['questionIds'].count(qid)!=1 or q['review']['mappings']!=[v['mapping']]:raise ValueError('Published concept placement differs')
        entries.append({'id':qid,'approvalFingerprint':entry['publicationFingerprint'],'imageSha256':im['sha256'],'contentSha256':entry['record']['contentSha256'],
            'conceptId':concept['id'],'questionSha256':checksum(q),'explanationSha256':checksum(e),'mappingSha256':checksum(q['review']['mappings'])})
    for old in old_concepts:
        new=copy.deepcopy(next(c for c in concepts if c['id']==old['id']))
        new['questionIds']=[qid for qid in new['questionIds'] if qid not in ids]
        new['mappingEvidence']=[edge for edge in new['mappingEvidence'] if edge['questionId'] not in ids]
        if new!=old:raise ValueError('Existing concept content or Practice placement changed')
    if len(list((h.ROOT/'public/questions').iterdir()))!=456:raise ValueError('Unexpected public images')
    report={'schema':'itpec-historical-release-v1','preparationCommit':BASELINE,'candidateManifestSha256':MANIFEST_SHA,'authorizationSha256':state['authorizationSha256'],
        'scope':SCOPE,'authorizedCount':36,'excludedUnapproved':297,'practiceCount':420,'historicalCount':36,'total':456,'images':456,'conceptCounts':state['conceptCounts'],
        'practiceRecordsSha256':checksum({q['id']:q for q in previous}),'records':entries}
    return report


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('command',choices=['freeze','approve','verify','receipt']);parser.add_argument('--authorization',type=Path);args=parser.parse_args()
    if args.command=='freeze':freeze(args.authorization)
    elif args.command=='approve':approve()
    else:
        report=verify_public()
        if args.command=='receipt':
            if PUBLIC_RECEIPT.exists() and h.read_json(PUBLIC_RECEIPT)!=report:raise ValueError('Never silently refresh a published approval receipt')
            h.write_json(PUBLIC_RECEIPT,report)
        elif h.read_json(PUBLIC_RECEIPT)!=report:raise ValueError('Published approval receipt is stale')
        print(json.dumps({'approved':36,'excludedUnapproved':297,'publicTotal':456,'originalPracticeUnchanged':420,'receiptSha256':checksum(report)}))
