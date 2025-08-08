#!/usr/bin/env python3
"""
Temporary fix script to add 'n/a' to ALL empty cells in events.tsv files 
for processed EEG-BIDS datasets (R1_L100 to R12_L100).

This script fixes the issue where the process_metadata.py script was not 
preserving 'n/a' values when processing events.tsv files. It handles all 
columns that should contain 'n/a' for missing values (duration, value, 
user_answer, correct_answer, feedback, etc.) while preserving numeric columns.

Usage: python fix_events_duration.py
"""

import os
import pandas as pd
from pathlib import Path

def fix_events_file(events_file_path):
    """Fix ALL empty cells in events.tsv files by setting them to 'n/a'."""
    try:
        # Read the events file
        df = pd.read_csv(events_file_path, sep='\t')
        
        # Count total empty values before fixing
        total_empty_before = df.isna().sum().sum() + (df == '').sum().sum()
        
        if total_empty_before > 0:
            # Skip 'onset' column as it should contain numeric values, not 'n/a'
            # Also skip any purely numeric columns that shouldn't have 'n/a'
            columns_to_fix = []
            for col in df.columns:
                if col != 'onset':  # Don't modify onset times
                    # Check if column has any non-numeric string values (indicating it can have 'n/a')
                    sample_values = df[col].dropna().astype(str)
                    if len(sample_values) > 0:
                        # If any value contains non-numeric characters, treat as string column
                        has_strings = any(not val.replace('.', '').replace('-', '').isdigit() 
                                        for val in sample_values if val != '')
                        if has_strings or col in ['duration', 'value', 'event_code', 'feedback', 
                                                'user_answer', 'correct_answer']:
                            columns_to_fix.append(col)
            
            changes_made = False
            total_fixed = 0
            
            for col in columns_to_fix:
                # Count empty values in this column
                empty_count = df[col].isna().sum() + (df[col] == '').sum()
                if empty_count > 0:
                    # Replace empty strings and NaN with 'n/a'
                    df[col] = df[col].fillna('n/a')
                    df[col] = df[col].replace('', 'n/a')
                    total_fixed += empty_count
                    changes_made = True
                    print(f"    Fixed {empty_count} empty values in '{col}' column")
            
            # Write back only if changes were made
            if changes_made:
                df.to_csv(events_file_path, sep='\t', index=False)
                print(f"    Total fixed: {total_fixed} empty cells")
                return True
            else:
                print("    No empty values found in fixable columns")
                return False
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
    
    print("Fixing ALL empty cells in events.tsv files by replacing with 'n/a'")
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
    print(f"Fixed events.tsv files by replacing empty cells with 'n/a'")
    
    return 0


if __name__ == '__main__':
    main()
