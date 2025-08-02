"""Command line interface for SheetWise."""

import argparse
import sys
import os
from pathlib import Path
import json

import pandas as pd

from . import SpreadsheetLLM, FormulaParser, CompressionVisualizer, WorkbookManager, SmartTableDetector


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="SheetWise: Encode spreadsheets for Large Language Models"
    )

    parser.add_argument(
        "input_file",
        nargs="?",  # Make input_file optional
        help="Path to input spreadsheet file (.xlsx, .xls, or .csv)",
    )

    parser.add_argument("-o", "--output", help="Output file path (default: stdout)")

    parser.add_argument(
        "--compression-ratio", type=float, default=None, help="Target compression ratio"
    )

    parser.add_argument(
        "--vanilla",
        action="store_true",
        help="Use vanilla encoding instead of compression",
    )

    parser.add_argument("--stats", action="store_true", help="Show encoding statistics")

    parser.add_argument("--demo", action="store_true", help="Run demo with sample data")
    
    parser.add_argument("--auto-config", action="store_true", 
                       help="Automatically configure compression parameters")
    
    parser.add_argument("--format", choices=['text', 'json', 'html'], default='text',
                       help="Output format (text, json, or html)")
    
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Enable verbose logging")
    
    # New command-line options for enhanced features
    feature_group = parser.add_argument_group('Enhanced Features')
    
    feature_group.add_argument("--extract-formulas", action="store_true",
                             help="Extract and analyze formulas from the spreadsheet")
    
    feature_group.add_argument("--visualize", action="store_true",
                             help="Generate visualization of spreadsheet compression")
    
    feature_group.add_argument("--multi-sheet", action="store_true",
                             help="Process all sheets in a workbook")
    
    feature_group.add_argument("--detect-tables", action="store_true",
                             help="Detect and extract tables from the spreadsheet")
    
    feature_group.add_argument("--report", action="store_true",
                             help="Generate comprehensive HTML report")

    args = parser.parse_args()

    # Handle demo mode
    if args.demo:
        from .utils import create_realistic_spreadsheet

        print("Running SheetWise demo...")
        df = create_realistic_spreadsheet()
        sllm = SpreadsheetLLM(enable_logging=args.verbose)

        print(f"Created demo spreadsheet: {df.shape}")
        
        # Choose encoding method based on options
        if args.vanilla:
            print("Using vanilla encoding...")
            encoded = sllm.encode_vanilla(df)
            encoding_type = "vanilla"
        elif args.auto_config:
            print("Using auto-configuration...")
            encoded = sllm.compress_with_auto_config(df)
            encoding_type = "auto-compressed"
        else:
            encoded = sllm.compress_and_encode_for_llm(df)
            encoding_type = "compressed"
        
        # Get stats if requested
        stats = {}
        if args.stats:
            stats = sllm.get_encoding_stats(df)
            print(f"\nEncoding Statistics ({encoding_type}):")
            for key, value in stats.items():
                if isinstance(value, float):
                    print(f"  {key}: {value:.2f}")
                else:
                    print(f"  {key}: {value}")
        
        # Handle visualization if requested
        if args.visualize:
            print("Generating visualization...")
            visualizer = CompressionVisualizer()
            compressed_result = sllm.compress_spreadsheet(df)
            
            # Create heatmap visualization
            fig = visualizer.create_data_density_heatmap(df)
            viz_path = "density_heatmap.png"
            visualizer.save_visualization_to_file(fig, viz_path)
            print(f"Saved visualization to {viz_path}")
            
            # Create comparison visualization
            fig2 = visualizer.compare_original_vs_compressed(df, compressed_result)
            viz_path2 = "compression_comparison.png"
            visualizer.save_visualization_to_file(fig2, viz_path2)
            print(f"Saved comparison visualization to {viz_path2}")
        
        # Handle table detection if requested
        if args.detect_tables:
            print("Detecting tables...")
            detector = SmartTableDetector()
            tables = detector.detect_tables(df)
            
            print(f"Detected {len(tables)} tables:")
            for i, table in enumerate(tables):
                print(f"  Table {i+1}: Rows {table.start_row}-{table.end_row}, Columns {table.start_col}-{table.end_col}")
                print(f"    Type: {table.table_type.value}, Headers: {table.has_headers}")
        
        # Handle output format
        if args.format == "json":
            # Convert numpy types to native Python types for JSON serialization
            json_stats = {}
            if stats:
                for key, value in stats.items():
                    if hasattr(value, 'item'):  # numpy scalar
                        json_stats[key] = value.item()
                    elif isinstance(value, tuple):  # shape tuple
                        json_stats[key] = list(value)
                    else:
                        json_stats[key] = value
            
            output_data = {
                "encoding_type": encoding_type,
                "data_shape": list(df.shape),  # Convert to list for JSON
                "output_length": len(encoded),
                "content": encoded
            }
            
            if args.stats:
                output_data["statistics"] = json_stats
            
            formatted_output = json.dumps(output_data, indent=2)
            print(f"\nJSON Output:")
            print(formatted_output)
        else:
            # Text format (default)
            print(f"\nLLM-ready output ({encoding_type}, {len(encoded)} characters):")
            print(encoded[:500] + "..." if len(encoded) > 500 else encoded)
        
        return

    # Validate input file is provided when not in demo mode
    if not args.input_file:
        print("Error: input_file is required when not using --demo", file=sys.stderr)
        parser.print_help()
        sys.exit(1)

    # Validate input file
    if not Path(args.input_file).exists():
        print(f"Error: Input file '{args.input_file}' not found", file=sys.stderr)
        sys.exit(1)

    try:
        # Initialize SpreadsheetLLM
        sllm = SpreadsheetLLM()

        # Load spreadsheet
        df = sllm.load_from_file(args.input_file)
        print(f"Loaded spreadsheet: {df.shape} ({args.input_file})", file=sys.stderr)

        # Generate encoding
        if args.vanilla:
            encoded = sllm.encode_vanilla(df)
        else:
            encoded = sllm.compress_and_encode_for_llm(df)

        # Show statistics if requested
        if args.stats:
            stats = sllm.get_encoding_stats(df)
            print("\nEncoding Statistics:", file=sys.stderr)
            for key, value in stats.items():
                if isinstance(value, float):
                    print(f"  {key}: {value:.2f}", file=sys.stderr)
                else:
                    print(f"  {key}: {value}", file=sys.stderr)
            print("", file=sys.stderr)

        # Output result
        if args.output:
            with open(args.output, "w") as f:
                f.write(encoded)
            print(f"Encoded output written to: {args.output}", file=sys.stderr)
        else:
            print(encoded)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
