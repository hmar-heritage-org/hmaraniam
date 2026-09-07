# hmaraniam

**Zero-dependency language identification for Hmar.**

> *"Hmar a ni am?" ("Is it Hmar?")*

`hmaraniam` is a Python library that identifies Hmar text and tells it apart from English and the related Kuki-Chin / Zo languages (Mizo, Paite, Thadou, Vaiphei, Gangte, Zou).

Maintained by the [Hmar Heritage Foundation](https://hmarheritage.pages.dev) as part of the Hmar Heritage Archival Project.

---

## Features

- **Frequency-weighted detection:** Scores each token using corpus log-frequencies (`log(1 + count)`) built from 2 Hmar Bibles and 583 verified web articles, covering 45,042 unigrams. Core structural words like `chu`, `chun`, and `an` score higher than rare or loanword tokens.
- **Dual diacritic scoring:** Reports `casual_hmar_ratio` (ASCII-normalized for QWERTY typing) and `formal_hmar_ratio` (exact diacritic matches).
- **Sibling Zo language resolution:** Separates Mizo, Paite, Thadou, Gangte, Zou, and Vaiphei from Hmar using dialect-exclusive particles and per-language vocabulary lists.
- **Separate confidence scores:** `hmar_confidence` answers "how Hmar is this text?" independently of `detected_language_confidence`, which rates the overall classification call.
- **Consistent output shape:** Every call returns the same dictionary structure, including word counts, frequency-weighted ratios, sibling scores, and diacritic breakdowns.
- **Raw text cleanup:** Strips HTML tags, Markdown syntax (bold, italic, links, code blocks), URLs, and email addresses from pasted input before scoring.
- **Custom vocabulary:** Pass custom unigram sets, extra domain words, or custom stopword lists directly to the `Detector`.
- **Offline first:** Ships with a bundled shard so it works without a network call. CDN sync via jsDelivr is available when you need the latest data.
- **Zero dependencies:** Pure Python standard library. No PyTorch, TensorFlow, NumPy, or spaCy.

---

## Design

`hmaraniam` answers one question: *"Is this text Hmar?"* It does not correct spelling or modify the input.

**Diacritic normalization.** Mobile keyboards produce inconsistent accent codepoints. `casual_hmar_ratio` strips diacritics before matching so `ṭha` and `tha` both score against the same vocabulary entry.

**Token boundaries.** When you need precise control over how a token is defined (for example, whether `mithiem-hai` counts as one word or two), pass a pre-tokenized list. The library will not re-split it. For plain strings, it tokenizes by word boundary.

**Vocabulary, not grammar.** The score reflects dictionary overlap, not sentence structure. A list of valid Hmar words scores the same as a grammatical sentence with the same words.

---

## Installation

```bash
pip install hmaraniam
```

---

## Output schema

```json
{
  "language": "hmar",
  "hmar_confidence": 0.9842,
  "detected_language_confidence": 0.9842,
  "sibling_heuristic": false,
  "mode": "basic",
  "scores": {
    "casual_hmar_ratio": 0.9524,
    "weighted_hmar_ratio": 0.9103,
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
    "sibling_lang_scores": {},
    "hmar_diacritic_words_count": 17,
    "non_hmar_diacritic_words_count": 0,
    "total_diacritic_words_count": 17
  }
}
```

---

## Usage

### Quick start

```python
import hmaraniam

# Authentic text quote from L. Keivom archive (Coleman Factor, 2002)
sample_text = "Khawvel fe dan phung ei en chun, ram le hnam damna thuruk chu lien lema intel le insung khawm, zai khat le trong khata luong khawm a nih."

result = hmaraniam.detect(sample_text)
print(result)
```

### Pre-tokenized inputs

If you need to define token boundaries yourself (for example, to treat `mithiem-hai` as a single token rather than two words), pass a list, JSON file, CSV, or line-delimited TXT. The library scores each entry as-is without re-splitting.

#### Supported formats

1. **JSON array (`tokens.json`):**
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

2. **CSV (`tokens.csv`):**
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

3. **Line-delimited TXT (`tokens.txt`, 1 word per line):**
   ```text
   khawvel
   fe
   dan
   mithiem-hai
   pathien
   hnenah
   ```
   *Usage:* `hmaraniam.detect("tokens.txt")` or CLI `hmaraniam tokens.txt`

4. **Python list:**
   ```python
   tokens = ["mithiem-hai", "pathien", "hnenah", "khawvel"]
   result = hmaraniam.detect(tokens)
   ```

---

### Raw text

Pass a plain string or a `.txt` file path and the library tokenizes it automatically. HTML, Markdown, and URLs are stripped before scoring.

```python
# Raw text string
result = hmaraniam.detect("Khawvel fe dan phung ei en chun, ram le hnam damna thuruk...")

# Raw text file
result = hmaraniam.detect("path/to/article.txt")
```

### Custom unigrams and stopwords

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

### Modes

```python
from hmaraniam import Detector

# Basic mode (default, 45k core unigrams)
basic_detector = Detector(mode="basic")

# High mode (loads extended unigram shards, falls back to basic if unavailable)
high_detector = Detector(mode="high")

# Offline-only (uses cached or bundled data, no network calls)
offline_detector = Detector(offline_only=True)
```

---

## Datasets

- **[Hmar Unigrams (`unigrams`)](https://huggingface.co/datasets/hmar-heritage-org/unigrams):** 58,983 verified Hmar surface words and active loanwords.
- **[Corpus Archive (`corpus-archive`)](https://huggingface.co/datasets/hmar-heritage-org/corpus-archive):** Archival text corpus of Hmar literature and lexicons.

---

## Error handling

`hmaraniam` raises standard Python exceptions:

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

MIT License. Published by the Hmar Heritage Foundation.

---

## Citation

```bibtex
@software{hmaraniam_2026,
  author       = {Hmar Heritage Foundation},
  title        = {hmaraniam: Zero-dependency language identification library for Hmar},
  year         = {2026},
  publisher    = {PyPI / GitHub},
  iso_code     = {hmr},
  glottolog    = {hmar1241},
  clade        = {Zo Languages},
  howpublished = {\url{https://github.com/hmar-heritage-org/hmaraniam}}
}
```
