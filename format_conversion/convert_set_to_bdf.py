#!/usr/bin/env python3
"""
Convert EEGLAB SET files to BDF format using emgio.

This script scans for SET files in the HBN dataset and converts them to BDF format
while preserving the directory structure and generating conversion reports.

Usage: convert_set_to_bdf.py <INPUT_DIR> <OUTPUT_DIR>
"""

import os
import sys
import glob
import argparse
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


def create_output_path(set_file_path, dataset_path, output_dir):
    """Create output path maintaining directory structure."""
    # Get relative path from dataset root
    rel_path = os.path.relpath(set_file_path, dataset_path)
    
    # Replace .set extension with .bdf
    rel_path = rel_path.replace('.set', '.bdf')
    
    # Create output path directly in the output directory
    output_path = os.path.join(output_dir, rel_path)
    
    # Ensure output directory exists
    output_dir_path = os.path.dirname(output_path)
    os.makedirs(output_dir_path, exist_ok=True)
    
    # Return path without extension (emgio will add .bdf)
    return output_path.replace('.bdf', '')


def convert_set_to_bdf(set_file_path, output_path):
    """Convert a single SET file to BDF format."""
    try:
        print(f"Loading: {set_file_path}")
        
        # Load EEGLAB data
        emg = EMG.from_file(set_file_path, importer='eeglab')
        
        # Get basic info about the data
        info = {
            'input_file': set_file_path,
            'output_file': f"{output_path}.bdf",
            'channels': list(emg.signals.columns) if hasattr(emg, 'signals') else [],
            'n_channels': len(emg.signals.columns) if hasattr(emg, 'signals') else 0,
            'sampling_rate': emg.get_sampling_frequency() if hasattr(emg, 'get_sampling_frequency') else 'unknown',
            'duration_seconds': emg.get_duration() if hasattr(emg, 'get_duration') else 'unknown',
            'metadata': dict(emg.metadata) if hasattr(emg, 'metadata') else {}
        }
        
        # Force BDF format and export
        print(f"Exporting to: {output_path}.bdf")
        emg.to_edf(output_path, format='bdf')
        
        info['conversion_status'] = 'success'
        info['timestamp'] = datetime.now().isoformat()
        
        print(f"✓ Successfully converted: {set_file_path}")
        return info
        
    except Exception as e:
        error_info = {
            'input_file': set_file_path,
            'output_file': f"{output_path}.bdf",
            'conversion_status': 'error',
            'error_message': str(e),
            'error_traceback': traceback.format_exc(),
            'timestamp': datetime.now().isoformat()
        }
        print(f"✗ Error converting {set_file_path}: {e}")
        return error_info


def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description='Convert EEGLAB SET files to BDF format',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s /path/to/input/bids /path/to/output/bdf
  %(prog)s ~/data/eeg_set ~/data/eeg_bdf
        """
    )
    parser.add_argument('input_dir', help='Input directory containing SET files')
    parser.add_argument('output_dir', help='Output directory for BDF files')
    
    args = parser.parse_args()
    
    # Define paths from arguments
    dataset_path = os.path.abspath(args.input_dir)
    output_dir = os.path.abspath(args.output_dir)
    
    print("=" * 80)
    print("EEGLAB SET to BDF Conversion Script")
    print("=" * 80)
    print(f"Input directory: {dataset_path}")
    print(f"Output directory: {output_dir}")
    
    # Check if dataset exists
    if not os.path.exists(dataset_path):
        print(f"Error: Input directory does not exist: {dataset_path}")
        return 1
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Find all SET files
    print("\nScanning for SET files...")
    set_files = find_set_files(dataset_path)
    print(f"Found {len(set_files)} SET files")
    
    if len(set_files) == 0:
        print("No SET files found!")
        return 1
    
    # Create output directory for reports
    report_dir = os.path.join(output_dir, 'conversion_reports')
    os.makedirs(report_dir, exist_ok=True)
    
    # Initialize conversion report
    conversion_report = {
        'conversion_type': 'SET_to_BDF',
        'input_directory': dataset_path,
        'output_directory': output_dir,
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
            output_path = create_output_path(set_file, dataset_path, output_dir)
            
            # Convert the file
            result = convert_set_to_bdf(set_file, output_path)
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
    report_file = os.path.join(report_dir, f'bdf_conversion_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json')
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

