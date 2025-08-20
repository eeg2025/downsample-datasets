#!/usr/bin/env python3
"""
Convert EEGLAB SET files to EDF format using emgio.

This script scans for SET files in the HBN dataset and converts them to EDF format
while preserving the directory structure and generating conversion reports.
"""

import os
import sys
import glob
from pathlib import Path
import time
import json
import traceback
from datetime import datetime

try:
    from emgio import EMG
except ImportError:
    print("Error: emgio package not found.")
    print("Please install with: pip install git+https://github.com/neuromechanist/emgio.git")
    sys.exit(1)


def find_set_files(dataset_path):
    """Find all SET files in the dataset."""
    pattern = os.path.join(dataset_path, "**", "*.set")
    set_files = glob.glob(pattern, recursive=True)
    return sorted(set_files)


def create_output_path(set_file_path, dataset_path, output_base):
    """Create output path maintaining directory structure."""
    # Get relative path from dataset root
    rel_path = os.path.relpath(set_file_path, dataset_path)
    
    # Replace .set extension with .edf and adjust path for EDF output
    rel_path = rel_path.replace('.set', '.edf')
    
    # Create output path
    output_path = os.path.join(output_base, 'edf_converted', rel_path)
    
    # Ensure output directory exists
    output_dir = os.path.dirname(output_path)
    os.makedirs(output_dir, exist_ok=True)
    
    # Return path without extension (emgio will add .edf)
    return output_path.replace('.edf', '')


def convert_set_to_edf(set_file_path, output_path):
    """Convert a single SET file to EDF format."""
    try:
        print(f"Loading: {set_file_path}")
        
        # Load EEGLAB data
        emg = EMG.from_file(set_file_path, importer='eeglab')
        
        # Get basic info about the data
        info = {
            'input_file': set_file_path,
            'output_file': f"{output_path}.edf",
            'channels': list(emg.signals.columns) if hasattr(emg, 'signals') else [],
            'n_channels': len(emg.signals.columns) if hasattr(emg, 'signals') else 0,
            'sampling_rate': emg.get_sampling_frequency() if hasattr(emg, 'get_sampling_frequency') else 'unknown',
            'duration_seconds': emg.get_duration() if hasattr(emg, 'get_duration') else 'unknown',
            'metadata': dict(emg.metadata) if hasattr(emg, 'metadata') else {}
        }
        
        # Force EDF format and export
        print(f"Exporting to: {output_path}.edf")
        emg.to_edf(output_path, format='edf')
        
        info['conversion_status'] = 'success'
        info['timestamp'] = datetime.now().isoformat()
        
        print(f"✓ Successfully converted: {set_file_path}")
        return info
        
    except Exception as e:
        error_info = {
            'input_file': set_file_path,
            'output_file': f"{output_path}.edf",
            'conversion_status': 'error',
            'error_message': str(e),
            'error_traceback': traceback.format_exc(),
            'timestamp': datetime.now().isoformat()
        }
        print(f"✗ Error converting {set_file_path}: {e}")
        return error_info


def main():
    # Define paths
    dataset_path = "/Users/yahya/Library/CloudStorage/GoogleDrive-pulcher88@gmail.com/My Drive/to Share/HBN Minisets/hbn_bids_R5_L100"
    output_base = "/Users/yahya/Library/CloudStorage/GoogleDrive-pulcher88@gmail.com/My Drive/to Share/HBN Minisets"
    
    print("=" * 80)
    print("EEGLAB SET to EDF Conversion Script")
    print("=" * 80)
    print(f"Dataset path: {dataset_path}")
    print(f"Output base: {output_base}")
    
    # Check if dataset exists
    if not os.path.exists(dataset_path):
        print(f"Error: Dataset path does not exist: {dataset_path}")
        return 1
    
    # Find all SET files
    print("\nScanning for SET files...")
    set_files = find_set_files(dataset_path)
    print(f"Found {len(set_files)} SET files")
    
    if len(set_files) == 0:
        print("No SET files found!")
        return 1
    
    # Create output directory for reports
    report_dir = os.path.join(output_base, 'conversion_reports')
    os.makedirs(report_dir, exist_ok=True)
    
    # Initialize conversion report
    conversion_report = {
        'conversion_type': 'SET_to_EDF',
        'dataset_path': dataset_path,
        'output_base': output_base,
        'start_time': datetime.now().isoformat(),
        'total_files': len(set_files),
        'conversions': []
    }
    
    # Convert each file
    successful_conversions = 0
    failed_conversions = 0
    
    print(f"\nStarting conversion of {len(set_files)} files...")
    start_time = time.time()
    
    for i, set_file in enumerate(set_files, 1):
        print(f"\n[{i}/{len(set_files)}] Processing: {os.path.basename(set_file)}")
        
        try:
            # Create output path
            output_path = create_output_path(set_file, dataset_path, output_base)
            
            # Convert the file
            result = convert_set_to_edf(set_file, output_path)
            conversion_report['conversions'].append(result)
            
            if result['conversion_status'] == 'success':
                successful_conversions += 1
            else:
                failed_conversions += 1
                
        except Exception as e:
            print(f"✗ Unexpected error processing {set_file}: {e}")
            failed_conversions += 1
            conversion_report['conversions'].append({
                'input_file': set_file,
                'conversion_status': 'error',
                'error_message': f"Unexpected error: {str(e)}",
                'timestamp': datetime.now().isoformat()
            })
    
    # Finalize report
    end_time = time.time()
    conversion_report.update({
        'end_time': datetime.now().isoformat(),
        'duration_seconds': end_time - start_time,
        'successful_conversions': successful_conversions,
        'failed_conversions': failed_conversions,
        'success_rate': successful_conversions / len(set_files) if len(set_files) > 0 else 0
    })
    
    # Save detailed report
    report_file = os.path.join(report_dir, f'edf_conversion_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json')
    with open(report_file, 'w') as f:
        json.dump(conversion_report, f, indent=2)
    
    # Print summary
    print("\n" + "=" * 80)
    print("CONVERSION SUMMARY")
    print("=" * 80)
    print(f"Total files processed: {len(set_files)}")
    print(f"Successful conversions: {successful_conversions}")
    print(f"Failed conversions: {failed_conversions}")
    print(f"Success rate: {conversion_report['success_rate']:.1%}")
    print(f"Total time: {conversion_report['duration_seconds']:.1f} seconds")
    print(f"Average time per file: {conversion_report['duration_seconds']/len(set_files):.1f} seconds")
    print(f"\nDetailed report saved to: {report_file}")
    
    if failed_conversions > 0:
        print(f"\nFailed conversions:")
        for conv in conversion_report['conversions']:
            if conv['conversion_status'] == 'error':
                print(f"  - {os.path.basename(conv['input_file'])}: {conv['error_message']}")
    
    return 0 if failed_conversions == 0 else 1


if __name__ == "__main__":
    sys.exit(main())

