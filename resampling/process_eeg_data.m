function process_eeg_data(input_dir, output_dir)
% PROCESS_EEG_DATA - Process EEG .set files: filter, resample, and save
%
% Usage: process_eeg_data('/Volumes/data/HBN/R5', '/Volumes/data/HBN/R5_L100')
%
% This function:
% 1. Finds all .set files in the input directory
% 2. Loads each file with EEGLAB
% 3. Applies bandpass filter (0.5-50 Hz)
% 4. Resamples from 500 Hz to 100 Hz
% 5. Checks and validates events
% 6. Saves to the output directory maintaining folder structure
%
% (c) 8/2025, Seyed Yahya Shirazi, SCCN, INC, UCSD

if nargin < 2
    error('Usage: process_eeg_data(input_dir, output_dir)');
end

% Initialize EEGLAB
addpath('~/Documents/git/eeglab')  % Add EEGLAB to MATLAB path
if ~exist('eeglab', 'file')
    error('EEGLAB not found. Please add EEGLAB to your MATLAB path.');
end

% Start EEGLAB without GUI
fprintf('Initializing EEGLAB...\n');
eeglab nogui;

% Find all .set files
fprintf('Finding .set files in %s...\n', input_dir);
set_files = dir(fullfile(input_dir, '**', '*.set'));

if isempty(set_files)
    error('No .set files found in %s', input_dir);
end

fprintf('Found %d .set files to process.\n', length(set_files));

% Process each file
for i = 1:length(set_files)
    try
        % Current file info
        input_file = fullfile(set_files(i).folder, set_files(i).name);
        rel_path = strrep(set_files(i).folder, input_dir, '');
        if startsWith(rel_path, filesep)
            rel_path = rel_path(2:end);
        end
        output_folder = fullfile(output_dir, rel_path);
        output_file = fullfile(output_folder, set_files(i).name);
        
        fprintf('\n[%d/%d] Processing: %s\n', i, length(set_files), set_files(i).name);
        
        % Create output directory if it doesn't exist
        if ~exist(output_folder, 'dir')
            mkdir(output_folder);
        end
        
        % Skip if output file already exists
        if exist(output_file, 'file')
            fprintf('  Output file already exists, skipping...\n');
            continue;
        end
        
        % Load EEG data
        fprintf('  Loading EEG data...\n');
        EEG = pop_loadset(input_file);
        
        % Check original sampling rate
        if EEG.srate ~= 500
            fprintf('  Warning: Expected 500 Hz, found %.1f Hz\n', EEG.srate);
        end
        
        % Apply bandpass filter (0.5-50 Hz)
        fprintf('  Applying bandpass filter (0.5-50 Hz)...\n');
        EEG = pop_eegfiltnew(EEG, 'locutoff', 0.5, 'hicutoff', 50);
        
        % Resample to 100 Hz
        fprintf('  Resampling to 100 Hz...\n');
        EEG = pop_resample(EEG, 100);
        
        % Check events
        fprintf('  Checking events...\n');
        if ~isempty(EEG.event)
            fprintf('    Found %d events\n', length(EEG.event));
            
            % Validate event latencies are within bounds
            max_latency = EEG.pnts;
            invalid_events = [EEG.event.latency] > max_latency | [EEG.event.latency] < 1;
            if any(invalid_events)
                fprintf('    Warning: %d events have invalid latencies, removing them\n', sum(invalid_events));
                EEG.event(invalid_events) = [];
            end
        else
            fprintf('    No events found\n');
        end
        
        % Update dataset info
        EEG = eeg_checkset(EEG);
        
        % Save the processed data
        fprintf('  Saving to: %s\n', output_file);
        [output_path, output_name, output_ext] = fileparts(output_file);
        full_filename = [output_name, output_ext];
        EEG = pop_saveset(EEG, 'filename', full_filename, 'filepath', output_path);
        
        fprintf('  ✓ Successfully processed\n');
        
    catch ME
        fprintf('  ✗ Error processing file: %s\n', ME.message);
        continue;
    end
end

fprintf('\n=== Processing complete! ===\n');
fprintf('Processed files saved to: %s\n', output_dir);

end