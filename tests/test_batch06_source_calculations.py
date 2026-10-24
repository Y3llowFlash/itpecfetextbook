"""Independent calculations; source operands, choices and keys remain private."""
import ast,itertools,math,operator,sys,unittest
from fractions import Fraction
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import hardware_batch06 as b


def evaluate(expression,variables):
    """Interpret literal source expressions without arbitrary code execution."""
    def visit(node):
        if isinstance(node,ast.Expression):return visit(node.body)
        if isinstance(node,ast.Constant) and isinstance(node.value,(int,bool)):return node.value
        if isinstance(node,ast.Name) and node.id in variables:return variables[node.id]
        if isinstance(node,ast.Tuple):return tuple(visit(item) for item in node.elts)
        if isinstance(node,ast.UnaryOp) and isinstance(node.op,ast.Not):return not visit(node.operand)
        if isinstance(node,ast.UnaryOp) and isinstance(node.op,ast.USub):return -visit(node.operand)
        if isinstance(node,ast.BoolOp):
            values=[visit(item) for item in node.values]
            return all(values) if isinstance(node.op,ast.And) else any(values)
        binary={ast.Add:operator.add,ast.Sub:operator.sub,ast.Mult:operator.mul,ast.Mod:operator.mod,ast.BitAnd:operator.and_,ast.BitOr:operator.or_}
        if isinstance(node,ast.BinOp) and type(node.op) in binary:return binary[type(node.op)](visit(node.left),visit(node.right))
        compares={ast.Eq:operator.eq,ast.NotEq:operator.ne,ast.Lt:operator.lt,ast.LtE:operator.le,ast.Gt:operator.gt,ast.GtE:operator.ge}
        if isinstance(node,ast.Compare) and all(type(op) in compares for op in node.ops):
            values=[visit(node.left),*[visit(n) for n in node.comparators]]
            return all(compares[type(op)](left,right) for op,left,right in zip(node.ops,values,values[1:]))
        if isinstance(node,ast.Call) and isinstance(node.func,ast.Name) and node.func.id in ['NAND','NOR'] and not node.keywords:
            values=[visit(item) for item in node.args]
            return not(all(values) if node.func.id=='NAND' else any(values))
        raise ValueError('Unsupported source-calculation operation')
    return visit(ast.parse(expression,mode='eval'))


def radix(value,base):
    integer,_,fraction=value.partition('.')
    return Fraction(int(integer or '0',base))+Fraction(int(fraction or '0',base),base**len(fraction))


@unittest.skipUnless((b.WORK/'source-review/calculation-inputs.json').exists(),'Private source operands intentionally absent from clones')
class SourceCalculations06(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        ledger=b.h.read_json(b.WORK/'source-review/calculation-inputs.json')
        assert ledger['sourceSha256']==b.audit.SOURCE_SHA and ledger['schema']=='itpec-private-batch06-source-calculations-v1'
        cls.cases=ledger['cases'];cls.records={r['regions'][0]['pdfPage']:r for r in b.h.read_json(b.h.WORK/'questions.json')}
        cls.reviews=b.h.read_json(b.h.WORK/'reviews.json')
        assert len(cls.cases)==40 and {case['pdfPage'] for case in cls.cases}==b.PAGES

    def check_group(self,group):
        cases=[case for case in self.cases if case['group']==group];self.assertTrue(cases)
        for case in cases:
            with self.subTest(page=case['pdfPage']):
                record=self.records[case['pdfPage']];review=self.reviews[record['id']]
                self.assertEqual(case['sourceBinding'],b.qa.extraction_binding(record))
                self.assertEqual(case['optionTextSha256'],b.qa.object_hash(review['extraction']['optionText']))
                self.assertTrue(b.h.valid_verification(record,review));kind=case['kind']
                if kind=='definition':matches=[case['independentlyReadChoice']]
                elif kind=='numeric':matches=self.numeric(case)
                else:
                    names=list(case['variables']);states=[dict(zip(names,values)) for values in itertools.product(*(case['variables'][n] for n in names))]
                    if kind=='expression':matches=[letter for letter,expr in case['choices'].items() if all(evaluate(expr,state)==evaluate(case['target'],state) for state in states)]
                    elif kind=='selector':
                        self.assertTrue(all(sum(bool(evaluate(expr,state)) for expr in case['enables'])==1 for state in states))
                        matches=[letter for letter,values in case['choices'].items() if evaluate(case['enables'][case['targetIndex']],dict(zip(names,values)))]
                    elif kind=='equivalence-set':
                        correct=[i for i,expr in enumerate(case['networks']) if all(evaluate(expr,state)==evaluate(case['target'],state) for state in states)]
                        matches=[letter for letter,indices in case['choices'].items() if indices==correct]
                    else:self.fail('Unknown source-calculation kind')
                self.assertEqual(len(matches),1);self.assertEqual(matches,[review['verification']['independentAnswer']])

    def numeric(self,case):
        args=case['inputs'];op=case['operation'];choices=case['choices']
        if op=='weighted-hit':
            cache,memory,effective=map(Fraction,args);result=(memory-effective)/(memory-cache)
        elif op=='weighted-average':
            miss,hit_time,miss_time=map(Fraction,args);result=(1-miss)*hit_time+miss*miss_time
        elif op=='equal-cache':
            cache_a,memory_a,cache_b,memory_b=map(Fraction,args);result=(memory_b-memory_a)/(memory_b-memory_a+cache_a-cache_b)
            self.assertEqual(result*cache_a+(1-result)*memory_a,result*cache_b+(1-result)*memory_b)
        elif op=='radix-sum':result=sum(radix(*arg) for arg in args)
        elif op=='radix-difference':result=radix(*args[0])-radix(*args[1])
        elif op=='radix-value':result=radix(*args)
        elif op=='shift-add':result=(1<<args[0])+args[1]
        elif op=='find-radix':return [letter for letter,value in choices.items() if evaluate(args[0],{'r':value})]
        elif op=='terminating':
            matches=[]
            for letter,value in choices.items():
                denominator=Fraction(value).denominator
                while (common:=math.gcd(denominator,args[0]))>1:denominator//=common
                if denominator==1:matches.append(letter)
            return matches
        else:self.fail('Unknown numeric operation')
        if 'roundDigits' in case:result=Fraction(str(round(float(result),case['roundDigits'])))
        return [letter for letter,value in choices.items() if (radix(str(value),case['choiceBase']) if 'choiceBase' in case else Fraction(str(value)))==result]

    def test_nested_nand_and_comparisons(self):self.check_group('nand-and-comparisons')
    def test_three_branch_gate_topology(self):self.check_group('three-branches')
    def test_complement_scopes(self):self.check_group('complement-scopes')
    def test_literal_selector_paths(self):self.check_group('selectors')
    def test_fanout_and_two_branch_logic(self):self.check_group('fanout')
    def test_half_adder_columns(self):self.check_group('half-adder')
    def test_alternative_networks_tables_and_conditions(self):self.check_group('networks-and-tables')
    def test_bitwise_remainders_and_divisibility(self):self.check_group('bitwise')
    def test_explicit_weighted_cache_conditions(self):self.check_group('weighted-cache')
    def test_radix_fraction_and_shift_operations(self):self.check_group('radix-and-shift')
    def test_independently_read_definition_choices(self):self.check_group('definitions')

if __name__=='__main__':unittest.main()
