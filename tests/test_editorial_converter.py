import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from editorial_convert import safe_output,classify_line,math_risk,merge_regions,snap_bounds,boundary_findings
from editorial_validate import Blocks,normalized


class EditorialConverterTests(unittest.TestCase):
    def test_public_and_external_output_paths_are_rejected(self):
        root=Path(__file__).resolve().parents[1]
        for path in [root/'public/editorial',root/'dist',root/'src/content',root.parent/'other']:
            with self.assertRaises(ValueError):safe_output(path)

    def test_math_is_not_guessed_from_undecoded_glyphs(self):
        self.assertEqual(math_risk({'text':'A \uf0d9 B','spans':[]}),'unmapped-special-font-glyph')
        self.assertEqual(math_risk({'text':'x = 2','spans':[]}),'spatial-expression')
        self.assertIsNone(math_risk({'text':'Original paragraph stays complete.','spans':[]}))

    def test_heading_detection_adapts_to_inserted_page_body_size(self):
        base={'text':'A source paragraph','spans':[{'size':14,'start':0,'end':18}],'bodySize':14}
        self.assertEqual(classify_line(base)[0],'paragraph')
        self.assertEqual(classify_line({**base,'text':'1 - 2 Original subsection','bodySize':12}),('heading',3))

    def test_overlapping_figure_pieces_are_one_rendered_assembly(self):
        groups=merge_regions([{'id':'a','bbox':[0,0,100,100]},{'id':'b','bbox':[80,30,140,130]}])
        self.assertEqual(len(groups),1)
        self.assertEqual([r['id'] for r in groups[0]['parts']],['a','b'])

    def test_html_audit_ignores_annotation_count_but_keeps_source_quote(self):
        p=Blocks();p.feed('<p id="source" data-source-block data-source-kind="paragraph">Original <a>source<small aria-label="3 published questions"> ↗ 3</small></a> words.</p>')
        self.assertEqual(normalized(p.blocks['source']['text']),'Original source words.')

    def test_source_object_extending_past_paper_does_not_break_boundary_review(self):
        import fitz
        from types import SimpleNamespace
        page=SimpleNamespace(rect=fitz.Rect(0,0,100,100),get_text=lambda _: [(-4,10,8,20,'label')],get_image_info=lambda: [])
        bounds=snap_bounds(page,[5,8,12,22])
        self.assertEqual(bounds[0],0)
        self.assertEqual(boundary_findings(page,bounds),[])


if __name__=='__main__':unittest.main()
