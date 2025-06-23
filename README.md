# ABCD Motion Regressor Generator

A Python-based tool for processing motion TSV files in a BIDS-like directory structure. This tool extracts and reformats motion regressors for analysis, handling files with potential misaligned data or unconventional formatting.

## Features

- **Automated Column Extraction**:
  - Processes motion TSV files, extracting specific columns required for analysis.
- **Handles Misaligned Data**:
  - Fixes rows with concatenated data into a single column.
- **Supports BIDS Naming**:
  - Compatible with subject/session/task/run BIDS-like directory structures.


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

    
    python main.py <data_dir> <subject> <session> <task> <run>
    


Positional Arguments:
- `<data_dir>`: Path to the directory containing the motion TSV files.
- `<subject>`: Subject identifier (e.g., `sub-01`).
- `<session>`: Session identifier (e.g., `ses-01`).
- `<task>`: Task identifier (e.g., `task-rest`).
- `<run>`: Run identifier (e.g., `run-01`). 

## Example:
    python main.py /path/to/data sub-01 ses-01 task-rest run-01
## Expected File Structure
The tool assumes the following directory structure:
```<data_dir>/
    <subject>/
        <session>/
            func/
                <subject>_<session>_task-<task>_<run>_desc-includingFD_motion.tsv
```
- Each motion TSV file should contain columns for translation and rotation parameters along with their respective derivatives.
- The script will create a new TSV file with the extracted and reformatted data.

- The output file will be named `<subject>_<session>_task-<task>_<run>_motion.tsv`.
- The output file will be saved in the same directory as the input file.

## Output
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

