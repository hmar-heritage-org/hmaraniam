# hmaraniam 🇲z

**High-precision, zero-dependency language identification library for Hmar.**

> *"Hmar a ni am?"* — *"Is it Hmar?"*

`hmaraniam` is a lightweight Python library designed to accurately distinguish Hmar text from English and other Kuki-Chin / Zo languages (Mizo, Kuki, Paite, Vaiphei).

---

## Key Features

- **Microsecond Speed:** $O(1)$ dictionary lookups with no heavy ML dependencies (PyTorch/TensorFlow free).
- **Dual-Lens Diacritic Engine:** Reports both `casual_hmar_ratio` (ASCII-normalized for standard QWERTY typing) and `formal_hmar_ratio` (exact diacritic matching for formal literary text).
- **Dual Continuous Confidence Metrics:** Disambiguates language metrics into `hmar_confidence` (permanent metric answering *"How confident are we that this text is Hmar?"*) and `detected_language_confidence` (confidence in the overall classification choice).
- **Standardized Schema:** Guarantees an immutable JSON output structure across all calls, including `non_hmar_words_count` and `diacritic_words_count`.
- **Extensible & Customizable:** Allows developers to supply `custom_unigrams`, `extra_unigrams`, `custom_stopwords`, or disable default stopwords.
- **Dual Offline/CDN Architecture:** Automatically syncs with the live `hmar-heritage-org/hmaraniam` unigram dataset via jsDelivr CDN, with automatic local disk caching and bundled fallback.

---

## Design Principles

- **Language Identification vs. Spell Correction:** `hmaraniam` objectively evaluates vocabulary identity (*"Is this text Hmar?"*). It is not a spell checker or proofreading tool and does not make opinionated, un-empirical assumptions to "correct" typos, accent slash variations (e.g., acute `á` vs grave `à` vs circumflex `â`), or non-standard mobile keyboard codepoints (e.g. `ṭ` vs `ţ` vs `ț`).
- **ASCII Normalization (`casual_hmar_ratio`) as Universal Ground Truth:** Because mobile keyboards and digital writers output diverse accent/slash codepoints, ASCII normalization (`strip_diacritics`) is the only deterministic, device-agnostic strategy to evaluate vocabulary identity across all platforms without font-dependency risks.
- **Deterministic 1-Token-Per-Row Boundaries:** To avoid engine-level guessing on orthographic variants (e.g. hyphenated `"mithiem-hai"`, spaced `"mithiem hai"`, or compound `"mithiemhai"`), `hmaraniam` natively evaluates 1-token-per-row inputs (JSON, CSV, line-delimited TXT, Python Lists) with zero internal mutation.

---

## Installation

```bash
pip install hmaraniam
```

---

## Standard Output Schema

```json
{
  "language": "hmar",
  "hmar_confidence": 0.9842,
  "detected_language_confidence": 0.9842,
  "mode": "basic",
  "scores": {
    "casual_hmar_ratio": 0.9524,
    "formal_hmar_ratio": 0.8095,
    "english_stopword_ratio": 0.0000,
    "sibling_zo_stopword_ratio": 0.0000,
    "unknown_words_ratio": 0.0476,
    "total_words": 21,
    "hmar_words_count": 20,
    "non_hmar_words_count": 1,
    "unknown_words_count": 1,
    "english_stopwords_count": 0,
    "sibling_zo_stopwords_count": 0,
    "hmar_diacritic_words_count": 17,
    "non_hmar_diacritic_words_count": 0,
    "total_diacritic_words_count": 17
  }
}
```

---

## Usage

### Quick Start

```python
import hmaraniam

# Authentic text quote from L. Keivom archive (Coleman Factor, 2002)
sample_text = "Khawvel fe dan phung ei en chun, ram le hnam damna thuruk chu lien lema intel le insung khawm, zai khat le trong khata luong khawm a nih."

result = hmaraniam.detect(sample_text)
print(result)
```

### Deterministic 1-Token-Per-Row Inputs (Recommended Gold Standard)

For high-precision NLP pipelines where exact token boundaries matter (e.g. distinguishing `"mithiem-hai"` vs `"mithiem hai"` vs `"mithiemhai"`), `hmaraniam` evaluates 1-token-per-row inputs with **zero internal engine guessing or re-tokenization**:

#### Expected File Formats & Code Examples

1. **JSON Array File (`tokens.json`):**
   ```json
   [
     "khawvel",
     "fe",
     "dan",
     "mithiem-hai",
     "pathien",
     "hnenah"
   ]
   ```
   *Usage:* `hmaraniam.detect("tokens.json")` or CLI `hmaraniam tokens.json`

2. **CSV File (`tokens.csv`):**
   ```csv
   token
   khawvel
   fe
   dan
   mithiem-hai
   pathien
   hnenah
   ```
   *Usage:* `hmaraniam.detect("tokens.csv")` or CLI `hmaraniam tokens.csv`

3. **Line-Delimited TXT File (`tokens.txt` - 1 word per line):**
   ```text
   khawvel
   fe
   dan
   mithiem-hai
   pathien
   hnenah
   ```
   *Usage:* `hmaraniam.detect("tokens.txt")` or CLI `hmaraniam tokens.txt`

4. **Python List (`List[str]`):**
   ```python
   tokens = ["mithiem-hai", "pathien", "hnenah", "khawvel"]
   result = hmaraniam.detect(tokens)
   ```

---

### Non-Parsed Raw Text Documents (Convenience Fallback)

For un-tokenized prose, web articles, or raw string inputs (`article.txt`, raw text string, or stdin pipe), `hmaraniam` automatically extracts word tokens using basic word-boundary regex matching:

```python
# Raw text string evaluation
result = hmaraniam.detect("Khawvel fe dan phung ei en chun, ram le hnam damna thuruk...")

# Raw text article file evaluation
result = hmaraniam.detect("path/to/article.txt")
```

### Custom Unigrams & Stopwords

```python
from hmaraniam import Detector

# Provide custom unigrams or extra domain vocabulary
detector = Detector(
    mode="basic",
    extra_unigrams=["customworda", "customwordb"],
    custom_stopwords=["and", "the", "with"],
    disable_default_stopwords=False
)

result = detector.detect("Khawvel fe dan phung...")
```

### Modes & Advanced Options

```python
from hmaraniam import Detector

# Basic Mode (Active default ~30k core unigrams)
basic_detector = Detector(mode="basic")

# High Mode (Scans data/shards/ and loads all available unigram shards, falling back seamlessly to basic)
high_detector = Detector(mode="high")

# Offline-only mode (uses cached/bundled dataset without network calls)
offline_detector = Detector(offline_only=True)
```

---

## Empirical Benchmarks & Performance

`hmaraniam` has been empirically validated across both **controlled parallel corpus datasets** (Parallel Zo Bibles across multiple literary genres) and **unfiltered real-world web archives** (~1,300 scraped articles and raw HTML pages across 5 major publishers).

### 1. Controlled Parallel Zo Bible Benchmark

Evaluated across parallel chapters (Genesis 1, Exodus 20, Matthew 5, Luke 2, Romans 8, Revelation 21) across 10 parallel Bible translations in 8 Zo languages + English:

| Language | Edition / Source | Evaluated Passages | Target Class | Engine Assigned Label | Classification Accuracy | Avg Hmar Confidence | Key Distinguishing Metrics |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| **Hmar** | CLB (Contemporary) | Gen 1, Ex 20, Matt 5, Luke 2, Rom 8, Rev 21 | `hmar` | `hmar` | **100%** | **1.0000** | `casual_hmar_ratio` $\ge 0.95$, `unknown_words_ratio` $\le 0.05$ |
| **Hmar** | OV (Old Version) | Gen 1, Ex 20, Matt 5, Luke 2, Rom 8, Rev 21 | `hmar` | `hmar` | **100%** | **1.0000** | Formal diacritic match + `hmar_diacritic_words_count` $>0$ |
| **Mizo** | OV (Mizo Bible) | Gen 1, Ex 20, Matt 5, Luke 2, Rom 8, Rev 21 | `other` | `other` | **100%** | **0.0000** | `sibling_zo_stopwords` (`pathian`, `hnenah`, `avangin`, `tichuan`) & `unknown_words_ratio` ($\approx 24\%$) |
| **Paite** | Paite Bible | Gen 1, Ex 20, Matt 5, Luke 2, Rom 8, Rev 21 | `other` | `other` | **100%** | **0.0000** | `sibling_zo_stopwords` (`pasian`, `tungah`, `simhuai`) & `unknown_words_ratio` ($\approx 51\%$) |
| **Vaiphei** | Vaiphei Bible | Gen 1, Ex 20, Matt 5, Luke 2, Rom 8, Rev 21 | `other` | `other` | **100%** | **0.0000** | `sibling_zo_stopwords` (`pathian`, `tiu-in`, `apat`) & `unknown_words_ratio` ($\approx 38\%$) |
| **Gangte** | Gangte Bible | Gen 1, Ex 20, Matt 5, Luke 2, Rom 8, Rev 21 | `other` | `other` | **100%** | **0.0000** | `sibling_zo_stopwords` (`pathen`, `hepa`, `dih-in`) & `unknown_words_ratio` ($\approx 40\%$) |
| **Zou** | Zou Bible | Gen 1, Ex 20, Matt 5, Luke 2, Rom 8, Rev 21 | `other` | `other` | **100%** | **0.0000** | `sibling_zo_stopwords` (`pasian`, `a-in`, `leh-in`) & `unknown_words_ratio` ($\approx 51\%$) |
| **Thadou** | Thadou-Kuki Bible | Gen 1, Ex 20, Matt 5, Luke 2, Rom 8, Rev 21 | `other` | `other` | **100%** | **0.0000** | `sibling_zo_stopwords` (`pathen`, `chun`, `tichun`) & `unknown_words_ratio` ($\approx 67\%$) |
| **English** | WEB (World English) | Gen 1, Ex 20, Matt 5, Luke 2, Rom 8, Rev 21 | `english` | `english` | **100%** | **0.0000** | `english_stopword_ratio` ($>0.08$) & `unknown_words_ratio` ($>0.70$) |

> **Cognate Resolution:** Closely related sibling languages like Mizo share up to 78% unigram overlap with Hmar. `hmaraniam` cleanly resolves sibling Zo languages without requiring massive full dictionaries by combining vocabulary completeness (`unknown_words_ratio` $\le 0.18$) with curated structural markers (`sibling_zo_stopwords`).

---

### 2. Real-World Web Archive Benchmark (~1,300 Scraped Documents)

Evaluated on real-world scraped web archives across 5 major Hmar/Zo web publishers:

| Publisher Web Archive | Corpus Source / Format | Evaluated Items | Hmar Posts Detected (%) | English Posts Detected (%) | Other / Mixed Posts (%) | Avg Hmar Confidence | Mean Casual Hmar Ratio | Mean Formal Hmar Ratio | Mean Unknown Words Ratio | Primary Content Profile |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **L. Keivom Archive** (`keivom`) | Blogger API JSON | 300 | **199 (66.3%)** | 32 (10.7%) | 69 (23.0%) | **0.8320** | **79.3%** | 70.0% | 20.7% | Authentic Hmar literary essays & prose |
| **Inpui Journal** (`inpui`) | Blogger API JSON | 291 | **124 (42.6%)** | 67 (23.0%) | 100 (34.4%) | **0.7400** | **63.7%** | 55.7% | 36.3% | Bilingual news journal & opinion pieces |
| **HSA Portal** (`hsa`) | WordPress API JSON | 177 | **23 (13.0%)** | 38 (21.5%) | **116 (65.5%)** | 0.5730 | **53.7%** | 46.7% | 46.3% | Student association alerts & mixed posts |
| **Hmarram.com** (`hmarram`) | WordPress API JSON | 235 | 12 (5.1%) | **209 (88.9%)** | 14 (6.0%) | 0.7762 | 31.2% | 23.8% | 68.8% | Tech articles & English press releases |
| **Virthli News** (`virthli`) | Scraped Raw HTML | 296 | 5 (1.7%) | **267 (90.2%)** | 24 (8.1%) | 0.8721 | 17.6% | 13.4% | 82.4% | Employment alerts & exam guidelines |

- **Literary Archives:** Archives like L. Keivom and Inpui Journal feature rich Hmar prose and opinion articles, achieving high Hmar classification rates ($42.6\% - 66.3\%$) and high token ratios ($63.7\% - 79.3\%$).
- **Community News & Recruitment Notices:** Community portals like Hmarram and Virthli publish predominantly in English (recruitment notices, exam guidelines, press statements). `hmaraniam` accurately tags these as `"english"` or `"other"` without false-positive over-classification.

---

## Error Handling

`hmaraniam` provides clear, descriptive error messages:

```python
import hmaraniam

# Raises ValueError for unsupported modes
try:
    hmaraniam.detect("Text", mode="ultra")
except ValueError as e:
    print(e)

# Raises TypeError for non-string input
try:
    hmaraniam.detect(12345)
except TypeError as e:
    print(e)
```

---

## License

Published under the MIT License by the **Hmar Heritage Project**.

