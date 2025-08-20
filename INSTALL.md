# Installation Guide

This guide provides step-by-step instructions for setting up the EEG Data Processing Pipeline.

## Prerequisites

### System Requirements
- Operating System: Linux, macOS, or Windows with WSL
- Python 3.8 or higher
- MATLAB (for resampling pipeline only)
- Git

### Check Python Version
```bash
python3 --version
```

## Installation Steps

### 1. Clone the Repository

```bash
git clone https://github.com/eeg2025/downsample-datasets.git
cd downsample-datasets
```

### 2. Create a Virtual Environment (Recommended)

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On Linux/macOS:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### 3. Install Python Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

This will install:
- `pandas` - Data manipulation and BIDS metadata handling
- `numpy` - Numerical operations
- `emgio` - EEG format conversion (automatically installed from GitHub)
- `matplotlib` - Visualization for signal comparison
- `scipy` - Signal processing utilities
- `joblib` - Parallel processing (optional)

### 4. Verify Installation

```bash
# Test Python imports
python3 -c "import pandas, numpy, matplotlib, scipy, emgio; print('All packages installed successfully!')"
```

## MATLAB Setup (For Resampling Only)

### 1. Install EEGLAB

1. Download EEGLAB from: https://eeglab.org/download/
2. Extract to a directory (e.g., `/opt/eeglab` or `C:\eeglab`)
3. Add EEGLAB to MATLAB path:

```matlab
% In MATLAB command window:
addpath('/path/to/eeglab')
savepath  % Save path permanently
eeglab    % Initialize EEGLAB
```

### 2. Test MATLAB Setup

```bash
# Test MATLAB availability
matlab -batch "disp('MATLAB is working'); exit"
```

## Usage Examples

### Basic Usage

```bash
# Resample EEG data
./run_eeg_processing.sh /path/to/input/bids /path/to/output/resampled

# Convert to BDF format
./run_bdf_conversion.sh /path/to/input/bids /path/to/output/bdf
```

### Python-Only Usage

```bash
# Convert formats directly
python3 format_conversion/convert_set_to_bdf.py /input/dir /output/dir

# Compare signals
python3 utils/compare_signal_formats.py /original/dir /converted/dir
```

## Troubleshooting

### Common Issues

#### 1. emgio Installation Fails
If `pip install -r requirements.txt` fails on emgio:

```bash
# Install emgio manually
pip install git+https://github.com/neuromechanist/emgio.git
```

#### 2. Permission Denied on Shell Scripts
```bash
# Make scripts executable
chmod +x run_eeg_processing.sh
chmod +x run_bdf_conversion.sh
```

#### 3. MATLAB Not Found
Ensure MATLAB is in your system PATH:

```bash
# Add to ~/.bashrc or ~/.zshrc
export PATH="/Applications/MATLAB_R2023a.app/bin:$PATH"  # macOS
export PATH="/usr/local/MATLAB/R2023a/bin:$PATH"        # Linux
```

#### 4. Python Package Conflicts
If you encounter package conflicts:

```bash
# Create a fresh virtual environment
python3 -m venv venv_fresh
source venv_fresh/bin/activate
pip install -r requirements.txt
```

## Development Setup

For contributing to the project:

```bash
# Install in development mode
pip install -e .

# Install development dependencies
pip install pytest black flake8
```

## Docker Setup (Optional)

For a fully reproducible environment:

```dockerfile
# Dockerfile (example)
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["/bin/bash"]
```

Build and run:
```bash
docker build -t eeg-pipeline .
docker run -it -v /path/to/data:/data eeg-pipeline
```

## Next Steps

After installation:
1. Read the [README](README.md) for detailed usage instructions
2. Check example data in the repository
3. Run test conversions on sample files
4. Report issues at: https://github.com/eeg2025/downsample-datasets/issues