# Empirical Length-Sensitivity & Threshold Benchmark

This report evaluates `hmaraniam` across **4 structural tiers** (clauses, single verses, multi-verse combos, full chapters) across 10 parallel Zo language editions to determine exact threshold boundaries and length sensitivity.

## Tier 1: Clause / Sub-Verse
*Single clause between punctuation (~3–8 words)*

| Language | Edition | Target | Sample Count ($N$) | Avg Words | Accuracy | Mean Hmar Conf | Mean Casual Ratio | Stopword Hit Rate (%) | Mean Unknown Ratio |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **English** | WEB | `english` | 150 | 7.8 | **92.7%** | 0.0000 | 25.7% | 0.0% | 74.3% |
| **Gangte** | BSI | `other` | 150 | 8.8 | **8.7%** | 0.3092 | 70.6% | 47.3% | 29.4% |
| **Hmar** | CLB | `hmar` | 150 | 7.9 | **98.0%** | 0.6490 | 95.1% | 8.0% | 4.9% |
| **Hmar** | OV | `hmar` | 150 | 7.9 | **98.7%** | 0.6517 | 95.2% | 8.0% | 4.8% |
| **Mizo** | CLB | `other` | 150 | 8.2 | **10.7%** | 0.4037 | 77.8% | 32.7% | 22.2% |
| **Mizo** | OV | `other` | 150 | 7.9 | **17.3%** | 0.3802 | 77.0% | 23.3% | 23.0% |
| **Paite** | BSI | `other` | 150 | 7.1 | **14.0%** | 0.0255 | 43.3% | 62.0% | 56.7% |
| **Thadou** | BSI | `other` | 150 | 7.3 | **1.3%** | 0.0083 | 29.2% | 72.7% | 70.8% |
| **Vaiphei** | BSI | `other` | 150 | 9.2 | **18.7%** | 0.1554 | 57.8% | 64.0% | 42.2% |
| **Zou** | BSI | `other` | 150 | 8.7 | **30.0%** | 0.0264 | 43.1% | 67.3% | 56.9% |

## Tier 2: Single Verse
*1 full verse (~10–25 words)*

| Language | Edition | Target | Sample Count ($N$) | Avg Words | Accuracy | Mean Hmar Conf | Mean Casual Ratio | Stopword Hit Rate (%) | Mean Unknown Ratio |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **English** | WEB | `english` | 100 | 24.5 | **99.0%** | 0.0000 | 24.2% | 0.0% | 75.8% |
| **Gangte** | BSI | `other` | 100 | 29.4 | **4.0%** | 0.4178 | 72.3% | 84.0% | 27.7% |
| **Hmar** | CLB | `hmar` | 100 | 28.7 | **100.0%** | 0.9433 | 94.5% | 8.0% | 5.5% |
| **Hmar** | OV | `hmar` | 100 | 28.6 | **100.0%** | 0.9418 | 94.5% | 8.0% | 5.5% |
| **Mizo** | CLB | `other` | 100 | 25.0 | **3.0%** | 0.5323 | 76.7% | 81.0% | 23.3% |
| **Mizo** | OV | `other` | 100 | 29.5 | **3.0%** | 0.5163 | 75.7% | 90.0% | 24.3% |
| **Paite** | BSI | `other` | 100 | 23.4 | **0.0%** | 0.0162 | 45.4% | 94.0% | 54.6% |
| **Thadou** | BSI | `other` | 100 | 21.1 | **0.0%** | 0.0000 | 30.7% | 95.0% | 69.3% |
| **Vaiphei** | BSI | `other` | 100 | 30.2 | **2.0%** | 0.1072 | 57.6% | 96.0% | 42.4% |
| **Zou** | BSI | `other` | 100 | 24.1 | **1.0%** | 0.0161 | 45.3% | 99.0% | 54.7% |

## Tier 3: Multi-Verse Combo
*4 consecutive verses combined (~40–100 words)*

| Language | Edition | Target | Sample Count ($N$) | Avg Words | Accuracy | Mean Hmar Conf | Mean Casual Ratio | Stopword Hit Rate (%) | Mean Unknown Ratio |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **English** | WEB | `english` | 1520 | 89.2 | **100.0%** | 0.0000 | 24.6% | 0.0% | 75.4% |
| **Gangte** | BSI | `other` | 1520 | 108.0 | **0.0%** | 0.2323 | 66.6% | 97.4% | 33.4% |
| **Hmar** | CLB | `hmar` | 1520 | 100.5 | **100.0%** | 0.9846 | 93.8% | 19.5% | 6.2% |
| **Hmar** | OV | `hmar` | 1520 | 99.7 | **100.0%** | 0.9847 | 93.9% | 19.7% | 6.1% |
| **Mizo** | CLB | `other` | 1520 | 93.8 | **0.1%** | 0.5010 | 75.0% | 97.0% | 25.0% |
| **Mizo** | OV | `other` | 1517 | 103.7 | **0.0%** | 0.4816 | 74.5% | 98.0% | 25.5% |
| **Paite** | BSI | `other` | 1520 | 87.0 | **0.0%** | 0.0021 | 43.8% | 99.0% | 56.2% |
| **Thadou** | BSI | `other` | 1520 | 76.1 | **0.0%** | 0.0013 | 26.4% | 99.1% | 73.6% |
| **Vaiphei** | BSI | `other` | 1520 | 109.1 | **0.0%** | 0.0597 | 58.4% | 99.1% | 41.6% |
| **Zou** | BSI | `other` | 1520 | 89.9 | **0.2%** | 0.0048 | 44.6% | 99.8% | 55.4% |

## Tier 4: Full Chapter
*Entire chapter (~300–800 words)*

| Language | Edition | Target | Sample Count ($N$) | Avg Words | Accuracy | Mean Hmar Conf | Mean Casual Ratio | Stopword Hit Rate (%) | Mean Unknown Ratio |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **English** | WEB | `english` | 180 | 753.3 | **100.0%** | 0.0000 | 24.5% | 0.0% | 75.5% |
| **Gangte** | BSI | `other` | 180 | 911.7 | **0.0%** | 0.2172 | 66.5% | 100.0% | 33.5% |
| **Hmar** | CLB | `hmar` | 180 | 848.5 | **100.0%** | 0.9987 | 93.8% | 75.0% | 6.2% |
| **Hmar** | OV | `hmar` | 180 | 842.3 | **100.0%** | 0.9988 | 94.0% | 75.6% | 6.0% |
| **Mizo** | CLB | `other` | 180 | 791.8 | **0.0%** | 0.4979 | 75.0% | 100.0% | 25.0% |
| **Mizo** | OV | `other` | 180 | 874.4 | **0.0%** | 0.4789 | 74.4% | 100.0% | 25.6% |
| **Paite** | BSI | `other` | 180 | 734.3 | **0.0%** | 0.0000 | 44.4% | 100.0% | 55.6% |
| **Thadou** | BSI | `other` | 180 | 642.5 | **0.0%** | 0.0000 | 26.6% | 100.0% | 73.4% |
| **Vaiphei** | BSI | `other` | 180 | 921.6 | **0.0%** | 0.0226 | 58.4% | 100.0% | 41.6% |
| **Zou** | BSI | `other` | 180 | 759.5 | **0.0%** | 0.0001 | 45.0% | 100.0% | 55.0% |

## Threshold & Length-Sensitivity Observations
- **Tier 4 (Full Chapters):** 100.0% accuracy across all languages. Stopword hit rate reaches 100% on Sibling Zo text, pulling confidence down cleanly.
- **Tier 3 (Multi-Verse Combos, ~40–100 words):** Accuracy remains high across all languages as stopword presence is consistent.
- **Tier 2 (Single Verses, ~10–25 words):** Sibling Zo stopword hit rates drop slightly on short single verses, testing stopword coverage balance.
- **Tier 1 (Clauses / Sub-Verse, ~3–8 words):** Ultra-short clauses demonstrate the fundamental limit of unigram-only dictionary matching when short sentences lack dialect-exclusive markers.
