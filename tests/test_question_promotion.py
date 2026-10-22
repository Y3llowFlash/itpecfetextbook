"""Isolated synthetic approval/promotion tests; never change the real public catalog."""
import hashlib
import importlib.util
import json
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
import fitz

ROOT=Path(__file__).resolve().parents[1]
CLI=ROOT/'node_modules/tsx/dist/cli.mjs'

class PromotionTests(unittest.TestCase):
    def fixture(self,root):
        for folder in ['scripts','src/lib','src/content']:
            # Test-only code/content copy; no source PDF folder is copied or enumerated.
            shutil.copytree(ROOT/folder,root/folder)
        (root/'public/data').mkdir(parents=True);(root/'public/questions').mkdir()
        (root/'package.json').write_text('{"type":"module"}')
        (root/'public/data/questions.json').write_text('[]')
        (root/'public/data/import-manifest.json').write_text(json.dumps({'version':1,'policy':'is_published === true','total':0,'sources':[],'duplicatesRemoved':0}))
        concepts=json.loads((root/'src/content/concepts.json').read_text('utf8'));concept=next(c for c in concepts if c['id']=='cache-memory');concept['questionIds']=[];concept['mappingEvidence']=[]
        (root/'src/content/concepts.json').write_text(json.dumps([concept]));(root/'src/content/explanations.json').write_text('[]')
        source=root/'data-sources/historical-pdfs/Technology-01.pdf';source.parent.mkdir(parents=True)
        with fitz.open() as pdf:
            p=pdf.new_page();p.insert_text((50,60),'Q1. Synthetic fixture: what is one plus one?\na) One\nb) Two\nc) Three\nd) Four');p.insert_text((50,780),'Ans: (b)');p.insert_text((450,800),'2020 April');pdf.save(source)
        spec=importlib.util.spec_from_file_location('fixture_import',root/'scripts/historical_questions.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        module.extract();records=module.read_json(module.WORK/'questions.json');record=records[0]
        node=next(n for n in module.read_json(root/'src/content/hardware-toc.json')['nodes'] if n['number']=='3-5-1')
        review={'contentSha256':record['contentSha256'],'verification':{'status':'verified','independentAnswer':'b','method':'calculation','evidence':[{'expression':'1+1','result':2}],'reasoning':['Add the two units.']},'explanation':{'summary':'The sum is two.','steps':['1+1=2'],'takeaway':'Add both units.'},'mapping':{'status':'verified','chapterId':'fe-v1-ch01','sectionId':node['sectionId'],'subsectionId':node['id'],'headingNumber':'3-5-1','conceptId':'cache-memory','evidence':'synthetic test mapping only','reason':'Synthetic fixture only'},'metadata':{'status':'verified','examType':'FE','paper':'AM','subject':'A','evidence':'synthetic fixture only'},'extraction':{'status':'complete','reviewedImages':[a['sha256']for a in record['images']],'imageDescription':'Synthetic one-plus-one question with four choices','optionText':{'a':'One','b':'Two','c':'Three','d':'Four'}}}
        module.write_json(module.WORK/'reviews.json',{record['id']:review})
        return module,records,record

    def run_publisher(self,root,dry=False):
        run=subprocess.run(['node',str(CLI),'scripts/publish-historical-questions.ts']+(['--dry-run']if dry else []),cwd=root,capture_output=True,text=True,encoding='utf8')
        self.assertEqual(run.returncode,0,run.stdout+run.stderr);return run.stdout

    def snapshot(self,root):
        return {str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest()for folder in ['public','src']for p in (root/folder).rglob('*')if p.is_file()}

    def test_unapproved_exclusion_dryrun_new_promotion_and_idempotency(self):
        with tempfile.TemporaryDirectory(prefix='promotion-',dir=ROOT/'.local') as directory:
            root=Path(directory);module,records,record=self.fixture(root)
            self.assertIn('"approvedInputs": 0',self.run_publisher(root,True))
            module.approve(records,record['id'],'synthetic owner fixture')
            before=self.snapshot(root);self.run_publisher(root,True);self.assertEqual(before,self.snapshot(root))
            self.run_publisher(root)
            catalog=json.loads((root/'public/data/questions.json').read_text('utf8'));self.assertEqual(len(catalog),1);self.assertEqual(catalog[0]['id'],record['id']);self.assertEqual(catalog[0]['correctAnswer'],'b')
            self.assertEqual(len(json.loads((root/'src/content/explanations.json').read_text('utf8'))),1)
            before=self.snapshot(root);self.run_publisher(root);self.assertEqual(before,self.snapshot(root))

    def test_duplicate_retains_practice_answer_id_and_explanation(self):
        with tempfile.TemporaryDirectory(prefix='promotion-',dir=ROOT/'.local') as directory:
            root=Path(directory);module,records,record=self.fixture(root);a=record['images'][0]
            q={'id':'2020S-AM-Q001','examId':'2020S_FE_AM','year':2020,'season':'S','number':1,'subject':'A','paper':'AM','correctAnswer':'a','options':['a','b','c','d'],'is_published':True,'image':{'src':'/questions/canonical.webp','sha256':a['sha256'],'width':a['width'],'height':a['height']},'source':{'questionPdf':'original.pdf','pageStart':1,'pageEnd':1},'mapping':{'verified':'preserve me'}}
            (root/'public/data/questions.json').write_text(json.dumps([q]));shutil.copy(module.WORK/a['path'],root/'public/questions/canonical.webp')
            (root/'public/data/import-manifest.json').write_text(json.dumps({'version':1,'policy':'is_published === true','total':1,'sources':[{'published':1}],'duplicatesRemoved':0}))
            explanation=[{'questionId':q['id'],'answer':'a','summary':'Existing authoritative explanation'}];(root/'src/content/explanations.json').write_text(json.dumps(explanation))
            module.approve(records,record['id'],'synthetic owner fixture');self.run_publisher(root)
            catalog=json.loads((root/'public/data/questions.json').read_text('utf8'));self.assertEqual(len(catalog),1)
            self.assertEqual({k:v for k,v in catalog[0].items()if k!='review'},q)
            self.assertEqual(catalog[0]['review']['discrepancies'][0]['printedAnswer'],'b');self.assertEqual(catalog[0]['review']['discrepancies'][0]['authoritativeAnswer'],'a')
            self.assertEqual(json.loads((root/'src/content/explanations.json').read_text('utf8')),explanation)
    def test_new_concept_requires_exact_source_paragraph_and_updates_contents(self):
        with tempfile.TemporaryDirectory(prefix='promotion-',dir=ROOT/'.local') as directory:
            root=Path(directory);module,records,record=self.fixture(root)
            node=next(n for n in module.read_json(root/'src/content/hardware-toc.json')['nodes']if n['number']=='3-5-2')
            html=(root/'src/content/source-hardware/cpu-and-main-memory.html').read_text('utf8');start=html.index('id="'+node['id']+'"')
            match=re.search(r'<p\b([^>]*data-source-kind="paragraph"[^>]*)>([\s\S]*?)</p>',html[start:])
            passage=re.search(r'\bid="([^"]+)"',match.group(1)).group(1)
            reviews=module.read_json(module.WORK/'reviews.json');review=reviews[record['id']]
            review['mapping'].update(headingNumber='3-5-2',subsectionId=node['id'],conceptId='synthetic-reviewed-pipeline',title='Synthetic pipeline fixture',summary='Test fixture only',sourceHighlight={'passageId':passage,'fragmentSha256':hashlib.sha256(match.group(2).encode()).hexdigest()})
            module.write_json(module.WORK/'reviews.json',reviews);module.approve(records,record['id'],'synthetic owner fixture')
            self.run_publisher(root)
            concepts=json.loads((root/'src/content/concepts.json').read_text('utf8'));added=next(c for c in concepts if c['id']=='synthetic-reviewed-pipeline')
            self.assertEqual(added['sourceHighlight']['passageId'],passage)
            contents=json.loads((root/'src/content/hardware-toc.json').read_text('utf8'));self.assertIn(added['id'],next(n for n in contents['nodes']if n['number']=='3-5-2')['conceptIds'])

if __name__=='__main__':unittest.main()
