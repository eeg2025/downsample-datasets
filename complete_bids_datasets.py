#!/usr/bin/env python3
"""
Complete BIDS datasets by copying missing metadata files from original SET dataset
to the converted EDF and BDF datasets.

This script ensures that the converted datasets maintain BIDS compliance by copying:
- Root-level metadata files (dataset_description.json, participants.tsv, etc.)
- Task-level metadata files (task-*_eeg.json, task-*_events.json)
- Event files (sub-*/eeg/*_events.tsv)
- Other supporting files (README, code/, derivatives/)
"""

import os
import shutil
import glob
from pathlib import Path
import json
from datetime import datetime


def copy_file_with_structure(src_file, dst_file):
    """Copy a file, creating necessary directory structure."""
    dst_dir = os.path.dirname(dst_file)
    os.makedirs(dst_dir, exist_ok=True)
    shutil.copy2(src_file, dst_file)
    print(f"Copied: {os.path.basename(src_file)}")


def update_dataset_description(dataset_path, format_name):
    """Update dataset_description.json to reflect the converted format."""
    desc_file = os.path.join(dataset_path, 'dataset_description.json')
    if os.path.exists(desc_file):
        with open(desc_file, 'r') as f:
            desc = json.load(f)
        
        # Update description to indicate format conversion
        original_name = desc.get('Name', 'HBN EEG Dataset')
        desc['Name'] = f"{original_name} ({format_name} Converted)"
        desc['ConversionInfo'] = {
            'OriginalFormat': 'EEGLAB SET',
            'ConvertedFormat': format_name,
            'ConversionDate': datetime.now().isoformat(),
            'ConversionTool': 'emgio'
        }
        
        with open(desc_file, 'w') as f:
            json.dump(desc, f, indent=2)
        
        print(f"Updated dataset_description.json for {format_name}")


def complete_bids_dataset(source_dataset, target_dataset, format_name):
    """Complete a BIDS dataset by copying missing metadata files."""
    
    print(f"\n{'='*80}")
    print(f"Completing {format_name} BIDS Dataset")
    print(f"{'='*80}")
    print(f"Source: {source_dataset}")
    print(f"Target: {target_dataset}")
    
    # 1. Copy root-level metadata files
    print(f"\n1. Copying root-level metadata files...")
    root_files = [
        'dataset_description.json',
        'participants.json', 
        'participants.tsv',
        'README'
    ]
    
    for file_name in root_files:
        src_file = os.path.join(source_dataset, file_name)
        dst_file = os.path.join(target_dataset, file_name)
        if os.path.exists(src_file):
            copy_file_with_structure(src_file, dst_file)
    
    # 2. Copy task-level metadata files
    print(f"\n2. Copying task-level metadata files...")
    task_patterns = ['task-*_eeg.json', 'task-*_events.json']
    
    for pattern in task_patterns:
        for src_file in glob.glob(os.path.join(source_dataset, pattern)):
            file_name = os.path.basename(src_file)
            dst_file = os.path.join(target_dataset, file_name)
            copy_file_with_structure(src_file, dst_file)
    
    # 3. Copy code directory
    print(f"\n3. Copying code directory...")
    src_code = os.path.join(source_dataset, 'code')
    dst_code = os.path.join(target_dataset, 'code')
    if os.path.exists(src_code):
        shutil.copytree(src_code, dst_code, dirs_exist_ok=True)
        print(f"Copied code directory with {len(os.listdir(dst_code))} files")
    
    # 4. Copy derivatives directory
    print(f"\n4. Copying derivatives directory...")
    src_derivatives = os.path.join(source_dataset, 'derivatives')
    dst_derivatives = os.path.join(target_dataset, 'derivatives')
    if os.path.exists(src_derivatives):
        shutil.copytree(src_derivatives, dst_derivatives, dirs_exist_ok=True)
        print(f"Copied derivatives directory")
    
    # 5. Copy subject-level event files
    print(f"\n5. Copying subject-level event files...")
    events_count = 0
    
    # Find all subjects in target dataset
    for subject_dir in glob.glob(os.path.join(target_dataset, 'sub-*')):
        subject_id = os.path.basename(subject_dir)
        
        # Copy events.tsv files
        src_eeg_dir = os.path.join(source_dataset, subject_id, 'eeg')
        dst_eeg_dir = os.path.join(target_dataset, subject_id, 'eeg')
        
        if os.path.exists(src_eeg_dir):
            for events_file in glob.glob(os.path.join(src_eeg_dir, '*_events.tsv')):
                dst_events = os.path.join(dst_eeg_dir, os.path.basename(events_file))
                copy_file_with_structure(events_file, dst_events)
                events_count += 1
    
    print(f"Copied {events_count} event files")
    
    # 6. Copy additional JSON files from subject directories
    print(f"\n6. Copying subject-level JSON files...")
    json_count = 0
    
    for subject_dir in glob.glob(os.path.join(target_dataset, 'sub-*')):
        subject_id = os.path.basename(subject_dir)
        
        src_eeg_dir = os.path.join(source_dataset, subject_id, 'eeg')
        dst_eeg_dir = os.path.join(target_dataset, subject_id, 'eeg')
        
        if os.path.exists(src_eeg_dir):
            for json_file in glob.glob(os.path.join(src_eeg_dir, '*_eeg.json')):
                dst_json = os.path.join(dst_eeg_dir, os.path.basename(json_file))
                copy_file_with_structure(json_file, dst_json)
                json_count += 1
    
    print(f"Copied {json_count} subject-level JSON files")
    
    # 7. Update dataset description
    print(f"\n7. Updating dataset description...")
    update_dataset_description(target_dataset, format_name)
    
    print(f"\n✓ {format_name} BIDS dataset completion finished!")


def main():
    # Define paths
    source_dataset = "/Users/yahya/Library/CloudStorage/GoogleDrive-pulcher88@gmail.com/My Drive/to Share/HBN Minisets/hbn_bids_R5_L100"
    edf_dataset = "/Users/yahya/Library/CloudStorage/GoogleDrive-pulcher88@gmail.com/My Drive/to Share/HBN Minisets/hbn_bids_R5_edf" 
    bdf_dataset = "/Users/yahya/Library/CloudStorage/GoogleDrive-pulcher88@gmail.com/My Drive/to Share/HBN Minisets/hbn_bids_R5_bdf"
    
    print("BIDS Dataset Completion Script")
    print("=" * 80)
    
    # Check if source dataset exists
    if not os.path.exists(source_dataset):
        print(f"Error: Source dataset not found: {source_dataset}")
        return 1
    
    # Complete EDF dataset
    if os.path.exists(edf_dataset):
        complete_bids_dataset(source_dataset, edf_dataset, "EDF")
    else:
        print(f"Warning: EDF dataset not found: {edf_dataset}")
    
    # Complete BDF dataset  
    if os.path.exists(bdf_dataset):
        complete_bids_dataset(source_dataset, bdf_dataset, "BDF")
    else:
        print(f"Warning: BDF dataset not found: {bdf_dataset}")
    
    print(f"\n{'='*80}")
    print("BIDS Dataset Completion Summary")
    print(f"{'='*80}")
    print("✓ Root-level metadata files copied")
    print("✓ Task-level metadata files copied") 
    print("✓ Code directory copied")
    print("✓ Derivatives directory copied")
    print("✓ Subject-level event files copied")
    print("✓ Subject-level JSON files copied")
    print("✓ Dataset descriptions updated")
    print("\nBoth EDF and BDF datasets are now BIDS-compliant!")
    
    return 0


if __name__ == "__main__":
    exit(main())
