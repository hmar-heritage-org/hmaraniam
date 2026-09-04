"""
Unit tests for hmaraniam pure string detector engine.
"""

import unittest
from hmaraniam import Detector, detect


class TestHmaraniam(unittest.TestCase):

    def test_hmar_detection_basic(self):
        sample_text = "Tuking chanchinbu a hung suok tlangval a nih. Inpui le Virthli thuthang."
        res = detect(sample_text, mode="basic")
        self.assertEqual(res["language"], "hmar")
        self.assertEqual(res["mode"], "basic")
        self.assertIn(res["confidence"], ["definitely", "likely"])
        self.assertGreater(res["scores"]["hmar_ratio"], 0.5)

    def test_hmar_detection_high_mode(self):
        sample_text = "Tuking chanchinbu a hung suok tlangval a nih. Inpui le Virthli thuthang."
        detector = Detector(mode="high", offline_only=True)
        res = detector.detect(sample_text)
        self.assertEqual(res["language"], "hmar")
        self.assertEqual(res["mode"], "high")

    def test_english_detection(self):
        sample_text = "The quick brown fox jumps over the lazy dog. This is an official notice and document for the public."
        res = detect(sample_text)
        self.assertEqual(res["language"], "english")
        self.assertGreater(res["scores"]["english_stopword_ratio"], 0.03)

    def test_empty_input(self):
        res = detect("")
        self.assertEqual(res["language"], "unknown")
        self.assertEqual(res["confidence"], "uncertain")
        self.assertEqual(res["scores"]["total_words"], 0)

    def test_error_handling(self):
        with self.assertRaises(ValueError):
            Detector(mode="invalid_mode")

        with self.assertRaises(TypeError):
            detect(12345)  # type: ignore

    def test_detector_offline_mode(self):
        detector = Detector(offline_only=True)
        res = detector.detect("Hi Hmar tawng thumal nih.")
        self.assertEqual(res["language"], "hmar")

    def test_detect_paragraphs(self):
        detector = Detector(offline_only=True)
        multi_text = "Hmar thumal hung insuok a nih.\n\nThe official meeting was held yesterday with all representatives present."
        paras = detector.detect_paragraphs(multi_text)
        self.assertEqual(len(paras), 2)
        self.assertEqual(paras[0]["language"], "hmar")
        self.assertEqual(paras[1]["language"], "english")


if __name__ == "__main__":
    unittest.main()
