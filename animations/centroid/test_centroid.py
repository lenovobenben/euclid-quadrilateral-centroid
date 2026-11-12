"""Catch display regressions in the circle, text, and transformed geometry."""

import tempfile
import unittest
from unittest.mock import patch

import numpy as np
from manim import Circle, Dot, Text, tempconfig

from centroid import LABEL_OFFSETS, PLOT_BOUNDS, QuadrilateralCentroid, View, load_geometry


class AnimationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        temporary = tempfile.TemporaryDirectory()
        cls.addClassCleanup(temporary.cleanup)
        cls.enterClassContext(tempconfig({
            "media_dir": temporary.name, "dry_run": True, "skip_animations": True,
            "progress_bar": "none", "verbosity": "ERROR", "frame_rate": 60,
            "pixel_width": 1280, "pixel_height": 720,
        }))
        cls.scene = QuadrilateralCentroid()
        cls.text_bounds = []
        cls.circle_fills = []
        original_play = cls.scene.play

        def observe(*args, **kwargs):
            result = original_play(*args, **kwargs)
            for root in cls.scene.mobjects:
                for item in root.get_family():
                    if isinstance(item, Text):
                        cls.text_bounds.append((item.text, item.get_left()[0], item.get_right()[0],
                                                item.get_bottom()[1], item.get_top()[1]))
                    if isinstance(item, Circle) and not isinstance(item, Dot):
                        cls.circle_fills.append(item.get_fill_opacity())
            return result

        with patch.object(cls.scene, "play", new=observe):
            cls.scene.render()

    def test_circle_stays_unfilled_and_in_frame(self):
        self.assertTrue(self.circle_fills)
        self.assertTrue(all(opacity == 0 for opacity in self.circle_fills))
        circle = self.scene.objects["circle"]
        left, right, bottom, top = PLOT_BOUNDS
        self.assertGreater(circle.get_left()[0], left)
        self.assertLess(circle.get_right()[0], right)
        self.assertGreater(circle.get_bottom()[1], bottom)
        self.assertLess(circle.get_top()[1], top)
        center = circle.get_center()
        radius = self.scene.data["circle_radius"] * self.scene.view.scale
        for name in "EIJ":
            point = self.scene.view.at(self.scene.points[name])
            self.assertAlmostEqual(np.linalg.norm(point - center), radius)

    def test_text_and_labels(self):
        for content, left, right, bottom, top in self.text_bounds:
            with self.subTest(content=content):
                self.assertGreaterEqual(left, -7.1)
                self.assertLessEqual(right, 7.1)
                self.assertGreaterEqual(bottom, -3.95)
                self.assertLessEqual(top, 3.95)
        for view in (self.scene.view, View((-0.75, 0.75), (-2.65, 0), 1.6)):
            names = "EMNIJG"
            for name in names:
                label = view.at(self.scene.points[name]) + np.array([*LABEL_OFFSETS[name], 0])
                own_distance = np.linalg.norm(label - view.at(self.scene.points[name]))
                for other in names:
                    if name != other:
                        self.assertLess(own_distance, np.linalg.norm(label - view.at(self.scene.points[other])),
                                        (name, other))

    def test_relations_and_sections(self):
        data, _ = load_geometry()
        points = {name: np.array(point) for name, point in data["points"].items()}
        np.testing.assert_allclose(points["I"], 2 * points["M"] - points["E"])
        np.testing.assert_allclose(points["J"], 2 * points["N"] - points["E"])
        np.testing.assert_allclose(points["G"], (points["E"] + points["I"] + points["J"]) / 3)
        np.testing.assert_allclose(points["G"] - points["V"], (points["V"] - points["E"]) / 3)
        self.assertEqual(len(self.scene.sections), 15)
        starts = [section["start_seconds"] for section in self.scene.sections]
        self.assertEqual(starts, sorted(starts))
        self.assertGreater(self.scene.time, 60)
        self.assertLess(self.scene.time, 70)
        special = data["special_examples"]
        self.assertEqual(special["one_midpoint"]["branch"], "M_equals_E")
        self.assertEqual(special["parallelogram"]["branch"], "parallelogram")


if __name__ == "__main__":
    unittest.main()
