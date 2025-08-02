from textstatslite.core import get_text_statistics, analyze_text_file
import argparse
import json
import sys

def main():
    parser = argparse.ArgumentParser(description="Analyze text statistics.")
    parser.add_argument("input", help="Text input or path to text file (.txt or .md)")
    parser.add_argument("--file", action="store_true", help="Treat input as a file path")
    parser.add_argument("--exclude-stopwords", action="store_true", help="Exclude stopwords from word stats")
    args = parser.parse_args()

    try:
        if args.file:
            stats = analyze_text_file(args.input, exclude_stopwords=args.exclude_stopwords)
        else:
            stats = get_text_statistics(args.input, exclude_stopwords=args.exclude_stopwords)
        print(json.dumps(stats, indent=4))
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()