#!/bin/bash

# EEG Data Processing Pipeline
# This script processes EEG-BIDS data from 500 Hz to 100 Hz
# 
# Usage: ./run_eeg_processing.sh <INPUT_DIR> <OUTPUT_DIR>
#
# Arguments:
#   INPUT_DIR:  Path to input BIDS dataset directory
#   OUTPUT_DIR: Path to output directory for processed data

set -e  # Exit on any error

# Check arguments
if [ $# -ne 2 ]; then
    echo "Error: Wrong number of arguments"
    echo "Usage: $0 <INPUT_DIR> <OUTPUT_DIR>"
    echo ""
    echo "Arguments:"
    echo "  INPUT_DIR:  Path to input BIDS dataset directory"
    echo "  OUTPUT_DIR: Path to output directory for processed data"
    echo ""
    echo "Example:"
    echo "  $0 /path/to/input/bids /path/to/output/processed"
    exit 1
fi

# Configuration
INPUT_DIR="$1"
OUTPUT_DIR="$2"

echo "=========================================="
echo "EEG Data Processing Pipeline"
echo "=========================================="
echo "Input:  $INPUT_DIR"
echo "Output: $OUTPUT_DIR"
echo ""

# Check if input directory exists
if [ ! -d "$INPUT_DIR" ]; then
    echo "Error: Input directory $INPUT_DIR does not exist"
    exit 1
fi

# Check if MATLAB is available
if ! command -v matlab &> /dev/null; then
    echo "Error: MATLAB not found. Please ensure MATLAB is in your PATH."
    exit 1
fi

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python3 not found. Please ensure Python3 is in your PATH."
    exit 1
fi

# Create output directory
echo "Creating output directory..."
mkdir -p "$OUTPUT_DIR"

echo ""
echo "=========================================="
echo "Step 1: Processing EEG data with MATLAB"
echo "=========================================="

# Run MATLAB processing
matlab -batch "addpath('$(pwd)'); process_eeg_data('$INPUT_DIR', '$OUTPUT_DIR'); exit;"

if [ $? -ne 0 ]; then
    echo "Error: MATLAB processing failed"
    exit 1
fi

echo ""
echo "=========================================="
echo "Step 2: Processing metadata files"
echo "=========================================="

# Check if pandas is available
python3 -c "import pandas" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Installing pandas..."
    pip3 install pandas
fi

# Run metadata processing
python3 process_metadata.py "$INPUT_DIR" "$OUTPUT_DIR"

if [ $? -ne 0 ]; then
    echo "Error: Metadata processing failed"
    exit 1
fi

echo ""
echo "=========================================="
echo "Step 3: Verification"
echo "=========================================="

# Count files
echo "File counts:"
echo "Input .set files:  $(find "$INPUT_DIR" -name "*.set" | wc -l)"
echo "Output .set files: $(find "$OUTPUT_DIR" -name "*.set" | wc -l)"
echo "Input JSON files:  $(find "$INPUT_DIR" -name "*_eeg.json" | wc -l)"
echo "Output JSON files: $(find "$OUTPUT_DIR" -name "*_eeg.json" | wc -l)"
echo "Input events files: $(find "$INPUT_DIR" -name "*events.tsv" | wc -l)"
echo "Output events files: $(find "$OUTPUT_DIR" -name "*events.tsv" | wc -l)"

echo ""
echo "=========================================="
echo "Processing Complete!"
echo "=========================================="
echo "Processed data saved to: $OUTPUT_DIR"
echo ""
echo "Summary of changes:"
echo "- EEG data: Bandpass filtered (0.5-50 Hz) and resampled to 100 Hz"
echo "- JSON files: SamplingFrequency updated from 500 to 100"
echo "- Events files: 'sample' column removed"
echo "- Other BIDS files: Copied unchanged"
echo ""
echo "You can now use the processed data in $OUTPUT_DIR"