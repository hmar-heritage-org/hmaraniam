# Changelog

---

## [0.2.0] — 2026-09-07

### Changed

- **Frequency-weighted detection engine:** Scoring now uses log-frequencies (`log(1 + corpus_count)`) built from 2 Hmar Bibles (CLB and OV) and 583 verified web articles. Core particles like `chu`, `chun`, `an`, `le`, and `ka` outweigh rare or loanword tokens proportionally.
- **Unigram shard format:** `unigrams_set_001.json` is now a frequency dictionary `{"word": count}` instead of a plain list. The loader still accepts the old list format.
- **Shard vocabulary:** Grew from ~37,000 to 45,042 entries. 7,532 pure English words were filtered out while keeping Hmar structural particles that overlap with English (e.g. `in`, `an`, `is`).
- **Token repetition cap:** Tokens repeated more than 3 times in a single input are capped, so copy-pasted or spammy text does not skew the frequency score.
- **`effective_hmar_ratio`:** Classification now uses `max(casual_hmar_ratio, weighted_hmar_ratio)`. The binary match rate acts as a floor so text with rare or technical vocabulary still classifies correctly.

### Added

- `weighted_hmar_ratio` field in `scores`: the log-frequency weighted proportion of Hmar tokens.
- Raw text preprocessing: HTML tags, Markdown bold/italic/link syntax, code blocks, URLs, and email addresses are stripped from plain string input before scoring.
- 7 new unit tests (21 total): schema key consistency, whitespace-only input, single-word input, Mizo and Paite sibling detection, HTML sanitization, Markdown sanitization, and `weighted_hmar_ratio` scaling.
- `weighted_hmar_ratio` and `sibling_lang_scores` added to the empty result dict so the output schema is consistent regardless of input.

### Fixed

- Markdown underscore italic syntax like `_word_` caused the wrapped token to be dropped during tokenization. Underscore markers are now stripped before the tokenizer runs.
- `_empty_result()` was missing `weighted_hmar_ratio` and `sibling_lang_scores`, so code iterating over both empty and non-empty results would get a `KeyError`.

---

## [0.1.7] — 2026-08-31

- Initial public release with binary set-based detection engine.
- Bundled `unigrams_set_001.json` with ~37,000 Hmar unigrams.
- Sibling Zo language detection via `sibling_zo_stopwords.json` and `sibling_zo_exclusive.json`.
- CDN-backed shard loading with local disk cache and offline fallback.
- CLI interface via `hmaraniam` entry point.
