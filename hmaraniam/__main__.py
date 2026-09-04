"""
Command-line interface for hmaraniam detector engine.
"""

import sys
import json
import argparse
from hmaraniam import detect, __version__


def main():
    parser = argparse.ArgumentParser(
        prog="hmaraniam",
        description="hmaraniam - High-precision language identification engine for Hmar ('Hmar a ni am?')."
    )
    parser.add_argument(
        "-v", "--version",
        action="version",
        version=f"%(prog)s {__version__}"
    )
    parser.add_argument(
        "text",
        nargs="?",
        help="Text string to evaluate (if omitted, reads from stdin)"
    )
    parser.add_argument(
        "--mode",
        choices=["basic", "high"],
        default="basic",
        help="Detection mode ('basic' or 'high')"
    )

    args = parser.parse_args()

    if args.text:
        input_text = args.text
    elif not sys.stdin.isatty():
        input_text = sys.stdin.read()
    else:
        parser.print_help()
        sys.exit(0)

    result = detect(input_text, mode=args.mode)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
