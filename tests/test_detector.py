"""
Unit tests for hmaraniam pure string detector engine with standardized schema, custom unigrams, and custom stopwords.
"""

import unittest
from hmaraniam import Detector, detect


class TestHmaraniam(unittest.TestCase):

    def test_hmar_detection_basic(self):
        sample_text = "Khawvel fe dan phung ei en chun, ram le hnam damna thuruk chu lien lema intel le insung khawm a nih."
        res = detect(sample_text, mode="basic")
        self.assertEqual(res["language"], "hmar")
        self.assertGreaterEqual(res["confidence_score"], 0.70)
        self.assertIn("casual_hmar_ratio", res["scores"])
        self.assertIn("non_hmar_words_count", res["scores"])
        self.assertEqual(res["scores"]["total_words"], 21)

    def test_hmar_detection_high_mode(self):
        sample_text = "Khawvel fe dan phung ei en chun, ram le hnam damna thuruk chu lien lema intel le insung khawm a nih."
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
        self.assertEqual(res["confidence_score"], 0.0)
        self.assertEqual(res["scores"]["total_words"], 0)
        self.assertEqual(res["scores"]["non_hmar_words_count"], 0)

    def test_custom_unigrams(self):
        custom_detector = Detector(
            mode="basic",
            custom_unigrams=["alpha", "beta", "gamma"],
            disable_default_stopwords=True,
            offline_only=True,
        )
        res = custom_detector.detect("alpha beta gamma alpha")
        self.assertEqual(res["language"], "hmar")
        self.assertEqual(res["scores"]["hmar_words_count"], 4)
        self.assertEqual(res["scores"]["non_hmar_words_count"], 0)

    def test_custom_stopwords(self):
        custom_detector = Detector(
            mode="basic",
            custom_stopwords=["customstopa", "customstopb"],
            offline_only=True,
        )
        res = custom_detector.detect("customstopa customstopb customstopa")
        self.assertGreater(res["scores"]["english_stopwords_count"], 0)

    def test_error_handling(self):
        with self.assertRaises(ValueError):
            Detector(mode="invalid_mode")

        with self.assertRaises(TypeError):
            detect(12345)  # type: ignore

    def test_detect_paragraphs(self):
        detector = Detector(offline_only=True)
        multi_text = "Hmar thumal hung insuok a nih.\n\nThe official meeting was held yesterday with all representatives present."
        paras = detector.detect_paragraphs(multi_text)
        self.assertEqual(len(paras), 2)
        self.assertEqual(paras[0]["language"], "hmar")
        self.assertEqual(paras[1]["language"], "english")


if __name__ == "__main__":
    unittest.main()
