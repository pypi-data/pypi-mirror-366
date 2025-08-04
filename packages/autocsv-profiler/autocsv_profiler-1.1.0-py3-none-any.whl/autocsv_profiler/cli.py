#!/usr/bin/env python3
"""
Command-line interface for AutoCSV Profiler
"""

import sys
import os
import argparse
from pathlib import Path

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Comprehensive automated CSV data analysis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  autocsv-profiler data.csv
  autocsv-profiler data.csv --output ./results
  autocsv-profiler data.csv --delimiter ";"
        """
    )
    
    parser.add_argument(
        "csv_file",
        help="Path to the CSV file to analyze"
    )
    
    parser.add_argument(
        "--output", "-o",
        default=None,
        help="Output directory (default: same as CSV file with '_analysis' suffix)"
    )
    
    parser.add_argument(
        "--delimiter", "-d",
        default=None,
        help="CSV delimiter (default: auto-detect)"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="autocsv-profiler 1.1.0"
    )
    
    args = parser.parse_args()
    
    # Validate CSV file exists
    csv_path = Path(args.csv_file)
    if not csv_path.exists():
        print(f"Error: CSV file not found: {csv_path}")
        sys.exit(1)
    
    # Set up output directory
    if args.output:
        output_dir = Path(args.output)
    else:
        output_dir = csv_path.parent / f"{csv_path.stem}_analysis"
    
    output_dir.mkdir(exist_ok=True)
    
    # Copy CSV to output directory
    import shutil
    csv_copy = output_dir / csv_path.name
    shutil.copy2(csv_path, csv_copy)
    
    print(f"AutoCSV Profiler v1.1.0")
    print(f"Input file: {csv_path}")
    print(f"Output directory: {output_dir}")
    print()
    
    # Auto-detect delimiter if not provided
    if not args.delimiter:
        print("Detecting delimiter...")
        try:
            from .recognize_delimiter import detect_delimiter
            delimiter = detect_delimiter(str(csv_copy))
            print(f"Detected delimiter: '{delimiter}'")
        except Exception as e:
            print(f"Could not auto-detect delimiter: {e}")
            delimiter = ","
            print(f"Using default delimiter: ','")
    else:
        delimiter = args.delimiter
        print(f"Using specified delimiter: '{delimiter}'")
    
    print()
    print("Starting comprehensive analysis...")
    
    # Run the main analysis
    try:
        from .auto_csv_profiler import main as analysis_main
        analysis_main(str(csv_copy), str(output_dir))
        
        print()
        print("=" * 50)
        print("Analysis completed successfully!")
        print(f"Results saved in: {output_dir}")
        print("=" * 50)
        
    except Exception as e:
        print(f"Error during analysis: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()