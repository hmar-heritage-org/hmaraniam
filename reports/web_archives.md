# Benchmark Report: Real-World Digital Web Archives

This report evaluates `hmaraniam` across real-world web article archives collected from 5 major Hmar/Zo web publisher portals.
Web text presents distinct challenges including mixed code-switching, English technical/site navigation headers, informal spelling variations, and un-sanitized HTML remnants.

## Web Archive Corpus Sources
| Publisher Archive | Platform / Format | Description & Language Profile |
| :--- | :--- | :--- |
| **L. Keivom Archive** | Blogger JSON | Literary prose, essays, and translations by L. Keivom (predominantly Hmar & English). |
| **Inpui Journal** | Blogger JSON | News portal and community discussions (mixed Hmar & English news). |
| **HSA Portal** | WordPress API | Hmar Students' Association portal (student announcements, English & Hmar). |
| **Hmarram Online** | WordPress API | Community articles & official notifications (predominantly English announcements). |
| **Virthli News** | Raw HTML | Regional news archive (predominantly English job postings & regional press releases). |

## Detection Results Summary

| Publisher Archive | Format | Total Evaluated | Hmar Detected (%) | English Detected (%) | Other / Mixed (%) | Mean Hmar Conf. | Mean Casual Ratio | Mean Formal Ratio | Mean Unknown Ratio |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **L. Keivom Archive** | Blogger JSON export | 300 | **192 (64.0%)** | 32 (10.7%) | 76 (25.3%) | 0.8220 | 78.8% | 69.5% | 21.2% |
| **Hmarram Online** | WordPress REST API | 235 | **12 (5.1%)** | 209 (88.9%) | 14 (6.0%) | 0.7658 | 31.0% | 23.7% | 69.0% |
| **Inpui Journal** | Blogger JSON export | 291 | **120 (41.2%)** | 66 (22.7%) | 105 (36.1%) | 0.7357 | 63.5% | 55.6% | 36.5% |
| **HSA Portal** | WordPress REST API | 177 | **23 (13.0%)** | 38 (21.5%) | 116 (65.5%) | 0.5679 | 53.5% | 46.5% | 46.5% |
| **Virthli News** | Raw Scraped HTML | 296 | **5 (1.7%)** | 267 (90.2%) | 24 (8.1%) | 0.8694 | 17.4% | 13.2% | 82.6% |

## Core Insights & Analysis
- **Total Scraped Web Documents Evaluated:** 1299 items across 5 publisher archives.
- **Total Hmar Articles Identified:** 352 articles with strong confidence.
- **High-Density Hmar Literary Archives:** L. Keivom Archive (**64.0% Hmar**, mean confidence 0.8220) and Inpui Journal (**41.2% Hmar**) contain high proportions of pure Hmar text.
- **English & Notification Portals:** Hmarram Online (**88.9% English**) and Virthli News (**90.2% English**) consist primarily of English press releases, circulars, and job notifications, which `hmaraniam` cleanly distinguishes from Hmar text.
- **Unknown Word Distribution:** Web articles exhibit ~21%–46% unknown words due to proper nouns (names, places, organization acronyms like HSA/YMA), specialized terms, and English loanwords.
