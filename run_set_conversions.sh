#!/bin/bash

# Script to run both EDF and BDF conversions of SET files using emgio
# This script activates the conda environment and runs both conversion scripts

set -e  # Exit on any error

echo "=============================================================================="
echo "SET to EDF/BDF Conversion Script"
echo "=============================================================================="
echo "This script will convert all SET files in the HBN dataset to both EDF and BDF formats"
echo ""

# Check if conda is available
if ! command -v conda &> /dev/null; then
    echo "Error: conda is not available. Please ensure conda is installed and in PATH."
    exit 1
fi

# Activate conda environment
echo "Activating conda environment: torch-312"
eval "$(conda shell.bash hook)"
conda activate torch-312

if [ $? -ne 0 ]; then
    echo "Error: Failed to activate conda environment torch-312"
    echo "Please ensure the environment exists: conda env list"
    exit 1
fi

echo "Successfully activated torch-312 environment"
echo ""

# Get current directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Make Python scripts executable
chmod +x "$SCRIPT_DIR/convert_set_to_edf.py"
chmod +x "$SCRIPT_DIR/convert_set_to_bdf.py"

echo "Starting EDF conversion..."
echo "------------------------------------------------------------------------------"
python "$SCRIPT_DIR/convert_set_to_edf.py"
EDF_STATUS=$?

echo ""
echo "Starting BDF conversion..."
echo "------------------------------------------------------------------------------"
python "$SCRIPT_DIR/convert_set_to_bdf.py"
BDF_STATUS=$?

echo ""
echo "=============================================================================="
echo "CONVERSION COMPLETE"
echo "=============================================================================="

if [ $EDF_STATUS -eq 0 ]; then
    echo "✓ EDF conversion completed successfully"
else
    echo "✗ EDF conversion completed with errors"
fi

if [ $BDF_STATUS -eq 0 ]; then
    echo "✓ BDF conversion completed successfully"
else
    echo "✗ BDF conversion completed with errors"
fi

echo ""
echo "Output directories:"
echo "  - EDF files: /Users/yahya/Library/CloudStorage/GoogleDrive-pulcher88@gmail.com/My Drive/to Share/HBN Minisets/edf_converted/"
echo "  - BDF files: /Users/yahya/Library/CloudStorage/GoogleDrive-pulcher88@gmail.com/My Drive/to Share/HBN Minisets/bdf_converted/"
echo "  - Reports:   /Users/yahya/Library/CloudStorage/GoogleDrive-pulcher88@gmail.com/My Drive/to Share/HBN Minisets/conversion_reports/"

if [ $EDF_STATUS -eq 0 ] && [ $BDF_STATUS -eq 0 ]; then
    echo ""
    echo "🎉 All conversions completed successfully!"
    exit 0
else
    echo ""
    echo "⚠️  Some conversions failed. Check the detailed reports for more information."
    exit 1
fi

