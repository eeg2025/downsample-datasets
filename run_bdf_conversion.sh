#!/bin/bash

# BDF Conversion and BIDS Completion Pipeline
# This script converts SET files to BDF format and completes the BIDS structure
# 
# Usage: ./run_bdf_conversion.sh <INPUT_DIR> <OUTPUT_DIR>
#
# Arguments:
#   INPUT_DIR:  Path to input BIDS dataset directory containing SET files
#   OUTPUT_DIR: Path to output directory for BDF files and BIDS structure

set -e  # Exit on any error

# Check arguments
if [ $# -ne 2 ]; then
    echo "Error: Wrong number of arguments"
    echo "Usage: $0 <INPUT_DIR> <OUTPUT_DIR>"
    echo ""
    echo "Arguments:"
    echo "  INPUT_DIR:  Path to input BIDS dataset directory containing SET files"
    echo "  OUTPUT_DIR: Path to output directory for BDF files and BIDS structure"
    echo ""
    echo "Example:"
    echo "  $0 /path/to/input/bids /path/to/output/bdf"
    exit 1
fi

# Configuration
INPUT_DIR="$1"
OUTPUT_DIR="$2"

echo "=========================================="
echo "BDF Conversion and BIDS Completion Pipeline"
echo "=========================================="
echo "Input:  $INPUT_DIR"
echo "Output: $OUTPUT_DIR"
echo ""

# Check if input directory exists
if [ ! -d "$INPUT_DIR" ]; then
    echo "Error: Input directory $INPUT_DIR does not exist"
    exit 1
fi

# Check if Python is available
if ! command -v conda &> /dev/null; then
    echo "Error: Conda not found. Please ensure conda is in your PATH."
    exit 1
fi

# Activate conda environment
echo "Activating torch-312 conda environment..."
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate torch-312

if [ $? -ne 0 ]; then
    echo "Error: Failed to activate torch-312 conda environment"
    exit 1
fi

# Check if Python is available in the environment
if ! command -v python3 &> /dev/null; then
    echo "Error: Python3 not found in torch-312 environment."
    exit 1
fi

# Create output directory
echo "Creating output directory..."
mkdir -p "$OUTPUT_DIR"

echo ""
echo "=========================================="
echo "Step 1: Converting SET files to BDF format"
echo "=========================================="

# Run SET to BDF conversion
python3 format_conversion/convert_set_to_bdf.py "$INPUT_DIR" "$OUTPUT_DIR"

if [ $? -ne 0 ]; then
    echo "Error: SET to BDF conversion failed"
    exit 1
fi

echo ""
echo "=========================================="
echo "Step 2: Completing BIDS structure"
echo "=========================================="

# Run BIDS completion
python3 format_conversion/complete_bids_datasets.py "$INPUT_DIR" "$OUTPUT_DIR" "BDF"

if [ $? -ne 0 ]; then
    echo "Error: BIDS completion failed"
    exit 1
fi

echo ""
echo "=========================================="
echo "Step 3: Verification"
echo "=========================================="

# Count files
echo "File counts:"
echo "Input .set files:  $(find "$INPUT_DIR" -name "*.set" 2>/dev/null | wc -l)"
echo "Output .bdf files: $(find "$OUTPUT_DIR" -name "*.bdf" 2>/dev/null | wc -l)"
echo "Input JSON files:  $(find "$INPUT_DIR" -name "*_eeg.json" 2>/dev/null | wc -l)"
echo "Output JSON files: $(find "$OUTPUT_DIR" -name "*_eeg.json" 2>/dev/null | wc -l)"
echo "Input events files: $(find "$INPUT_DIR" -name "*events.tsv" 2>/dev/null | wc -l)"
echo "Output events files: $(find "$OUTPUT_DIR" -name "*events.tsv" 2>/dev/null | wc -l)"

echo ""
echo "=========================================="
echo "Processing Complete!"
echo "=========================================="
echo "Processed data saved to: $OUTPUT_DIR"
echo ""
echo "Summary of changes:"
echo "- EEG data: Converted from SET to BDF format"
echo "- JSON files: Copied with format information updated"
echo "- Events files: Copied unchanged"
echo "- BIDS structure: Complete metadata and directory structure"
echo ""
echo "You can now use the BDF dataset in $OUTPUT_DIR"

# Deactivate conda environment
echo ""
echo "Deactivating conda environment..."
conda deactivate