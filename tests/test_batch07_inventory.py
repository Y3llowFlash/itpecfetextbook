"""Exhaustive inventory and frozen source-bound disposition regressions."""
from copy import deepcopy
from pathlib import Path
import sys
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import hardware_batch07 as b
import hardware_batch07_audit as audit


@unittest.skipUnless((b.WORK/'audit.json').exists(),'Private audit intentionally absent from clones')
class Inventory07Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ledger=b.h.read_json(b.WORK/'decisions.json')
        cls.records=b.h.read_json(b.WORK/'before/questions.json')
        cls.before=b.h.read_json(b.WORK/'before/reviews.json')
        cls.pages=b.core.book_pages();cls.public=b.h.read_json(b.h.ROOT/'public/data/questions.json')

    def validate(self,root=None,ledger=None):
        return audit.validate_inventory(ledger or self.ledger,self.records,self.before,self.pages,self.public,root=root)

    def mutation(self,edit,*,triage=False,rebind=True):
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary)
            for name in ['audit.json','uncertain-triage.json']:b.h.write_json(root/name,b.h.read_json(b.WORK/name))
            name='uncertain-triage.json' if triage else 'audit.json'
            value=b.h.read_json(root/name);edit(value);b.h.write_json(root/name,value)
            ledger=deepcopy(self.ledger)
            if rebind:ledger['triageSha256' if triage else 'auditSha256']=b.h.digest((root/name).read_bytes())
            with self.assertRaises(ValueError):self.validate(root,ledger)

    def test_all56_exactly_one_disposition_and_no_forced40(self):
        counts=self.validate();self.assertEqual(sum(counts.values()),56)
        self.assertEqual(counts,{'repairable-for-batch07':31,'deferred-protected':25})
        self.assertEqual(len(self.ledger['entries']),31)

    def test_missing_duplicate_unrecognized_or_stale_audit_rejected(self):
        self.mutation(lambda d:d['questions'].pop())
        self.mutation(lambda d:d['questions'].__setitem__(0,d['questions'][1]))
        self.mutation(lambda d:d['questions'][0].update(disposition='both-ready-and-deferred'))
        self.mutation(lambda d:d['questions'][0].update(decisionReason='changed'),rebind=False)

    def test_no_protected_qualified_or_uncertain_selection(self):
        rows=b.h.read_json(b.WORK/'audit.json')['questions']
        protected=[r for r in rows if r['protected']]
        self.assertEqual({r['pdfPage'] for r in protected},b.core.PROTECTED)
        self.assertTrue(all(not r['selected'] for r in protected))
        self.mutation(lambda d:next(r for r in d['questions'] if r['protected']).update(disposition='repairable-for-batch07',eligibleAfterRepairs=True,singleAnswerGrading=True,blockers=[]))
        self.mutation(lambda d:d['questions'][0].update(selected=True),triage=True)
        self.mutation(lambda d:d['questions'].pop(),triage=True)

    def test_every_source_binding_and_context_is_checked(self):
        self.mutation(lambda d:d['questions'][0].update(beforeReviewSha256='stale'))
        self.mutation(lambda d:d['questions'][0]['sourceBinding'].update(images=['wrong']))
        self.mutation(lambda d:d['questions'][0]['textbookEvidence'][0].update(checkedExcerpt='Fabricated direct source teaching'))
        self.mutation(lambda d:d['questions'][0]['textbookEvidence'][0].update(printedPage=999))

    def test_source_conflicts_and_genuine_coverage_gaps_remain_explicit(self):
        rows={r['pdfPage']:r for r in b.h.read_json(b.WORK/'audit.json')['questions']}
        self.assertEqual(rows[313]['blockers'],['source-explanation-numeric-conflict'])
        self.assertIn('40000000',rows[313]['decisionReason'])
        self.assertEqual(rows[191]['blockers'],['verified-explanation-does-not-work-question'])
        for p in [102,134,249]:self.assertEqual(rows[p]['conceptId'],'radix-conversion')
        self.assertFalse(rows[70]['selected'])
        for p in [4,123]:self.assertTrue(rows[p]['directTeaching']);self.assertTrue(rows[p]['newHighlightWarranted'])
        self.assertEqual(rows[322]['textbookEvidence'][1]['pdfPage'],307)
        self.assertEqual(rows[322]['textbookEvidence'][1]['role'],'secondary')


if __name__=='__main__':unittest.main()
