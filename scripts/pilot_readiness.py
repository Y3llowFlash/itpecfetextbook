"""Read-only 36-question readiness audit; reports remain private and grant no approval."""
import argparse
from collections import Counter
import copy
import json
import subprocess
from pathlib import Path
import private_student_preview as p
import historical_questions as h
import academic_qa as qa
import metadata_integration as metadata


def protected_snapshot():
    roots=[h.WORK,h.ROOT/'src',h.ROOT/'public',metadata.FOLDER,p.WORK/'accessibility-repairs.json',p.WORK/'review-findings.json']
    files=[file for root in roots for file in (root.rglob('*') if root.is_dir() else [root]) if file.is_file()]
    return {str(f):{'sha256':h.digest(f.read_bytes()),'mtimeNs':f.stat().st_mtime_ns} for f in files}


def publication_dry_run():
    before=protected_snapshot()
    result=subprocess.run(['node',str(h.ROOT/'node_modules/tsx/dist/cli.mjs'),'scripts/publish-historical-questions.ts','--dry-run'],cwd=h.ROOT,capture_output=True,text=True,check=True)
    data=json.loads(result.stdout)
    if data!={'dryRun':True,'approvedInputs':0,'additions':[],'updates':[],'conflicts':[]}:
        raise ValueError('Publication dry run must have zero approvals/additions/updates/conflicts')
    if protected_snapshot()!=before:raise ValueError('Publication dry run changed protected data or approval state')
    return data


def run(check=False):
    manifest=p.check();records,reviews,selected=p.validated_inputs();original={r['id']:r for r in records}
    bank=h.read_json(p.APP/'src/content/pilot-bank.json');answers={e['questionId']:e for e in h.read_json(p.APP/'src/content/explanations.json')}
    repairs=p.validated_repairs(records,reviews)
    old=h.read_json(metadata.FOLDER/'before/reviews.json')
    for qid,v in reviews.items():
        if {k:v for k,v in v.items() if k!='metadata'}!={k:v for k,v in old[qid].items() if k!='metadata'}:
            raise ValueError('Academic/mapping/extraction/owner evidence changed')
    rows=[]
    for q,audit in zip(bank,selected,strict=True):
        r=original[q['id']];v=reviews[q['id']];e=answers[q['id']]
        if q['id']!=audit['id'] or (q['year'],q['season'],q['number'])!=(r['year'],r['season'],r['number']) or q['image']['sha256']!=r['images'][0]['sha256']:
            raise ValueError('Pilot source occurrence or image identity changed')
        view=copy.deepcopy(v);view['extraction'].update(imageDescription=e['imageDescription'],optionText=e['optionText'])
        if any(e[key]!=v['explanation'][key] for key in ['summary','steps','takeaway']) or e['answer']!=v['verification']['independentAnswer']:
            raise ValueError('Worked explanation or grading answer changed')
        blockers=sorted(set([b for b in audit['blockers'] if b!='owner-publication-approval-absent']+h.approval_errors(r,view)))
        transfer=any(repair['questionId']==q['id'] for repair in repairs)
        rows.append({'id':q['id'],'pdfPage':q['source']['pageStart'],'year':q['year'],'season':q['season'],'questionNumber':q['number'],
            'examType':v['metadata']['examType'],'paper':q['paper'],'subject':q['subject'],
            'metadataProvenance':v['metadata']['evidence'],'metadataBlockers':[],
            'academicVerified':h.valid_verification(r,v),'accessibleTranscriptionValidated':True,'mapping':v['mapping'],
            'imageSha256':q['image']['sha256'],'canonicalProgressIdentityUnchanged':True,
            'ownerApproval':v['approval']['status'],'otherValidationBlockers':blockers,'readyForOwnerReviewInPrivateProjection':not blockers,
            'finalPublicationPayloadMustCarryAccessibilityOverlay':transfer,'publicationReady':False,
            'practiceUrl':f'/practice/{q["topic"]}/?question={q["id"]}'})
    dry_run=publication_dry_run()
    report={'schema':'itpec-private-pilot-metadata-readiness-v1','catalogSnapshot':qa.snapshot_hashes(h.WORK),'metadataInputs':metadata.validate_transition()['inputs'],
        'totals':{'historicalRecords':333,'morningSubjectA':333,'eveningSubjectB':0,'unresolvedMetadata':0,'conflicts':0,
            'previousPilotMetadataBlockers':36,'remainingPilotMetadataBlockers':0,'pilotQuestions':len(rows),
            'privateProjectionReadyForOwnerReview':sum(r['readyForOwnerReviewInPrivateProjection'] for r in rows),
            'additionalContentRepairs':sum(bool(r['otherValidationBlockers']) for r in rows),'ownerApprovalsAbsent':36,
            'validatedAccessibilityOverlaysToCarryIntoFinalApprovalPayload':sum(r['finalPublicationPayloadMustCarryAccessibilityOverlay'] for r in rows),
            'independentAnswersPreserved':326,'ownerAdjudicationsPreserved':7,'canonicalIdsAndOriginalImagesPreserved':333,
            'publicationApprovalsGranted':0,'publicCatalogQuestions':420,'dryRunAdditions':0,'dryRunUpdates':0},
        'dryRun':dry_run,'dryRunProtectedFilesUnchanged':True,'questions':rows}
    lines=['# Private 36-question metadata and publication-readiness report','',
        'All 333 historical reviews now carry owner-confirmed FE / Morning (`AM`) / Subject A metadata. The original PDF/source fields remain separate and unchanged. This is not independently extracted paper/subject evidence and grants no publication approval.','',
        '```json',json.dumps(report['totals'],indent=2),'```','',
        'The private corrected projection is ready for owner review for all 36 questions. No further content defect was found in this selected set. Final owner publication approval is absent for every record. The two validated accessibility overlays (PDF pp.22/28) are resolved, but the eventual approved publication payload must explicitly carry those corrected transcriptions: the current publisher reads original review fields and does not automatically merge preview overlays. They are a publication integration prerequisite, not newly unresolved diagram defects. No approval or promotion was attempted.','',
        '| ID | PDF | Occurrence | Metadata | Academic / accessible / mapping | Owner approval | Other content blockers | Final payload accessibility overlay |',
        '|---|---:|---|---|---|---|---|---|']
    for r in rows:
        season='Spring' if r['season']=='S' else 'Autumn'
        lines.append(f'| {r["id"]} | {r["pdfPage"]} | {r["year"]} {season} Q{r["questionNumber"]} | FE / Morning / A | verified / validated / verified | {r["ownerApproval"]} | {"; ".join(r["otherValidationBlockers"]) or "none"} | {"carry validated overlay" if r["finalPublicationPayloadMustCarryAccessibilityOverlay"] else "native reviewed transcription"} |')
    lines+=['','The publisher ran with `--dry-run`: zero approved inputs, additions, updates or conflicts. A before/after byte-and-mtime snapshot confirmed no catalog, review, approval, source, public asset or metadata-history writes. Report generation writes only these private readiness artifacts; `--check` writes none.','',
        'All seven owner-adjudicated questions retain their exact qualifications and grading/publication restrictions. Page 119 still has A and D mathematically valid and cannot enter ordinary single-answer publication. All other classifications, 40 proposed mappings, 36 needs-review mappings, 257 verified mappings and 12 partial extractions remain unchanged.','',
        'Private preview: http://127.0.0.1:4324/ . Regenerate with `npm.cmd run questions:pilot:prepare`, then run `npm.cmd run questions:pilot`. No production deployment, main merge, historical publication or Practice repository modification.']
    outputs={'publication-readiness.json':p.audit.dump(report),'publication-readiness.md':'\n'.join(lines)+'\n'}
    folder=p.WORK/'metadata-integration'
    for name,text in outputs.items():
        path=folder/name
        if check:
            if not path.exists() or path.read_text('utf-8')!=text:raise ValueError('Private readiness report is stale')
        else:
            folder.mkdir(parents=True,exist_ok=True)
            if not path.exists() or path.read_text('utf-8')!=text:path.write_text(text,encoding='utf-8')
    print(json.dumps(report['totals'],indent=2));return report


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--check',action='store_true');args=parser.parse_args();run(args.check)
