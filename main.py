#!/usr/bin/env python3
"""
TSV Motion Data Processor

This tool processes motion TSV files in BIDS-like directory structure.
It checks for specific input files and generates processed output files
if they don't already exist.
"""

import pandas as pd
import os
import sys
from pathlib import Path
import argparse


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

        print(f"  Detected columns: {headers}")

        # Reload the data, skipping the header
        df_split = pd.read_csv(input_filepath, sep='   ', header=None, skiprows=1, engine='python')
        # print(df_split.head())

        # Assign headers to the new DataFrame
        df_split.columns = headers
        # print(df_split.head())

        # Validate required columns
        required_cols = list(column_mapping.keys())
        missing_cols = [col for col in required_cols if col not in df_split.columns]
        if missing_cols:
            print(f"  Error: Missing required columns: {missing_cols}")
            print(f"  Available columns in file: {list(df_split.columns)}")
            return False
        
        # Select and rename the required columns
        df_filtered = df_split[required_cols].rename(columns=column_mapping)
        
        # print(f"  Filtered dataframe shape: {df_filtered.shape}")
        # print(f"  Filtered columns: {list(df_filtered.columns)}")
        # print(f"  First row sample: {df_filtered.iloc[0].to_dict()}")
        
        # Save the processed data
        print(f"  Saving processed data to: {output_filepath}")
        df_filtered.to_csv(output_filepath, sep='\t', index=False)
        
        # Print summary
        print(f"  ✓ Processing completed successfully!")
        print(f"  Rows processed: {len(df_filtered)}")
        print(f"  Columns extracted: {len(df_filtered.columns)}")
        
        return True
        
    except FileNotFoundError:
        print(f"  Error: File not found: {input_filepath}")
        return False
    except pd.errors.EmptyDataError:
        print(f"  Error: The file is empty: {input_filepath}")
        return False
    except Exception as e:
        print(f"  Error processing file: {str(e)}")
        return False


def process_subject_session(data_dir, subject, session, task, run):
    """
    Process motion files for a specific subject/session/task/run combination.
    
    Args:
        data_dir (str): Root data directory
        subject (str): Subject ID (e.g., 'sub-01')
        session (str): Session ID (e.g., 'ses-01')
        task (str): Task name (e.g., 'rest')
        run (str): Run number (e.g., 'run-01')
    """
    
    # Construct the func directory path
    func_dir = Path(data_dir) / subject / session / 'func'
    
    if not func_dir.exists():
        print(f"Error: func directory does not exist: {func_dir}")
        return
    
    print(f"\nProcessing: {subject}/{session}/func/ - task: {task}, run: {run}")
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
        output_filename = base_filename+ f'_{new_run}' + pattern['output_suffix']
        
        input_filepath = func_dir / input_filename
        output_filepath = func_dir / output_filename
        
        print(f"\nChecking pattern: {pattern['description']}")
        print(f"  Input file: {input_filename}")
        print(f"  Output file: {output_filename}")
        
        # Check if input file exists
        if not input_filepath.exists():
            print(f"  Input file does not exist, skipping...")
            continue
            
        # Check if output file already exists
        if output_filepath.exists():
            print(f"  Output file already exists, skipping...")
            continue
        
        # Process the file
        print(f"  Processing {pattern['description']}...")
        if process_motion_tsv(str(input_filepath), str(output_filepath)):
            processed_count += 1
        else:
            print(f"  Failed to process {input_filename}")
    
    if processed_count > 0:
        print(f"\n✓ Successfully processed {processed_count} file(s) for {subject}/{session}")
    else:
        print(f"\n○ No files needed processing for {subject}/{session}")


def main():
    """Main function to handle command line arguments."""
    
    parser = argparse.ArgumentParser(
        description='Process motion TSV files in BIDS-like directory structure',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python tsv_motion_processor.py /data sub-01 ses-01 rest run-01
  python tsv_motion_processor.py /path/to/data sub-02 ses-baseline task1 run-02
  
Expected directory structure:
  data_dir/
    subject/
      session/
        func/
          subject_session_task-TASK_run_desc-filteredincludingFD_motion.tsv
          subject_session_task-TASK_run_desc-includingFD_motion.tsv
        """
    )
    
    parser.add_argument('data_dir', help='Root data directory path')
    parser.add_argument('subject', help='Subject ID (e.g., sub-01)')
    parser.add_argument('session', help='Session ID (e.g., ses-01)')
    parser.add_argument('task', help='Task name (e.g., rest)')
    parser.add_argument('run', help='Run identifier (e.g., run-01)')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Validate data directory
    data_dir = Path(args.data_dir)
    if not data_dir.exists():
        print(f"Error: Data directory does not exist: {data_dir}")
        sys.exit(1)
    
    # Process the specified subject/session/task/run
    try:
        process_subject_session(
            str(data_dir), 
            args.subject, 
            args.session, 
            args.task, 
            args.run
        )
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)
    
    print("\nProcessing completed!")


if __name__ == "__main__":
    main()