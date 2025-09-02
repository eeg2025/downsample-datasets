#!/usr/bin/env python3
"""
Process BDF files to remove Cz reference channel and update channels.tsv files.

This script:
1. Loads BDF files with 129 channels (128 EEG + Cz reference)
2. Removes the Cz reference channel (channel 129)
3. Resaves the BDF with only 128 channels
4. Updates the channels.tsv file to remove Cz and set reference to 'Cz' for all channels
"""

import os
import sys
import glob
import argparse
import pandas as pd
import numpy as np
from pathlib import Path
import json
from datetime import datetime
import traceback
import shutil

try:
    from emgio import EMG
except ImportError:
    print("Error: emgio package not found.")
    print("Please install with: pip install git+https://github.com/neuromechanist/emgio.git")
    sys.exit(1)


def find_bdf_files(dataset_path):
    """Find all BDF files in the dataset."""
    pattern = os.path.join(dataset_path, "**", "*_eeg.bdf")
    bdf_files = glob.glob(pattern, recursive=True)
    return sorted(bdf_files)


def process_bdf_file(bdf_path, backup=True):
    """
    Process a single BDF file to remove Cz reference channel.
    
    Args:
        bdf_path: Path to the BDF file
        backup: Whether to create a backup of the original file
    
    Returns:
        dict: Processing result information
    """
    try:
        print(f"Processing: {bdf_path}")
        
        # Load the BDF file
        emg = EMG.from_file(bdf_path, importer='edf')
        
        # Check if we have 129 channels
        n_channels = len(emg.signals.columns)
        print(f"  Found {n_channels} channels")
        
        if n_channels != 129:
            return {
                'file': bdf_path,
                'status': 'skipped',
                'message': f'File has {n_channels} channels, expected 129',
                'timestamp': datetime.now().isoformat()
            }
        
        # Get channel names
        channel_names = list(emg.signals.columns)
        
        # Verify last channel is Cz
        if channel_names[-1] != 'Cz':
            print(f"  Warning: Last channel is '{channel_names[-1]}', not 'Cz'")
        
        # Remove the last channel (Cz)
        emg.signals = emg.signals.iloc[:, :-1]
        
        # Remove Cz from channels dictionary and fix channel types
        if hasattr(emg, 'channels'):
            if 'Cz' in emg.channels:
                del emg.channels['Cz']
                print(f"  Removed 'Cz' from channels dictionary")
            
            # Fix channel_type from EMG to EEG for all channels
            for ch_name in emg.channels:
                if 'channel_type' in emg.channels[ch_name]:
                    emg.channels[ch_name]['channel_type'] = 'EEG'
        
        # Create backup if requested
        if backup:
            backup_path = bdf_path + '.backup'
            if not os.path.exists(backup_path):
                shutil.copy2(bdf_path, backup_path)
                print(f"  Created backup: {backup_path}")
        
        # Save the modified BDF (without extension, emgio adds it)
        output_path = bdf_path.replace('.bdf', '')
        emg.to_edf(output_path, format='bdf', create_channels_tsv=False)
        print(f"  Saved modified BDF with {len(emg.signals.columns)} channels")
        
        return {
            'file': bdf_path,
            'status': 'success',
            'original_channels': n_channels,
            'final_channels': len(emg.signals.columns),
            'removed_channel': channel_names[-1],
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            'file': bdf_path,
            'status': 'error',
            'error': str(e),
            'traceback': traceback.format_exc(),
            'timestamp': datetime.now().isoformat()
        }


def update_channels_tsv(channels_tsv_path):
    """
    Update channels.tsv file to remove Cz and set reference to 'Cz' for all channels.
    
    Args:
        channels_tsv_path: Path to the channels.tsv file
    
    Returns:
        dict: Update result information
    """
    try:
        print(f"  Looking for channels.tsv: {os.path.basename(channels_tsv_path)}")
        
        # Read the channels.tsv file
        channels_df = pd.read_csv(channels_tsv_path, sep='\t')
        
        # Check if Cz is in the channels
        if 'Cz' not in channels_df['name'].values:
            return {
                'file': channels_tsv_path,
                'status': 'skipped',
                'message': 'Cz channel not found in channels.tsv',
                'timestamp': datetime.now().isoformat()
            }
        
        # Remove the Cz row
        original_count = len(channels_df)
        channels_df = channels_df[channels_df['name'] != 'Cz']
        
        # Update reference column to 'Cz' for all channels
        if 'reference' in channels_df.columns:
            channels_df['reference'] = 'Cz'
        else:
            # Add reference column if it doesn't exist
            channels_df['reference'] = 'Cz'
        
        # Ensure type column remains as EEG
        if 'type' in channels_df.columns:
            channels_df['type'] = 'EEG'
        
        # Create backup
        backup_path = channels_tsv_path + '.backup'
        if not os.path.exists(backup_path):
            shutil.copy2(channels_tsv_path, backup_path)
            print(f"  Created backup: {backup_path}")
        
        # Save the updated channels.tsv
        channels_df.to_csv(channels_tsv_path, sep='\t', index=False, na_rep='n/a')
        print(f"  Updated channels.tsv: {original_count} -> {len(channels_df)} channels")
        
        return {
            'file': channels_tsv_path,
            'status': 'success',
            'original_channels': original_count,
            'final_channels': len(channels_df),
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            'file': channels_tsv_path,
            'status': 'error',
            'error': str(e),
            'traceback': traceback.format_exc(),
            'timestamp': datetime.now().isoformat()
        }


def main():
    parser = argparse.ArgumentParser(
        description='Process BDF files to remove Cz reference channel',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s /Volumes/S1/Datasets/HBN/minisets/R6_mini_L100_bdf
  %(prog)s /path/to/bids/dataset --no-backup
        """
    )
    parser.add_argument('dataset_path', help='Path to BIDS dataset with BDF files')
    parser.add_argument('--no-backup', action='store_true', 
                       help='Do not create backup files')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be done without making changes')
    
    args = parser.parse_args()
    
    dataset_path = os.path.abspath(args.dataset_path)
    
    print("=" * 80)
    print("BDF Cz Reference Channel Removal")
    print("=" * 80)
    print(f"Dataset path: {dataset_path}")
    print(f"Create backups: {not args.no_backup}")
    print(f"Dry run: {args.dry_run}")
    
    if not os.path.exists(dataset_path):
        print(f"Error: Dataset path does not exist: {dataset_path}")
        return 1
    
    # Find all BDF files
    print("\nScanning for BDF files...")
    bdf_files = find_bdf_files(dataset_path)
    print(f"Found {len(bdf_files)} BDF files")
    
    if len(bdf_files) == 0:
        print("No BDF files found!")
        return 1
    
    # Initialize report
    report = {
        'dataset_path': dataset_path,
        'start_time': datetime.now().isoformat(),
        'dry_run': args.dry_run,
        'bdf_processing': [],
        'channels_tsv_updates': []
    }
    
    # Process each BDF file
    successful_bdf = 0
    failed_bdf = 0
    
    for i, bdf_path in enumerate(bdf_files, 1):
        print(f"\n[{i}/{len(bdf_files)}] {os.path.basename(bdf_path)}")
        
        if args.dry_run:
            print("  [DRY RUN] Would process this file")
            continue
        
        result = process_bdf_file(bdf_path, backup=not args.no_backup)
        report['bdf_processing'].append(result)
        
        if result['status'] == 'success':
            successful_bdf += 1
            
            # Look for corresponding channels.tsv with proper naming
            bdf_dir = os.path.dirname(bdf_path)
            bdf_basename = os.path.basename(bdf_path).replace('_eeg.bdf', '')
            channels_tsv_path = os.path.join(bdf_dir, f'{bdf_basename}_channels.tsv')
            
            if os.path.exists(channels_tsv_path):
                tsv_result = update_channels_tsv(channels_tsv_path)
                report['channels_tsv_updates'].append(tsv_result)
            else:
                print(f"  No channels.tsv found at: {channels_tsv_path}")
        else:
            failed_bdf += 1
    
    # Finalize report
    report['end_time'] = datetime.now().isoformat()
    report['bdf_files_processed'] = len(bdf_files)
    report['bdf_successful'] = successful_bdf
    report['bdf_failed'] = failed_bdf
    
    # Save report
    if not args.dry_run:
        report_path = os.path.join(dataset_path, f'cz_removal_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json')
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"\nReport saved to: {report_path}")
    
    # Print summary
    print("\n" + "=" * 80)
    print("PROCESSING SUMMARY")
    print("=" * 80)
    print(f"BDF files processed: {successful_bdf}/{len(bdf_files)}")
    print(f"Failed: {failed_bdf}")
    
    if not args.dry_run:
        tsv_successful = sum(1 for r in report['channels_tsv_updates'] if r['status'] == 'success')
        print(f"Channels.tsv files updated: {tsv_successful}")
    
    return 0 if failed_bdf == 0 else 1


if __name__ == "__main__":
    sys.exit(main())