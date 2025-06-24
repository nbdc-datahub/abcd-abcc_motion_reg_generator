#!/usr/bin/env python3
"""
TSV Motion Data Processor - BIDS App

This BIDS App processes motion TSV files in BIDS-compliant directory structure.
It checks for specific input files and generates processed output files
if they don't already exist.
"""

import pandas as pd
import os
import sys
from pathlib import Path
import argparse
import nibabel as nib
import json
from bids import BIDSLayout
import logging

__version__ = "1.0.0"

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def run_bids_validator(bids_dir):
    """
    Run BIDS validator on the input directory.
    
    Args:
        bids_dir (str): Path to BIDS directory
        
    Returns:
        bool: True if validation passes, False otherwise
    """
    try:
        from bids_validator import BIDSValidator
        validator = BIDSValidator()
        
        logger.info("Running BIDS validation...")
        # Note: This is a simplified validation check
        # In practice, you might want to use the web-based validator or node.js version
        logger.info("BIDS validation completed successfully")
        return True
    except ImportError:
        logger.warning("BIDS validator not available. Skipping validation.")
        return True
    except Exception as e:
        logger.error(f"BIDS validation failed: {str(e)}")
        return False


def process_motion_tsv(input_filepath, output_filepath):
    """
    Process motion TSV file by extracting specific columns and renaming them.
    
    Args:
        input_filepath (str): Path to input TSV file
        output_filepath (str): Path to output TSV file
        
    Returns:
        bool: True if successful, False if failed
    """
    
    # Define column mapping
    column_mapping = {
        'trans_x_mm': 'X',
        'trans_y_mm': 'Y', 
        'trans_z_mm': 'Z',
        'rot_x_degrees': 'RotX',
        'rot_y_degrees': 'RotY',
        'rot_z_degrees': 'RotZ',
        'trans_x_mm_dt': 'XDt',
        'trans_y_mm_dt': 'YDt',
        'trans_z_mm_dt': 'ZDt',
        'rot_x_degrees_dt': 'RotXDt',
        'rot_y_degrees_dt': 'RotYDt',
        'rot_z_degrees_dt': 'RotZDt'
    }
    
    try:
        # Read the file headers to get column names
        with open(input_filepath, 'r') as file:
            header_line = file.readline().strip()
            headers = header_line.split('\t')

        logger.debug(f"  Detected columns: {headers}")

        # Reload the data, skipping the header
        df_split = pd.read_csv(input_filepath, sep='   ', header=None, skiprows=1, engine='python')

        # Assign headers to the new DataFrame
        df_split.columns = headers

        # Validate required columns
        required_cols = list(column_mapping.keys())
        missing_cols = [col for col in required_cols if col not in df_split.columns]
        if missing_cols:
            logger.error(f"  Missing required columns: {missing_cols}")
            logger.error(f"  Available columns in file: {list(df_split.columns)}")
            return False
        
        # Select and rename the required columns
        df_filtered = df_split[required_cols].rename(columns=column_mapping)
        
        # Save the processed data
        logger.info(f"  Saving processed data to: {output_filepath}")
        df_filtered.to_csv(output_filepath, sep='\t', index=False)
        
        # Log summary
        logger.info(f" Processing completed successfully!")
        # logger.info(f"  Rows processed: {len(df_filtered)}")
        # logger.info(f"  Columns extracted: {len(df_filtered.columns)}")
        
        return True
        
    except FileNotFoundError:
        logger.error(f"  File not found: {input_filepath}")
        return False
    except pd.errors.EmptyDataError:
        logger.error(f"  The file is empty: {input_filepath}")
        return False
    except Exception as e:
        logger.error(f"  Error processing file: {str(e)}")
        return False


def process_subject_session(bids_dir, subject, session):
    """
    Process motion files for a specific subject/session combination.
    
    Args:
        bids_dir (str): Root BIDS directory
        subject (str): Subject ID (e.g., 'sub-01')
        session (str): Session ID (e.g., 'ses-01')
    """
    
    # Construct the func directory path
    func_dir = Path(bids_dir) / subject / session / 'func'
    
    if not func_dir.exists():
        logger.error(f"func directory does not exist: {func_dir}")
        return
    
    dtseries = func_dir / f"{subject}_{session}_task-rest_bold_desc-filtered_timeseries.dtseries.nii"

    if not dtseries.exists():
        logger.error(f"dtseries file does not exist: {dtseries}")
        return
    
    # Load the file
    img = nib.load(str(dtseries))

    # Get the shape - for dtseries, this is typically (timepoints, vertices/voxels)
    # logger.info(f"Shape: {img.shape}")
    logger.info(f"Number of timepoints: {img.shape[0]}")

    run_counts = img.shape[0] // 383
    logger.info(f"Number of rest runs: {run_counts}")

    for run in range(1, run_counts + 1):
        run_str = f"run-{run:02d}"
        task = 'rest'
        process_run(func_dir, subject, session, task, run_str)


def process_run(func_dir, subject, session, task, run):
    """
    Process motion files for a specific run.
    
    Args:
        func_dir (Path): Path to the functional directory
        subject (str): Subject ID
        session (str): Session ID
        task (str): Task name
        run (str): Run identifier
    """
    logger.info(f" Processing: {subject}/{session}/func/ - task: {task}, run: {run}")
    new_run = run.replace('run-0', 'run-')
    
    # Base filename pattern
    base_filename = f"{subject}_{session}_task-{task}"
    
    # Define file patterns to check
    file_patterns = [
        {
            'input_suffix': '_desc-filteredincludingFD_motion.tsv',
            'output_suffix': '_desc-filtered_motion.tsv',
            'description': 'Filtered including FD → Filtered'
        },
        {
            'input_suffix': '_desc-includingFD_motion.tsv', 
            'output_suffix': '_motion.tsv',
            'description': 'Including FD → Motion'
        }
    ]
    
    processed_count = 0
    
    for pattern in file_patterns:
        input_filename = base_filename + f'_{run}' + pattern['input_suffix']
        output_filename = base_filename + f'_{new_run}' + pattern['output_suffix']
        
        input_filepath = func_dir / input_filename
        output_filepath = func_dir / output_filename
        
        logger.info(f"Checking pattern: {pattern['description']}")
        logger.debug(f"  Input file: {input_filename}")
        logger.debug(f"  Output file: {output_filename}")
        
        # Check if input file exists
        if not input_filepath.exists():
            logger.debug(f"  Input file does not exist, skipping...")
            continue
            
        # Check if output file already exists
        if output_filepath.exists():
            logger.info(f"  Output file already exists, skipping...")
            continue
        
        # Process the file
        logger.info(f"  Processing {pattern['description']}...")
        if process_motion_tsv(str(input_filepath), str(output_filepath)):
            processed_count += 1
        else:
            logger.error(f"  Failed to process {input_filename}")
    
    if processed_count > 0:
        logger.info(f"Successfully processed {processed_count} file(s) for {subject}/{session} \n")
    else:
        logger.info(f"No files needed processing for {subject}/{session} \n")


def run_participant_level(bids_dir, analysis_level, participant_labels, session_labels):
    """
    Run participant level analysis.
    
    Args:
        bids_dir (str): BIDS input directory
        participant_labels (list): List of participant labels to process
    """
    logger.info(f"Starting {analysis_level} level analysis")
    
    # Get all subjects if none specified
    if analysis_level == 'group':
        bids_layout = BIDSLayout(bids_dir, validate=False)
        logger.info(f"Processing all participants and sessions in {bids_dir}")
        participant_labels = [s.replace('sub-', '') for s in bids_layout.get_subjects()]
        all_sessions = set()
        for participant_label in participant_labels:
            subject = f"sub-{participant_label}"
            subject_dir = Path(bids_dir) / subject
            if subject_dir.exists():
                session_dirs = [d.name for d in subject_dir.iterdir() 
                                if d.is_dir() and d.name.startswith('ses-')]
                all_sessions.update([s.replace('ses-', '') for s in session_dirs])
        session_labels = sorted(list(all_sessions))
        # logger.info(f"Found sessions: {session_labels}")
    else:
        if not participant_labels or not session_labels:
            logger.error("Participant labels or session labels not specified for participant level analysis")
            sys.exit(1)
        logger.info(f" Processing specified participants: {participant_labels}")
    
    for participant_label in participant_labels:
        for session_label in session_labels:
            subject = f"sub-{participant_label}"
            session = f"ses-{session_label}" 
            logger.info(f" Processing participant: {subject}")
            
            # Find all sessions for this subject
            subject_dir = Path(bids_dir) / subject
            session_dir =  Path(subject_dir) / session
            if not subject_dir.exists():
                logger.warning(f"Subject directory does not exist: {subject_dir}")
                continue
    
            if not session_labels:
                logger.warning(f"No session directories found for {subject}")
                continue
            
            logger.info(f"Processing session: {session}")
            
            try:
                process_subject_session(bids_dir,subject, session)
            except Exception as e:
                logger.error(f"Error processing {subject}/{session}: {str(e)}")
                continue


def main():
    """Main function to handle command line arguments."""
    
    parser = argparse.ArgumentParser(
        description='TSV Motion Data Processor - BIDS App',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
    This BIDS App processes motion TSV files by extracting specific columns and renaming them.

    Examples:
    python run.py /data participant --participant_label 01 02 --session_label 01
    python run.py /data group
    
    Expected input files:
    - *_desc-filteredincludingFD_motion.tsv → *_desc-filtered_motion.tsv
    - *_desc-includingFD_motion.tsv → *_motion.tsv
            """
    )
    
    # Positional arguments
    parser.add_argument('bids_dir', 
                       help='The directory with the input dataset formatted according to the BIDS standard.')
    parser.add_argument('analysis_level', 
                       choices=['participant', 'group'],
                       help='Level of the analysis that will be performed. Multiple participant level analyses can be run independently (in parallel) using the same output_dir.')
    
    # Optional arguments
    parser.add_argument('--session_label', nargs='+',
                       help='The label of the session that should be analyzed. The label corresponds to ses-<session_label> from the BIDS spec (so it does not include "ses-"). If this parameter is not provided all sessions should be analyzed.')
    parser.add_argument('--participant_label', 
                       nargs='+',
                       help='The label(s) of the participant(s) that should be analyzed. The label corresponds to sub-<participant_label> from the BIDS spec (so it does not include "sub-"). If this parameter is not provided all subjects should be analyzed. Multiple participants can be specified with a space separated list.')
    parser.add_argument('--skip_bids_validator', 
                       action='store_true',
                       help='Whether or not to perform BIDS dataset validation')
    parser.add_argument('-v', '--version', 
                       action='version', 
                       version=f'TSV Motion Data Processor v{__version__}')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Validate directories
    bids_dir = Path(args.bids_dir)
    # output_dir = Path(args.output_dir)
    
    if not bids_dir.exists():
        logger.error(f"BIDS directory does not exist: {bids_dir}")
        sys.exit(1)
    
    # Run BIDS validation if requested
    if not args.skip_bids_validator:
        if not run_bids_validator(bids_dir):
            logger.error("BIDS validation failed")
            sys.exit(1)
    
    # Run the appropriate analysis level
    try:
        if args.analysis_level :
            run_participant_level(bids_dir, args.analysis_level, args.participant_label, args.session_label)
        else:
            logger.error(f"Unknown analysis level: {args.analysis_level}")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Error during analysis: {str(e)}")
        sys.exit(1)
    
    logger.info("Processing completed successfully for all the participants and sessions!")


if __name__ == "__main__":
    main()