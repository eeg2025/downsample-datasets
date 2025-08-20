# EEG Data Processing Pipeline

A comprehensive pipeline for processing, resampling, and converting EEG-BIDS datasets. Designed for the HBN (Healthy Brain Network) EEG datasets and the EEG2025 NeurIPS Challenge.

## 📁 Project Structure

```
resample_dataset/
│
├── resampling/              # EEG resampling and filtering tools
│   ├── process_eeg_data.m      # MATLAB script for filtering & resampling
│   └── process_metadata.py     # Update BIDS metadata after resampling
│
├── format_conversion/       # Format conversion tools
│   ├── convert_set_to_bdf.py   # Convert EEGLAB SET → BDF format
│   ├── convert_set_to_edf.py   # Convert EEGLAB SET → EDF format
│   └── complete_bids_datasets.py # Maintain BIDS structure after conversion
│
├── utils/                   # Utility and validation tools
│   ├── compare_signal_formats.py    # Compare signals between formats
│   ├── fix_events_duration.py       # Fix event duration issues
│   ├── signal_comparison_results/   # Comparison visualizations
│   └── SIGNAL_COMPARISON_SUMMARY.md # Detailed comparison report
│
├── run_eeg_processing.sh    # Main script for resampling pipeline
├── run_bdf_conversion.sh    # Main script for BDF conversion
├── LICENSE
└── README.md               # This file
```

## 🚀 Quick Start

### Resample EEG Data (500Hz → 100Hz)

```bash
./run_eeg_processing.sh /path/to/input/bids /path/to/output/resampled
```

### Convert to BDF Format

```bash
./run_bdf_conversion.sh /path/to/input/bids /path/to/output/bdf
```

## 🔧 Features

### 1. **EEG Resampling & Filtering**
- Downsamples EEG data from 500 Hz to 100 Hz
- Applies bandpass filter (0.5-50 Hz) to remove artifacts
- Validates and cleans event markers
- Updates BIDS metadata accordingly

### 2. **Format Conversion**
- Converts EEGLAB SET files to:
  - BDF (BioSemi Data Format)
  - EDF (European Data Format)
- Preserves all signal information and metadata
- Maintains complete BIDS structure

### 3. **Signal Validation**
- Compare signals between different formats
- Generate correlation plots and difference visualizations
- Produce detailed comparison reports

## 📋 Requirements

### For Resampling Pipeline
- **MATLAB** with **EEGLAB** toolbox installed
- **Python 3.x** with pandas
- **Bash shell** (macOS/Linux)

### For Format Conversion
- **Python 3.x** with:
  - pandas
  - emgio library (path: `/Users/yahya/Documents/git/emgio`)
- **Conda** environment: `torch-312`

## 📖 Detailed Usage

### Resampling Pipeline

The resampling pipeline processes an EEG-BIDS dataset to reduce sampling rate and apply filters:

```bash
./run_eeg_processing.sh <INPUT_DIR> <OUTPUT_DIR>
```

**What it does:**
1. **EEG Data (.set files)**:
   - Applies bandpass filter: 0.5-50 Hz
   - Resamples: 500 Hz → 100 Hz
   - Validates and cleans events

2. **JSON Metadata**:
   - Updates `SamplingFrequency` from 500 to 100

3. **Events Files**:
   - Removes `sample` column (tied to original 500 Hz sampling)

4. **Other Files**:
   - Copies unchanged to maintain BIDS structure

### Format Conversion Pipeline

Convert EEGLAB SET files to BDF or EDF format:

```bash
# For BDF conversion
./run_bdf_conversion.sh <INPUT_DIR> <OUTPUT_DIR>

# For EDF conversion (create your own script using convert_set_to_edf.py)
python3 format_conversion/convert_set_to_edf.py <INPUT_DIR> <OUTPUT_DIR>
```

**What it does:**
1. Converts all SET files to the specified format
2. Maintains complete BIDS directory structure
3. Updates metadata to reflect format change
4. Generates conversion reports

### Signal Comparison

Validate conversions by comparing signals:

```bash
python3 utils/compare_signal_formats.py <ORIGINAL_DIR> <CONVERTED_DIR>
```

This generates:
- Correlation plots for each file
- Signal difference visualizations
- Summary statistics report

## 📊 Processing Details

### Input Structure
```
/path/to/input/
├── dataset_description.json
├── participants.tsv
├── sub-*/
│   └── eeg/
│       ├── *.set (EEG data files)
│       ├── *.fdt (EEGLAB data files)
│       ├── *_eeg.json (metadata)
│       ├── *_events.tsv (event files)
│       └── other BIDS files
```

### Output Structure
```
/path/to/output/
├── dataset_description.json (updated)
├── participants.tsv (copied)
├── sub-*/
│   └── eeg/
│       ├── *.set/.bdf/.edf (processed/converted)
│       ├── *.fdt (if SET format)
│       ├── *_eeg.json (updated metadata)
│       ├── *_events.tsv (processed)
│       └── other BIDS files (copied)
```

## ⚡ Performance

- **Resampling**: ~1-2 minutes per subject
- **Format Conversion**: ~30 seconds per file
- **Resume Capability**: Skips already processed files
- **Error Handling**: Individual file errors don't stop the pipeline

## 🔍 Troubleshooting

### EEGLAB Not Found
```
Error: EEGLAB not found. Please add EEGLAB to your MATLAB path.
```
**Solution**: In MATLAB, run:
```matlab
addpath('/path/to/eeglab')
eeglab  % Initialize EEGLAB
```

### Conda Environment Missing
```
Error: Failed to activate torch-312 conda environment
```
**Solution**: Create the environment:
```bash
conda create -n torch-312 python=3.12
conda activate torch-312
pip install pandas
```

### MATLAB Not in PATH
```
Error: MATLAB not found. Please ensure MATLAB is in your PATH.
```
**Solution**: Add MATLAB to PATH or use full path:
```bash
export PATH="/Applications/MATLAB_R2023a.app/bin:$PATH"
```

## 📝 Notes

- Original data is never modified
- Output preserves complete BIDS structure
- Processing can be resumed if interrupted
- Events are validated and cleaned during resampling
- All conversions maintain signal fidelity

## 🤝 Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.

## 📄 License

See LICENSE file for details.

## 👥 Authors

Developed for processing HBN-EEG datasets for the EEG2025 NeurIPS Challenge.

---

For more information about BIDS format: https://bids.neuroimaging.io/
For EEGLAB documentation: https://eeglab.org/