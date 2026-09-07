# Changelog

All notable changes to `hmaraniam` are documented here.

---

## [0.2.0] — 2026-09-07

### Changed

- **Frequency-weighted detection engine:** Replaced binary set membership scoring with log-frequency weighted scoring (`log(1 + corpus_count)`) compiled from 2 Hmar Bibles (CLB & OV) and 583 verified web articles. Core Hmar particles (`chu`, `chun`, `an`, `le`, `ka`) now carry proportionally higher signal than rare or loanword tokens.
- **Unigram shard format:** `unigrams_set_001.json` changed from a plain word list `["word1", "word2"]` to a frequency dictionary `{"word": count}`. The shard loader is fully backwards-compatible and still accepts legacy list format.
- **Shard vocabulary:** Expanded from ~37,000 to **45,042 verified Hmar unigrams** after filtering 7,532 pure English lexicon words while preserving overlapping Hmar structural particles.
- **Input token repetition cap:** A per-sentence token repetition cap of 3 prevents repeated words from skewing frequency-weighted ratios on short or copy-pasted text.
- **`effective_hmar_ratio`:** Classification logic and confidence scoring now use `max(casual_hmar_ratio, weighted_hmar_ratio)` as the primary signal, ensuring the binary match rate acts as a safety net for text with rare or technical vocabulary.

### Added

- **`weighted_hmar_ratio`** field in `scores` output — the log-frequency weighted proportion of Hmar tokens in the input.
- **`_sanitize_raw_text()` QOL preprocessor:** Automatically strips HTML tags, Markdown code blocks, Markdown bold/italic/link syntax, URLs, and email addresses from raw pasted strings before token evaluation.
- **7 new unit tests** (21 total): schema completeness, whitespace-only input, single-word input, sibling language detection (Mizo, Paite), HTML sanitization, Markdown sanitization, and `weighted_hmar_ratio` scaling.
- **`sibling_lang_scores` and `weighted_hmar_ratio`** added to `_empty_result()` for consistent schema across all output paths.

### Fixed

- Markdown underscore italic syntax (`_word_`) previously caused word tokens to be silently dropped during tokenization. Fixed by adding bold/italic marker stripping to `_sanitize_raw_text()`.
- `_empty_result()` schema was missing `weighted_hmar_ratio` and `sibling_lang_scores` keys, causing schema mismatch for consumers iterating both empty and non-empty result dicts.

---

## [0.1.7] — 2026-08-31

- Initial public release with binary set-based detection engine.
- Bundled `unigrams_set_001.json` with ~37,000 Hmar unigrams.
- Sibling Zo language detection via `sibling_zo_stopwords.json` and `sibling_zo_exclusive.json`.
- CDN-backed shard loading with local disk cache and offline fallback.
- CLI interface via `hmaraniam` entry point.
