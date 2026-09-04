# hmaraniam 🇲z

**High-precision, zero-dependency language identification library for Hmar.**

> *"Hmar a ni am?"* — *"Is it Hmar?"*

`hmaraniam` is a lightweight Python library designed to accurately distinguish Hmar text from English and other Kuki-Chin / Zo languages (Mizo, Kuki, Paite, Vaiphei).

---

## Key Features

- **Microsecond Speed:** $O(1)$ dictionary lookups with no heavy ML dependencies (PyTorch/TensorFlow free).
- **Dual-Lens Diacritic Engine:** Reports both `casual_hmar_ratio` (ASCII-normalized for standard QWERTY typing) and `formal_hmar_ratio` (exact diacritic matching for formal literary text).
- **Mathematical Confidence Score:** Returns an empirical, quantitative `confidence_score` between `0.0000` and `1.0000` (incorporating Bayesian document length weighting).
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
  "confidence_score": 0.9452,
  "orthography": "casual_qwerty",
  "mode": "basic",
  "scores": {
    "casual_hmar_ratio": 0.9524,
    "formal_hmar_ratio": 0.8095,
    "english_stopword_ratio": 0.0000,
    "total_words": 21,
    "hmar_words_count": 20,
    "non_hmar_words_count": 1,
    "english_stopwords_count": 0,
    "diacritic_words_count": 1
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
