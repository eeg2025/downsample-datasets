#!/usr/bin/env python3
# process_metadata.py
# This script is used to process the metadata files for the resampled EEG-BIDS dataset.
# It is specifically designed for the HBN-EEG datasets for the EEG2025 NeurIPS Challenge.
# It is used to update the SamplingFrequency in the .json files from 500 to 100
# and remove the 'sample' column from the events.tsv files while preserving all 'n/a' values.
# It also copies other files maintaining the directory structure.
#
# (c) 8/2025, Seyed Yahya Shirazi, SCCN, INC, UCSD
"""
Process metadata files for resampled EEG-BIDS dataset.

This script:
1. Updates SamplingFrequency in .json files from 500 to 100
2. Removes the 'sample' column from events.tsv files while preserving all 'n/a' values
3. Copies other files maintaining the directory structure
"""

import os
import json
import pandas as pd
import shutil
from pathlib import Path
import argparse


def update_json_files(input_dir, output_dir):
    """Update SamplingFrequency in EEG JSON files."""
    print("Updating JSON files...")
    
    # Find all _eeg.json files
    json_files = list(Path(input_dir).rglob("*_eeg.json"))
    
    for json_file in json_files:
        try:
            # Calculate relative path and output location
            rel_path = json_file.relative_to(input_dir)
            output_file = Path(output_dir) / rel_path
            
            # Create output directory
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Read JSON file
            with open(json_file, 'r') as f:
                data = json.load(f)
            
            # Update sampling frequency
            if 'SamplingFrequency' in data:
                old_freq = data['SamplingFrequency']
                data['SamplingFrequency'] = 100
                print(f"  {rel_path}: {old_freq} Hz → 100 Hz")
            else:
                print(f"  {rel_path}: Adding SamplingFrequency = 100 Hz")
                data['SamplingFrequency'] = 100
            
            # Write updated JSON
            with open(output_file, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            print(f"  Error processing {json_file}: {e}")


def process_events_files(input_dir, output_dir):
    """Remove sample column from events.tsv files while preserving ALL 'n/a' values in all columns."""
    print("Processing events.tsv files...")
    
    # Find all events.tsv files
    events_files = list(Path(input_dir).rglob("*events.tsv"))
    
    for events_file in events_files:
        try:
            # Calculate relative path and output location
            rel_path = events_file.relative_to(input_dir)
            output_file = Path(output_dir) / rel_path
            
            # Create output directory
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Read events file with keep_default_na=False to preserve 'n/a' as literal strings
            # Only treat empty strings as missing values, not 'n/a'
            df = pd.read_csv(events_file, sep='\t', keep_default_na=False, na_values=[''])
            
            # Remove sample column if it exists
            if 'sample' in df.columns:
                df = df.drop('sample', axis=1)
                print(f"  {rel_path}: Removed 'sample' column")
            else:
                print(f"  {rel_path}: No 'sample' column found")
            
            # Ensure all empty cells that should be 'n/a' are properly set
            # Skip 'onset' column as it should contain numeric values
            for col in df.columns:
                if col != 'onset':  # Don't modify onset times
                    # Replace any remaining empty strings or NaN with 'n/a'
                    df[col] = df[col].fillna('n/a')
                    df[col] = df[col].replace('', 'n/a')
            
            # Write updated events file
            df.to_csv(output_file, sep='\t', index=False, na_rep='n/a')
            
        except Exception as e:
            print(f"  Error processing {events_file}: {e}")


def copy_other_files(input_dir, output_dir):
    """Copy other BIDS files (excluding .set, .fdt, .json, events.tsv)."""
    print("Copying other BIDS files...")
    
    # Extensions to skip (will be handled by MATLAB or other functions)
    skip_extensions = {'.set', '.fdt'}
    skip_patterns = {'_eeg.json', 'events.tsv'}
    
    for root, dirs, files in os.walk(input_dir):
        for file in files:
            # Skip files we handle elsewhere
            file_path = Path(root) / file
            
            # Check if we should skip this file
            skip_file = False
            
            # Skip by extension
            if file_path.suffix in skip_extensions:
                skip_file = True
            
            # Skip by pattern
            for pattern in skip_patterns:
                if pattern in file:
                    skip_file = True
                    break
            
            if skip_file:
                continue
            
            # Calculate output path
            rel_path = file_path.relative_to(input_dir)
            output_file = Path(output_dir) / rel_path
            
            # Create output directory
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Copy file
            try:
                shutil.copy2(file_path, output_file)
                print(f"  Copied: {rel_path}")
            except Exception as e:
                print(f"  Error copying {rel_path}: {e}")


def main():
    parser = argparse.ArgumentParser(description='Process EEG-BIDS metadata files')
    parser.add_argument('input_dir', help='Input directory (e.g., /Volumes/data/HBN/R5)')
    parser.add_argument('output_dir', help='Output directory (e.g., /Volumes/data/HBN/R5_L100)')
    
    args = parser.parse_args()
    
    input_dir = Path(args.input_dir)
    output_dir = Path(args.output_dir)
    
    if not input_dir.exists():
        print(f"Error: Input directory {input_dir} does not exist")
        return 1
    
    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Processing metadata files from {input_dir} to {output_dir}")
    print("=" * 60)
    
    # Process different file types
    update_json_files(input_dir, output_dir)
    print()
    process_events_files(input_dir, output_dir)
    print()
    copy_other_files(input_dir, output_dir)
    
    print("\n" + "=" * 60)
    print("Metadata processing complete!")


if __name__ == '__main__':
    main()