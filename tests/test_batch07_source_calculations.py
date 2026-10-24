"""Independent source calculations; private operands and source choices stay local."""
import itertools
import math
import unittest
from fractions import Fraction
from test_batch06_source_calculations import evaluate
import hardware_batch07 as b


@unittest.skipUnless((b.WORK/'source-review/calculation-inputs.json').exists(),'Private source operands absent from clones')
class SourceCalculations07(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=b.h.read_json(b.WORK/'source-review/calculation-inputs.json')
        cls.records={r['regions'][0]['pdfPage']:r for r in b.h.read_json(b.h.WORK/'questions.json')}
        cls.reviews=b.h.read_json(b.h.WORK/'reviews.json')
        cls.book=b.core.book_pages()

    def test_exact_source_bound_calculation_scope(self):
        self.assertEqual(self.data['sourceSha256'],b.audit.SOURCE_SHA)
        self.assertEqual(len(self.data['cases']),b.COUNT)
        self.assertEqual({c['pdfPage'] for c in self.data['cases']},b.PAGES)
        for c in self.data['cases']:
            r=self.records[c['pdfPage']];v=self.reviews[r['id']]
            self.assertEqual(c['sourceBinding'],b.qa.extraction_binding(r))
            self.assertEqual(c['optionTextSha256'],b.qa.object_hash(v['extraction']['optionText']))

    def test_boolean_circuits_all_states_and_source_complement_scopes(self):
        for c in self.data['cases']:
            if c['kind']!='boolean':continue
            names=list(c['variables']);states=[dict(zip(names,v)) for v in itertools.product(*c['variables'].values())]
            matches=[letter for letter,expr in c['choices'].items() if all(bool(evaluate(expr,s))==bool(evaluate(c['target'],s)) for s in states)]
            with self.subTest(page=c['pdfPage']):self.assert_match(c,matches)

    def test_binary_patterns_bitwise_algorithms_and_literal_led_masks(self):
        for c in self.data['cases']:
            if c['kind']=='led':
                on=[name for i,name in enumerate(c['ports']) if bool((c['value']>>i)&1)==c['onValue']]
                self.assert_match(c,[k for k,v in c['choices'].items() if set(v)==set(on)])
            elif c['kind']=='alternating':
                # Positional proof: x is sum 2^(2k+1); x/2 has the disjoint even
                # powers. Their union is all powers 0..2n-1, hence 2^(2n)-1.
                for n in range(1,65):
                    x=sum(2**(2*k+1) for k in range(n))
                    result=x+x//2
                    choices=[2**(2*n),2**(2*n)-1,2**(2*n+1),2**(2*n+1)-1]
                    self.assert_match(c,[chr(97+i) for i,v in enumerate(choices) if v==result])
            elif c['kind']=='rightmost':
                for width in range(1,11):
                    for x in range(1,2**width):
                        intermediate=x^(x-1);mask=2**width-1
                        values={'a':x&intermediate,'b':(~(x&intermediate))&mask,'c':x|intermediate,'d':x^intermediate}
                        expected=next(1<<i for i in range(width) if x&(1<<i))
                        self.assertEqual(values['a'],expected)
                # Distinguish functions over the domain, not at one example.
                matches=[k for k in 'abcd' if all(({'a':x&(x^(x-1)),'b':(~(x&(x^(x-1))))&255,'c':x|(x^(x-1)),'d':x^(x^(x-1))})[k]==(x&-x) for x in range(1,256))]
                self.assert_match(c,matches)

    def test_weighted_cache_ranking_hit_ratio_and_finite_octal(self):
        for c in self.data['cases']:
            if c['kind']=='cache-ranking':
                times={k:Fraction(v[0]) if len(v)==1 else Fraction(v[0])*Fraction(v[1],100)+Fraction(v[2])*(1-Fraction(v[1],100)) for k,v in c['systems'].items()}
                order=sorted(times,key=times.get)
                self.assert_match(c,[k for k,v in c['choices'].items() if v==order])
                alternate={k:Fraction(v[0]) if len(v)==1 else Fraction(v[0])+Fraction(v[2])*(1-Fraction(v[1],100)) for k,v in c['systems'].items()}
                self.assertEqual(order,sorted(alternate,key=alternate.get))
            elif c['kind']=='hit-ratio':
                cache,memory,effective=map(Fraction,c['values']);ratio=(memory-effective)/(memory-cache)
                self.assert_match(c,[k for k,v in c['choices'].items() if Fraction(v)==ratio])
            elif c['kind']=='terminating':
                matches=[]
                for k,v in c['choices'].items():
                    denominator=Fraction(v).denominator
                    while (common:=math.gcd(denominator,c['base']))>1:denominator//=common
                    if denominator==1:matches.append(k)
                self.assert_match(c,matches)

    def test_definitions_supported_by_exact_teaching_not_printed_keys(self):
        for c in self.data['cases']:
            if c['kind']!='definition':continue
            self.assertTrue(c['independentRationale']);self.assertTrue(c['sourceTeaching'])
            for ev in c['sourceTeaching']:
                self.assertIn(ev['checkedExcerpt'],b.h.norm(self.book[ev['pdfPage']-1]['text']))
            self.assert_match(c,[c['independentlyReadChoice']])

    def assert_match(self,c,matches):
        self.assertEqual(len(matches),1,(c['pdfPage'],matches))
        v=self.reviews[self.records[c['pdfPage']]['id']]
        self.assertTrue(b.h.valid_verification(self.records[c['pdfPage']],v))
        self.assertEqual(matches,[v['verification']['independentAnswer']],c['pdfPage'])


if __name__=='__main__':unittest.main()
