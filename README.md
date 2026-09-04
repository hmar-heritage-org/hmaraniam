# hmaraniam 🇲z

**High-precision, zero-dependency language identification library for Hmar.**

> *"Hmar a ni am?"* — *"Is it Hmar?"*

`hmaraniam` is a lightweight Python library designed to accurately distinguish Hmar text from English and other Kuki-Chin / Zo languages (Mizo, Kuki, Paite, Vaiphei).

---

## Key Features

- **Microsecond Speed:** $O(1)$ dictionary lookups with no heavy ML dependencies (PyTorch/TensorFlow free).
- **Dual Offline/CDN Architecture:** Automatically syncs with the live `hmar-heritage-org/hmaraniam` unigram dataset via jsDelivr CDN, with automatic local disk caching and bundled fallback.
- **Linguistically Aware:** Anchored on a curated 30,600+ surface word Hmar unigram vocabulary and core Hmar grammar particles (`ruokchu`, `popah`, `haiin`, `naw`, `chun`, `tlat`).
- **Granular Classification:** Provides 3-way language labeling (`hmar`, `english`, `other`), confidence ratings (`definitely`, `likely`, `uncertain`), and match ratios.
- **HTML & URL Aware:** Built-in `detect_html()` strips scripts, styles, and tags, while automatically filtering URLs/emails before tokenization.
- **Flexible Detection Modes:** Supports `mode="basic"` (active default core ~30k vocabulary) and `mode="high"` (auto-discovers all extended dataset shards, falling back seamlessly to basic).

---

## Installation

```bash
pip install hmaraniam
```

---

## Usage

### Quick Start

```python
import hmaraniam

result = hmaraniam.detect("Tuking chanchinbu a hung suok tlangval a nih.")

print(result)
# Output:
# {
#     "language": "hmar",
#     "confidence": "definitely",
#     "mode": "basic",
#     "scores": {
#         "hmar_ratio": 0.875,
#         "english_stopword_ratio": 0.0,
#         "total_words": 8,
#         "hmar_matches": 7,
#         "english_stop_matches": 0
#     }
# }
```

### HTML & Web Post Detection

Pass raw HTML strings directly — `hmaraniam` automatically strips scripts, styles, comments, and HTML tags:

```python
import hmaraniam

raw_html = """
<html>
    <body>
        <h1>Tuking Chanchinbu</h1>
        <p>Tuking chanchinbu a hung suok tlangval a nih. https://virthli.in/article/123</p>
    </body>
</html>
"""

result = hmaraniam.detect_html(raw_html)
print(result["language"]) # 'hmar'
```

### File Detection

```python
import hmaraniam

# Automatically detects HTML vs plain text files based on extension
result = hmaraniam.detect_file("article.html")
```

### Paragraph-Level Classification

For multi-paragraph articles or code-switched documents:

```python
from hmaraniam import Detector

detector = Detector()
paragraphs = detector.detect_paragraphs("""
Tuking chanchinbu a hung suok tlangval a nih.

The official statement was released by the committee.
""")

for p in paragraphs:
    print(f"[{p['language'].upper()}] {p['text_snippet']}")
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
    print(e) # "Invalid detection mode 'ultra'. Supported modes are 'basic' (default) and 'high'."

# Raises TypeError for non-string input
try:
    hmaraniam.detect(12345)
except TypeError as e:
    print(e) # "Expected text input to be a string, got int"

# Raises FileNotFoundError for missing files
try:
    hmaraniam.detect_file("non_existent.html")
except FileNotFoundError as e:
    print(e) # "Target file does not exist or is not a valid file: 'non_existent.html'"
```

---

## License

Published under the MIT License by the **Hmar Heritage Project**.
