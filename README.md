# hmaraniam 🇲z

**Zero-dependency language identification library for Hmar.**

> *"Hmar a ni am?"* — *"Is it Hmar?"*

`hmaraniam` is a lightweight, zero-dependency Python library that identifies Hmar text and cleanly distinguishes it from English and related Kuki-Chin / Zo languages (Mizo, Paite, Thadou, Vaiphei, Gangte, Zou).

Maintained by the [Hmar Heritage Foundation](https://hmarheritage.pages.dev) as part of the Hmar Heritage Archival Project.

---

## Features

- **Fast dictionary lookups:** Uses $O(1)$ set matching backed by **36,510 verified pure Hmar unigrams** with no machine learning dependencies (PyTorch and TensorFlow free).
- **Dual diacritic scoring:** Reports `casual_hmar_ratio` (ASCII-normalized for standard QWERTY typing) and `formal_hmar_ratio` (exact diacritic matches for formal text).
- **Specific Sibling Language Resolution:** Distinguishes sibling Zo languages (`mizo`, `paite`, `thadou`, `gangte`, `zou`, `vaiphei`) using dialect-exclusive particles and exclusive vocabulary sets.
- **Separate confidence scores:** Separates overall classification confidence (`detected_language_confidence`) from Hmar-specific confidence (`hmar_confidence`).
- **Consistent JSON output:** Returns the same dictionary structure for every call, including word counts, sibling scores, and diacritic breakdowns.
- **Custom unigrams & stopwords:** Pass custom unigram sets, extra domain vocabulary, or custom stopword lists.
- **Offline & CDN dataset loading:** Syncs unigram sets via jsDelivr CDN with local disk caching and bundled offline fallbacks.

---

## Design Principles

- **Language ID vs. Spell Correction:** `hmaraniam` measures vocabulary identity (*"Is this text Hmar?"*). It is not a spell checker and does not modify typos, character variants (acute `á`, grave `à`, circumflex `â`), or mobile keyboard codepoints (`ṭ` vs `ţ`).
- **ASCII Normalization (`casual_hmar_ratio`):** Mobile keyboards produce varying accent codepoints. Stripping diacritics (`strip_diacritics`) allows consistent vocabulary evaluation across devices.
- **1-Token-Per-Row Boundaries:** To evaluate hyphenated (`mithiem-hai`), spaced (`mithiem hai`), or compound (`mithiemhai`) terms directly, `hmaraniam` accepts 1-token-per-row inputs (JSON, CSV, TXT, Python lists) without re-tokenizing.
- **Vocabulary Identity vs. Grammar:** `hmaraniam` measures dictionary presence and token overlap, not syntax or semantics. A random sequence of valid Hmar words yields a high vocabulary score regardless of grammatical structure.

---

## Installation

```bash
pip install hmaraniam
```

---

## Output Schema

```json
{
  "language": "hmar",
  "hmar_confidence": 0.9842,
  "detected_language_confidence": 0.9842,
  "sibling_heuristic": false,
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
    "sibling_lang_scores": {},
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

### 1-Token-Per-Row Inputs

When token boundaries are pre-defined (such as distinguishing `"mithiem-hai"` vs `"mithiem hai"` vs `"mithiemhai"`), `hmaraniam` evaluates 1-token-per-row inputs without internal re-tokenization:

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

### Un-tokenized Raw Text Documents

For raw text files or strings (`article.txt`, raw text string, or stdin pipe), `hmaraniam` extracts word tokens using word-boundary regex matching:

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

# Basic Mode (Default ~30k core unigrams)
basic_detector = Detector(mode="basic")

# High Mode (Loads extended unigram shards, falling back to basic if unavailable)
high_detector = Detector(mode="high")

# Offline-only mode (uses cached or bundled dataset without network calls)
offline_detector = Detector(offline_only=True)
```

---

## Benchmarks & Evaluation

### 1. Parallel Zo Bible Passages

Evaluated across parallel chapters (Genesis 1, Exodus 20, Matthew 5, Luke 2, Romans 8, Revelation 21) across 10 Bible translations in 8 Zo languages + English:

| Language | Edition / Source | Target Class | Engine Assigned Label | Classification Accuracy | Avg Hmar Confidence | Key Distinguishing Metrics |
| :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| **Hmar** | CLB (Contemporary) | `hmar` | `hmar` | **100%** | **1.0000** | `casual_hmar_ratio` $\ge 0.94$, `unknown_words_ratio` $\le 0.06$ |
| **Hmar** | OV (Old Version) | `hmar` | `hmar` | **100%** | **1.0000** | Formal diacritic match + `hmar_diacritic_words_count` $>0$ |
| **English** | WEB (World English) | `english` | `english` | **100%** | **0.0000** | `english_stopword_ratio` ($>0.08$) & `unknown_words_ratio` ($>0.70$) |
| **Mizo** | CLB / OV (Mizo Bibles) | `mizo` | `mizo` | **100%** | **0.4861** | Matched Mizo exclusive particles (`pathian`, `hnenah`, `avangin`, `tichuan`) |
| **Paite** | Paite Bible (BSI) | `paite` | `paite` | **100%** | **0.0000** | Matched Paite exclusive particles (`pasian`, `toupa`, `kipat`) & 13.3k exclusive words |
| **Thadou** | Thadou-Kuki Bible | `thadou` | `thadou` | **100%** | **0.0000** | Matched Thadou exclusive particles (`pathen`, `hiche`, `hinanleh`) & 47.2k exclusive words |

> **Cognate Resolution:** Related Zo languages like Mizo share up to 74% vocabulary overlap with Hmar. `hmaraniam` separates sibling Zo languages by combining vocabulary coverage thresholds with dialect-exclusive structural particles and exclusive wordlists.

---

### 2. Web Archive Evaluation (~1,300 Documents)

Evaluated on scraped web documents from 5 Hmar/Zo web publishers:

| Publisher Web Archive | Corpus Source / Format | Evaluated Items | Hmar Posts (%) | English Posts (%) | Other / Mixed Posts (%) | Avg Hmar Confidence | Mean Casual Hmar Ratio | Mean Formal Hmar Ratio | Mean Unknown Words Ratio | Primary Content Profile |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **L. Keivom Archive** (`keivom`) | Blogger API JSON | 300 | **192 (64.0%)** | 32 (10.7%) | 76 (25.3%) | **0.8220** | **78.8%** | 69.5% | 21.2% | Hmar literary essays & prose |
| **Inpui Journal** (`inpui`) | Blogger API JSON | 291 | **120 (41.2%)** | 66 (22.7%) | 105 (36.1%) | **0.7357** | **63.5%** | 55.6% | 36.5% | Bilingual news journal & opinion pieces |
| **HSA Portal** (`hsa`) | WordPress API JSON | 177 | **23 (13.0%)** | 38 (21.5%) | **116 (65.5%)** | 0.5679 | **53.5%** | 46.5% | 46.5% | Student association alerts & mixed posts |
| **Hmarram.com** (`hmarram`) | WordPress API JSON | 235 | 12 (5.1%) | **209 (88.9%)** | 14 (6.0%) | 0.7658 | 31.0% | 23.7% | 69.0% | Tech articles & English press releases |
| **Virthli News** (`virthli`) | Scraped Raw HTML | 296 | 5 (1.7%) | **267 (90.2%)** | 24 (8.1%) | 0.8694 | 17.4% | 13.2% | 82.6% | Employment alerts & exam guidelines |

---

## Datasets & Repositories

- **[Hmar Unigrams Dataset (`unigrams`)](https://huggingface.co/datasets/hmar-heritage-org/unigrams):** 59,137 verified Hmar surface words and active loanwords generated via `hmaraniam`'s extraction pipeline.
- **[Corpus Archive (`corpus-archive`)](https://huggingface.co/datasets/hmar-heritage-org/corpus-archive):** Archival text corpus preserving Hmar literature, lexicons, and parallel Bible datasets.

---

## Error Handling

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

Published under the MIT License by the **Hmar Heritage Foundation**.
