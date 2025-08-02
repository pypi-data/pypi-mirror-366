"""
Command line interface for Count PDF Page.
"""

import argparse
import os
import sys

from .core import process_directory, generate_markdown_report


def main() -> None:
    """
    Main function for command line interface.
    """
    parser = argparse.ArgumentParser(
        description="Count pages in PDF files and generate a markdown report."
    )

    parser.add_argument(
        "directory",
        nargs="?",
        default=".",
        help="Directory to scan for PDF files (default: current directory)",
    )

    parser.add_argument(
        "-o",
        "--output",
        default="count_pdf_page_report.md",
        help="Output markdown file name (default: count_pdf_page_report.md)",
    )

    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Enable verbose output"
    )

    parser.add_argument("--version", action="version", version="%(prog)s 0.1.0")

    args = parser.parse_args()

    # Resolve directory path
    target_dir = os.path.abspath(args.directory)

    if not os.path.exists(target_dir):
        print(f"Error: Directory '{target_dir}' does not exist.", file=sys.stderr)
        sys.exit(1)

    if not os.path.isdir(target_dir):
        print(f"Error: '{target_dir}' is not a directory.", file=sys.stderr)
        sys.exit(1)

    if args.verbose:
        print(f"Scanning for PDF files in: {target_dir}")

    try:
        # Process directory
        results, total_pages = process_directory(target_dir)

        if not results:
            print("No PDF files found in the specified directory.")
            return

        if args.verbose:
            print(f"Found {len(results)} PDF files")
            for filename, page_count in results:
                status = (
                    f"{page_count} pages" if isinstance(page_count, int) else "Error"
                )
                print(f"  {filename}: {status}")

        # Generate markdown report
        markdown_content = generate_markdown_report(results, total_pages)

        # Determine output path
        if os.path.isabs(args.output):
            output_path = args.output
        else:
            output_path = os.path.join(target_dir, args.output)

        # Save to markdown file
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(markdown_content)

        print(f"Report saved to: {output_path}")
        print(f"Total pages processed: {total_pages}")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
