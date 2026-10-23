"""Release receipt checks use synthetic records and never approve real data."""
import copy
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import release_36 as release


class ReleasePreservationTests(unittest.TestCase):
    def test_only_candidate_approval_fields_can_change(self):
        before={'candidate':{'answer':'a','approval':{'status':'unapproved'}},'private':{'answer':'b','approval':{'status':'unapproved'}}}
        after=copy.deepcopy(before);after['candidate']['approval']={'status':'approved','fingerprint':'bound'}
        release.unchanged_reviews(before,after,{'candidate'})
        for dimension in ['answer','approval']:
            changed=copy.deepcopy(after);changed['private'][dimension]='unauthorized'
            with self.subTest(dimension=dimension),self.assertRaises(ValueError):release.unchanged_reviews(before,changed,{'candidate'})
        changed=copy.deepcopy(after);changed['candidate']['answer']='c'
        self.assertRaises(ValueError,release.unchanged_reviews,before,changed,{'candidate'})
        changed=copy.deepcopy(after);changed['extra']={}
        self.assertRaises(ValueError,release.unchanged_reviews,before,changed,{'candidate'})

    def test_canonical_receipt_is_order_independent_and_content_bound(self):
        self.assertEqual(release.checksum({'b':2,'a':['✓',1]}),release.checksum({'a':['✓',1],'b':2}))
        self.assertNotEqual(release.checksum({'a':'original'}),release.checksum({'a':'edited'}))


if __name__=='__main__':unittest.main()
