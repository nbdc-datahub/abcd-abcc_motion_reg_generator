# ABCD Motion Regressor Generator

A BIDS App for processing motion TSV files in BIDS-compliant directory structures. This tool extracts and reformats motion regressors for analysis, handling files with potential misaligned data or unconventional formatting. 

## Features

- **BIDS Compliant**:
  - Designed to work with BIDS-like directory structures, specifically for subjects and sessions.
  - Follows BIDS App standards with participant/group analysis levels
  - Supports parallel processing of multiple participants
- **Automated Column Extraction**:
  - Processes motion TSV files, extracting specific columns required for analysis.
  - Fixes rows with concatenated data into a single column.
- **Automatic task run detection**:
  - Identifies count of  `rest run` based on the length of concatenated timeseries file.
  - Generates a motion TSV file with the extracted columns, only for the the runs that are not already present in the directory.
- **Flexible Processing**:
  - Process specific participants and sessions or all data
  - Supports both participant-level and group-level analysis
  - In-place processing (output written to same BIDS directory)


## Requirements

This project uses a Conda environment for managing dependencies.

### Setup the Environment

1. Create a new Conda environment using the `environment.yml` file:
   ```bash
   conda env create -f environment.yml

2. Activate the environment:
   ```bash
   conda activate abcd_motion_reg_generator
   
## Usage
Command-Line Interface  
Run the script with the following arguments:

    
    python run.py bids_dir {participant,group} [options]
    
**Positional Arguments**:
- `bids_dir`: The directory with the input dataset formatted according to the BIDS standard.
- `{participant,group}`: Level of analysis to perform
  - `participant`: Process individual participants (can run in parallel)
  - `group`: Process all participants and sessions in the bids directory
- **Note**: The `group` level analysis might take hours or even days depending on the size of the dataset and the number of participants.

**Optional Arguments**:
- `--participant_label PARTICIPANT_LABEL [PARTICIPANT_LABEL ...]`: 
  - The label(s) of participant(s) to analyze (without "sub-" prefix)
  - If not provided, all subjects will be processed
  - Multiple participants: `--participant_label 01 02 03`
- `--session_label SESSION_LABEL [SESSION_LABEL ...]`:
  - The label(s) of session(s) to analyze (without "ses-" prefix)
  - If not provided, all sessions will be processed
  - Multiple sessions: `--session_label 0A 0B`
- `-v, --version`: Show program version and exit
- `-h, --help`: Show help message and exit

## Example:
Process specific participant and session:

    python run.py /path/to/bids/data participant --participant_label 01 --session_label 0A
Process all participants and sessions:

    python run.py /path/to/bids/data group
Process multiple participants, sessions:

    python run.py /path/to/bids/data participant --participant_label 01 02 --session_label 0A 0B


## Expected File Structure
The tool assumes the following directory structure:
```<data_dir>/
    <subject>/
        <session>/
            func/
                sub-<participant>_ses-<session>_task-rest_bold_desc-filtered_timeseries.dtseries.nii
                sub-<participant>_ses-<session>_task-rest_run-01_desc-includingFD_motion.tsv
                sub-<participant>_ses-<session>_task-rest_run-01_desc-filteredincludingFD_motion.tsv
                sub-<participant>_ses-<session>_task-rest_run-02_desc-includingFD_motion.tsv
                sub-<participant>_ses-<session>_task-rest_run-02_desc-filteredincludingFD_motion.tsv
                ...
```
## Required Input Files:
- **Timeseries file**: `*_task-rest_bold_desc-filtered_timeseries.dtseries.nii`
  - Used to determine the number of rest runs 

- **Motion files**:
  - `*_desc-includingFD_motion.tsv`
  - `*_desc-filteredincludingFD_motion.tsv`
  - Each motion TSV file should contain columns for translation and rotation parameters along with their respective derivatives.
  - The script will create a new TSV file with the extracted and reformatted data.

- The output file will be named `<subject>_<session>_task-<task>_<run>_motion.tsv`.
- The output file will be saved in the same directory as the input file.

## Output
The tool processes input files and creates corresponding output files in the same directory:
- File Transformations:
  - `*_desc-includingFD_motion.tsv` → `*_motion.tsv`
  - `*_desc-filteredincludingFD_motion.tsv` → `*_desc-filtered_motion.tsv`
- Output Columns:
  The output TSV file will contain the following columns:
    - `X`: Translation in the x-direction.
    - `Y`: Translation in the y-direction.
    - `Z`: Translation in the z-direction.
    - `RotX`: Rotation around the x-axis.
    - `RotY`: Rotation around the y-axis.
    - `RotZ`: Rotation around the z-axis.   
    - `XDt`: Derivative of translation in the x-direction.
    - `YDt`: Derivative of translation in the y-direction.
    - `ZDt`: Derivative of translation in the z-direction.
    - `RotXDt`: Derivative of rotation around the x-axis.
    - `RotYDt`: Derivative of rotation around the y-axis.
    - `RotZDt`: Derivative of rotation around the z-axis.   

## Version Information
- Version: 1.0.0
- BIDS Version: 1.6.0
- Python: 3.7+

## Dependencies
- pandas
- nibabel
- pathlib
- argparse
- json
- logging
- pybids (optional, for enhanced BIDS support)
