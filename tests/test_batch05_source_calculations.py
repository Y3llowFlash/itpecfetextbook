"""Independent numeric and truth-table checks of the private, source-reviewed payload.

No original question text, private choices, or candidate answers are checked in.
"""
import itertools
import re
import sys
from pathlib import Path
import unittest
from fractions import Fraction
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import hardware_batch05 as b


@unittest.skipUnless((b.WORK/'decisions.json').exists(),'Private original-source package absent')
class SourceCalculationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows={e['pdfPage']:e for e in b.h.read_json(b.WORK/'decisions.json')['entries']}
        cls.records={r['regions'][0]['pdfPage']:r for r in b.h.read_json(b.h.WORK/'questions.json')}
        cls.reviews=b.h.read_json(b.h.WORK/'reviews.json')

    def answer(self,page):return self.reviews[self.records[page]['id']]['verification']['independentAnswer']

    def test_nand_and_nor_options_preserve_source_topology_and_unique_answer(self):
        ops={'NAND':lambda x,y:int(not(x and y)),'NOR':lambda x,y:int(not(x or y))}
        for page in [223,243]:
            correct=[]
            for letter,choice in self.rows[page]['extraction']['optionText'].items():
                outputs=[]
                for a,bb in itertools.product([0,1],repeat=2):
                    for cc in ([0,1] if page==243 else [0]):
                        env={**ops,'A':a,'B':bb,'C':cc}
                        for statement in choice.split(';'):
                            name,formula=statement.strip().split('=',1)
                            self.assertRegex(formula,r'^[A-Z(),]+$')
                            env[name]=eval(formula,{'__builtins__':{}},env)
                        expected=int(a==bb) if page==223 else int(not((a and bb) and (bb or cc)))
                        outputs.append(env['Y' if page==223 else 'F']==expected)
                if all(outputs):correct.append(letter)
            self.assertEqual(correct,[self.answer(page)])

    def test_original_latch_table_polarity_and_feedback(self):
        for page,nand in [(190,True),(208,False)]:
            valid=[]
            for letter,text in self.rows[page]['extraction']['optionText'].items():
                tokens=text.split('; ');expected=[]
                for s,r in itertools.product([0,1],repeat=2):
                    stable=[]
                    for q,qbar in itertools.product([0,1],repeat=2):
                        good=(q==int(not(s and qbar)) and qbar==int(not(r and q))) if nand else (q==int(not(r or qbar)) and qbar==int(not(s or q)))
                        if good:stable.append((q,qbar))
                    expected.append('unchanged' if len(stable)==2 else 'unstable' if stable[0][0]==stable[0][1] else f'({stable[0][0]},{stable[0][1]})')
                if tokens==expected:valid.append(letter)
            self.assertEqual(valid,[self.answer(page)])

    def test_numeric_conditions_and_exact_source_option_identity(self):
        # Operands from the independently read source stay private with their bindings.
        ledger=b.h.read_json(b.WORK/'source-review/calculation-inputs.json')
        self.assertEqual(ledger['sourceSha256'],b.audit.SOURCE_SHA)
        self.assertEqual(len(ledger['cases']),12)
        def radix(value,base):
            integer,_,fraction=value.partition('.')
            return Fraction(int(integer or '0',base))+Fraction(int(fraction or '0',base),base**len(fraction))
        def choice_value(text,base):
            if base=='range':return tuple(map(int,re.findall(r'-?\d+',text)))
            return radix(re.match(r'[0-9A-F.]+',text)[0],base)
        for case in ledger['cases']:
            page=case['pdfPage'];args=case['inputs'];op=case['operation']
            self.assertEqual(case['sourceBinding'],b.qa.extraction_binding(self.records[page]))
            if op=='quotient':result=Fraction(*args)
            elif op=='radix':result=radix(*args)
            elif op=='scaled-radix':result=radix(*args[:2])*args[2]
            elif op=='sum':result=sum(args)
            elif op=='popcount':result=args[0].bit_count()
            elif op=='identifier-bits':result=(args[0]-1).bit_length()
            elif op=='shift-and-add':result=(1<<args[0])+1
            elif op=='signed-range':result=(-(1<<(args[0]-1)),(1<<(args[0]-1))-1)
            elif op=='sequential-cache':
                hit,cache,memory=map(Fraction,args);result=hit*cache+(1-hit)*(cache+memory)
            elif op=='hierarchy':
                m1,m2,t1,t2,tm=map(Fraction,args);result=(1-m1)*t1+m1*(1-m2)*t2+m1*m2*tm
            else:self.fail('Unknown independently reviewed operation')
            matches=[letter for letter,text in self.rows[page]['extraction']['optionText'].items() if choice_value(text,case['choiceRadix'])==result]
            self.assertEqual(matches,[self.answer(page)])
        self.assertIn('incremental',self.reviews[self.records[274]['id']]['explanation']['takeaway'])


if __name__=='__main__':unittest.main()
