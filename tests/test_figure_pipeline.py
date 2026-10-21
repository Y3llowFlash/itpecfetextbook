"""Pipeline edge checks, without creating a PDF or depending on the source archive."""
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
import fitz
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from figures import boundary_findings, snap_bounds, render


def page(words=(), images=()):
    return SimpleNamespace(rect=fitz.Rect(0, 0, 600, 840),
                           get_text=lambda _: words,
                           get_image_info=lambda: [{'bbox': b} for b in images])


class FigurePipelineTests(unittest.TestCase):
    def test_severed_caption_is_reported(self):
        source = page([(20, 20, 100, 40, 'caption')])
        self.assertEqual(len(boundary_findings(source, [30, 15, 120, 50])), 1)

    def test_fragmented_connector_is_reported(self):
        source = page(images=[(20, 20, 80, 80)])
        self.assertEqual(boundary_findings(source, [40, 0, 100, 100])[0][1], 'image/connector')

    def test_suggestion_expands_instead_of_cutting_label_and_connector(self):
        source = page([(20, 20, 100, 40, 'caption')], [(90, 30, 160, 65)])
        crop = snap_bounds(source, [30, 15, 120, 50])
        self.assertLess(crop[0], 20)
        self.assertGreater(crop[2], 160)
        self.assertEqual(boundary_findings(source, crop), [])

    def test_complete_region_is_unchanged(self):
        source = page([(30, 30, 100, 50, 'label')])
        self.assertEqual(snap_bounds(source, [20, 20, 120, 60]), [20, 20, 120, 60])

    def test_render_rejects_outside_or_empty_crop_before_any_export(self):
        for crop in [[-1, 20, 40, 60], [0, 0, 0, 1], [0, 0, 700, 840]]:
            with self.assertRaises(ValueError):
                render([page()], 1, Path('.local/should-not-exist.png'), crop=crop)


if __name__ == '__main__':
    unittest.main()
