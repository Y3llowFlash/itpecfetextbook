"""Owner-confirmed FE metadata normalization; examination season is unrelated."""
import copy

POLICY_REFERENCE = 'Explicit owner instruction: Morning / Subject A Metadata Integration, 2026-10-23'
POLICY_INSTRUCTIONS_SHA = '7789861b24ca233e1c0a22264029f9d7ff066eebf46e2edb6650425ab31da928'


def normalize_metadata(existing=None, *, subject=None, paper=None, evidence=None):
    """Preserve explicit values; defaults never replace a declared Subject B."""
    old=copy.deepcopy(existing or {})
    if old.get('examType') not in [None,'FE']:
        raise ValueError('Source-specific examination level conflicts with FE owner policy')
    aliases={'Morning':'AM','Evening':'B','PM':'B'}
    prior_paper=aliases.get(old.get('paper'),old.get('paper'))
    declared=subject is not None or paper is not None
    paper=aliases.get(paper,paper)
    if subject is not None and subject not in ['A','B']:
        raise ValueError('Subject must be explicitly A or B')
    if paper is not None and paper not in ['AM','A','B']:
        raise ValueError('Unknown historical paper value')
    inferred_subject='A' if paper in ['AM','A'] else 'B' if paper=='B' else None
    if subject and inferred_subject and subject!=inferred_subject:
        raise ValueError('Declared paper and subject conflict')
    chosen_subject=subject or inferred_subject or old.get('subject') or ('B' if prior_paper=='B' else 'A')
    if chosen_subject not in ['A','B'] or prior_paper not in [None,'AM','A','B']:
        raise ValueError('Existing source-specific metadata is unsupported; review required')
    if prior_paper and ('B' if prior_paper=='B' else 'A')!=chosen_subject or old.get('subject') and old['subject']!=chosen_subject:
        raise ValueError('Source-specific paper/subject conflicts with owner declaration')
    chosen_paper=paper or prior_paper or ('B' if chosen_subject=='B' else 'AM')
    if (chosen_paper=='B')!=(chosen_subject=='B'):
        raise ValueError('Paper/subject conflict')
    if prior_paper and declared and ('B' if prior_paper=='B' else 'A')!=('B' if chosen_paper=='B' else 'A'):
        raise ValueError('Explicit metadata must never be overwritten')
    # An already confirmed explicit occurrence keeps all its provenance and values.
    if not declared and old.get('paper') and old.get('subject'):
        return old
    provenance=evidence or {'kind':'owner-confirmation','basis':'owner-default' if not declared else 'explicit-owner-declaration',
        'reference':POLICY_REFERENCE,'instructionsSha256':POLICY_INSTRUCTIONS_SHA,'publicationApprovalGranted':False}
    if provenance.get('kind') not in ['owner-confirmation','source-specific-evidence']:
        raise ValueError('Explicit metadata needs owner or source-specific provenance')
    if old.get('status')=='verified' and old.get('paper')==chosen_paper and old.get('subject')==chosen_subject and provenance in old.get('evidence',[]):
        return old
    result=copy.deepcopy(old)
    if old:result['history']=[*old.get('history',[]),{k:v for k,v in old.items() if k!='history'}]
    result.update(status='verified',examType='FE',paper=chosen_paper,subject=chosen_subject,
        evidence=[provenance],reason='Paper and subject established by explicit owner policy; not extracted from the PDF.')
    return result


def initial_reviews(records, *, subject=None):
    reviews={}
    for r in records:
        if r.get('examType') not in [None,'FE']:raise ValueError('Explicit source examination level conflicts with FE default')
        explicit={k:r[k] for k in ['examType','paper','subject'] if r.get(k) is not None}
        provenance={'kind':'source-specific-evidence','reference':'Explicit import metadata fields',
            'declaredFields':copy.deepcopy(explicit),'sourceReferences':copy.deepcopy(r.get('sourceReferences',[]))}
        if explicit.get('paper') and explicit.get('subject'):
            explicit.update(status='verified',evidence=[provenance])
        meta=normalize_metadata(explicit,subject=subject,evidence=provenance if explicit.get('paper') or explicit.get('subject') else None)
        reviews[r['id']]={'contentSha256':r['contentSha256'],'metadata':meta}
    return reviews


def merge_metadata(records, reviews, policy):
    ids=[r['id'] for r in records]
    if len(ids)!=333 or len(set(ids))!=333 or policy.get('scope')!=ids or set(reviews)!=set(ids):
        raise ValueError('Owner metadata policy requires the exact 333-question scope')
    if policy.get('examType')!='FE' or policy.get('paper')!='AM' or policy.get('subject')!='A' or policy.get('publicationApprovalGranted') is not False:
        raise ValueError('Metadata confirmation is not permission to approve or change the declared scope')
    updated=copy.deepcopy(reviews);changes=[]
    evidence={'kind':'owner-confirmation','basis':'explicit-owner-instruction','reference':POLICY_REFERENCE,
        'instructionsSha256':policy['instructionsSha256'],'sourceSha256':policy['sourceSha256'],
        'scope':'Technology-01, all 333 questions','paper':'AM','subject':'A','publicationApprovalGranted':False}
    for r in records:
        old=reviews[r['id']]
        if r.get('examType') not in [None,'FE'] or r.get('subject') not in [None,'A'] or r.get('paper') not in [None,'AM','A','Morning']:
            raise ValueError('Explicit original source metadata conflicts with the scoped owner confirmation')
        if old.get('contentSha256')!=r['contentSha256'] or any(s['sha256']!=policy['sourceSha256'] for s in r['sourceReferences']):
            raise ValueError('Stale metadata question/source binding')
        if old.get('approval',{}).get('status')!='unapproved':
            raise ValueError('Existing publication authority requires separate review; cannot carry it across metadata changes')
        meta=normalize_metadata(old.get('metadata'),subject='A',paper='AM',evidence=evidence)
        if meta!=old.get('metadata'):changes.append(r['id'])
        updated[r['id']]['metadata']=meta
    return updated,changes
