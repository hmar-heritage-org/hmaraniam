"""
Interactive, Navigable Command-Line Interface & Help System for hmaraniam.
"""

import sys
import json
import argparse
from typing import List, Optional
from hmaraniam import Detector, detect, __version__

HELP_TOPICS = {
    "inputs": """
================================================================================
hmaraniam HELP: INPUT FORMATS, CONCRETE EXAMPLES & BOUNDARIES
================================================================================

hmaraniam distinguishes between DETERMINISTIC 1-TOKEN-PER-ROW INPUTS
and NON-PARSED RAW TEXT DOCUMENTS (Convenience Fallback).

--------------------------------------------------------------------------------
1. DETERMINISTIC 1-TOKEN-PER-ROW INPUTS
--------------------------------------------------------------------------------
Preserves exact token boundaries without internal engine guessing or re-tokenization.
Ideal for distinguishing orthographic variants like "mithiem-hai" vs "mithiem hai".

A. JSON Array File (tokens.json):
   [
     "khawvel",
     "fe",
     "dan",
     "mithiem-hai",
     "pathien",
     "hnenah"
   ]
   Usage: hmaraniam tokens.json

B. CSV File (tokens.csv):
   token
   khawvel
   fe
   dan
   mithiem-hai
   pathien
   hnenah
   Usage: hmaraniam tokens.csv

C. Line-Delimited TXT File (tokens.txt - 1 word per line):
   khawvel
   fe
   dan
   mithiem-hai
   pathien
   hnenah
   Usage: hmaraniam tokens.txt

D. Python List / Set:
   tokens = ["khawvel", "fe", "dan", "mithiem-hai"]
   hmaraniam.detect(tokens)

--------------------------------------------------------------------------------
2. NON-PARSED RAW TEXT DOCUMENTS (Convenience Fallback)
--------------------------------------------------------------------------------
For raw un-tokenized prose containing full sentences or multi-word lines, the engine
extracts word tokens using basic word boundary regex matching.

A. Raw Article File (article.txt):
   Khawvel fe dan phung ei en chun, ram le hnam damna thuruk chu lien lema...
   Usage: hmaraniam article.txt

B. Raw Text String / Stdin Pipe:
   hmaraniam "Khawvel fe dan phung ei en chun, ram le hnam damna thuruk..."
   echo "Khawvel fe dan phung..." | hmaraniam
""",

    "schema": """
================================================================================
hmaraniam HELP: STANDARDIZED JSON OUTPUT SCHEMA & METRICS
================================================================================

hmaraniam outputs an immutable JSON payload for every classification request:

{
  "language": "hmar",                     # Primary classification label ("hmar", "english", "other")
  "hmar_confidence": 0.9842,               # Permanent Hmar confidence float [0.0000 - 1.0000]
  "detected_language_confidence": 0.9842,  # Confidence score for the assigned language label
  "mode": "basic",                        # Active detection mode ("basic" or "high")
  "scores": {
    "casual_hmar_ratio": 0.9524,          # Ratio of tokens matching Hmar vocabulary in plain ASCII
    "formal_hmar_ratio": 0.8095,          # Ratio of tokens matching exact formal Hmar diacritics
    "english_stopword_ratio": 0.0000,     # Ratio of English stopword matches
    "sibling_zo_stopword_ratio": 0.0000,   # Ratio of Sibling Zo (Mizo/Paite/Vaiphei) structural markers
    "unknown_words_ratio": 0.0476,        # Ratio of unrecognized tokens against vocabulary
    "total_words": 21,                    # Total token count evaluated
    "hmar_words_count": 20,               # Count of recognized Hmar word tokens
    "non_hmar_words_count": 1,            # Count of unrecognized word tokens
    "unknown_words_count": 1,             # Count of unknown tokens
    "english_stopwords_count": 0,         # Count of English stopwords
    "sibling_zo_stopwords_count": 0,      # Count of Sibling Zo stopwords
    "hmar_diacritic_words_count": 17,     # Count of recognized Hmar words typed with diacritics
    "non_hmar_diacritic_words_count": 0,  # Count of non-Hmar diacritic words isolated
    "total_diacritic_words_count": 17     # Total diacritic token count
  }
}
""",

    "wordlists": """
================================================================================
hmaraniam HELP: CUSTOM WORDLISTS & STOPWORDS
================================================================================

hmaraniam allows developers to extend or completely replace the bundled unigrams
and stopwords using CLI flags or the Python API:

CLI Flags:
  --custom-unigrams FILE   Replace the bundled unigram database with a custom file (.json/.csv/.txt).
  --extra-unigrams FILE    Append extra domain vocabulary to the active dataset.
  --custom-stopwords FILE  Add custom stopwords.
  --no-default-stopwords   Disable bundled English & Sibling Zo stopwords.

CLI Examples:
  # Append extra domain terminology
  hmaraniam --extra-unigrams domain_terms.txt input.json

  # Completely replace default vocabulary with a custom dataset
  hmaraniam --custom-unigrams my_vocab.json --no-default-stopwords input.json

Python API:
  from hmaraniam import Detector

  detector = Detector(
      custom_unigrams="my_vocab.json",
      disable_default_stopwords=True
  )
""",

    "design": """
================================================================================
hmaraniam HELP: DESIGN & NORMALIZATION PRINCIPLES
================================================================================

1. Language Identification vs. Spell Correction:
   hmaraniam evaluates vocabulary identity ("Is this text Hmar?"). It is NOT a spell
   checker or proofreading tool. It does not perform opinionated character rewrites to
   "correct" typos, accent slash variations (á/à/â), or non-standard mobile keyboard codepoints (ṭ/ţ/ț).

2. ASCII Normalization (casual_hmar_ratio) as Universal Ground Truth:
   Because mobile keyboards output diverse accent/slash codepoints, ASCII normalization
   (strip_diacritics) serves as the primary device-agnostic detection metric.

3. Deterministic 1-Token-Per-Row Boundaries:
   To avoid engine-level guessing on orthographic variants ("mithiem-hai" vs "mithiem hai"),
   1-token-per-row inputs (JSON, CSV, TXT, Python Lists) are evaluated 1:1 with zero internal mutation.
""",

    "integrate": """
================================================================================
hmaraniam HELP: BUILDING APPLICATIONS & PIPELINES ON TOP OF HMARANIAM
================================================================================

1. Python API Microservice (FastAPI / Flask):
   from fastapi import FastAPI
   import hmaraniam

   app = FastAPI()
   detector = hmaraniam.Detector(mode="basic", offline_only=True)

   @app.post("/detect")
   def detect_language(tokens: List[str]):
       return detector.detect(tokens)

2. Shell Pipeline & jq Filtering:
   cat tokens.json | hmaraniam --compact | jq '.hmar_confidence'

3. Batch Corpus Filtering (Paragraph Level):
   from hmaraniam import Detector
   detector = Detector()
   paragraphs = detector.detect_paragraphs(full_document_text)
""",

    "info": """
================================================================================
hmaraniam HELP: PROJECT INFO & DATASET RESOURCES
================================================================================

- GitHub Repository: https://github.com/hmar-heritage-org/hmaraniam
- PyPI Package:     https://pypi.org/project/hmaraniam/
- Open Data CDN:     https://cdn.jsdelivr.net/gh/hmar-heritage-org/hmaraniam@main/hmaraniam/data/
- License:           MIT License (Hmar Heritage Project)
"""
}


def print_main_help():
    print(f"""hmaraniam {__version__} - Zero-dependency language identification engine for Hmar.

USAGE:
  hmaraniam [options] [input]
  hmaraniam help [topic]

NAVIGABLE HELP TOPICS:
  hmaraniam help inputs     - Guide on 1-token-per-row inputs (JSON, CSV, TXT, stdin)
  hmaraniam help schema     - Field-by-field breakdown of the JSON output schema & metrics
  hmaraniam help wordlists  - How to extend or replace vocabulary & stopwords
  hmaraniam help design     - Core principles: Language ID vs Spell Correction & Diacritics
  hmaraniam help integrate - Building APIs, web services, & shell pipelines on top of hmaraniam
  hmaraniam help info       - Repository links, dataset CDN resources, & license details

OPTIONS:
  -h, --help                Show this help sitemap and exit.
  -v, --version             Show version number and exit.
  --mode {{basic,high}}       Detection mode ('basic' ~30k unigrams or 'high' extended). Default: basic.
  --custom-unigrams FILE    Replace default unigram dataset with a custom file (.json/.csv/.txt).
  --extra-unigrams FILE     Append extra domain words to vocabulary dataset.
  --custom-stopwords FILE   Add custom stopwords.
  --no-default-stopwords    Disable bundled English & Sibling Zo stopwords.
  --offline                 Force offline-only dataset loading (disables network checks).
  --compact                 Output single-line compact JSON (ideal for shell scripts).

EXAMPLES:
  # Evaluate a raw text string
  hmaraniam "Khawvel fe dan phung ei en chun, ram le hnam damna thuruk chu..."

  # Evaluate a pre-tokenized JSON array file (1 token per item)
  hmaraniam tokens.json

  # Evaluate with custom extra domain unigrams
  hmaraniam --extra-unigrams domain_words.txt input.json
""")


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "help":
        if len(sys.argv) > 2:
            topic = sys.argv[2].lower().strip()
            if topic in HELP_TOPICS:
                print(HELP_TOPICS[topic])
            else:
                print(f"Unknown help topic '{topic}'. Available topics: {', '.join(sorted(HELP_TOPICS.keys()))}")
        else:
            print_main_help()
        sys.exit(0)

    parser = argparse.ArgumentParser(
        prog="hmaraniam",
        description="hmaraniam - Zero-dependency language identification engine for Hmar ('Hmar a ni am?').",
        add_help=False
    )
    parser.add_argument("-h", "--help", action="store_true", help="Show help sitemap and exit")
    parser.add_argument("-v", "--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument("input", nargs="?", help="Text string or path to token file (.json, .csv, .txt)")
    parser.add_argument("--mode", choices=["basic", "high"], default="basic", help="Detection mode ('basic' or 'high')")
    parser.add_argument("--custom-unigrams", help="Path to custom unigrams file (.json/.csv/.txt)")
    parser.add_argument("--extra-unigrams", help="Path to extra unigrams file (.json/.csv/.txt)")
    parser.add_argument("--custom-stopwords", help="Path to custom stopwords file (.json/.csv/.txt)")
    parser.add_argument("--no-default-stopwords", action="store_true", help="Disable default stopwords")
    parser.add_argument("--offline", action="store_true", help="Force offline dataset loading")
    parser.add_argument("--compact", action="store_true", help="Output compact single-line JSON")

    args, unknown = parser.parse_known_args()

    if args.help:
        print_main_help()
        sys.exit(0)

    if args.input:
        input_data = args.input
    elif not sys.stdin.isatty():
        input_data = sys.stdin.read()
    else:
        print_main_help()
        sys.exit(0)

    try:
        detector = Detector(
            mode=args.mode,
            offline_only=args.offline,
            custom_unigrams=args.custom_unigrams,
            extra_unigrams=args.extra_unigrams,
            custom_stopwords=args.custom_stopwords,
            disable_default_stopwords=args.no_default_stopwords
        )

        result = detector.detect(input_data)

        if args.compact:
            print(json.dumps(result, separators=(",", ":")))
        else:
            print(json.dumps(result, indent=2))
    except (FileNotFoundError, ValueError, TypeError) as e:
        sys.stderr.write(f"Error: {e}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
