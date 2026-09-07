"""
Unit tests for hmaraniam pure string/token detector engine.
"""

import unittest
import unicodedata
from hmaraniam import Detector, detect


class TestHmaraniam(unittest.TestCase):

    def test_hmar_detection_basic(self):
        sample_text = "Khawvel fe dan phung ei en chun, ram le hnam damna thuruk chu lien lema intel le insung khawm, zai khat le trong khata luong khawm a nih."
        res = detect(sample_text, mode="basic")
        self.assertEqual(res["language"], "hmar")
        self.assertGreaterEqual(res["hmar_confidence"], 0.70)
        self.assertGreaterEqual(res["detected_language_confidence"], 0.70)
        self.assertIn("casual_hmar_ratio", res["scores"])
        self.assertIn("formal_hmar_ratio", res["scores"])
        self.assertIn("non_hmar_words_count", res["scores"])

    def test_formal_diacritic_scores(self):
        sample_text = "Khawvel fe dan phung ei en chun, Pathien a ṭha â, thil lien le mawi a thaw a nih."
        res = detect(sample_text)
        self.assertEqual(res["language"], "hmar")
        self.assertGreater(res["scores"]["hmar_diacritic_words_count"], 0)
        self.assertEqual(res["scores"]["non_hmar_diacritic_words_count"], 0)
        self.assertGreater(res["scores"]["total_diacritic_words_count"], 0)
        self.assertGreater(res["scores"]["formal_hmar_ratio"], 0.0)

    def test_nfd_unicode_diacritics(self):
        sample_text_nfd = unicodedata.normalize("NFD", "Khawvel fe dan phung ei en chun, Pathien a ṭha â, thil lien le mawi a thaw a nih.")
        res = detect(sample_text_nfd)
        self.assertEqual(res["language"], "hmar")
        self.assertGreater(res["scores"]["hmar_diacritic_words_count"], 0)
        self.assertEqual(res["scores"]["non_hmar_diacritic_words_count"], 0)

    def test_non_hmar_diacritic_isolation(self):
        # "rôle" and "château" are French words with circumflexes, NOT Hmar words
        sample_text = "This official document details the rôle and status of the château for all members."
        res = detect(sample_text)
        self.assertEqual(res["language"], "english")
        # Ensure non-Hmar diacritic words are separated into non_hmar_diacritic_words_count
        self.assertEqual(res["scores"]["hmar_diacritic_words_count"], 0)
        self.assertEqual(res["scores"]["non_hmar_diacritic_words_count"], 2)
        self.assertEqual(res["scores"]["total_diacritic_words_count"], 2)

    def test_pre_tokenized_list_input(self):
        # 1 word per item in pre-tokenized list (evaluated "as is")
        tokens = ["khawvel", "fe", "dan", "phung", "ei", "en", "chun"]
        res = detect(tokens)
        self.assertEqual(res["language"], "hmar")
        self.assertEqual(res["scores"]["total_words"], 7)
        self.assertEqual(res["scores"]["hmar_words_count"], 7)
        self.assertEqual(res["scores"]["non_hmar_words_count"], 0)

    def test_hmar_detection_high_mode(self):
        sample_text = "Khawvel fe dan phung ei en chun, ram le hnam damna thuruk chu lien lema intel le insung khawm, zai khat le trong khata luong khawm a nih."
        detector = Detector(mode="high", offline_only=True)
        res = detector.detect(sample_text)
        self.assertEqual(res["language"], "hmar")
        self.assertGreaterEqual(res["hmar_confidence"], 0.70)

    def test_english_detection(self):
        sample_text = "The quick brown fox jumps over the lazy dog. This is an official notice and document for the public."
        res = detect(sample_text)
        self.assertEqual(res["language"], "english")
        self.assertGreater(res["scores"]["english_stopword_ratio"], 0.03)
        self.assertGreater(res["detected_language_confidence"], 0.50)
        self.assertLess(res["hmar_confidence"], 0.20)

    def test_empty_input(self):
        res = detect("")
        self.assertEqual(res["language"], "unknown")
        self.assertEqual(res["hmar_confidence"], 0.0)
        self.assertEqual(res["detected_language_confidence"], 0.0)
        self.assertEqual(res["scores"]["total_words"], 0)

    def test_custom_unigrams(self):
        custom_detector = Detector(
            mode="basic",
            custom_unigrams=["alpha", "beta", "gamma"],
            disable_default_stopwords=True,
            offline_only=True,
        )
        res = custom_detector.detect(["alpha", "beta", "gamma", "alpha"])
        self.assertEqual(res["language"], "hmar")
        self.assertEqual(res["scores"]["hmar_words_count"], 4)

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

    def test_hyphenated_token_preservation(self):
        # Verify hyphenated tokens like 'mithiem-hai' are preserved as single tokens
        tokens = ["mithiem-hai", "pathien", "hnenah", "khawvel"]
        res = detect(tokens)
        self.assertEqual(res["scores"]["total_words"], 4)

    def test_deterministic_file_token_inputs(self):
        import tempfile
        import json
        from pathlib import Path
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            
            # JSON array file
            json_file = tmppath / "tokens.json"
            with open(json_file, "w", encoding="utf-8") as f:
                json.dump(["khawvel", "fe", "dan", "phung", "ei", "en", "chun"], f)
            res_json = detect(json_file)
            self.assertEqual(res_json["language"], "hmar")
            self.assertEqual(res_json["scores"]["total_words"], 7)

            # TXT line-delimited file (1 token per row)
            txt_file = tmppath / "tokens.txt"
            with open(txt_file, "w", encoding="utf-8") as f:
                f.write("khawvel\nfe\ndan\nphung\nei\nen\nchun\n")
            res_txt = detect(txt_file)
            self.assertEqual(res_txt["language"], "hmar")
            self.assertEqual(res_txt["scores"]["total_words"], 7)

    def test_slash_inputs_handling(self):
        # Raw text with URLs, dates, and slash choices should not crash with FileNotFoundError
        raw_text = "Khawvel fe dan / thuruk on 23/04/2005 and/or visit https://hmarheritage.org"
        res = detect(raw_text)
        self.assertIn(res["language"], ["hmar", "english", "other"])
        self.assertGreater(res["scores"]["total_words"], 0)

    def test_result_schema_completeness(self):
        # Both empty and non-empty results must have identical score key sets
        res_empty = detect("")
        res_normal = detect("Khawvel fe dan phung ei en chun")
        self.assertEqual(
            sorted(res_empty["scores"].keys()),
            sorted(res_normal["scores"].keys()),
            "Empty result schema does not match normal result schema"
        )
        # Both must contain the frequency-weighted ratio key
        self.assertIn("weighted_hmar_ratio", res_empty["scores"])
        self.assertIn("weighted_hmar_ratio", res_normal["scores"])
        # Both must contain sibling_lang_scores
        self.assertIn("sibling_lang_scores", res_empty["scores"])
        self.assertIn("sibling_lang_scores", res_normal["scores"])
        # Both must contain hmar stopword keys
        self.assertIn("hmar_stopword_ratio", res_empty["scores"])
        self.assertIn("hmar_stopword_ratio", res_normal["scores"])
        self.assertIn("hmar_stopwords_count", res_empty["scores"])
        self.assertIn("hmar_stopwords_count", res_normal["scores"])

    def test_whitespace_only_input(self):
        # Whitespace-only strings should behave identically to empty string
        for ws in ["   ", "\t", "\n\n\n", "  \t  \n  "]:
            res = detect(ws)
            self.assertEqual(res["language"], "unknown")
            self.assertEqual(res["scores"]["total_words"], 0)
            self.assertEqual(res["hmar_confidence"], 0.0)

    def test_single_word_input(self):
        # Single known Hmar word: should be hmar with low (short-text) confidence
        res = detect("khawvel")
        self.assertEqual(res["language"], "hmar")
        self.assertGreater(res["hmar_confidence"], 0.0)
        self.assertEqual(res["scores"]["total_words"], 1)
        self.assertEqual(res["scores"]["hmar_words_count"], 1)

    def test_sibling_language_detection(self):
        # Mizo — dense exclusive particle markers (avangin, chutichuan, hnenah, buatsaih)
        mizo_text = "Avangin chutichuan Pathian hnenah buatsaih rawh."
        res_mizo = detect(mizo_text)
        self.assertEqual(res_mizo["language"], "mizo")
        self.assertLess(res_mizo["hmar_confidence"], 0.30)

        # Paite — clear exclusive particle markers (pasian, ahi, toupa, ajehchu)
        paite_text = "Pasian vualzawlna chu ahi, toupa ajehchu om ta hen."
        res_paite = detect(paite_text)
        self.assertEqual(res_paite["language"], "paite")
        self.assertLess(res_paite["hmar_confidence"], 0.30)

    def test_html_sanitization(self):
        # HTML-wrapped Hmar text should correctly detect as hmar
        html_text = "<p><b>Pathien</b> a ṭha â, <em>khawvel fe dan</em> phung ei en chun.</p>"
        res = detect(html_text)
        self.assertEqual(res["language"], "hmar")
        self.assertGreater(res["hmar_confidence"], 0.0)

    def test_markdown_sanitization(self):
        # Markdown bold/italic/link syntax should not eat Hmar word tokens
        md_text = "_Pathien_ le **khawvel** fe [dan phung](https://hmar.org) ei en chun."
        res = detect(md_text)
        self.assertEqual(res["language"], "hmar")
        # Pathien and khawvel must still be counted — total words should include them
        self.assertGreaterEqual(res["scores"]["hmar_words_count"], 4)

    def test_weighted_hmar_ratio_scaling(self):
        # High-frequency core Hmar text should score high weighted ratio
        hmar_text = "Khawvel fe dan phung ei en chun, ram le hnam damna thuruk chu lien a nih."
        res = detect(hmar_text)
        self.assertGreater(res["scores"]["weighted_hmar_ratio"], 0.50)

        # Pure English text should score near-zero weighted ratio
        eng_text = "The quick brown fox jumps over the lazy dog and never looks back."
        res_eng = detect(eng_text)
        self.assertLess(res_eng["scores"]["weighted_hmar_ratio"], 0.40)

    def test_mizo_article_discrimination(self):
        # Long-form Mizo text with high cognate overlap must cleanly detect as mizo with 0% Hmar confidence
        mizo_article = (
            "Tunlai khawvel hmasawnna leh changkannain a ken tel internet leh social media-te hi "
            "mi tu pawhin kan hmang nasa tawh em em a; heng hian kan chhungte, thiante, thawhpuite "
            "leh hmelhriat dangte nena kan inlaichin danah nghawng a nei nasa hle tih pawh kan hre "
            "theuh awm e. Kan pi leh pu ten an lo suangtuah thiam phak bakin kan nunphung a inthlak a, "
            "kan rilru put hmang leh khawvel thlir dan pawh nasa takin a inher danglam tawh bawk."
        )
        res = detect(mizo_article)
        self.assertEqual(res["language"], "mizo")
        self.assertEqual(res["hmar_confidence"], 0.0)
        self.assertGreaterEqual(res["detected_language_confidence"], 0.90)
    def test_contemporary_hmar_discrimination(self):
        # Contemporary Hmar text with loanwords / modern spelling must remain 100% Hmar
        sample1 = (
            "Ka nu chu March 10, 2025, zantieng khan a boral a. "
            "Ka unauhai ta dinga sek taka ka um a ngai ti ka hriet leiin ka sûn ve naw ni awm takkin "
            "sek tak chun ka um a. A hmangaitu tamtak inhuoltu neia thi ani a."
        )
        res1 = detect(sample1)
        self.assertEqual(res1["language"], "hmar")
        self.assertGreaterEqual(res1["hmar_confidence"], 0.85)
        self.assertFalse(res1["sibling_heuristic"])

        sample2 = (
            "Hi a chunga tiengbik hai hi Hmar ṭawng in ei inlet chun andik thei ta nawh asanchu "
            "Sak le Thlang hi changtieng le vawitieng, an um tak leiin. "
            "Leihnuoi hin nghat dan bik aneia, nuomthu a map hai va hem danglam kha thil thei an naw a."
        )
        res2 = detect(sample2)
        self.assertEqual(res2["language"], "hmar")
        self.assertGreaterEqual(res2["hmar_confidence"], 0.85)
        self.assertFalse(res2["sibling_heuristic"])


if __name__ == "__main__":
    unittest.main()

