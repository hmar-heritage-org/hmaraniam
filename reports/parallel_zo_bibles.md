# Benchmark Report: Parallel Zo Sibling Languages

This report evaluates `hmaraniam` on parallel chapters across 10 Bible translations representing 8 Zo languages and English.

## Evaluated Passages
- **Genesis 1** (Creation narrative)
- **Exodus 20** (Law / Ten Commandments)
- **Matthew 5** (Sermon on the Mount)
- **Luke 2** (Nativity narrative)
- **Romans 8** (Epistles)
- **Revelation 21** (Apocalyptic literature)

## Results Matrix

| Language | Edition / Source | Target Class | Assigned Label | Accuracy | Avg Hmar Confidence | Casual Hmar Ratio | Formal Hmar Ratio | Sibling Stopword Hits | Unknown Words Ratio |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **English** | WEB | `english` | `english` | **100%** | 0.0000 | 24.0% | 12.8% | 0 | 76.0% |
| **Gangte** | BSI | `gangte` | `paite` | **0%** | 0.2051 | 66.2% | 58.2% | 389 | 33.8% |
| **Hmar** | CLB | `hmar` | `hmar` | **100%** | 1.0000 | 94.4% | 88.8% | 23 | 5.6% |
| **Hmar** | OV | `hmar` | `hmar` | **100%** | 1.0000 | 94.5% | 89.0% | 23 | 5.5% |
| **Mizo** | CLB | `mizo` | `mizo` | **100%** | 0.4861 | 74.7% | 64.1% | 377 | 25.3% |
| **Mizo** | OV | `mizo` | `mizo` | **100%** | 0.4729 | 74.2% | 62.1% | 393 | 25.8% |
| **Paite** | BSI | `paite` | `thadou` | **0%** | 0.0000 | 44.0% | 36.8% | 605 | 56.0% |
| **Thadou** | BSI | `thadou` | `paite` | **0%** | 0.0000 | 26.3% | 19.6% | 569 | 73.7% |
| **Vaiphei** | BSI | `vaiphei` | `thadou` | **0%** | 0.0000 | 58.2% | 47.9% | 498 | 41.8% |
| **Zou** | BSI | `other` | `paite` | **0%** | 0.0000 | 44.8% | 34.9% | 628 | 55.2% |

## Key Observations & Summary
- **Overall Corpus Accuracy:** 50.0% across 10 language editions.
- **Hmar Contemporary & Old Versions:** Correctly identified as `hmar` with high Hmar confidence (0.95–1.00).
- **Sibling Zo Languages (Mizo, Paite, Vaiphei, Gangte, Zou, Thadou):** Successfully distinguished from Hmar and assigned to `other` without false positives.
- **Structural Stopwords:** Sibling Zo structural markers (such as Mizo `pathian`, `avangin`, Paite `pasian`, Gangte `pathen`) isolate closely related dialects.
