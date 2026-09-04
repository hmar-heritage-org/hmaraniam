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

# Authentic text from L. Keivom archive
sample_text = "Khawvel fe dan phung ei en chun, ram le hnam damna thuruk chu lien lema intel le insung khawm a nih."

result = hmaraniam.detect(sample_text)

print(result)
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

`hmaraniam` has been empirically evaluated across both **controlled parallel corpus datasets** (Parallel Zo Bibles across multiple genres) and **unfiltered real-world web archives** (~1,300 scraped articles and raw HTML pages across 5 major publishers).

### 1. Parallel Zo Bible Benchmark (Controlled Parallel Test)

Evaluated across parallel chapters (Genesis 1, Exodus 20, Matthew 5, Luke 2, Romans 8, Revelation 21) across 10 parallel Bible translations in 8 Zo languages + English:

| Language / Translation | Sample Corpus | Assigned Class | Precision / Accuracy | Avg Hmar Confidence | Sibling Zo Marker Match |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **Hmar** (CLB & OV) | Contemporary & Old Versions | `hmar` | **100%** | **1.0000** | 0.0000 |
| **English** (WEB) | World English Bible | `english` | **100%** | 0.0000 | 0.0000 |
| **Mizo** (OV) | Mizo Bible | `other` | **100%** | 0.0000 | High (`pathian`, `hnenah`, `avangin`) |
| **Paite** | Paite Bible | `other` | **100%** | 0.0000 | High (`pasian`, `tungah`) |
| **Vaiphei** | Vaiphei Bible | `other` | **100%** | 0.0000 | High (`pathian`, `tiu-in`) |
| **Gangte** | Gangte Bible | `other` | **100%** | 0.0000 | High (`pathen`, `hepa`) |
| **Zou** | Zou Bible | `other` | **100%** | 0.0000 | High (`pasian`, `a-in`) |
| **Thadou** | Thadou-Kuki Bible | `other` | **100%** | 0.0000 | High (`pathen`, `chun`) |

> **Cognate Separation:** Closely related sibling languages like Mizo share up to 78% unigram overlap with Hmar. `hmaraniam` cleanly separates sibling Zo languages using vocabulary completeness (`unknown_words_ratio` $\le 0.18$) and curated `sibling_zo_stopwords`.

---

### 2. Real-World Web Archive Benchmark (Scraped Web Data)

Evaluated on ~1,300 real-world scraped web documents across 5 major Hmar/Zo web publishers:

| Publisher Archive | Evaluated Items | Hmar Detected % | English Detected % | Other / Mixed % | Avg Hmar Confidence | Mean Casual Hmar Ratio |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **L. Keivom Archive** (`keivom`) | 300 | **66.3%** (199) | 10.7% (32) | 23.0% (69) | **0.8320** | **79.3%** |
| **Inpui Journal** (`inpui`) | 291 | **42.6%** (124) | 23.0% (67) | 34.4% (100) | **0.7400** | **63.7%** |
| **HSA Portal** (`hsa`) | 177 | **13.0%** (23) | 21.5% (38) | **65.5%** (116) | 0.5730 | **53.7%** |
| **Hmarram.com** (`hmarram`) | 235 | 5.1% (12) | **88.9%** (209) | 6.0% (14) | 0.7762 | 31.2% |
| **Virthli News** (`virthli`) | 296 | 1.7% (5) | **90.2%** (267) | 8.1% (24) | 0.8721 | 17.6% |

- **Literary Archives:** Archives like L. Keivom and Inpui Journal consist of authentic Hmar prose, essays, and opinion pieces, achieving high Hmar detection rates ($42.6\% - 66.3\%$) and strong token ratios ($63.7\% - 79.3\%$).
- **Community News & Job Alerts:** Community portals like Hmarram and Virthli publish heavily in English (recruitment alerts, exam guidelines, press releases). `hmaraniam` accurately tags these as `"english"` or `"other"` without false-positive over-classification.

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

