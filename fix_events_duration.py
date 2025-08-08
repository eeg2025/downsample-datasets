#!/usr/bin/env python3
"""
Temporary fix script to add 'n/a' to empty duration and feedback columns 
in events.tsv files for processed EEG-BIDS datasets (R1_L100 to R12_L100).

This script fixes the issue where the process_metadata.py script was not 
preserving 'n/a' values when processing events.tsv files.

Usage: python fix_events_duration.py
"""

import os
import pandas as pd
from pathlib import Path

def fix_events_file(events_file_path):
    """Fix empty duration and feedback columns by setting them to 'n/a'."""
    try:
        # Read the events file
        df = pd.read_csv(events_file_path, sep='\t')
        
        # Check if duration column exists and fix empty values
        changes_made = False
        if 'duration' in df.columns:
            # Count empty values before fixing
            empty_duration_count = df['duration'].isna().sum() + (df['duration'] == '').sum()
            if empty_duration_count > 0:
                # Replace empty strings and NaN with 'n/a'
                df['duration'] = df['duration'].fillna('n/a')
                df['duration'] = df['duration'].replace('', 'n/a')
                changes_made = True
                print(f"    Fixed {empty_duration_count} empty duration values")
        
        # Check if feedback column exists and fix empty values
        if 'feedback' in df.columns:
            # Count empty values before fixing
            empty_feedback_count = df['feedback'].isna().sum() + (df['feedback'] == '').sum()
            if empty_feedback_count > 0:
                # Replace empty strings and NaN with 'n/a' (but preserve existing non-empty values)
                mask = (df['feedback'].isna()) | (df['feedback'] == '')
                df.loc[mask, 'feedback'] = 'n/a'
                changes_made = True
                print(f"    Fixed {empty_feedback_count} empty feedback values")
        
        # Write back only if changes were made
        if changes_made:
            df.to_csv(events_file_path, sep='\t', index=False)
            return True
        else:
            print("    No empty values found")
            return False
            
    except Exception as e:
        print(f"    Error processing {events_file_path}: {e}")
        return False


def fix_dataset(dataset_path):
    """Fix all events.tsv files in a dataset."""
    print(f"\nProcessing dataset: {dataset_path}")
    
    if not dataset_path.exists():
        print(f"  Dataset {dataset_path} does not exist, skipping...")
        return 0
    
    # Find all events.tsv files
    events_files = list(dataset_path.rglob("*events.tsv"))
    
    if not events_files:
        print("  No events.tsv files found")
        return 0
    
    print(f"  Found {len(events_files)} events.tsv files")
    fixed_count = 0
    
    for events_file in events_files:
        rel_path = events_file.relative_to(dataset_path)
        print(f"  Processing: {rel_path}")
        
        if fix_events_file(events_file):
            fixed_count += 1
    
    print(f"  Fixed {fixed_count}/{len(events_files)} files")
    return fixed_count


def main():
    """Main function to fix all R*_L100 datasets."""
    base_path = Path("/Volumes/data/HBN")
    
    if not base_path.exists():
        print(f"Error: Base path {base_path} does not exist")
        return 1
    
    print("Fixing empty duration and feedback columns in events.tsv files")
    print("=" * 70)
    
    total_fixed = 0
    total_datasets = 0
    
    # Process R1_L100 to R12_L100
    for r in range(1, 13):
        dataset_name = f"R{r}_L100"
        dataset_path = base_path / dataset_name
        
        fixed_count = fix_dataset(dataset_path)
        total_fixed += fixed_count
        total_datasets += 1
    
    print("\n" + "=" * 70)
    print(f"Processing complete!")
    print(f"Processed {total_datasets} datasets")
    print(f"Fixed events.tsv files with empty duration/feedback columns")
    
    return 0


if __name__ == '__main__':
    main()
