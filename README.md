# EEG Data Processing Pipeline

This pipeline processes EEG-BIDS datasets from 500 Hz to 100 Hz with filtering and resampling.

## Overview

The pipeline processes an EEG-BIDS dataset (for example, at `/Volumes/data/HBN/R5`) and creates a new dataset at `/Volumes/data/HBN/R5_L100` with the following modifications. This is specifically designed for the HBN-EEG datasets for the EEG2025 NeurIPS Challenge.

1. **EEG Data (.set files)**:
   - Bandpass filter: 0.5-50 Hz
   - Resample: 500 Hz → 100 Hz
   - Validate events

2. **JSON Metadata**:
   - Update `SamplingFrequency` from 500 to 100

3. **Events Files**:
   - Remove `sample` column (tied to original 500 Hz sampling)

4. **Other Files**:
   - Copy unchanged to maintain BIDS structure

## Requirements

- **MATLAB** with **EEGLAB** installed and in the MATLAB path
- **Python 3** with **pandas** (will be installed automatically if missing)
- **Bash shell** (macOS/Linux)

## Usage

### Quick Start (Recommended)

```bash
./run_eeg_processing.sh
```

### Manual Steps

If you prefer to run steps individually:

1. **Process EEG data (MATLAB)**:

   ```matlab
   % In MATLAB:
   addpath('/path/to/this/directory');
   addpath('path/to/this/eeglab')
   process_eeg_data('/Volumes/data/HBN/R5', '/Volumes/data/HBN/R5_L100');
   ```

2. **Process metadata (Python)**:

   ```bash
   python3 process_metadata.py /Volumes/data/HBN/R5 /Volumes/data/HBN/R5_L100
   ```

## Files

- `run_eeg_processing.sh` - Main pipeline script
- `process_eeg_data.m` - MATLAB function for EEG processing
- `process_metadata.py` - Python script for metadata processing

## What Gets Processed

### Input Structure

```shell
/Volumes/data/HBN/R5/
├── sub-*/
│   └── eeg/
│       ├── *.set (EEG data files)
│       ├── *.fdt (EEGLAB data files)
│       ├── *_eeg.json (metadata)
│       ├── *_events.tsv (event files)
│       └── other BIDS files
```

### Output Structure

```shell
/Volumes/data/HBN/R5_L100/
├── sub-*/
│   └── eeg/
│       ├── *.set (processed: filtered + resampled)
│       ├── *.fdt (processed: filtered + resampled)
│       ├── *_eeg.json (updated: SamplingFrequency = 100)
│       ├── *_events.tsv (modified: sample column removed)
│       └── other BIDS files (copied)
```

## Processing Details

### MATLAB Processing (`process_eeg_data.m`)
- Loads each `.set` file using EEGLAB
- Applies bandpass filter (0.5-50 Hz) using `pop_eegfiltnew`
- Resamples to 100 Hz using `pop_resample`
- Validates event latencies after resampling
- Saves processed data maintaining original filenames

### Metadata Processing (`process_metadata.py`)
- Updates `SamplingFrequency` in all `*_eeg.json` files
- Removes `sample` column from all `*_events.tsv` files
- Copies other BIDS files unchanged

## Error Handling

- Files are processed individually - errors in one file won't stop the pipeline
- Existing output files are skipped (resume capability)
- Invalid events are automatically removed
- Detailed progress logging

## Performance

- Processing time depends on dataset size
- Typical processing: ~1-2 minutes per subject
- Progress is shown for each file
- Can be interrupted and resumed (skips existing outputs)

## Verification

After processing, the script will show file counts to verify completion:
- Input vs output .set files
- Input vs output JSON files  
- Input vs output events files

## Troubleshooting

### EEGLAB Not Found

```shell
Error: EEGLAB not found. Please add EEGLAB to your MATLAB path.
```

**Solution**: In MATLAB, run `addpath('/path/to/eeglab')` and `eeglab` to initialize.

### MATLAB Not in PATH

```shell
Error: MATLAB not found. Please ensure MATLAB is in your PATH.
```

**Solution**: Add MATLAB to your system PATH or run with full path: `/Applications/MATLAB_R2023a.app/bin/matlab`

### Python Dependencies
If pandas is missing, it will be installed automatically. For manual installation:

```bash
pip3 install pandas
```

## Notes

- Original data at `/Volumes/data/HBN/R5` is not modified
- Output preserves complete BIDS structure
- Processing can be resumed if interrupted
- Events are validated and cleaned during resampling
