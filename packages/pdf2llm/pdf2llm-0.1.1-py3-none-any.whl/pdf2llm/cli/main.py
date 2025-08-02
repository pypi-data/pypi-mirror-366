"""Command-line interface for PDF extraction."""

import argparse
import sys
from pathlib import Path
from typing import List
import json

from pdf2llm.core.extractor import PDFExtractor, ExtractionResult


def setup_parser() -> argparse.ArgumentParser:
    """Set up command line argument parser."""
    parser = argparse.ArgumentParser(
        description="Extract PDF content for LLM consumption",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Extract single PDF to markdown
  uv run -m pdf_utils.cli.main document.pdf
  
  # Extract to specific directory
  uv run -m pdf_utils.cli.main document.pdf -o extracted_docs/
  
  # Batch process multiple PDFs
  uv run -m pdf_utils.cli.main *.pdf -o zoning_docs/
  
  # Extract as plain text without images
  uv run -m pdf_utils.cli.main document.pdf --format text --no-images
  
  # Analyze only (no extraction)
  uv run -m pdf_utils.cli.main document.pdf --analyze-only
  
  # High quality image extraction
  uv run -m pdf_utils.cli.main document.pdf --dpi 300 --image-format png
        """
    )
    
    # Positional arguments
    parser.add_argument(
        'pdfs',
        nargs='+',
        type=Path,
        help='PDF file(s) to process'
    )
    
    # Output options
    parser.add_argument(
        '-o', '--output-dir',
        type=Path,
        default=Path('extracted'),
        help='Output directory (default: extracted/)'
    )
    
    parser.add_argument(
        '--format',
        choices=['markdown', 'text', 'both'],
        default='markdown',
        help='Output format (default: markdown)'
    )
    
    # Image options
    parser.add_argument(
        '--no-images',
        action='store_true',
        help='Skip image extraction'
    )
    
    parser.add_argument(
        '--image-format',
        choices=['png', 'jpg', 'jpeg'],
        default='png',
        help='Image format (default: png)'
    )
    
    parser.add_argument(
        '--dpi',
        type=int,
        default=150,
        help='DPI for image extraction (default: 150)'
    )
    
    # Processing options
    parser.add_argument(
        '--no-page-chunks',
        action='store_true',
        help='Disable page boundary markers'
    )
    
    parser.add_argument(
        '--analyze-only',
        action='store_true',
        help='Only analyze PDF structure, no extraction'
    )
    
    parser.add_argument(
        '--quiet',
        action='store_true',
        help='Minimal output'
    )
    
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output results as JSON'
    )
    
    # Advanced options
    parser.add_argument(
        '--token-limit',
        type=int,
        help='Warn if content exceeds token limit'
    )
    
    parser.add_argument(
        '--split-pages',
        action='store_true',
        help='Save each page as separate file'
    )
    
    return parser


def print_analysis(pdf_path: Path, analysis: dict, quiet: bool = False):
    """Print PDF analysis results."""
    if quiet:
        return
        
    print(f"\nAnalyzing: {pdf_path.name}")
    print(f"Pages: {analysis['total_pages']}")
    print(f"Images: {analysis['total_images']}")
    print(f"Tables: {analysis['total_tables']}")
    
    if analysis['has_images'] or analysis['has_tables']:
        print("\nContent types found:")
        if analysis['has_images']:
            print("  ✓ Images")
        if analysis['has_tables']:
            print("  ✓ Tables")


def print_result(pdf_path: Path, result: ExtractionResult, args):
    """Print extraction results."""
    if args.json:
        output = {
            "pdf": str(pdf_path),
            "output_path": str(result.output_path) if result.output_path else None,
            "token_estimate": result.token_estimate,
            "page_count": result.page_count,
            "has_images": result.has_images,
            "has_tables": result.has_tables,
            "image_count": len(result.image_paths) if result.image_paths else 0
        }
        print(json.dumps(output, indent=2))
    elif not args.quiet:
        print(f"\n✓ Extracted: {pdf_path.name}")
        print(f"  Output: {result.output_path}")
        print(f"  Tokens: ~{result.token_estimate:,}")
        if result.image_paths:
            print(f"  Images: {len(result.image_paths)} extracted")
        
        if args.token_limit and result.token_estimate > args.token_limit:
            print(f"  ⚠️  Warning: Exceeds token limit ({args.token_limit:,})")


def process_pdf(pdf_path: Path, extractor: PDFExtractor, args) -> ExtractionResult:
    """Process a single PDF file."""
    if args.analyze_only:
        analysis = extractor.analyze_structure(pdf_path)
        print_analysis(pdf_path, analysis, args.quiet)
        return None
    
    # Extract content
    if args.format == 'both':
        # Extract both formats
        results = []
        for fmt in ['markdown', 'text']:
            result = extractor.extract(
                pdf_path,
                output_format=fmt,
                analyze_first=not args.quiet
            )
            output_path = extractor.save_extraction(
                result, 
                pdf_path, 
                format_suffix=f"_{fmt}"
            )
            results.append(result)
        return results[0]  # Return markdown result as primary
    else:
        result = extractor.extract(
            pdf_path,
            output_format=args.format,
            analyze_first=not args.quiet
        )
        extractor.save_extraction(result, pdf_path)
        return result


def main():
    """Main CLI entry point."""
    parser = setup_parser()
    args = parser.parse_args()
    
    # Validate inputs
    pdf_files = []
    for pdf_path in args.pdfs:
        if pdf_path.is_file() and pdf_path.suffix.lower() == '.pdf':
            pdf_files.append(pdf_path)
        elif pdf_path.is_file():
            print(f"Warning: Skipping non-PDF file: {pdf_path}")
        else:
            # Try glob pattern
            matches = list(Path.cwd().glob(str(pdf_path)))
            pdf_matches = [p for p in matches if p.suffix.lower() == '.pdf']
            if pdf_matches:
                pdf_files.extend(pdf_matches)
            else:
                print(f"Warning: No PDF files found for pattern: {pdf_path}")
    
    if not pdf_files:
        print("Error: No valid PDF files to process")
        sys.exit(1)
    
    # Create extractor
    extractor = PDFExtractor(
        output_dir=args.output_dir,
        image_format=args.image_format,
        dpi=args.dpi,
        page_chunks=not args.no_page_chunks
    )
    
    # Process PDFs
    if not args.quiet and not args.json:
        print(f"Processing {len(pdf_files)} PDF file(s)...")
        print(f"Output directory: {args.output_dir.absolute()}")
    
    results = []
    for pdf_path in pdf_files:
        try:
            result = process_pdf(pdf_path, extractor, args)
            if result:
                print_result(pdf_path, result, args)
                results.append((pdf_path, result))
        except Exception as e:
            if args.json:
                print(json.dumps({"error": str(e), "pdf": str(pdf_path)}, indent=2))
            else:
                print(f"\n✗ Error processing {pdf_path.name}: {e}")
    
    # Summary
    if len(pdf_files) > 1 and not args.quiet and not args.json:
        successful = len([r for r in results if r[1] is not None])
        print(f"\n{'='*50}")
        print(f"Processed {successful}/{len(pdf_files)} PDFs successfully")
        print(f"Output saved to: {args.output_dir.absolute()}")


if __name__ == "__main__":
    main()