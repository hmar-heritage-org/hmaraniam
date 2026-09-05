# hmaraniam 🇲z

**Zero-dependency language identification library for Hmar.**

> *"Hmar a ni am?"* — *"Is it Hmar?"*

`hmaraniam` is a lightweight Python library that identifies Hmar text and distinguishes it from English and related Kuki-Chin / Zo languages (such as Mizo, Kuki, Paite, and Vaiphei).

---

## Features

- **Fast dictionary lookups:** Uses $O(1)$ set matching with no machine learning dependencies (PyTorch and TensorFlow free).
- **Dual diacritic scoring:** Reports `casual_hmar_ratio` (ASCII-normalized for standard QWERTY typing) and `formal_hmar_ratio` (exact diacritic matches for formal text).
- **Separate confidence scores:** Separates overall classification confidence (`detected_language_confidence`) from Hmar-specific confidence (`hmar_confidence`).
- **Consistent JSON output:** Returns the same dictionary structure for every call, including word counts and diacritic breakdowns.
- **Custom unigrams & stopwords:** Pass custom unigram sets, extra domain vocabulary, or custom stopword lists.
- **Offline & CDN dataset loading:** Syncs unigram sets via jsDelivr CDN with local disk caching and bundled offline fallbacks.

---

## Design Principles

- **Language ID vs. Spell Correction:** `hmaraniam` measures vocabulary identity (*"Is this text Hmar?"*). It is not a spell checker and does not modify typos, character variants (acute `á`, grave `à`, circumflex `â`), or mobile keyboard codepoints (`ṭ` vs `ţ`).
- **ASCII Normalization (`casual_hmar_ratio`):** Mobile keyboards produce varying accent codepoints. Stripping diacritics (`strip_diacritics`) allows consistent vocabulary evaluation across devices.
- **1-Token-Per-Row Boundaries:** To evaluate hyphenated (`mithiem-hai`), spaced (`mithiem hai`), or compound (`mithiemhai`) terms directly, `hmaraniam` accepts 1-token-per-row inputs (JSON, CSV, TXT, Python lists) without re-tokenizing.

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

> **Cognate Resolution:** Related Zo languages like Mizo share up to 78% vocabulary overlap with Hmar. `hmaraniam` distinguishes sibling Zo languages by combining vocabulary coverage (`unknown_words_ratio` $\le 0.18$) with structural markers (`sibling_zo_stopwords`).

---

### 2. Web Archive Evaluation (~1,300 Documents)

Evaluated on scraped web documents from 5 Hmar/Zo web publishers:

| Publisher Web Archive | Corpus Source / Format | Evaluated Items | Hmar Posts (%) | English Posts (%) | Other / Mixed Posts (%) | Avg Hmar Confidence | Mean Casual Hmar Ratio | Mean Formal Hmar Ratio | Mean Unknown Words Ratio | Primary Content Profile |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **L. Keivom Archive** (`keivom`) | Blogger API JSON | 300 | **199 (66.3%)** | 32 (10.7%) | 69 (23.0%) | **0.8320** | **79.3%** | 70.0% | 20.7% | Hmar literary essays & prose |
| **Inpui Journal** (`inpui`) | Blogger API JSON | 291 | **124 (42.6%)** | 67 (23.0%) | 100 (34.4%) | **0.7400** | **63.7%** | 55.7% | 36.3% | Bilingual news journal & opinion pieces |
| **HSA Portal** (`hsa`) | WordPress API JSON | 177 | **23 (13.0%)** | 38 (21.5%) | **116 (65.5%)** | 0.5730 | **53.7%** | 46.7% | 46.3% | Student association alerts & mixed posts |
| **Hmarram.com** (`hmarram`) | WordPress API JSON | 235 | 12 (5.1%) | **209 (88.9%)** | 14 (6.0%) | 0.7762 | 31.2% | 23.8% | 68.8% | Tech articles & English press releases |
| **Virthli News** (`virthli`) | Scraped Raw HTML | 296 | 5 (1.7%) | **267 (90.2%)** | 24 (8.1%) | 0.8721 | 17.6% | 13.4% | 82.4% | Employment alerts & exam guidelines |

- **Literary Archives:** Sites like L. Keivom and Inpui Journal contain Hmar prose, resulting in higher Hmar classification rates (42%–66%).
- **Community News & Job Alerts:** Portals like Hmarram and Virthli publish mostly recruitment notices and exam guidelines in English, which classify as `"english"` or `"other"`.

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

Published under the MIT License by the **Hmar Heritage Project**.
