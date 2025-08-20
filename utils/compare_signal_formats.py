#!/usr/bin/env python3
"""
Signal Comparison Script: SET vs EDF vs BDF formats

This script compares EEG signals between the original EEGLAB SET files
and the converted EDF/BDF formats to assess signal loss and format differences.

Features:
- Load data from all three formats using MNE-Python
- Calculate signal differences and correlation metrics
- Generate comparison plots for visual inspection
- Analyze signal quality metrics (SNR, spectral properties)
- Save detailed reports and plots as PNG files
"""

import os
import sys
import random
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import json
import warnings
from datetime import datetime

# MNE imports
import mne
from mne_bids import BIDSPath, read_raw_bids
from scipy import signal as sp_signal
from scipy.stats import pearsonr

# Suppress warnings for cleaner output
warnings.filterwarnings('ignore')
mne.set_log_level('WARNING')


def load_set_file(file_path):
    """Load EEGLAB SET file using MNE."""
    try:
        raw = mne.io.read_raw_eeglab(file_path, preload=True, verbose=False)
        return raw
    except Exception as e:
        print(f"Error loading SET file {file_path}: {e}")
        return None


def load_edf_file(file_path):
    """Load EDF file using MNE.""" 
    try:
        raw = mne.io.read_raw_edf(file_path, preload=True, verbose=False)
        return raw
    except Exception as e:
        print(f"Error loading EDF file {file_path}: {e}")
        return None


def load_bdf_file(file_path):
    """Load BDF file using MNE."""
    try:
        raw = mne.io.read_raw_bdf(file_path, preload=True, verbose=False)
        return raw
    except Exception as e:
        print(f"Error loading BDF file {file_path}: {e}")
        return None


def calculate_signal_metrics(raw1, raw2, label1, label2):
    """Calculate comprehensive signal comparison metrics between two raw objects."""
    
    # Get common channels
    common_channels = list(set(raw1.ch_names) & set(raw2.ch_names))
    if not common_channels:
        return None
    
    # Pick common channels and get data
    raw1_picked = raw1.copy().pick_channels(common_channels)
    raw2_picked = raw2.copy().pick_channels(common_channels)
    
    # Get data arrays
    data1 = raw1_picked.get_data()
    data2 = raw2_picked.get_data()
    
    # Ensure same length (truncate to shorter)
    min_length = min(data1.shape[1], data2.shape[1])
    data1 = data1[:, :min_length]
    data2 = data2[:, :min_length]
    
    metrics = {
        'common_channels': len(common_channels),
        'data_length': min_length,
        'sampling_rate_1': raw1_picked.info['sfreq'],
        'sampling_rate_2': raw2_picked.info['sfreq'],
        'channel_correlations': [],
        'mean_correlation': 0,
        'rms_error': 0,
        'max_absolute_diff': 0,
        'mean_absolute_diff': 0,
        'snr_ratio': 0,
        'spectral_similarity': 0
    }
    
    # Calculate per-channel correlations
    correlations = []
    for i in range(len(common_channels)):
        try:
            corr, _ = pearsonr(data1[i], data2[i])
            if not np.isnan(corr):
                correlations.append(corr)
        except:
            continue
    
    if correlations:
        metrics['channel_correlations'] = correlations
        metrics['mean_correlation'] = np.mean(correlations)
    
    # Calculate error metrics
    diff = data1 - data2
    metrics['rms_error'] = np.sqrt(np.mean(diff**2))
    metrics['max_absolute_diff'] = np.max(np.abs(diff))
    metrics['mean_absolute_diff'] = np.mean(np.abs(diff))
    
    # Calculate SNR-like metric
    signal_power = np.mean(data1**2)
    noise_power = np.mean(diff**2)
    if noise_power > 0:
        metrics['snr_ratio'] = 10 * np.log10(signal_power / noise_power)
    
    # Spectral similarity (using first channel for simplicity)
    if len(common_channels) > 0:
        try:
            f1, psd1 = sp_signal.welch(data1[0], fs=raw1_picked.info['sfreq'])
            f2, psd2 = sp_signal.welch(data2[0], fs=raw2_picked.info['sfreq'])
            
            # Interpolate to common frequency grid
            f_common = f1
            psd2_interp = np.interp(f_common, f2, psd2)
            
            # Calculate spectral correlation
            spec_corr, _ = pearsonr(psd1, psd2_interp)
            if not np.isnan(spec_corr):
                metrics['spectral_similarity'] = spec_corr
        except:
            pass
    
    return metrics


def create_comparison_plot(raw_set, raw_edf, raw_bdf, common_channels, output_path, title="Signal Comparison"):
    """Create a comprehensive comparison plot between the three formats."""
    
    # Select first 4 channels for plotting
    plot_channels = common_channels[:4]
    
    fig, axes = plt.subplots(len(plot_channels), 1, figsize=(15, 3*len(plot_channels)))
    if len(plot_channels) == 1:
        axes = [axes]
    
    # Time window for plotting (first 10 seconds)
    duration = 10.0  # seconds
    
    for i, ch_name in enumerate(plot_channels):
        ax = axes[i]
        
        # Get channel data
        ch_idx_set = raw_set.ch_names.index(ch_name)
        ch_idx_edf = raw_edf.ch_names.index(ch_name)  
        ch_idx_bdf = raw_bdf.ch_names.index(ch_name)
        
        # Get time points
        n_samples = int(duration * raw_set.info['sfreq'])
        times = np.arange(n_samples) / raw_set.info['sfreq']
        
        # Get data
        data_set = raw_set.get_data()[ch_idx_set, :n_samples]
        data_edf = raw_edf.get_data()[ch_idx_edf, :n_samples]
        data_bdf = raw_bdf.get_data()[ch_idx_bdf, :n_samples]
        
        # Plot signals
        ax.plot(times, data_set * 1e6, label='SET (Original)', alpha=0.8, linewidth=1)
        ax.plot(times, data_edf * 1e6, label='EDF (16-bit)', alpha=0.8, linewidth=1)
        ax.plot(times, data_bdf * 1e6, label='BDF (24-bit)', alpha=0.8, linewidth=1)
        
        ax.set_title(f'Channel: {ch_name}')
        ax.set_xlabel('Time (s)')
        ax.set_ylabel('Amplitude (µV)')
        ax.legend()
        ax.grid(True, alpha=0.3)
    
    plt.suptitle(title, fontsize=16)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()


def create_difference_plot(raw_set, raw_edf, raw_bdf, common_channels, output_path, title="Signal Differences"):
    """Create plots showing differences between formats."""
    
    plot_channels = common_channels[:4]
    
    fig, axes = plt.subplots(len(plot_channels), 2, figsize=(15, 3*len(plot_channels)))
    if len(plot_channels) == 1:
        axes = axes.reshape(1, -1)
    
    duration = 10.0  # seconds
    
    for i, ch_name in enumerate(plot_channels):
        # Get channel data
        ch_idx_set = raw_set.ch_names.index(ch_name)
        ch_idx_edf = raw_edf.ch_names.index(ch_name)
        ch_idx_bdf = raw_bdf.ch_names.index(ch_name)
        
        n_samples = int(duration * raw_set.info['sfreq'])
        times = np.arange(n_samples) / raw_set.info['sfreq']
        
        data_set = raw_set.get_data()[ch_idx_set, :n_samples]
        data_edf = raw_edf.get_data()[ch_idx_edf, :n_samples]
        data_bdf = raw_bdf.get_data()[ch_idx_bdf, :n_samples]
        
        # Plot SET - EDF difference
        diff_edf = (data_set - data_edf) * 1e6
        axes[i, 0].plot(times, diff_edf, 'r-', alpha=0.8, linewidth=1)
        axes[i, 0].set_title(f'{ch_name}: SET - EDF Difference')
        axes[i, 0].set_xlabel('Time (s)')
        axes[i, 0].set_ylabel('Difference (µV)')
        axes[i, 0].grid(True, alpha=0.3)
        
        # Plot SET - BDF difference
        diff_bdf = (data_set - data_bdf) * 1e6
        axes[i, 1].plot(times, diff_bdf, 'b-', alpha=0.8, linewidth=1)
        axes[i, 1].set_title(f'{ch_name}: SET - BDF Difference')
        axes[i, 1].set_xlabel('Time (s)')
        axes[i, 1].set_ylabel('Difference (µV)')
        axes[i, 1].grid(True, alpha=0.3)
    
    plt.suptitle(title, fontsize=16)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()


def create_correlation_heatmap(correlations_edf, correlations_bdf, output_path, title="Channel Correlations"):
    """Create heatmap showing correlations between formats."""
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    # Convert to arrays and create heatmaps
    if correlations_edf:
        corr_edf_array = np.array(correlations_edf).reshape(-1, 1)
        im1 = ax1.imshow(corr_edf_array.T, cmap='RdYlBu_r', vmin=0, vmax=1, aspect='auto')
        ax1.set_title('SET vs EDF Correlations')
        ax1.set_xlabel('Channel Index')
        plt.colorbar(im1, ax=ax1)
    
    if correlations_bdf:
        corr_bdf_array = np.array(correlations_bdf).reshape(-1, 1)
        im2 = ax2.imshow(corr_bdf_array.T, cmap='RdYlBu_r', vmin=0, vmax=1, aspect='auto')
        ax2.set_title('SET vs BDF Correlations')
        ax2.set_xlabel('Channel Index')
        plt.colorbar(im2, ax=ax2)
    
    plt.suptitle(title, fontsize=16)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()


def compare_file_trio(set_file, edf_file, bdf_file, output_dir, file_id):
    """Compare a trio of files (SET, EDF, BDF) and generate analysis."""
    
    print(f"\nProcessing file trio: {file_id}")
    print(f"SET: {os.path.basename(set_file)}")
    print(f"EDF: {os.path.basename(edf_file)}")
    print(f"BDF: {os.path.basename(bdf_file)}")
    
    # Load files
    raw_set = load_set_file(set_file)
    raw_edf = load_edf_file(edf_file)
    raw_bdf = load_bdf_file(bdf_file)
    
    if not all([raw_set, raw_edf, raw_bdf]):
        print("Failed to load one or more files, skipping...")
        return None
    
    # Find common channels
    common_channels = list(set(raw_set.ch_names) & set(raw_edf.ch_names) & set(raw_bdf.ch_names))
    if not common_channels:
        print("No common channels found, skipping...")
        return None
    
    print(f"Found {len(common_channels)} common channels")
    
    # Calculate metrics
    metrics_edf = calculate_signal_metrics(raw_set, raw_edf, "SET", "EDF")
    metrics_bdf = calculate_signal_metrics(raw_set, raw_bdf, "SET", "BDF")
    
    # Create output directory for this file
    file_output_dir = os.path.join(output_dir, f"file_{file_id}")
    os.makedirs(file_output_dir, exist_ok=True)
    
    # Generate plots
    comparison_plot_path = os.path.join(file_output_dir, f"{file_id}_signal_comparison.png")
    create_comparison_plot(raw_set, raw_edf, raw_bdf, common_channels, 
                          comparison_plot_path, f"File {file_id}: Signal Comparison")
    
    difference_plot_path = os.path.join(file_output_dir, f"{file_id}_signal_differences.png")
    create_difference_plot(raw_set, raw_edf, raw_bdf, common_channels,
                          difference_plot_path, f"File {file_id}: Signal Differences")
    
    correlation_plot_path = os.path.join(file_output_dir, f"{file_id}_correlations.png") 
    create_correlation_heatmap(metrics_edf['channel_correlations'] if metrics_edf else [],
                              metrics_bdf['channel_correlations'] if metrics_bdf else [],
                              correlation_plot_path, f"File {file_id}: Channel Correlations")
    
    # Compile results
    results = {
        'file_id': file_id,
        'files': {
            'set': os.path.basename(set_file),
            'edf': os.path.basename(edf_file),
            'bdf': os.path.basename(bdf_file)
        },
        'common_channels': len(common_channels),
        'metrics_edf': metrics_edf,
        'metrics_bdf': metrics_bdf,
        'plots': {
            'signal_comparison': comparison_plot_path,
            'signal_differences': difference_plot_path,
            'correlations': correlation_plot_path
        }
    }
    
    print(f"SET vs EDF - Mean correlation: {metrics_edf['mean_correlation']:.4f}, RMS error: {metrics_edf['rms_error']:.2e}")
    print(f"SET vs BDF - Mean correlation: {metrics_bdf['mean_correlation']:.4f}, RMS error: {metrics_bdf['rms_error']:.2e}")
    
    return results


def find_file_trios(set_dir, edf_dir, bdf_dir, n_files=10):
    """Find matching file trios across the three datasets."""
    
    # Get all SET files
    set_files = []
    for root, dirs, files in os.walk(set_dir):
        for file in files:
            if file.endswith('.set'):
                set_files.append(os.path.join(root, file))
    
    # Find matching trios
    trios = []
    
    for set_file in set_files:
        # Extract subject and task info from path
        rel_path = os.path.relpath(set_file, set_dir)
        
        # Convert SET path to EDF/BDF paths
        edf_file = os.path.join(edf_dir, rel_path.replace('.set', '.edf'))
        bdf_file = os.path.join(bdf_dir, rel_path.replace('.set', '.bdf'))
        
        if os.path.exists(edf_file) and os.path.exists(bdf_file):
            trios.append((set_file, edf_file, bdf_file))
    
    # Randomly select n_files
    if len(trios) > n_files:
        trios = random.sample(trios, n_files)
    
    return trios


def create_summary_plots(all_results, output_dir):
    """Create summary plots across all compared files."""
    
    # Extract metrics for plotting
    correlations_edf = []
    correlations_bdf = []
    rms_errors_edf = []
    rms_errors_bdf = []
    snr_ratios_edf = []
    snr_ratios_bdf = []
    
    for result in all_results:
        if result['metrics_edf']:
            correlations_edf.append(result['metrics_edf']['mean_correlation'])
            rms_errors_edf.append(result['metrics_edf']['rms_error'])
            snr_ratios_edf.append(result['metrics_edf']['snr_ratio'])
        
        if result['metrics_bdf']:
            correlations_bdf.append(result['metrics_bdf']['mean_correlation'])
            rms_errors_bdf.append(result['metrics_bdf']['rms_error'])
            snr_ratios_bdf.append(result['metrics_bdf']['snr_ratio'])
    
    # Create summary plots
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    
    # Correlation comparison
    axes[0, 0].boxplot([correlations_edf, correlations_bdf], labels=['SET vs EDF', 'SET vs BDF'])
    axes[0, 0].set_title('Signal Correlations')
    axes[0, 0].set_ylabel('Correlation Coefficient')
    axes[0, 0].grid(True, alpha=0.3)
    
    # RMS Error comparison
    axes[0, 1].boxplot([rms_errors_edf, rms_errors_bdf], labels=['SET vs EDF', 'SET vs BDF'])
    axes[0, 1].set_title('RMS Errors')
    axes[0, 1].set_ylabel('RMS Error')
    axes[0, 1].set_yscale('log')
    axes[0, 1].grid(True, alpha=0.3)
    
    # SNR comparison
    axes[1, 0].boxplot([snr_ratios_edf, snr_ratios_bdf], labels=['SET vs EDF', 'SET vs BDF'])
    axes[1, 0].set_title('Signal-to-Noise Ratios')
    axes[1, 0].set_ylabel('SNR (dB)')
    axes[1, 0].grid(True, alpha=0.3)
    
    # Scatter plot: Correlation vs RMS Error
    axes[1, 1].scatter(correlations_edf, rms_errors_edf, label='SET vs EDF', alpha=0.7)
    axes[1, 1].scatter(correlations_bdf, rms_errors_bdf, label='SET vs BDF', alpha=0.7)
    axes[1, 1].set_xlabel('Correlation')
    axes[1, 1].set_ylabel('RMS Error')
    axes[1, 1].set_yscale('log')
    axes[1, 1].set_title('Correlation vs RMS Error')
    axes[1, 1].legend()
    axes[1, 1].grid(True, alpha=0.3)
    
    plt.suptitle('Signal Format Comparison Summary', fontsize=16)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'summary_comparison.png'), dpi=300, bbox_inches='tight')
    plt.close()


def main():
    """Main function to run signal comparison analysis."""
    
    # Dataset paths
    set_dataset = "/Users/yahya/Library/CloudStorage/GoogleDrive-pulcher88@gmail.com/My Drive/to Share/HBN Minisets/hbn_bids_R5_L100"
    edf_dataset = "/Users/yahya/Library/CloudStorage/GoogleDrive-pulcher88@gmail.com/My Drive/to Share/HBN Minisets/hbn_bids_R5_edf" 
    bdf_dataset = "/Users/yahya/Library/CloudStorage/GoogleDrive-pulcher88@gmail.com/My Drive/to Share/HBN Minisets/hbn_bids_R5_bdf"
    
    # Output directory
    output_dir = "/Users/yahya/Documents/git/resample_dataset/signal_comparison_results"
    os.makedirs(output_dir, exist_ok=True)
    
    print("=" * 80)
    print("EEG Signal Format Comparison: SET vs EDF vs BDF")
    print("=" * 80)
    print(f"SET Dataset: {set_dataset}")
    print(f"EDF Dataset: {edf_dataset}")
    print(f"BDF Dataset: {bdf_dataset}")
    print(f"Output Directory: {output_dir}")
    
    # Find file trios to compare
    print("\nFinding matching file trios...")
    trios = find_file_trios(set_dataset, edf_dataset, bdf_dataset, n_files=10)
    print(f"Found {len(trios)} matching file trios")
    
    if not trios:
        print("No matching file trios found!")
        return 1
    
    # Process each trio
    all_results = []
    for i, (set_file, edf_file, bdf_file) in enumerate(trios, 1):
        try:
            result = compare_file_trio(set_file, edf_file, bdf_file, output_dir, f"{i:02d}")
            if result:
                all_results.append(result)
        except Exception as e:
            print(f"Error processing trio {i}: {e}")
            continue
    
    if not all_results:
        print("No successful comparisons!")
        return 1
    
    # Create summary plots
    print(f"\nCreating summary plots...")
    create_summary_plots(all_results, output_dir)
    
    # Save detailed results
    results_file = os.path.join(output_dir, 'comparison_results.json')
    with open(results_file, 'w') as f:
        json.dump(all_results, f, indent=2, default=str)
    
    # Print summary statistics
    print("\n" + "=" * 80)
    print("COMPARISON SUMMARY")
    print("=" * 80)
    
    correlations_edf = [r['metrics_edf']['mean_correlation'] for r in all_results if r['metrics_edf']]
    correlations_bdf = [r['metrics_bdf']['mean_correlation'] for r in all_results if r['metrics_bdf']]
    
    rms_errors_edf = [r['metrics_edf']['rms_error'] for r in all_results if r['metrics_edf']]
    rms_errors_bdf = [r['metrics_bdf']['rms_error'] for r in all_results if r['metrics_bdf']]
    
    if correlations_edf:
        print(f"SET vs EDF:")
        print(f"  Mean correlation: {np.mean(correlations_edf):.4f} ± {np.std(correlations_edf):.4f}")
        print(f"  Median RMS error: {np.median(rms_errors_edf):.2e}")
    
    if correlations_bdf:
        print(f"SET vs BDF:")
        print(f"  Mean correlation: {np.mean(correlations_bdf):.4f} ± {np.std(correlations_bdf):.4f}")
        print(f"  Median RMS error: {np.median(rms_errors_bdf):.2e}")
    
    print(f"\nTotal files compared: {len(all_results)}")
    print(f"Results saved to: {output_dir}")
    print(f"Detailed results: {results_file}")
    
    return 0


if __name__ == "__main__":
    exit(main())
