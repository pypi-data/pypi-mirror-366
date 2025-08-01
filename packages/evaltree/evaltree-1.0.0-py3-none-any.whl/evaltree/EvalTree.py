#!/usr/bin/env	python3                             

"""
EvalTree: toolbox for comparative clustering evaluation of whole genome sequencing (WGS) pipelines for bacteria routine surveillance
By Joana Gomes Pereira
@INSA

"""
version = "1.0.0"
last_updated = "2025-07-31"

import datetime
import argparse
import os
import sys
import time
import textwrap
import pandas as pd
import glob
import fnmatch
import plotly.express as px
import plotly.io as pio
import plotly.graph_objects as go
import re
import random
import numpy as np
import subprocess
from scipy import stats
import math


def get_path_toolbox():

    """
    Retrieves the absolute path to the current script (EvalTree.py) and its respective directory.
    This is useful for correctly managing file paths relative to the script's location.

    Parameters
    ---------
    None
    
    Returns
    ---------
    path_toolbox_script: str
        The absolute path to the current script.
    directory_toolbox_script: str
        The absolute path to the directory containing the current script.
    """
    #print(f'\n---------------------------------------------- Function: get_path_toolbox ----------------------------------------------')
    
    path_toolbox_script = os.path.realpath(__file__)     
    directory_toolbox = os.path.dirname(path_toolbox_script)
    python = sys.executable

    return path_toolbox_script, directory_toolbox, python

def get_path_other_scripts(directory_toolbox):

    """
    Constructs the paths to locate the scripts that evaluate the pipeline congruence based from the toolbox directory.
    The following scripts are included:

    -**comparing_partition_v2.py** (Mixão et al., 2024): 
        This script has two analysis options: between_methods and stability.
        - The *between_methods* option compares methods from two pipelines to compute the congruence score, assessing the consistency between them. 
        - The *stability* option evaluates the cluster stability produced by a given method.

    -**get_best_part_correspondence.py** (Mixão et al., 2024): 
        For each pairwise pipeline comparison, this script identifies the threshold that provides 
        the most similar clustering results in the other pipeline (i.e., the best “correspondence point”), based on CS scores.

    -**remove_hifen_script.py** (Pereira et al., 2025):
        Automatically remove row(s) from the file ALL_CORRESPONDENDE.tsv that do not contain correspondence points produced by get_best_part_correspondence.py.
        Rename the file ALL_CORRESPONDENDE.tsv to All_correspondence.tsv.

    -**stats_outbreak_script.py** (Mixão et al., 2024):
        This script determines the percentage of clusters identified by a given pipeline at a certain threshold are also detected 
        — with the exact same composition — by another pipeline at a similar or higher threshold.

    Parameters
    ----------
    directory_tool1_script : str
        Path to the directory of the main toolbox script.
    
    Returns
    ---------  
    comparing_partitions_script: str
        Path to the script comparing_partition_v2.py.

    get_best_part_correspondence_script: str
        Path to the script get_best_part_correspondence.py. 
        
    remove_hifen_script: str
        Path to the script remove_hifen.py.        
        
    stats_outbreak_script: str
        Path to the script stats_outbreak_script.py.
    """
    #print(f'\n---------------------------------------------- Function: get_path_other_scripts ----------------------------------------------\n')

    comparing_partitions_script = os.path.join(directory_toolbox, 'scripts', 'ComparingPartitions', 'comparing_partitions_v2.py')

    get_best_part_correspondence_script = os.path.join(directory_toolbox, 'scripts', 'WGS_cluster_congruence', 'get_best_part_correspondence.py')

    remove_hifen_script = os.path.join(directory_toolbox, 'scripts', 'WGS_cluster_congruence','remove_hifen.py')

    stats_outbreak_script = os.path.join(directory_toolbox, 'scripts', 'WGS_cluster_congruence','stats_outbreak_analysis.py')

    return comparing_partitions_script, get_best_part_correspondence_script, remove_hifen_script, stats_outbreak_script 

def check_input_argument(input1, input2):

    """
    Verifies the existence of the specified input paths (-i1 and -i2) and categorizes them.
    If an input is a folder, it is added to the folders list; if it is a `.tsv` file, it is added to the files list.
    Based on the provided input arguments, the function returns two separate lists: one for folders and one for files.

    Parameters
    ----------
    input1: str
        Relative path to the first input argument.
    input2: str
        Relative path to the second input argument.
    
    Returns
    -------
    folders: list
        List of relative paths to input folders.
    files: list
        List of relative paths to input files.
    """
    #print(f'\n---------------------------------------------- Function: check_input_argument ----------------------------------------------\n')

    folders = []
    files = []
    
    arguments = [input1, input2]

    for elem in arguments:
        if elem is not None:

            if not os.path.exists(elem):
                sys.exit(f'Error: The input {elem} was not found.')

            if os.path.isdir(elem):
                folders.append(elem)

            elif os.path.isfile(elem):
                if elem.endswith('.tsv'):
                    files.append(elem)
                else:
                    sys.exit(f'\tError: Only files with the *.tsv extension are allowed. The extension of {elem} is not allowed.')
        else:
            print(f"\tWarning: Only one input file was provided. Inter-pipeline cluster congruence analysis will not be performed.\n")
    
    return folders, files

def check_folder(input_path):

    """
    Checks the input path for expected files. 
    The path must be a directory (e.g., a ReporTree folder). 
    This function searches for specific filenames and validates the file prefix consistency.

    Parameter
    ---------
    input_path: str
        Relative path to the directory.

    Returns
    -------
    partitions : str or None
        Relative path to the partition matrix file.
    partitions_summary : str or None
        Relative path to the partitions summary file.
    sample_interest : str or None
        Relative path to the sample of interest partitions summary file.
    clusterComposition : str or None
        Relative path to the cluster composition file.
    prefix : str or None
        Prefix present in all files.
    input_path : str
        Name of the input folder.
    stable_region : str or None
        Full path to the stable regions file.
    """
    #print(f'\n---------------------------------------------- Function: check_folder ----------------------------------------------\n')

    #if input_path == []:
        #sys.exit(f"\tError: The folder {input_path} is empty or does not exist.")

    files = [os.path.join(input_path, file) for file in os.listdir(input_path)] 

    partitions = None
    partitions_summary = None
    sample_interest = None
    clusterComposition = None
    stable_region = None
  
    prefix_list = []
    file_prefix_map = {}

    for file in files:
        if fnmatch.fnmatch(file,"*_clusterComposition.tsv"):
            clusterComposition = file 
            prefix_cc=file[:-23]
            prefix_list.append(prefix_cc)
            file_prefix_map[file] = prefix_cc

        elif fnmatch.fnmatch(file, "*_partitions.tsv") and not fnmatch.fnmatch(file, '*_w_partitions.tsv'):
            partitions = file
            prefix_mp=file[:-15]
            prefix_list.append(prefix_mp)
            file_prefix_map[file] = prefix_mp

        elif fnmatch.fnmatch(file,"*_partitions_summary.tsv") and not fnmatch.fnmatch(file, '*_SAMPLES_OF_INTEREST_partitions_summary.tsv'):
            partitions_summary = file
            prefix_ps=file[:-23]
            prefix_list.append(prefix_ps)
            file_prefix_map[file] = prefix_ps
            
        elif fnmatch.fnmatch(file,"*_SAMPLES_OF_INTEREST_partitions_summary.tsv"):
            sample_interest = file
            prefix_si=file[:-43]
            prefix_list.append(prefix_si)
            file_prefix_map[file] = prefix_si

        elif fnmatch.fnmatch(file,"*_stableRegions.tsv"):
            stable_region = file
            prefix_st=file[:-18]
            prefix_list.append(prefix_st)
            file_prefix_map[file] = prefix_st
        
    unique_prefixes = set(prefix_list)    
    list_prefixes = [os.path.basename(p) for p in unique_prefixes]

    if len(unique_prefixes) > 1:
        print(f"\nError: Multiple prefixes were found in the {input_path} folder: {' and '.join(list_prefixes)}. Please revise the structure of your input folder.")
        for prefix in unique_prefixes:
            for file, file_prefix in file_prefix_map.items():
                if file_prefix == prefix:
                    print(f"  - {file}")
        sys.exit()
    else:
        if list_prefixes == []:
            sys.exit('Without ReporTree files.')
        else:
            final_prefix = list_prefixes[0]
        
    print(f'\tFiles of {input_path}:')
    print(f'\t\tPrefix: {final_prefix}')
    print(f'\t\tPartition matrix: {partitions}')
    print(f'\t\tPartition summary: {partitions_summary}')
    print(f'\t\tSample of interest: {sample_interest}')
    print(f'\t\tCluster composition: {clusterComposition}')
    print(f'\t\tStable regions: {stable_region}')
  
    return partitions, partitions_summary, sample_interest, clusterComposition, final_prefix, input_path, stable_region

def check_output(output):

    """
    Checks if the specified path is a valid directory.
    If the path is not a valid directory, the program will stop with an error message.

    Parameter
    ---------
    output: str
        Relative path to the directory where the results will be saved.
    
    Return
    ------
    output: str
        Absolute path to the output directory.      
    """
    #print(f'\n---------------------------------------------- Function: check_output ----------------------------------------------\n') 


    if not os.path.isdir(output):
        sys.exit(f'\tError: The specified {output} is not a valid directory.')

    full_path_output = os.path.abspath(output)
    
    return full_path_output

def check_threshold(threshold):

    """
    Validates the format of the threshold argument for filtering the partition matrix.

    If the threshold is not "max", it must be in the format "X-Y", where X and Y are positive integers.
    If the format is incorrect, the program will stop with an error message.

    Parameter
    ---------
    threshold: str
        Range of thresholds to apply in the partition matrix file. 

    Return
    ------
    threshold: str
       The validated threshold string.
    """
    #print(f'\n---------------------------------------------- Function: check_threshold ----------------------------------------------\n')

    if threshold != 'max':
        parts = threshold.split('-')  

        if len(parts) != 2 or not all(part.isdigit() for part in parts):  
            sys.exit(f"\tError: The threshold argument (-t) must be in the format 'X-Y', where X and Y are positive integers.")

    return threshold
    
def check_score(score):

    """
    Checks that the score is a float between 0 and 3.
    If the format is incorrect, the program will stop with an error message.

    Parameter
    ---------
    score: str
        Score value as string.

    Return
    ------
    score_value: str
        Validated score.
    """
    #print(f'\n---------------------------------------------- Function: check_score ----------------------------------------------\n')

    try:
        score_value=float(score)  
        if not 0 <= score_value <= 3:
            sys.exit(f"\tError: The score value {float(score)} is out of the allowed range (0 to 3).")   
    except ValueError as e:
        sys.exit(f"\tError: The score value {score} is not a float.")

    return score_value

def check_file(file):

    """
    Check the structure of the input file (either a sequence-type matrix or a partition matrix).
    
    Parameter
    ---------
    file: str
        Relative path to the input matrix file.
    
    Returns
    -------
    filename : str
        Absolute path to the input file.
    prefix : str
        Prefix of the input file.
    path_directory : str
        Directory name where the file is located.
    file_type : bool
        False for sequence-type matrix; True for partition matrix.
    n_samples : int
        Number of samples present in the file.
    n_groups : int or None
        Number of groups if applicable (only for sequence-type matrix).
    """
    #print(f'\n---------------------------------------------- Function: check_file ----------------------------------------------\n')
    
    df = pd.read_table(file)
    nr_columns = df.shape[1]
    n_samples = df.shape[0]

    filename = os.path.abspath(file)
    prefix_file = os.path.basename(file) 
    path_directory = filename.split('/')[-2]

    if nr_columns == 2:
        n_groups = len(df.iloc[:,1].unique())
        prefix = prefix_file.split('.tsv')[0]
        file_type = False 
           
    elif nr_columns > 2:

        prefix = prefix_file.split('.tsv')[0]
        n_groups = None
        file_type = True
   
    return filename, prefix, path_directory, file_type, n_samples, n_groups

def check_str_plots_threshold(plots_thresholds):

    """
    Check if the threshold has the correct format. 
    Otherwise, the program will terminate with an error message indicating that the format is incorrect.

    Parameter
    ---------
    plots_thresholds: str
        One or more thresholds provided by the user, separated by commas and without spaces.
    Return
    ------
    plots_thresholds: list
        Valid list of plot thresholds in the format 'METHOD-NxM.M' (e.g., MST-4x1.0)
    """     
    #print(f'\n---------------------------------------------- Function: check_str_plots_thresholds ----------------------------------------------\n')   

    pattern = r'^[A-Za-z]+-\d+x\d+\.\d+$'

    thresholds = [th for th in plots_thresholds.split(",")]

    values=[]
    for th in thresholds:
        if not re.match(pattern, th):
            sys.exit(f"\tError: The value '{th}' does not follow the expected format (e.g., METHOD-NxM.M). Multiple plots must be separated by commas and without spaces.")
        values.append(th)
    
    return values
    
def check_combinations_arguments(plots_summary_arg, data_folder, data_files):

    """
    Check the argument combinations provided by the user. 
    If any combination of arguments is invalid, the program will stop.

    Parameters
    ----------
    plots_summary_arg: str
        Type of file to be used for clustering characterization.
        
    data_folder: list
        List containing information about the input files, file prefixes, and directories.
    
    data_file: list
        List containing information about the input files, file prefixes, and directories.

    Return
    ------
    go_clustering: boolean
        Indicates whether clustering characterization can be executed.
    go_outbreak: boolean
        Indicates whether outbreak analysis can be executed.
    """
    #print(f'\n---------------------------------------------- Function: check_combinations_arguments ----------------------------------------------\n')

    type_file = plots_summary_arg
   
    args = sys.argv  
    if '-pcn'  in args and '-pcp' in args :
        sys.exit(f"\tError: It is not possible to provide the plots_category_number (-pcn) and plots_category_percentage (-pcp) at the same time.")
 
    errors = []
    go_clustering = False
    go_outbreaks = False

    if data_folder:
        for elem in data_folder:
            partitions_summary = elem[3] 
            sample_of_interest = elem[4] 
            cluster_composition = elem[5] 
            input_path = elem[2] 
            stable_regions = elem[6]

            if type_file == 'sample_of_interest':

                has_cp = '-cp' in args
                has_pt = '-pt' in args
                has_pcp = '-pcp' in args
                has_pcn = '-pcn' in args

                
                if not has_cp:
                    errors.append("\tError: For clustering analysis you must specify the column plots (-cp) argument with SAMPLE_OF_INTEREST_partitions_summary file.\n")

                if not has_pt:
                    errors.append("\tError: For clustering analysis you must specify the plots threshold (-pt) argument with SAMPLE_OF_INTEREST_partitions_summary file.\n")

                if sample_of_interest is None:
                    errors.append(f"\tError: The file SAMPLE_OF_INTEREST_partitions_summary does not exist in {input_path}.\n")

                if '-n' in args:
                    errors.append("\tError: It is impossible to use -n argument with SAMPLE_OF_INTEREST_partitions_summary file.\n")

                if has_pcp or has_pcn:
                    if not has_cp:
                        errors.append("\tError: Using '-pcp' or '-pcn' requires '-cp' to be specified.\n")
                    if not has_pt:
                        errors.append("\tError: Using '-pcp' or '-pcn' requires '-pt' to be specified.\n")
                    if sample_of_interest is None:
                        errors.append("\tError: Using '-pcp' or '-pcn' requires the SAMPLE_OF_INTEREST_partitions_summary file to be present.\n")

                go_clustering = True

            if type_file == 'partitions_summary':

                has_cp = '-cp' in args
                has_pt = '-pt' in args
                has_custom_clustering = any(opt in args for opt in ['-n', '-pcp', '-pcn'])

                if has_custom_clustering:
                    if not has_cp:
                        errors.append(f"\tError: Missing argument '-cp'.\n")
                    if not has_pt:
                        errors.append(f"\tError: Missing argument '-pt'.\n")
                    if partitions_summary is None:
                        errors.append(f"\tError: Missing partitions_summary file.\n")
                    go_clustering = len(errors) == 0
                elif has_cp and has_pt:
                    if partitions_summary is not None:
                        go_clustering = True
                    else:
                        errors.append(f"\tError: To run clustering with '-cp' and '-pt', you must also provide a valid partitions_summary file.\n")
                        go_clustering = False
                elif has_cp and not has_pt:
                    errors.append(f"\tError: Missing argument '-pt'. Both '-cp' and '-pt' are required to run clustering analysis.\n")
                    go_clustering = False
                elif has_pt and not has_cp:
                    errors.append(f"\tError: Missing argument '-cp'. Both '-cp' and '-pt' are required to run clustering analysis.\n")
                    go_clustering = False
                else:
                   
                    go_clustering = False

            
            if stable_regions is None:
                if '-n_stab' in args:
                    errors.append(f'\tError: It is impossible to use the -n_stab argument when the file stableRegions does not exist.\n')
                if '-n_thr' in args:
                    errors.append(f'\tError: It is impossible to use the -n_thr argument when the file stableRegions does not exist.\n')
                
            if '-to' in args:
                if cluster_composition is None:
                    errors.append(f'\tError: It is impossible to use the -to argument when the cluster_composition file is not in {input_path}.\n')
            
            if '-to' in args and len(data_folder) == 1:
                errors.append(f'\tError: It is impossible to use the -to argument only with one folder.\n')
                        
    if '-to' in args and len(data_files) == 1:
        errors.append(f'\tError: It is impossible to use the -to argument with input files.\n')

    if len(data_folder) == 2:
        if '-to' in args:
            if len(data_folder[0]) == 7 and len(data_folder[1]):
                if data_folder[0][5] is not None and data_folder [1][5] is not None:
                    go_outbreaks = True

    cluster_args = ['-cp', '-pt', '-n', '-ps', '-pcn', '-pcp']
    if data_files:
        if len(data_files) == 2:
           
            for elem in cluster_args:
                if elem in args:
                    errors.append(f'\tError: It is impossible to use the {elem} argument when input file(s) are provided.\n')

        if len(data_files) == 1 and len(data_folder) != 1:
            for elem in cluster_args:
                if elem in args:
                    errors.append(f'\tError: It is impossible to use the {elem} argument when input file(s) are provided.\n')

    if errors:
        unique_errors = set(errors)
        sys.exit(f"\nThe following problems were found:\n {' '.join(unique_errors)}")
            
    return go_clustering, go_outbreaks

def check_data_folders_file(data_folder, data_files):

    """
    Validates if the prefixes in data_folder and data_files are different.
    If valid, concatenates the prefixes into one string.

    Parameters
    ----------
    data_folder: list
        List of folder-related elements. Prefix in the second position.
    data_files: list
        List of file-related elements. Prefix in the second position.
    
    Returns
    -------
    data_folder : list
        The same input data_folder, unchanged.
    data_files : list
        The same input data_files, unchanged.
    prefix_both: str
        Concatenated prefix inputs (e.g., 'HC_vs_GT'). If only one input is present, returns its prefix.
    """
    #print(f'\n---------------------------------------------- Function: check_data_folders_file ----------------------------------------------\n')
 
    check_prefixes=[]

    if data_folder:
        for elem in data_folder:
            check_prefixes.append(elem[1])

    if data_files:
        for elem in data_files:
            check_prefixes.append(elem[1])

    if len(check_prefixes) == 2 and check_prefixes[0] == check_prefixes[1]:
        sys.exit(f"Error: Impossible to analyse inputs with the same prefix {check_prefixes[0]} and {check_prefixes[1]}.")
    
    if len(check_prefixes) == 2:
        prefix_both = check_prefixes[0] + '_vs_' + check_prefixes[1]
    else:
        prefix_both = check_prefixes[0]

    return data_folder, data_files, prefix_both        

def check_range_threshold(partition_matrix, threshold, log):
    
    """  
    Checks whether a given threshold range is valid within the column range of the partition matrix.
    If valid, decomposes the string threshold into two integers: start and end thresholds.

    Parameters
    ----------
    threshold: str
        Range threshold in the format 'start-end' or 'max'.
    
    partition_matrix: str
        Relative path to the partition matrix file.
    
    Returns
    -------
    start_threshold : int or None
        The start of the threshold range. None if 'max' is used.

    end_threshold : int or None
        The end of the threshold range. None if 'max' is used.
    """
    #print(f'\n---------------------------------------------- Function: check_range_threshold ----------------------------------------------')

    if threshold != 'max':
        parts = threshold.split('-')
        start_threshold = int(parts[0])  
        end_threshold = int(parts[1])    
        
        df = pd.read_table(partition_matrix) 
        columns_df = len(df.columns)
        column_range = (0, columns_df) 
        min_column,max_column=column_range  

        if start_threshold > end_threshold:
            sys.exit(f"\tError: Start threshold {start_threshold} is greater than end threshold {end_threshold}.")

        else:    
            if not (min_column <= start_threshold <= max_column):
                sys.exit(f"\tError: Start threshold {start_threshold} is outside the valid column range {column_range}.")
            
            if not (min_column <= end_threshold <= max_column):
                print_log(f'\t\tWarning: The final threshold ({end_threshold}) is higher than the available number of columns.',log)
    else:
        start_threshold = None
        end_threshold = None

    return start_threshold, end_threshold

def management_main_scripts(comparing_partitions_script, get_best_part_correspondence_script, remove_hifen_script, input1, input2, prefix_both, output, score, python, log):
    
    """
    Executes congruence scripts to evaluate the agreement between two genomic pipelines.
    This function orchestrates the execution of all previously mentioned scripts.
    
    Parameters
    ----------
    comparing_partitions_script : str
        Absolute path to the comparing_partitions_v2.py.
    get_best_part_correspondence_script : str
        Absolute path to the get_best_part_correspondence.py.
    remove_hifen_script : str
        Absolute path to the remove_hifen.py.

    input1 : str
        Path to the first input file (e.g., *_partitions.tsv or sequence type matrix). 
    input2 : str
        Path to the second input file (e.g, *_partitions.tsv or sequence type matrix).
    prefix_both: str
        Prefix added to the result files generated from both pipelines (e.g., XXX_vs_XXX).
    output : str
        Full path to the directory where the results will be saved.
    score : str
        Minimum score to consider two partitions as a correspondence.

    Returns
    -------
    Output files generated by each script include:

    - comparing_partitions_v2.py: 
        *_AdjustedRand.tsv, *_AdjWallace1.tsv, *_AdjWallace2.tsv, *_final_score.tsv, 
        *_Simpsons1.tsv, *_Simpsons2.tsv, *_Wallace1.tsv, *_Wallace2.tsv

    - get_best_part_correspondence.py: 
        *_ALL_CORRESPONDENCE.tsv

    - remove_hifen.py: 
        *_All_correspondence.tsv
    """
    #print_log(f'\n---------------------------------------------- Function:  management_all_scripts ----------------------------------------------', log)
    
    print_log(f'\tObtaining the cluster congruence score ...', log)
    
    #1- Running the first script with the user's inputs 
     
    print_log(f"\t\tRunning comparing_partitions_v2.py in “between_methods” mode.", log)
       
    cmd=[ python, comparing_partitions_script, "-o1", "0", "-o2", "0", "-a", "between_methods",
      "-log", f"{output}/{prefix_both}_Comparing_partitions.log", "-t", f"{output}/{prefix_both}",
      "-i1", input1, "-i2", input2, "--keep-redundants"]
    
    print_log(f'\t\t\t{" ".join(cmd)}', log)  
    subprocess.run(cmd)
    
    print_log(f"\t\tDone.\n", log)
  
    #2- Running the second script with the user's inputs #Input directory with all the *final_score.tsv files 
      
    print_log(f'\tIdentifying the inter-pipeline “corresponding points”', log)
    print_log(f'\t\tRunning get_best_part_correspondence.py with a score of {score}.', log)
    cmd=[python, get_best_part_correspondence_script, "-i", output, "-s", str(score)]
    print_log(f'\t\t\t{" ".join(cmd)}', log) 

    subprocess.run(cmd)
    print_log(f"\t\tDone.\n", log)

    # # 3- Execution of the third script - remove hyphens from ALL_CORRESPONDENCE.tsv

    print_log("\t\tFiltering output file with remove_hifen.py.", log)
    cmd=[python, remove_hifen_script, "-i", f"{output}/ALL_CORRESPONDENCE.tsv", "-o", f"{output}/{prefix_both}_ALL_CORRESPONDENCE.tsv"]
    print_log(f'\t\t\t{" ".join(cmd)}', log) 
    subprocess.run(cmd)
    print_log(f"\t\tDone.\n", log)

    original_file=(f"{output}/{prefix_both}_ALL_CORRESPONDENCE.tsv")
    path_all_correspondence_lower=(f"{output}/{prefix_both}_All_correspondence.tsv")
    os.rename(original_file, path_all_correspondence_lower)
    path_all_correspondence=(f"{output}/ALL_CORRESPONDENCE.tsv")
    os.remove(path_all_correspondence)

    return path_all_correspondence_lower
    
def tendency_slop(correspondence, pipeline1, pipeline2, output_folder):  #correspondence=ALL_CORRESPONDENCE.tsv

    """
    This function is part of the script heatmap_final_score.py (Mixão et. al., 2024), and is responsible for generating the *_slope.tsv file.
    This file contains information about the r-value and p-value of the trend line.
    
    Parameters
    ----------
    correspondence: str
        Absolute path to the All_correspondence.tsv file.
    pipeline1: str
        Prefix of the first pipeline.
    pipeline2: str
        Prefix of the second pipeline.
    output_folder: str
        Full path to the directory where the results will be saved.

    Return
    ------
    comparison: str
        An empty string.  The function generates a *_slope.tsv file in the output folder.
    """
    #print(f'\n---------------------------------------------- Function:  tendency_slop ----------------------------------------------')

    possible_comparison_names = [pipeline1 + "_vs_" + pipeline2, pipeline2 + "_vs_" + pipeline1]
    mx = pd.read_table(correspondence)	
    all_comparisons = pd.unique(mx[mx.columns[0]])

    comparison = ""
    for comp1 in all_comparisons:
        if "_rev" not in comp1:
            if comp1 in possible_comparison_names:

                extension = output_folder + "/" + comp1 + "_slope.tsv"
                with open(extension, "w+") as out:
                    print("#comp1\tcomp2\tslope\tintercept\tr_value\tp_value\tstd_err", file = out)
                    for comp2 in all_comparisons:
                        if "_rev" in comp2:
                            if comp2.split("_rev")[0] == comp1:
                                comps = [comp1, comp2]
                                flt_mx = mx.loc[mx[mx.columns[0]].isin(comps)]

                                if len(flt_mx[flt_mx.columns[0]].values.tolist()) == 0:
                                    print("No trend line will be provided as no congruence point was found!!")
                                else:
                                    if len(flt_mx[flt_mx[flt_mx.columns[0]] == comp1]["method1"].values.tolist()) != 0:
                                        slope, intercept, r_value, p_value, std_err = stats.linregress(flt_mx[flt_mx[flt_mx.columns[0]] == comp1]["method1"],flt_mx[flt_mx[flt_mx.columns[0]] == comp1]["method2"])
                                        print(comp1 + "\t" + comp2 + "\t" + str(slope) + "\t" + str(intercept) + "\t" + str(r_value) + "\t" + str(p_value) + "\t" + str(std_err), file = out)
                                    if len(flt_mx[flt_mx[flt_mx.columns[0]] == comp2]["method1"].values.tolist()) != 0:
                                        slope2, intercept2, r_value2, p_value2, std_err2 = stats.linregress(flt_mx[flt_mx[flt_mx.columns[0]] == comp2]["method1"],flt_mx[flt_mx[flt_mx.columns[0]] == comp2]["method2"])
                                        print(comp2 + "\t" + comp1 + "\t" + str(slope2) + "\t" + str(intercept2) + "\t" + str(r_value2) + "\t" + str(p_value2) + "\t" + str(std_err2), file = out)

    return comparison

def filter_partition_matrix(partition_matrix, prefix_single, start_threshold, end_threshold, output, log):
    
    """
    Applies a valid range threshold, when specified, to the partition matrix file.
    A new partition matrix file containing only the selected threshold columns is created.

    Parameters
    ----------
    partition_matrix: str
        Relative path to the partition matrix.
    prefix_single: str 
        Prefix to be used in the name of the filtered partition matrix file.
    output: str
        Path to the directory where the filtered matrix file will be saved
    start_threshold: int
        Starting column index for threshold selection in the partition matrix.
    end_threshold: int
        Ending column index for threshold selection in the partition matrix.

    Return
    ------
    input_filtered: str 
        Relative path to the new filtered partition matrix (*.tsv) containing only the selected threshold columns.
    """
    #print_log(f'\n---------------------------------------------- Function: filter_partition_matrix ----------------------------------------------', log)

    df = pd.read_table(partition_matrix)
     
    columns_to_keep = df.columns[start_threshold + 1 : end_threshold + 2]
    columns_to_keep_1 = [df.columns[0]] + list(columns_to_keep)
    df_filtered = df[columns_to_keep_1]
    input_filtered = f"{output}/{prefix_single}_partitions-filtered.tsv"
    df_filtered.to_csv(input_filtered, sep = '\t', index = False)
    
    print_log(f'\tFiltering the partitions table for the range {start_threshold}-{end_threshold}...',log)
   
    return input_filtered

def stability_region(output, partition_matrix, prefix, comparing_partitions_script, n_stability, thr_stability, python, log):
   
    """
    Executes the stability analysis using comparing_partitions_v2.py when the file *_stableRegions.tsv 
    does not already exist in the input directory. If executed, the command generates *_stableRegions.tsv and *_metrics.tsv files.

    Parameters
    ----------
    output: str
        Path to the directory where the results will be saved.
    partition_matrix: str
        Path to the input directory.
    comparing_partitions_script: str
        Path to the comparing_partitions_v2.py script.

    Return
    ------
    file_stability : str
        Path to the *_stableRegions.tsv file created.
    """
    #print_log(f'\n---------------------------------------------- Function: stability_region ----------------------------------------------', log)

    cmd = [
        python, comparing_partitions_script, "-i1", partition_matrix, "-o1", "0", "-a", "stability", "-n", str(n_stability), "-thr", str(thr_stability),
        "-log", f"{output}/{prefix}_Comparing_partitions.log", "-t", f"{output}/{prefix}", "--keep-redundants"]

    print_log(f'\t\t\t{" ".join(cmd)}', log)  

    subprocess.run(cmd, capture_output = True, text = True)

    file_stability = f'{output}/{prefix}_stableRegions.tsv'

    return file_stability

def get_heatmap(output, i1_prefix, i2_prefix, threshold, log):

    """
    Generates a heatmap figure representing the congruence score between two genomic pipelines,
    based on the *_final_score.tsv file.

    Parameters
    ----------
    output: str
        Path to the directory where the *_final_score.tsv file is located and where the heatmap will be saved.
    i1_prefix : str
        Prefix of the first pipeline (y-axis).
    i2_prefix : str
        Prefix of the second pipeline (x-axis).
    threshold : str
        Threshold value used to filter the partition matrix ('max' if no filtering).    
    Return
    ------
    fig_heatmap: class plotly.graph_objs._figure.Figure
        Plotly figure object of the heatmap. Also saved as PNG in the output folder.
    """
    #print_log(f'\n---------------------------------------------- Function: get_heatmap ----------------------------------------------', log)
   
    max_ticks = 16

    final_score = glob.glob(output +'/*_final_score.tsv' )[0]
    df = pd.read_csv(final_score, sep ='\t')
    df_filtered = df.drop(df.columns[0], axis = 1) 
    df_filtered.columns = range(len(df_filtered.columns))  
    n_lines, n_column = df_filtered.shape
    
    #---------------------------------
    fig_heatmap = px.imshow(df_filtered,                    
                            labels = dict(x = f"Threshold <br> -{i2_prefix}-</br>", y = f"Threshold <br> -{i1_prefix}-</br>"))

    if n_lines > max_ticks:
        step = math.ceil(n_lines/ max_ticks)
        y_list = list(range(0, n_lines, step))
    else:
        y_list=list(range(0,n_lines))
   
    if n_column > max_ticks:
        step = math.ceil(n_column / max_ticks)
        x_list = list(range(0, n_column, step))
    else:
        x_list = list(range(0, n_column))

    fig_heatmap.update_layout(
                            height = 500, 
                            width = 500, 
                            title_x = 0.5,   
                            xaxis = dict(scaleanchor = None, constrain='domain', tickvals = x_list),  
                            yaxis = dict(scaleanchor = None, constrain='domain', tickvals = y_list),
                            coloraxis = dict(colorscale = 'Blues', cmin = 0, cmax = 3))
    
    #--------------------------------------------------------------------------
    # For both other matrices:
    if n_column == 1:
        fig_heatmap.update_layout(xaxis = dict(tickmode = 'array', tickvals = [0], ticktext = [0]))
    if n_lines == 1:
        fig_heatmap.update_layout(yaxis = dict(tickmode = 'array', tickvals = [0], ticktext = [0]))
        
    #--------------------------------------------------------------------------
    #For the partitions filtered matrix:

    if threshold != 'max':

        #--------------------------------------------------------------------------
        # Partition matrix and sequence type

        if n_column == 1 and n_lines != 1:
            columns_y = df.iloc[:, 0]
            string_columns_y = [s.split('-')[1].split('x')[0] for s in columns_y]
            len_y = len(columns_y)
           
            if len_y <= max_ticks:
                index_y = list(range(len_y))
                fig_heatmap.update_layout(xaxis = dict(tickmode ='array', tickvals = [0], ticktext = [0]))
                fig_heatmap.update_layout(yaxis = dict(tickmode ='array', tickvals = index_y, ticktext = string_columns_y))
            else:  
                step_y = math.ceil(len_y / max_ticks)  
                list_index_y = [i * step_y for i in range(max_ticks)]
                list_strings_y = string_columns_y [::step_y]

                fig_heatmap.update_layout(
                    xaxis = dict(tickvals = [0], ticktext = [0]),
                    yaxis = dict(tickvals = list_index_y, ticktext = list_strings_y))
        
        #--------------------------------------------------------------------------
        # Both Partition matrix 

        if n_column != 1 and n_lines != 1:

            columns = df.columns.tolist()[1:]
            string_columns = [s.split('-')[1].split('x')[0] for s in columns]
            len_x = len(columns)

            if len_x > max_ticks:
                
                step_x = math.ceil(len_x / max_ticks)  
                list_index = [i * step_x for i in range(max_ticks)]
                list_strings = string_columns[::step_x]

                fig_heatmap.update_layout(
                    xaxis = dict(tickvals = list_index, ticktext = list_strings),
                    yaxis = dict(tickvals = list_index, ticktext = list_strings))
            else:

                fig_heatmap.update_layout(
                    xaxis = dict(tickvals = list(range(len_x)), ticktext = string_columns),
                    yaxis = dict(tickvals = list(range(len_x)), ticktext = string_columns))

    fig_heatmap.update_layout(margin=dict(l=0, r=0, t=20, b=0))
    fig_heatmap.write_image(f'{output}/{i1_prefix}_vs_{i2_prefix}_heatmap.png', format = "png")

    return fig_heatmap

def get_tendency(output, prefix_both, threshold, log):
    
    """
    Creates a scatter plot with trendline from *_All_correspondence.tsv,
    showing the best correspondence points between methods in each pipeline.
    
    Parameters
    ----------
    output: str
        Path to the directory where the *_All_correspondence.tsv file is located and where the figure will be saved.

    prefix_both: str 
        Prefix added to the result files generated from both pipelines (e.g., XXX_vs_XXX)
    Return
    ------
    fig_tendency: plotly.graph_objs._figure.Figure
        Plotly figure object of the scatter plot. Also saved as PNG in the output folder.
    """
    #print_log(f'\n---------------------------------------------- Function: get_tendency ----------------------------------------------', log)

    all_correspondence=glob.glob(output + '/*_All_correspondence.tsv')[0]
    df = pd.read_csv(all_correspondence, sep = "\t")

    df_1=df.iloc[:,0]
    
    values_rev = [string for string in df_1 if '_rev' in string]
    nr_point=len(df_1)
    nr_point_method_2 = len(values_rev)
    nr_point_method_1 = nr_point - nr_point_method_2

    for elem in values_rev:
        string_r=elem.split('_vs_')
        s = string_r[-1]
        string_modified=s[:-4]

        reverse_prefix = string_modified+'_vs_'+string_r[0]
    
    df_modified=df.replace(to_replace = elem, value = reverse_prefix)      

    x_axes = df_modified.columns[1]
    y_axes = df_modified.columns[2]

    fig_tendency = px.scatter(df_modified, x = x_axes, y = y_axes, trendline = "ols", color_discrete_sequence = ["orange", "blue"], color = 'comparison')  

    if threshold != 'max':
        values= threshold.split('-')
        first_value=int(values[0])
        second_value=int(values[1]) 
        values_list= [str(i) for i in range(first_value, second_value + 1)]
        n_elem=len(values_list)
        index_list=list(range(0, n_elem))

        text_list=[]
        for elem in values_list:
            text_list.append(elem)

        fig_tendency.update_layout(xaxis=dict(tickvals = index_list, ticktext=text_list))
        fig_tendency.update_layout(yaxis=dict(tickvals = index_list, ticktext=text_list))



    fig_tendency.update_layout(title_x = 0.5, legend=dict( orientation="h",yanchor="bottom",  y=-0.35, xanchor="center", x=0.5), margin=dict(l=0, r=0, t=20, b=0))
    fig_tendency.write_image(f'{output}/{prefix_both}_tendency.png', format = "png")
    
    return fig_tendency, nr_point_method_1, nr_point_method_2

def join_inputs_variables(data_folder, data_files):

    """
    Join the input variables provided in the command line for the congruence analysis.

    Parameters
    ----------
    data_folder: list
        List of folder-related elements.

    data_files: list
        List of folder-related elements.

    Return
    ------
    inputs_variables : list
        Combined list of all valid inputs.
    """

    #print(f'\n---------------------------------------------- Function: join_inputs_variables ----------------------------------------------')
    
    inputs_variables = []

    if data_folder:
        for elem in data_folder:
            inputs_variables.append(elem)
      
    if data_files:
        for elem in data_files:
            inputs_variables.append(elem)

    if len(inputs_variables) == 1:
        if inputs_variables[0][0] == None:
            sys.exit(f"\tError: It is impossible to proceed the analysis without a partition_matrix file.")

    if len(inputs_variables) == 2:
        i1,i2 = inputs_variables[0][0], inputs_variables[1][0]

        if i1 is None and i2 is None:
            sys.exit("\tError: It is impossible to proceed the analysis")
        else:
            print(f'\nChecking the command line:')
            print(f'\tThe provided arguments are all compatible. Everything is ready to run EvalTree.py :)\n')

    return inputs_variables

def load_and_prepare_data(file, log):

    """
    Identifies the type of partition summary file and processes it.
    
    The difference between *_partitions_summary.tsv and *_SAMPLE_OF_INTEREST_partitions_summary.tsv 
    is that the latter contains an extra 'SAMPLE_OF_INTEREST' column, which will be removed from the 
    dataframe if present.

    Parameters
    ----------
    file: str
        Path to the file that will be processed.

    Returns
    -------
    df_data : pandas DataFrame
        Returns the dataframe with or without the 'SAMPLE_OF_INTEREST' column, depending on the file type.

    """
    #print_log(f'\n---------------------------------------------- Function: load_and_prepare_data ----------------------------------------------\n', log)

    df = pd.read_table(file)
    first_cell = df.columns[0]

    if  first_cell == 'SAMPLE_OF_INTEREST':  
        df_data = df.iloc[:, 1:]  
    else:
        df_data = df

    return df_data

def order_cluster_by_size(df_data, log):

    """
    Checks if the 'cluster_length' column exists in the dataframe and sorts the dataframe by it in descending order.
    
    Parameters
    ----------
    df_data : pandas.DataFrame
        Dataframe with cluster data to analyze.

    Returns
    -------
    df_filtered : pandas.DataFrame or None
        Sorted dataframe by 'cluster_length', or None if the column doesn't exist.
    """
    #print_log(f'\n---------------------------------------------- Function: order_cluster_by_size ----------------------------------------------\n', log)

    if 'cluster_length' in df_data.columns:
        df_filtered = df_data.sort_values(by = 'cluster_length', ascending=False)
        #print_log(f'\t\tOrdering clusters by cluster-length (values in descending order)...', log)
    else:
        #print_log(f'\t\tOrdering clusters by cluster-length is not possible because, cluster-length column is not present in the file...', log)
        df_filtered = None

    return df_filtered

def check_plot_threshold(plots_thresholds, df_filtered, log):
    
    """
    Checking if the plots_threshold argument contains one or more integer thresholds.
    Generating the MST structure for each threshold as present in the file (sample_of_interest or partition_summary).

    Parameters
    ----------
    plots_thresholds: list
        One or more thresholds provided by the user, separated by commas and without spaces.
    df_filtered: pandas.DataFrame 
        Sorted dataframe containing the necessary data.
    Return
    ------
    method: list
        A list of thresholds in the format 'MST-{value}x1.0'.  
    """
    #print_log(f'\n---------------------------------------------- Function: check_plots_thresholds ----------------------------------------------\n', log)
   
    name_threshold_in_df = df_filtered.iloc[:,0].unique().tolist()  
    method = []
    for elem in plots_thresholds:
        if elem  in name_threshold_in_df:
            method.append(elem)
        else:
            print_log(f"\tThe plot threshold argument (method) {elem} does not exist in the file.", log)

    return method

def check_threshold_in_file(method, df_filtered, clustering_file, log):
    
    """
    Look for the unique thresholds in the file (*_partitions_summary.tsv or *_SAMPLE_OF_INTEREST_partitions_summary.tsv)
    Check if the threshold(s) entered exist in the selected file.

    Parameters
    ----------
    method: list
        A list of thresholds in the format 'MST-{value}x1.0'.
    df_filtered: pandas.DataFrame
        A dataframe containing data from the selected file.
    clustering_file: str
        Path to the file (partitions_summary or sample_of_interest)

    Return
    ------
    filtered_threshold: list
        List of valid thresholds that will be applied to df_filtered.
    """
    #print_log(f'\n---------------------------------------------- Function: check_threshold_in_file ----------------------------------------------\n', log)

    all_lines_in_one_column = df_filtered.iloc[:,0] 
    unique_threshold = all_lines_in_one_column.unique().tolist()
        
    filtered_threshold = []
      
    for elem in method:
        if elem not in unique_threshold:
            print(f'\tThe plot threshold argument (method) entered {elem} does not exist in the {clustering_file}...')   
        else:    
            filtered_threshold.append(elem)
 
    return filtered_threshold

def filter_df_by_plot_threshold(filtered_threshold, df_filtered, n_cluster, log):

    """
    Check if the number of clusters selected by the n_cluster argument can be applied to the dataframe.
    Filter the dataframe according to the threshold plots and limit the number of clusters per threshold.
    
    Parameters
    ----------
    filtered_threshold: list
        List of valid thresholds to be applied to df_filtered to generate cluster plots.
    
    df_filtered: pandas.DataFrame
        The dataframe is organized with the largest clusters.

    n_cluster: int
        The number of clusters (pie plot(s)) to be produced.

    Return
    ------
    result_df: pandas.DataFrame
        Dataframe with the selected information based on the provided arguments (threshold(s) and n_cluster). 
    """
    #print_log(f'\n---------------------------------------------- Function: filter_df_by_plot_threshold ----------------------------------------------\n', log)
    
    head = df_filtered.columns.tolist()
    name_partition = head[0]
    
    results = []

    for threshold in filtered_threshold:
        threshold_df = df_filtered[df_filtered[name_partition] == threshold]
        n_lines = len(threshold_df)
        
        if n_cluster > n_lines:
            print_log(f"\t\tThe entered n_cluster value ({n_cluster}) is higher than the number of lines in the threshold {threshold} dataframe ({n_lines}).", log)
            threshold_df_end = threshold_df.head(n_lines)
            results.append(threshold_df_end)
            print_log(f"\t\tIt will be produced plots according the number of lines available in the dataset for the {threshold}.", log)
        else:
            threshold_df_end = threshold_df.head(n_cluster)
            results.append(threshold_df_end)
           
    if not results:
        return None
    
    result_df = pd.concat(results)

    return result_df

def filtering_df_threshold(filtered_threshold, df_filtered, log):

    """
    Filter the dataframe according to the provided threshold values.

    Parameters
    ----------
    filtered_threshold : list
        List of valid thresholds to be applied to df_filtered.

    df_filtered: pandas.DataFrame
        DataFrame containing the clustering information, where the first column represents thresholds.

    Returns
    -------
    df_filtered_threshold: pandas.DataFrame
        DataFrame filtered by the thresholds in filtered_threshold.
    """
    #print_log(f'\n---------------------------------------------- Function: filtering_df_threshold ----------------------------------------------\n', log)

    head=df_filtered.columns.tolist()
    name_partition = head[0]
    
    results = []

    for threshold in filtered_threshold:
        if threshold in df_filtered.iloc[:,0].values:
            threshold_df = df_filtered[df_filtered[name_partition] == threshold]
            results.append(threshold_df)

    df_filtered_threshold = pd.concat(results)
   
    return df_filtered_threshold

def check_column_plots(user_columns_plots, result_df, log):

    """
    Validate whether the column name(s) selected for plotting exist in the dataframe.
    
    Parameters
    ----------
    user_columns_plots: str
        Column(s) selected by the user for plotting.
    result_df: pandas.DataFrame
        Dataframe containing the data to be plotted.

    Return
    ------
    check_columns: list
        A list of valid column names found in the dataframe.
    """
    #print_log(f'\n---------------------------------------------- Function: check_column_plots ----------------------------------------------\n', log)

    column_in_df = result_df.columns.tolist() 
    check_columns = []

    value_columns_plots = [col.strip() for col in user_columns_plots.split(',')]       
    for col in value_columns_plots:
        if col in column_in_df:
            check_columns.append(col)
        else:
            print_log(f'\t\tInvalid column name for plot: {col}. It does not exist.', log)              

    
    return check_columns

def generate_pastel_color():

    """Generation of the random color pallete to the cluster plots"""
    r = random.randint(100, 200)
    g = random.randint(100, 200)
    b = random.randint(100, 200)

    return f'#{r:02X}{g:02X}{b:02X}'

def check_structure_lines_column_plots(check_columns, result_df, plots_category_percentage, plots_category_number,output, prefix, plots_summary, category_colors, log):
    
    """
    Check if the rows of the valid column plots have the correct structure to perform the cluster characterization.
    Generate cluster characterization plots based on validated columns.
    
    Parameters
    ----------
    check_columns: list
        List of column names to be validated and plotted.
    result_df: pandas.DataFrame
        Dataframe containing the selected information to be processed.
    plots_category_percentage: float
        Percentage threshold for aggregating smaller categories.
    plots_category_number: int
        Maximum number of categories to show.
    output: str
        Path to the output directory where the images will be saved.
    prefix: str
        Prefix to be added to the output file names.
    plots_summary: str
        Type of file selected by user.
    category_colors: dict
        Dictionary to store and reuse colors for each category.

    Return
    ------
    results_list: list
        List of dictionaries containing:
        - A: the threshold
        - B: the column
        - C: the plotly figure object

    """
    #print_log(f'\n---------------------------------------------- Function: check_struture_lines_column_plots ----------------------------------------------\n', log)
  
    pattern_line_column_plot = r'^(.+ \(\d+(\.\d+)?%\))(, .+ \(\d+(\.\d+)?%\))*( \(n = \d+\))$'
    results_list = []
    flag = False
    strings = []
    for _,row in result_df.iterrows():
    
        for col in check_columns: 
            
            #---------------------
            mst = row.iloc[0]
            cluster = row.iloc[1]
            cluster_rename = cluster[0].upper() + cluster[1:]
            n_cluster_length = row['cluster_length']

            #-------------------------------
            #Check if the line is valid 

            if re.match(pattern_line_column_plot, str(row[col])):  
                
                #---------------------------------------------
                #Processing plots

                if plots_summary == 'sample_of_interest':
                    sample_increase = row['samples_increase']       
                else:
                    sample_increase = ''

                #---------------------------------
                # Split informations

                components_row = row[col].split(" (n =")[0].split(", ")
                category = []
                values = []

                for elem in components_row:
                    label, percentage = elem.split(" (")
                    percentage_value = percentage [:-2]  
                    category.append(label)
                    values.append(float(percentage_value))

                #--------------------------------------------------------
                #Processing information by plots_category_number argument

                if plots_category_percentage is not None:
                    plots_category_number = None
                
                if plots_category_number is not None:
                    if not flag:
                        flag = True
                    
                    list_category = category[0:plots_category_number]
                    list_values = values[0:plots_category_number]
                    percentage = sum(list_values)
                    remaining_percentage = 100 - percentage
                    if remaining_percentage != 0:
                        list_category.append('Others')
                        list_values.append(remaining_percentage) 

                #--------------------------------------------------------
                #Processing information by plots_category_percentage argument
                
                if plots_category_percentage is not None:
                    if not flag:
                        flag = True

                    other_values = []

                    for num in values:
                        if num <= plots_category_percentage:
                            
                            other_values.append(num)
                    
                    percentage = sum(other_values)

                    if percentage != 0:  
                        size = len(other_values)
                        list_category = category[:-size]
                        list_values = values[:-size]                        
                        list_category.append('Others')
                        list_values.append(percentage)
                    else:
                        list_category = category    
                        list_values = values

                #------------------------------------------
                # Definition of colors for each category
                colors = []
               
                for cat in list_category:
                    if cat not in category_colors:
                        category_colors[cat] = generate_pastel_color()  
                    colors.append(category_colors[cat])
                    
                #-----------------------------------------
                #Production of image

                df = pd.DataFrame({'Category': list_category, 'Percentage': list_values})
                fig = px.pie(df, values = 'Percentage', names = 'Category', title = f'{cluster_rename}')  
                fig.update_traces(marker = dict(colors = colors))

                fig.update_layout(title_x = 0.5, annotations = [dict(
                                            x = 0.5,
                                            y = -0.2,
                                            text = f'Number of samples: {n_cluster_length}<br>{sample_increase}',showarrow=False)])  
                
                fig.write_image(f'{output}/{prefix}_{mst}_{col}_{cluster_rename}.png', format="png")              
                result_dict = {'A': mst, 'B': col, 'C': fig}    
                results_list.append(result_dict)
                strings.append(f"\t\tAnalyzing threshold {mst}, column {col}.")
                
            else:
                print_log(f'\tError: INVALID values present in the line with the {col} column at the {mst}: {row[col]}.\n', log)
                results_list = None
                 
    unique_strings = set(strings)
    for elem in unique_strings:
        print_log(elem, log)  
    
    print_log(f'\tSaving the cluster characterization plots.', log)
    return results_list    

     
def select_nomenclature_change(df_filtered_threshold, log):
    
    """  
    Select clusters with increase behavior in the 'nomenclature_change' column.
    If the 'nomenclature_change' column exists, this function filters the DataFrame to retain
    only the clusters with specific increase or new related tags.
    
    Parameters
    ----------
    df_filtered: pd.DataFrame
        DataFrame containing filtered cluster data.
    Return
    ------
    result_df: pd.DataFrame or None
        A new DataFrame containing only the rows where nomenclature_change indicates cluster increase,
        or None if the column is missing or no valid categories are found.
    """
    #print_log(f'\n---------------------------------------------- Function: select_nomenclature_change ----------------------------------------------\n', log)
    results = []

    possibilities = ['kept (increase)','new','new (increase)', 'new (merge_increase)', 'new (split_increase)', 'new (split_merge_increase)']
    
    if 'nomenclature_change' in df_filtered_threshold.columns:
        data = df_filtered_threshold['nomenclature_change'].values.tolist()   
        unique_list = set(data)
        
        for elem in unique_list:
            if elem in possibilities:
                filtered_df = df_filtered_threshold[df_filtered_threshold['nomenclature_change'] == elem]
                results.append(filtered_df)  

        if results != []:
            result_df = pd.concat(results) 
        else: 
            result_df = None
            print_log(f'\tNo information about the behavior of the “Cluster Nomenclature System” in some of the most common situations in a routine surveillance scenario.', log)
    else:
        result_df = None
        print_log(f'\tColumn nomenclature change not found in the selected file.', log)
    
    return result_df 

def get_nr_lines_threshold(partition_matrix, log):

    """
    Retrieve the number of samples (rows) and thresholds (columns) from a *_partitions.tsv file.

    Parameters
    ----------
    partition_matrix: str
        Path to the *_partitions.tsv file.
    
    Returns
    -------
    nr_columns_df: int
        Number of thresholds (columns/partitions) presents in the file.
    nr_lines_df: int
        Number of samples (rows) present in the file.
    """
    #print_log(f'\n---------------------------------------------- Function: get_nr_lines_threshold ----------------------------------------------\n', log)

    df = pd.read_table(partition_matrix)
    nr_columns_df = (len(df.columns)-1)
    nr_lines_df = len(df)
    
    return nr_lines_df, nr_columns_df

def get_file_partition_by_threshold (partition_matrix, prefix, output, log):

    """
    Generate a *_cluters_partitions.tsv or  *_cluters_partitions-filered.tsv file 
    with the number of partitions per threshold for each partition matrix (normal or filtered).
    
    Parameters
    ---------
    partition_matrix: str
        Path to the *_partitions.tsv file.
    prefix: str
        Prefix to include in the output filename.
    output: str 
        Path to the directory where the results will be saved.
    Return
    ------
    file_partition_by_threshold: str
        Path to the newly generated file. 
    """
    #print_log(f'\n---------------------------------------------- Function: get_file_partition_by_threshold ----------------------------------------------\n', log)

    order_col = ["pipeline", "threshold", "partitions"]
    info_partitions = {"pipeline": [], "threshold": [], "partitions": []}
    
    partitions = pd.read_table(partition_matrix)
   
    for i in range(1,len(partitions.columns)):
        clusters = pd.unique(partitions[partitions.columns[i]])
        info_partitions["pipeline"].append(prefix)
        info_partitions["threshold"].append(i)
        info_partitions["partitions"].append(len(clusters))

    cluster_partition_matrix = pd.DataFrame(data = info_partitions, columns = order_col)
        
    if '-' in partition_matrix:
        file_partition_by_threshold = (f'{output}/{prefix}_clusters_partitions-filtered.tsv')
    else:
        file_partition_by_threshold = (f'{output}/{prefix}_clusters_partitions.tsv')
    
    cluster_partition_matrix.to_csv(file_partition_by_threshold, index = False, header = True, sep = "\t")
    
    return file_partition_by_threshold

def get_graph_partition_by_threshold(file_partition_by_threshold, prefix, prefix_both, yes_prefix_both, output, threshold ,log):

    """
    Generate a graphic showing the number of partitions vs. thresholds
    for one pipeline using the *_clusters_partitions.tsv or *_clusters_partitions-filtered.tsv file.
    
    Parameters
    ----------
    file_partition_by_threshold: str
        Relative path to the *_cluster_partitions file. 
    prefix: str
        Prefix to name the output.
    output: str
        Full path to the directory where the results will be saved.
    
    Returns
    -------
    fig_partition_vs_threshols: plotly.graph_objs._figure.Figure
        Plotly figure object showing the number of partitions by threshold.
        
    """
    #print_log(f'\n---------------------------------------------- Function: get_graph_partition_by_threshold ----------------------------------------------\n', log)

    df = pd.read_csv(file_partition_by_threshold, sep = '\t')

    fig_partition_vs_threshols=px.line(df, x = "threshold", y = "partitions", color = "pipeline",
                             labels = {'partitions': 'Partitions', 'threshold': 'Threshold'})
    
    if threshold != 'max':
        values= threshold.split('-')
        first_value=int(values[0])
        second_value=int(values[1]) 
        values_list= [str(i) for i in range(first_value, second_value + 1)]
        n_elem=len(values_list)
        index_list=list(range(0, n_elem))

        text_list=['A']
        for elem in values_list:
            text_list.append(elem)

        fig_partition_vs_threshols.update_layout(xaxis=dict(tickvals = index_list, ticktext=text_list))
    
    fig_partition_vs_threshols.update_layout(legend=dict (orientation="h",yanchor="bottom",y=-0.35,xanchor="center", x=0.5), margin=dict(l=0, r=0, t=20, b=0))

    if yes_prefix_both == False:
        fig_partition_vs_threshols.write_image(f'{output}/{prefix}_lineplot.png', format = "png")
    
    if yes_prefix_both == True:
        fig_partition_vs_threshols.write_image(f'{output}/{prefix_both}_lineplot.png', format = "png")
    
    return fig_partition_vs_threshols

def concatenation_files(file1, file2, output, prefix_both):

    """
    Concatenate two TSV files containing cluster partition data (one of each pipeline) and save the result.

    Parameters
    ----------
    file1 : str
        Path to the first TSV file.
    file2 : str
        Path to the second TSV file.
    output: str
        The directory where the combined file will be saved.
    prefix_both : str
        Prefix for naming the output file.

    Returns
    -------
    path: str
        Full path to the saved concatenated file.
    """
    #print(f'\n---------------------------------------------- Function: concatenation_files----------------------------------------------\n')

    df_cp1 = pd.read_csv(file1, sep = '\t')
    df_cp2 = pd.read_csv(file2, sep = '\t')
    df1 = pd.DataFrame(df_cp1)
    df2 = pd.DataFrame(df_cp2)

    df_combined = pd.concat([df1, df2])

    path = f'{output}/{prefix_both}_cluster_partitions.tsv'
    df_combined.to_csv(path, index = False, header = True, sep = "\t")

    return path

def organize_clusters(results_list):

    """
    Organizes plotly figure objects by threshold (e.g., MST) and by category 
    (e.g., source, country).

    Parameters
    ----------
    results_list : list
        A list of dictionaries, each containing:
        - "A": threshold/method string (e.g., 'MST-4x1.0')
        - "B": category string (e.g., 'country' or 'source')
        - "C": a Plotly figure object (plotly.graph_objs._figure.Figure)

    Returns
    -------
    mst_groups : dict
        The dictionary is organized by threshold and then by category.
    """
    #print(f'\n---------------------------------------------- Function: organize_clusters----------------------------------------------\n')
    
    method_groups = {}
    
    for item in results_list:
        method = item["A"]
        category = item["B"]
        image = item["C"]

        if method not in method_groups:
            method_groups[method] = {}

        if category not in method_groups[method]:
            method_groups[method][category] = []

        method_groups[method][category].append(image)
    
    return method_groups

def processing_block_names(file_stability, prefix, log):

    """
    Identifies the names of stability blocks in a *_stableRegions.tsv file and adds a prefix to each.

    Parameters
    -----------
    file_stability: str
        Path to the *_stableRegions.tsv file.
    
    prefix: str
        Prefix to prepend to each block name.

    Returns
    -------
    name_block : list or None
        List of block names with the given prefix, or None if the file is empty.
    """
    #print_log(f'\n---------------------------------------------- Function: processing_file_sta_reg----------------------------------------------\n', log)
   
    df = pd.read_csv(file_stability, sep = '\t', comment = "#", header = None)

    if df.empty:
        name_block = None
    else:
        name_block = []
        for elem in df[0]:
            string = f'{prefix}_' + elem
            name_block.append(string)

    return name_block

def processing_data(file, log):
    
    """
    Extracts the start and end positions of stability blocks from a *_stableRegions.tsv file.

    Paramenter
    ----------
    file: str
        Path to the *_stableRegions.tsv file.
    
    Returns
    -------
    first_data: list of int
        List of integers identifying the start of each stability block.

    final_data: list of int
        List of integers identifying the end of each stability block.

    values_block: list of int
        Combined and sorted list of all start and end points.
    """
    #print_log(f'\n---------------------------------------------- Function: processing_data----------------------------------------------\n', log)

    df = pd.read_csv(file, sep="\t", comment='#', header=None)
    
    first_data = []
    final_data = []

    for elem in df[1]:
        line = elem.split('-')
        value = line[3]
        first_partition = value.split('x')[0]
        first_data.append(int(first_partition))  

    for elem in df[2]:
        line = elem.split('-')
        value = line[1]
        last_partition = value.split('x')[0]
        final_data.append(int(last_partition)) 

    return first_data, final_data

def change_processing_data(final_df, i1_prefix, i2_prefix, output, log):

    """
    Conversion of dataframe values in logarithms to create the graph.

    Parameters
    ----------
    final_df: pd.DataFrame
        Dataframe with the start and end of each block per pipeline

    i1_prefix: str
        Prefix added to the result in pipeline i1

    i2_prefix: str
        Prefix added to the result in pipeline i2
    """

    #print_log(f'\n---------------------------------------------- Function: change_processing_data----------------------------------------------\n', log)

    df_final = final_df.rename(columns={"Finish": "temp"})
    
    df_final['temp']=np.log2(df_final['temp'])
    df_final['Start'] = np.log2(df_final['Start'])
    df_final['Finish'] = df_final['temp'] - df_final['Start']
    df1_inverted = df_final.iloc[::-1]  
     
    max_val = df1_inverted["temp"].max()
    max_val_1= int(round(2 ** max_val,0))
    list_tickvals = list(range(1, max_val_1 + 1))
    list_ticktext= [str (2 ** x) for x in range(1, max_val_1 + 1)]
    

    fig_st = px.bar(df1_inverted,
                    x="Finish",
                    y="Block_id",
                    base='Start',
                    color="Pipeline",  
                    orientation="h")

    fig_st.update_layout(
                    xaxis_title = "Threshold",
                    yaxis_title = '',
                    xaxis = dict(
                    tickvals = list_tickvals,  
                    ticktext = list_ticktext), 
                    yaxis = dict(showticklabels=False),  legend=dict( orientation="h",yanchor="bottom",y=-0.35,xanchor="center", x=0.5), margin=dict(l=0, r=0, t=20, b=0))
           
    if i2_prefix is None:
         prefix=f'{i1_prefix}'
    else:
        prefix=f'{i1_prefix}_vs_{i2_prefix}'

    fig_st.write_image(f'{output}/{prefix}_StableRegions.png', format='png')


    return fig_st

#################################################################### OUTBREAKS ###############################################################

def validate_combinations_outbreak(threshold_outbreak):

    """
    Validates the structure of threshold_outbreaks combinations, including their components, and
    identifies the comparison type and thresholds for outbreak analysis.

    The comparison type supported:
    - "equal" (defined by ',')
    - "lower_equal" (defined by '<=')

    Multiple combinations must be separated by semicolons (';'), without spaces.

    This function processes one or more threshold pairs, extracting threshold_1, threshold_2, and  the comparison type.

    It also validates that each threshold follows the expected pattern: string-integerxfloat (e.g., 'MST-7x1.0').

    Parameters
    ----------
    threshold_outbreak: str
        One or more outbreak threshold combinations provided by the user.

    Returns
    -------
    valid_combinations: list
        A list of sublists ([[threshold_1, threshold_2, comparison_type]]) containing valid combination structures 
        for downstream outbreak analysis.
    """
    #print(f'\n---------------------------------------------- Function: validate_combinations_outbreak----------------------------------------------\n')

    regex = r'^[A-Za-z]+-\d+x\d+\.\d+$'
    valid_combinations = []  
    combos = threshold_outbreak.split(';')
    
    for combo in combos:
       
        parts = combo.split(',')
         
        if len(parts) != 2:
            sys.exit(f"The combination '{combo}' must have 2 elements separated by a comma (e.g., 'MST-7x1.0,MST-7x1.0'). Multiple combinations must be separated by ; . Please, do not use spaces.")

        pattern1 = parts[0]

        if parts[1].startswith('<='):
            pattern2 = parts[1][2:]
        else:
            pattern2 = parts[1]
        
        if not re.match(regex, pattern1):
            sys.exit(f"Error: Pattern '{pattern1}' (part 1) is not in the correct format (e.g., 'MST-7x1.0'). Please, do not use spaces.")

        if not re.match(regex, pattern2):
            sys.exit(f"Error: Pattern '{parts[1]}' (part 2) is not in the correct format (e.g., 'MST-7x1.0' or '<=MST-10x1.0'). Please, do not use spaces.")
 
        if parts[1].startswith('<='):
            valid_combinations.append([parts[0], parts[1], 'lower_equal'])
        else:
            valid_combinations.append([parts[0], parts[1], 'equal'])

    return valid_combinations

def extract_integer_part(valid_combinations, log):

    """
    Extract the integer thresholds from string-formatted threshold.
    Paramenter
    ---------
    valid_combinations: list
        List of sublist ([[threshold_1, threshold_2, type_comparison]]),
        containing the valid combinations structure to use in the downstream outbreak analysis.

    Return
    ------
    extracted: list
        List of tuples [(integer, integer, type_comparison)] with the extracted integer values and the comparison type,
        to be used in the command-line call of the script `stats_outbreak_script.py`
    """
    #print_log(f'\n---------------------------------------------- Function: extract_integer_part----------------------------------------------\n', log)

    values_outbreak = []

    for p1, p2, comp in valid_combinations:
        n1 = int(p1.split('-')[1].split('x')[0])
        n2 = int(p2.split('-')[1].split('x')[0])
        values_outbreak.append((n1, n2, comp))

    return values_outbreak

def creation_tsv_stats_outbreak(clusterComposition_1, clusterComposition_2, output, prefix_both, log):

    """
    Create a new file (*_path_stats_outbreak.tsv) containing the path to each *clusterComposition.tsv file
    (these files can be obtained with ReporTree), which will be used as an input argument to stats_oubtreak analysis.py script.

    Parameters
    ----------
    clusterComposition_1: str
        Path to the *cluster_composition file of pipeline 1.
    and clusterComposition_2: str
        Path to the *cluster_composition file of pipeline 1.
    output: str
        Path to the directory where the results will be saved.
    prefix_both: str
        Prefix added to the result files generated from both pipelines (e.g., XXX_vs_XXX).
    
    Return
    ------
    df: pandas.DataFrame
        DataFrame containing the paths to the clusterComposition.tsv files.
    path_comparison_outbreak: str
        Path to the *_path_stats_outbreak.tsv file.
    """
    #print_log(f'\n---------------------------------------------- Function: creation_tsv_stats_outbreak ----------------------------------------------\n', log)    

    data=[[clusterComposition_1], [clusterComposition_2]]
    df=pd.DataFrame(data)
    path_stats_outbreak=f'{output}/{prefix_both}_path_stats_outbreak.tsv'
    df.to_csv(path_stats_outbreak, sep='\t', index=False, header=None)

    return df, path_stats_outbreak
                      
    
def calling_script_outbreak(python,stats_outbreak_script, path_stats_outbreak, output, prefix_both, values_outbreak, log):
    
    """
    Calls the outbreak script.

    Parameters:
    -----------
    stats_outbreak_script: str
        Path to the stats_outbreak_analysis.py script.
    path_stats_outbreak: str
        Path to the *_path_stats_outbreak.tsv file.
    output: str
        Path to the directory where the results will be saved.
    prefix_both: str
        Prefix added to the result files generated from both pipelines (e.g., XXX_vs_XXX)
    values_outbreak: list
        The struture of tuple list is i.e, [(threshold1, threshold2, type_comparison)] 

    Return:
    ------
    Files produced by script, i.e,:
        -XX_vs_XX_stats_outbreak_missing_clusters_INTEGER_equal_INTEGER.tsv
        -XX_vs_XX_stats_outbreak_pairwise_comparison_INTEGER_equal_INTEGER.tsv
        -XX_vs_XX_stats_outbreak_pairwise_comparison_INTEGER_equal_INTEGER_pct.tsv
        -XX_vs_XX_stats_outbreak_summary_INTEGER_equal_INTEGER.tsv       
    """
    #print_log(f'\n---------------------------------------------- Function: calling_script_outbreak ----------------------------------------------\n', log)

    if values_outbreak !=[]:
        for th1,th2,type_comparison in values_outbreak:
            
            cmd= [python, stats_outbreak_script, "-i", path_stats_outbreak, "-t1", str(th1), "-t2", str(th2),
            "-o", f"{output}/{prefix_both}_stats_outbreak", "-c", type_comparison]            

            subprocess.run(cmd,capture_output=True, text=True)

            print_log(f"\tRunning stats_outbreak_analysis.py for {th1} {type_comparison} {th2}", log)
            print_log(f'\t\t{" ".join(cmd)}', log)

        print_log(f"\tDone!", log)
    else:
        print_log(f'\tImpossible to call the stats_outbreak_analysis.py.', log)

def read_files_outbreak(output):
   
    """
    Identifying of the file *stats_outbreak_pairwise_comparison_*_pct.tsv, which contains percentage values of clusters detected by one pipeline that are also detected,
    with the exact same composition, by another pipeline.
    
    Parameters:
    ----------
    output: str
        Path to the directory where the results will be saved.

    Return:
    ------
    process_files: list
        List with the full path of *stats_outbreak_pairwise_comparison_*_pct.tsv.
    """
    #print(f'\n---------------------------------------------- Function: read_files_outbreak ----------------------------------------------\n')
    
    files_outbreak_pct=os.listdir(output)
    process_files=[]
    for file in files_outbreak_pct:
        if file.endswith('_pct.tsv'):
            path_file=f'{output}/{file}'
            abs_path_file=os.path.realpath(path_file)
            process_files.append(abs_path_file)
    
    return process_files
  
def creation_overlap_clusters(process_files, output, values_oubreak):

    """
    Production of the graphics with the overlap genetic clusters according the threshold outbreak.

    Parameters:
    -----------
    process_files: list
        List with the full path of *stats_outbreak_pairwise_comparison_*_pct.tsv.

    output: str
        Path to the directory where the results will be saved.
    
    values_outbreak: list
        List of tuples [(integer, integer, type_comparison)] 

    Return:
    ------
    fig_result: list
        List of images (plotly.graph_objs._figure.Figure). 
    """
    #print(f'\n---------------------------------------------- Function: creation_overlap_clusters ----------------------------------------------\n')

    result=[]
    for th1, thr2, type_compo in values_oubreak:
        for path in process_files:
            if f'_{th1}_{type_compo}_{thr2}_' in path:
                result.append([th1,thr2,type_compo,path])

    fig_result=[]   
    thresholds=[]
    for i in result:
        file=i[3]
        thr1=i[0]
        thr2=i[1]
        type_com=i[2]

        df=pd.read_table(file) 
        df_filtered = df.drop(df.columns[0], axis=1)
        
        if df_filtered.shape[1] == 2:
            values_col1 = df_filtered.columns[0]  
            values_col2 = df_filtered.columns[1]  
            
        if df_filtered.shape[0] <= 2:
            df_filtered[''] = ''
            values_col1 = df_filtered.columns[0]
            values_col2 = df_filtered.columns[1]
            
        df_percentage= df_filtered*100
        name_file=os.path.basename(file)
        base, ext=os.path.splitext(name_file)

        if type_com=='equal':
            string1=f'at {thr1} threshold'
            string2=f'at {thr2} threshold'
        else:
            string1=f'at {thr1} threshold'
            string2=f'at up {thr2} threshold'
        thresholds.append((thr1,thr2,type_com))
        
        colors = [[0, 'white'], [0.5, 'white'], [0.5, '#FDFD96'], [1, '#89B6E3']]  

        fig = go.Figure(data=go.Heatmap(
            z=df_percentage.values,  
            x =[f'{values_col1}', f'{values_col2}'],
            y =[f'{values_col1}', f'{values_col2}'],
            text=df_percentage.values,
            texttemplate="%{text:.2f}%",  
            textfont=dict(size=11, color="black"),
            colorscale=colors, 
            colorbar=dict(title="Overlap"),
            zmin=0, zmax=100
        ))

        fig.update_layout(
            xaxis_title=f"Cluster detected {string2}",
            yaxis_title=f"Cluster detected {string1}",
            plot_bgcolor='white',  
            paper_bgcolor='white', margin=dict(l=0, r=0, t=20, b=0))

        fig.write_image(f'{output}/{base}.png', format="png")
        fig_result.append(fig)
        
    return fig_result, thresholds

def get_plot_columns(file):

    """
    Get the names of the available columns for cluster plots in a given summary file (*_partition_summary or *_sample_of_interest), to perform the cluster characterization.

    Parameters
    ----------
    file: str
        Path to the *_partitions_summary.tsv or *_SAMPLE_OF_INTEREST_partitions_summary.tsv file.

    Return
    ------
    List of columns present in the file that are not part of the default memory_columns.
    If none are found, the program exits with an error message.
    """
    #print(f'\n---------------------------------------------- Function: get_plot_columns_list ----------------------------------------------\n')
   
    memory_columns = ['partition', 'cluster', 'nomenclature_change', 'n_increase', 'cluster_length', 'samples', 'samples_increase','SAMPLE_OF_INTEREST']

    df = pd.read_csv(file, sep = "\t")
    name_folder = file.split('/')[0]
    print(f"\nAvailable columns for {name_folder}:")

    columns_df=df.columns.tolist()

    attachement_list=[]
    for elem in columns_df:
        if elem not in memory_columns:
            attachement_list.append(elem)
    
    if attachement_list != []:   
        for elem in attachement_list:
            print(f'\t- {elem}')
    else:
        sys.exit(f'Error: No additional columns found in {file}.')       
   
def find_html_outbreak(output,prefix_both,log):
    
    """
    Check if there is an initial HTML report and if the second HTML report, created by the reanalysis of the threshold outbreak (-rto argument), exists.

    Parameters
    ---------
    output: str
        Path to the directory where the results will be saved.
    prefix_both: str
        Prefix added to the result files generated from both pipelines (e.g., XXX_vs_XXX)

    Return
    ------
    final_files: <class 'list'>
        If the files exist, a list with their relative paths is created.
    """
    #print_log(f'\n---------------------------------------------- Function: find_html_outbreak----------------------------------------------\n', log)
    
    all_files = os.listdir(output) 

    expected_new_report = f"{prefix_both}_2ºRUN_report.html"
    expected_report = f"{prefix_both}_report.html"

    if expected_new_report not in all_files:
        sys.exit(f"Error: {expected_new_report} not found!")

    if expected_report not in all_files:
        sys.exit(f"Error: {expected_report} not found!")

    final_files = [expected_new_report, expected_report]

    return final_files

def extration_section_original_file(output, final_files, log):

    """
    Extracts specific sections (e.g., clustering and congruence) from an original HTML file,
    and saves them in a temporary text file for later use (e.g., to merge with another report).

    Parameters:
    ----------
    output: str
        Path to the directory where the results will be saved.
    final_files: list
        List with relative paths to the HTML reports.

    Return:
    ------
    path_temp: str
        Path to the *.txt file with clustering and congruence information.
    """
    #print_log(f'\n---------------------------------------------- Function: extration_section_original_file----------------------------------------------\n', log)

    original = final_files[1]
    original_file = f'{output}/{original}'
   
    line = 71

    with open(original_file, "r") as f:
        lines = f.readlines()

    end = '<button class="accordion">Outbreak</button>'
    path_temp = f'{output}/exit.txt'

    with open(path_temp, "w") as f:
        for current_line in lines[line-1:]:
            if end in current_line:  
                break
            f.write(current_line)

    print_log(f"Content saved in: {path_temp}", log)
    return path_temp

def transfer_info_to_html_content(path_temp, html_content, log):

    """
    Reads clustering and congruence information from a temporary .txt file,
    appends it to the existing HTML header content, and deletes the .txt file.

    Parameters
    ----------
    path_temp: str
        Path to the *.txt file containing clustering and congruence information.

    html_content: str
        Initial content of the new HTML report (e.g., header section).

    Return:
    ------
    Merges the header of the new report with the clustering and congruence analysis from the initial report.
    """

    #print_log(f'\n---------------------------------------------- Function: transfer_info_to_html_content----------------------------------------------\n', log)

    if os.path.exists(path_temp):
        #print_log(path_temp, log)
        with open(path_temp, 'r') as input_file:
            content = input_file.read()
           
    else:
        print_log('There was a problem with the creation of the file containing information about clustering and congruence for the second HTML report.', log)
    html_content = content
    #os.remove(path_temp)
    return html_content
  
################################################################  MODULE 1  ################################################################################

def reading_sequence_type(sequence_type_file, output, prefix_st, log):

    """
    Reading the sequence type matrix.

    Parameters
    ----------
    sequence_type: str
        Full path to the sequence type matrix.

    output: str
        Path to the directory where the results will be saved.

    prefix_st: str
    	The prefix that will be added to the file.
     
    Returns
    -------
    fig: plotly.graph_objs._figure.Figure
        Code to produce figure
    """

    #print_log(f'\n---------------------------------------------- Function: reading_sequence_type----------------------------------------------\n', log)
    
    df=pd.read_table(sequence_type_file)
    column=df.columns[1]

    name_cluster=[]
    nr_cluster=[]

    for elem in df[column]:
        if elem not in name_cluster:
            name_cluster.append(elem)  
            number = df[column].tolist().count(elem) 
            nr_cluster.append(number)
            
    new_df = pd.DataFrame({"Cluster": name_cluster, "Count": nr_cluster})
    fig = px.bar(new_df, x="Cluster", y="Count", title=f"Most represented STs in the {prefix_st} pipeline", labels={"Cluster": "Cluster name", "Count": "Number of samples"})
    fig.update_layout(title_x=0.5)
    fig.write_image(f'{output}/{prefix_st}_pipeline_clusters.png', format='png')
    
    return fig


###########################################################################################################################################################
########################################################################## HTML ###########################################################################
###########################################################################################################################################################

def create_html(log, file_path_report):

    """
    Opening HTML file to save the dynamic graphs of the various analyses.
    
    Parameters
    ----------
    log: <class '_io.TextIOWrapper'>

    file_path_report: str
        Full path to the HTML file with all analysis results.

    Return
    ------
    html_content: str
        It contains the body of an HTML document.

    """
    #print_log(f'\n---------------------------------------------- Function: create_html----------------------------------------------\n',log)
    
    name_file=os.path.basename(file_path_report)      
    title="Report EvalTree"
        
    html_content= f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{title}</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script> 
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        section {{ margin: 20px 0; }}

        
        /* ------------------------- CLUSTERING images------------------------------------------- */
        .image-row {{  
            display: flex;
            flex-wrap: wrap;
            justify-content: space-around;
            margin-top: 20px;
        }}

        .image-item {{
            flex: 1 1 calc(25% - 20px); 
            box-sizing: border-box;
            margin: 10px;
            max-width: calc(25% - 20px);                 
        }}

        /* --------------------------- START Accordion ------------------------------------------- */
        .accordion {{
            background-color: #eee; 
            color: #444;
            cursor: pointer;
            padding: 18px; 
            width: 100%;
            border: none;
            text-align: left;
            outline: none; 
            font-size: 20px;
            transition: 0.4s;
            font-weight: bold; 
        }}
        .active, .accordion:hover {{background-color: #ccc;}}

        .panel {{ padding: 0 10px;
            display: none;
            background-color: white;
            overflow: hidden;}}

        /* --------------------------- END Accordion ------------------------------------------- */

        .image-heatmap {{
            display: flex;
            justify-content: space-around;
            margin-top: 20px;
            flex-wrap: wrap;
        }}

        .compact {{margin: 2px 0; line-height: 1.2;}}
    </style>
</head>
<body>
    <header>
        <h1>EvalTree Report</h1>
        <p> Toolbox for comparative clustering evaluation of whole genome sequencing pipelines for bacteria routine surveillance</p>
    </header>"""

    return html_content

def body_html(start, command_line,version):

    html_content=f"""<button class="accordion">Overview</button>
    <div class="panel">
        <p>Report generated on: {start}</p>
        <p>Entered command line: {command_line}</p>
        <p>Version: {version}</p>
    </div>
    """
    return html_content

def get_sequence_type(prefix_st,samples_st,groups_st,sequence_type_file):

    html_content=f"""
    <button class="accordion">Pipeline characterization: {prefix_st}</button> 
        <div class="panel">
            <p>Number of samples: {samples_st} </p>
            <p>Number of groups:{groups_st} </p>
            <p> Name of file: {sequence_type_file}</p>
    """
    return html_content

def sequence_type_image(fig_html):

    html_content=f"""
         <div>{fig_html}</div></div>
    """
    return html_content

def get_partitions_threshold(prefix_single, nr_lines_df, nr_columns_df, fig_partition_vs_threshols):

    fig_partition_vs_threshols.update_layout(margin=dict(l=0, r=0, t=20, b=0))
    fig_pt=pio.to_html(fig_partition_vs_threshols, include_plotlyjs='cdn', full_html=False)
    
    html_content= f"""<button class="accordion">Pipeline characterization: {prefix_single}</button> 
        <div class="panel">
        <h3> Summary: {prefix_single} </h3>
        <p> Number of samples: {nr_lines_df} </p>
        <p> Number of thresholds: {nr_columns_df} </p> 
        <h3> Number of partitions per threshold </h3> 
        <div> {fig_pt} </div>  
        <p> This line plot shows the number of partitions (groups) at each threshold. </p>  
    """
    return html_content

def get_clusters(mst_groups, prefix):

    """
    Display pie charts by threshold and category, generating CLUSTER HTML content for each pipeline.
    
    Parameters
    ----------

    mst_groups: dict
	Categories and images.
    prefix: str
        Prefix the name of the file that is being processed.

    Return
    -----
    HTML file with data chosen by the user."
    """

    html_content=''
    html_content +=f'<button class="accordion"> ReporTree clustering visualization: pipeline {prefix} </button>\n'
    html_content +=f'<div class="panel">\n'
    
    for mst, categories in mst_groups.items():

        html_content += f'<button class="accordion">Threshold: {mst}</button>\n'
        html_content += f'<div class="panel">\n'

        for category, images in categories.items():
            html_content += f"<h4>Category: {category}</h4>\n"
            html_content+=f'<div class="image-row">\n'   

            for image in images:
                #width_percent = 25
                fig_html=pio.to_html(image, include_plotlyjs = 'cdn', full_html = False)
                html_content += f'<div class="image-item">{fig_html}</div>\n' 
                #html_content += f'<div class="image-item" style="flex: 0 0 {width_percent}%; max-width: {width_percent}%;">{fig_html}</div>\n'
                 
            html_content += f"</div>\n" 
        html_content += f'</div>\n'
    html_content += f'</div>\n' 
    html_content += f'</div>\n' 

    return html_content

def summary_congruence():

    html_content=f"""
    </div>
    <button class="accordion">Inter-pipeline cluster congruence</button> 
        <div class="panel" >
       <p > This section evaluates the clustering congruence between two WGS-based pipelines by comparing their cluster compositon at all possible threshold levels.
       The goal is to assess how similarly the pipelines group the isolates, by measuring the consistency of cluster assignments at each threshold. 
        
        More detailed information is available on the
        <a href="https://github.com/insapathogenomics/CENTAUR/tree/main/EvalTree" target="_blank" rel="noopener noreferrer">
            EvalTree GitHub 
        </a>.
    </p>
        
    """
    return html_content

def summary_partition_threshold(fig_html_partition_threshold, prefix_both):

    html_content=f"""
        <h3> Number of partitions per threshold </h3>
        <div> {fig_html_partition_threshold} </div>
        <p class="compact"> The line plot shows the number of partitions  at each threshold.</p>
        <p class="compact"> Detailed information is available in the <code> {prefix_both}_cluster_partitions.tsv</code> file.</p>
    """
    return html_content
   
def congruence_stability(fig_html_st, prefix, prefix_2, n_stability, thr_stability):
   
    html_content=f"""
        <h3> Blocks of stability regions </h3>
        <div>{fig_html_st}</div>
        <p class="compact"> For each pipeline, clustering stability regions are defined as a range of thresholds e.g., {n_stability} with a nAWC of  e.g., {thr_stability} which cluster composition remains stable/consistent. </p>
        <p class="compact"> To better distinguish each region (represented by separated rectangle blocks), the blocks are vertically offset, starting on a different line. </p> 
        <p class="compact"> Distance thresholds (x axis) are presented in log2 scale. </p>
        <p class="compact"> Detailed information is available in the following files: </p>
    """
    
    html_content += f"- <code>{prefix}_metrics.tsv"
    if prefix_2 is not None:
        html_content += f" and {prefix_2}_metrics.tsv"
    html_content += f": summarizes all comparisons between consecutive pairs of thresholds (“n + 1” → “n”).</code>"
    
    html_content += f"<br>- <code>{prefix}_StableRegions.tsv"
    if prefix_2 is not None:
        html_content += f" and {prefix_2}_StableRegions.tsv"
    html_content += f": lists the block names, their respective threshold range, and the length of each block.</code>"


    return html_content
    
def congruence_heatmap(fig_html_heatmap, prefix_both):

    split_prefix=prefix_both.split('_')
    first=split_prefix[0]
    second=split_prefix[-1]

    html_content=f"""
        <h3> Congruence score </h3>
        <div class='image-heatmap'>{fig_html_heatmap} </div>
            <p class="compact"> The heatmap shows a pairwise comparison of clustering results from two pipelines, {first} and {second}, at all possible distance thresholds. </p>
            <p class="compact"> The congruence score (CS) is a metric ranging from 0 (no congruence between methods) to 3 (absolute congruence).</p>
            <p class="compact"> Detailed information is available in the <code> {prefix_both}_final_score.tsv </code> file.</p>
    """
    return html_content

def congruence_tendency(fig_tendency_html, score_value, prefix_both, nr_point_method_1, nr_point_method_2):

    pipeline1=prefix_both.split('_vs_')[0]
    pipeline2=prefix_both.split('_vs_')[-1]

    html_content= f"""
        <h3> Corresponding points </h3>
            <div> {fig_tendency_html} </div>
            <p class="compact"> This graph shows the corresponding points(thresholds) between the two pipelines in both directions above (CS >= {score_value}). </p>      
            <p class="compact"> When comparing a set of samples between two pipelines, the probability of two sample clustering together in one method/pipeline in a given threshold
            may not to be the same in the other method/pipeline. Therefore:</p>
            <p class="compact"> - First, the threshold in the {pipeline1} pipeline (method 1) that produces clustering results most similar to those in the {pipeline2} pipeline (method 2) is identified. </p>
            <p class="compact"> - Then, the threshold in the {pipeline2} pipeline (method 1) that produces clustering results most similar to those in the {pipeline1} pipeline (method 2) is identified.</p>
            <p class="compact"> Both methods produce similar clustering results when the tendency line has a slope near 1. </p>
            <p class="compact">A linear tendency line supported by {nr_point_method_1} (blue) and {nr_point_method_2} (orange) points is presented. </p>
            <p class="compact"> Detailed information is available in the <code> {prefix_both}_All_correspondence.tsv </code> file. </p>
            <p style="margin-bottom: 8px;"></p>
        </div>
    """
    return html_content

def congruence_st(fig_html_heatmap, prefix_both):

    html_content= f"""
        <button class="accordion">Congruence</button>
        <div class="panel">
            <p> This section makes it possible to evaluate the congruence of the two genomic pipelines. </p>
            <h3> Congruence score </h3>
            <div class="image">{fig_html_heatmap} </div>
            <p> Sequence type {prefix_both} pipelines</p>
        </div>
    """
    return html_content
   
def html_tradicional_typing(n_samples,n_groups, prefix):

    html_content= f"""  
        <button class="accordion">Sequence type {prefix}</button>
        <div class="panel">
            <p>Number of samples: {n_samples}</p>
            <p>Number of groups: {n_groups}</p> 
        </div>
    """
    return html_content

def image_outbreak(fig_result):

   
    html_content=''
    html_content +=f'<button class="accordion">Outbreak</button>'
    html_content +=f'<div class="panel">' 
    html_content+=f'<div class="image-row">\n'
    
    for fig in fig_result:
        fig_html=pio.to_html(fig, full_html=False, include_plotlyjs='cdn')  
        html_content += f'<div class="image-item">{fig_html}</div>' 
    #html_content+='</div>'
    html_content+='</div>'
    
    return html_content

def summary_outbreak(prefix_both, thresholds):
    
    html_content=f"""
    <p class="compact">Determines the percentage of clusters identified in a pipeline at a given threshold that could be detected with the same composition by another pipeline at a similar or even higher threshold.</p>   
    """
    for elem in thresholds:
        string1, string2, type_com = elem
        html_content += f"""<p class="compact"> Detailed information is available in the <code> {prefix_both}_stats_outbreak_summary_{string1}_{type_com}_{string2} file.</code></p>"""
        html_content += f"""<p class="compact"> Detailed information is available in the <code> {prefix_both}_stats_outbreak_pairwise_comparison_{string1}_{type_com}_{string2} file.</code></p>"""
    html_content += f"""</div> """
    
    return html_content

def references():

    html_content = f"""
    <p style="font-size: 10pt;"> <strong> References:</strong> </p>
    <p style="font-size: 8pt;"><a href="https://doi.org/10.1038/s41467-025-59246-8" target="_blank">Mixão V et al. (2025). Multi-country and intersectoral assessment of cluster congruence between pipelines for genomics surveillance of foodborne pathogens. <em>Nature Communications</em>, 16, Article 3961.</a></p>
    <p style="font-size: 8pt;"> EvalTree relies on the work of other developers. So you must also cite: </p>
    <p style="font-size: 8pt;"> -<a href="https://genomemedicine.biomedcentral.com/articles/10.1186/s13073-023-01196-1"> Mixão V et al. (2023). ReporTree: a surveillance-oriented tool to strengthen the linkage between pathogen genetic clusters and epidemiological data.</a></p>
    <p style="font-size: 8pt;"> -<a href="https://journals.asm.org/doi/10.1128/jcm.02536-05?permanently=true"> Carriço J et al. (2006). Illustration of a Common Framework for Relating Multiple Typing Methods by Application to Macrolide-Resistant Streptococcus pyogenes.</a></p>
   <br></br>
    <p style="text-align: center; max-width: 1000px; margin: 0 auto;">
        <em>EvalTree.py</em> is a tool developed in the frame of the <strong>CENTAUR project</strong> (supported by the European ISIDORe initiative) at the
        Genomics and Bioinformatics Unit of the Department of Infectious Diseases in the National Institute of Health Dr. Ricardo Jorge (INSA, Portugal).
    </p>

    """

    return html_content
def javascript_function():

    html_content=f"""
    <script>
    var acc = document.getElementsByClassName("accordion");
    var i;

    for (i = 0; i < acc.length; i++) {{
        acc[i].addEventListener("click", function() {{
            var panel = this.nextElementSibling;
            if (panel.style.display === "block") {{
                panel.style.display = "none";
            }} else {{
                panel.style.display = "block";
            }}
        }});
    }}
    </script>
    """

    return html_content

def write_html(html_content, file_path_report, log):
    
    """
    Writing HTML

    Parameters
    ----------
    html_content: str
        Code of HTML report.

    file_path_report: str
        Path of the report  HTML file.
    Return
    -----
    file_path_report: str
        HTML file with results.
    """
    #print(f'\n---------------------------------------------- Function: write_html----------------------------------------------\n')

    with open(file_path_report, "w") as file:
        file.write(html_content)
    print_log(f"\nReport successfully generated in:\n {file_path_report}.\n", log)     

def create_html_footer():
    return """
    </body>
    </html>
    """

def close_painel(prefix, message=None):
    html_content = f"""
    <button class="accordion">Clusters {prefix}</button>
    <div class="panel">
    """

    if message:
        html_content += f'<p>{message}</p>\n'

    html_content += "</div>\n"
    html_content += "</div>\n"

    return html_content


def print_log(message, log):
	""" print messages in the terminal and in the log file """

	print(message)
	print(message, file = log)



def is_folder_empty(folder_path):
    """
    Checks if a folder exists and is empty.
    """
    if os.path.exists(folder_path) and not os.listdir(folder_path):
        sys.exit(f"The folder '{folder_path}' exists but is empty.") 


#####################################################################################################################################
###################################################################***###############################################################
###############################################################***EvalTree***##########################################################
###################################################################***###############################################################
#####################################################################################################################################

def main():
    """
    This function is instrumental in the tool. 
    It manages the flow of the program, determining which functions to call and in what order.

    Parameters
    ---------
        Without parameters, it will pass all arguments entered by the user.
    
    Returns
    ---------
        None

    """
    #-------------------------------------------------------------------------------------------------------------------------------------
    #  Configures the parser for command line arguments

    parser = argparse.ArgumentParser(description="Running EvalTree")
    parser = argparse.ArgumentParser(prog="EvalTree.py",
                                    formatter_class=argparse.RawDescriptionHelpFormatter,
                                    description=textwrap.dedent("""                                                                                                                                   
    EvalTree.py
    
    EvalTree was designed for comparing two genomic pipeline inputs (e.g., cg/wgMLST, traditional sequence-type matrix), with three main functionalities:

    - Evaluates the congruence between the pipelines.
    - Characterizes genetic clusters.
    - Detects closely related outbreak clusters at given thresholds.
    
    The EvalTree toolbox accepts two types of inputs: folders and files.
    - Folders must be derived from ReporTree outputs (highly recommended). Pipelines of cg/wgMLST should contain clustering data (clusters and/or singletons) for
     all possible thresholds in a partition.tsv file.
    - Files can be partition files or other types of files with classifications (e.g., sequence-type, serotypes).
    It will return an interactive HTML report based on the selected arguments.

    The following arguments are used for specific analyses:

    - plot_summary, plots_threshold, column_plot, n_cluster, plots_category_number, plots_category_percentage: These are used exclusively to characterize genetic clusters from
    ReporTree output files (e.g., *_partitions_summary.tsv).
    - score and threshold: These are used in the cg/wgMLST pipeline congruence analysis.
    - threshold_outbreak, repeat_threshold_outbreak: These are used in the outbreak analysis, utilizing the cluster_composition.tsv file produced by ReporTree."""))

    # Mandatory arguments
    parser.add_argument("-i1", "--input1",
            action = "store",
            required = True,
            help = '[MANDATORY] Specifies the first input type (folder or file), requiring the full path. \
                    The folder must contain the partition matrix file with clustering data, and is highly recommended to be a Reportree output folder.\
                    Alternatively, the file can be a traditional sequence-type matrix or a partition matrix.\
                    Using either of these input types enables the analysis.')

    parser.add_argument("-i2", "--input2",
            action = "store", 
            required = False,
            help = '[OPTIONAL] Specifies the second input type (folder or file), requiring the full path. \
                    The folder must contain the partition matrix file with clustering data, and is highly recommended to be a Reportree output folder. \
                    Alternatively, the file can be a traditional sequence-type matrix or a partition matrix. \
                    Using either of these input types enables the analysis.')
    
    parser.add_argument("-o", "--output",
            action = "store",
            help = '[OPTIONAL] Specifies the output directory for storing all analysis results. \
                    If no folder is provided, the program will automatically create one based on the prefix of the files.')

    # Optional arguments
    parser.add_argument('-s', '--score',
            dest = 'score',
            default = '2.85',
            help = '[OPTIONAL] Define a minimum score to consider two partitions (one from each pipeline) as corresponding. The score accepts values between 0 and 3.\
                Partition - It refer to the number of identical clusters that exist at the same threshold.')
    
    parser.add_argument('-t', '--threshold', 
            dest = 'threshold', 
            default = 'max', 
            help = '[OPTIONAL] Defines an integer range to select or filter threshold columns from the partition matrix file. \
                    A filtered partition matrix, containing only the selected columns, will be created and used for subsequent analysis. \
                    Ranges are specified using a hyphen to separate the minimum and maximum values (e.g., 10-20). \
                    If this option is not set, the script will perform clustering for all possible thresholds in the range 0 to the maximum threshold.')
    
    parser.add_argument('-ps', '--plots_summary', 
            dest = 'plots_summary', 
            choices = ['partitions_summary','sample_of_interest'], 
            default = 'partitions_summary',
            help = '[OPTIONAL] Specify the type of cluster characterization file (partitions_summary.tsv or SAMPLES_OF_INTEREST_partitions_summary.tsv), both of which are expected to be located within a Reportree results folder. \
                    Using the partition_summary option, the largest clusters present in the file will be characterized. \
                    Alternatively, the samples_of_interest option will characterize all clusters, including those resulting from the addition of new samples (kept increase, new, new (increase), new (merge_increase), new (split_increase), new (split_merge_increase)).')
           
    parser.add_argument('-n', '--n_cluster',
            dest = 'n_cluster',
            type = int,
            default = 3,
            help = '[OPTIONAL] Specify the number of top clusters to be displayed from the partitions_summary.tsv file, which must be located within a Reportree results folder. \
                    This argument is not applicable when using the samples_of_interest option.')
    
    parser.add_argument('-cp', '--columns_plots', 
            dest = 'columns_plots', 
            help = '[OPTIONAL] Name(s) of the column(s) to process the characterization of the clustering data in the selected file (specified by the plots_summary argument). \
                    For multiple column names, indicate them separated by commas without spaces (e.g., column1,column2).')
    
    parser.add_argument('-pt','--plots_threshold',
            dest='plots_threshold',
            help='[OPTIONAL] Identify the integer threshold(s) to be applied to the file specified by the plots_summary argument. \
                    For multiple thresholds, indicate them separated by commas without spaces (e.g., X,Y,Z). \
                    This generates a pie chart showing the clustering data for the specified threshold(s), according to the columns_plot argument.')

    parser.add_argument('-pcn','--plots_category_number',
            dest='plots_category_number',
            default=5,
            type=int,
            help='[OPTIONAL] Determines the number of plot categories in the partitions_summary.tsv or SAMPLES_OF_INTEREST_partitions_summary.tsv file\
            that are intended to be collapsed into the '"Other"' category for visualization in the cluster plots.\
            When there are more than 5 slices (default), they will be combined into one category named Other')
    
    parser.add_argument('-pcp','--plots_category_percentage',
            dest='plots_category_percentage',
            type=float,
            help='[OPTIONAL] Determines the percentage of plot categories in the partitions_summary.tsv or SAMPLES_OF_INTEREST_partitions_summary.tsv file\
            that are intended to be collapse into the '"Other"'category for visualization in the cluster plots.\
            Slices plots with a lower percentage than the entered plots_category_percentage will be combined into one category named Others')
    
    parser.add_argument('-to', '--threshold_outbreak',
            dest='threshold_outbreak',
            type=str,
            help='[OPTIONAL] Determine the number of clusters identified in one pipeline at a given threshold \
            that will exist with the same composition in another pipeline at the same or a higher threshold.\
            Full attention, this argument has its own structure: two threshold (strings-methods) and the type of comparison is \
                either equal (defined by , ) or lower_equal (defined by <= ) \
                Threshold1: Threshold at which the genetic clusters must be identified for the pipeline of interest.\
                Threshold2: Threshold at which the genetic clusters must be searched in the other pipelines.\
                Comparison (equal or lower equal): \
                    - ''equal'': Used to assess whether a cluster is detected at a given threshold by another pipeline. \
                        Use a comma '','' to separate threshold1,threshold2. Example of expression: MST-7x1.0,MST-7x1.0.\
                    - ''lower_equal'': Used to assess whether a cluster is detected up to a given threshold in another pipeline. \
                        Use <= between threshold1<=threshold2. Example of expression: MST-7x1.0,<=MST-9x1.0.\
                            \
                For multiple pair of threshold values, use '';'' as a separator. Example of expression: "MST-7x1.0,MST-7x1.0;<=MST-7x1.0,MST-10x1.0" represents two pair of threshold values.')
    
    parser.add_argument('-list', '--list',
            dest='list',
            choices=['partitions_summary','sample_of_interest'],
            help='[OPTIONAL] Specify the names of the columns present in the partitions_summary.tsv or SAMPLES_OF_INTEREST_partitions_summary.tsv file.')

    parser.add_argument('-rto','--repeat_threshold_outbreak',
            dest='repeat_threshold_outbreak',
            action="store_true",
            help='[OPTIONAL] This argument can only be used after of a previous analysis of threshold_outbreak.')
    
    parser.add_argument('-v', '--version',
            action='version',
            version='EvalTree 1.0.0, last update 2025-07-31', 
            help='[OPTIONAL] Specify the version number of EvalTree.')
    
    parser.add_argument('-n_stab', '--n_stability',
            dest = 'n_stability',
            default = 5,
            type = int,
            help = '[OPTIONAL] Range of threshold which the cluster composition can be conistent/stable.')
    
    parser.add_argument('-thr_stab', '--thr_stability',
            dest = 'thr_stability',
            default = 0.99,
            type = float,
            help = '[OPTIONAL] The neighborhood Adjusted Wallace Coefficient (nAWC) threshold used to determine if a clustering threshold is considered consistent or stable.')
    
    #------------------------------------------------------------------
    # INITIAL INFORMATIONS    
    # Read the command line arguments and retrieve paths

    args = parser.parse_args()
    path_toolbox_script, directory_toolbox, python = get_path_toolbox()
    comparing_partitions_script, get_best_part_correspondence_script, remove_hifen_script, stats_outbreak_script = get_path_other_scripts(directory_toolbox)
    
    #------------------------------------------------------------------
    # I- Structural validation of the arguments
    #   I1- Check the input argument(s) (-i1 and/or -i2)

    input1 = None
    input2 = None

    if args.input1:
        input1 = args.input1
    
    if args.input2:
        input2=args.input2 
    
    folders, files = check_input_argument(input1, input2)
    print(f'Checking inputs:')
     
    data_folder = []
    if folders !=[]:

        for folder in folders:
            is_folder_empty(folder)   

        for folder in folders:
            print(f"\tFolder: {folder}")
            partitions, partitions_summary, sample_interest, clusterComposition, prefix, input_path, stable_region = check_folder(folder)
            data_folder += [[partitions, prefix, input_path, partitions_summary, sample_interest, clusterComposition, stable_region]]  #7
                                                                       
    data_files = []
    for file in files:
        print(f"\n\tFile: {file}")
        file, prefix_file, path_directory, file_type, n_samples, n_groups = check_file(file)
        print(f"\t\tPrefix: {prefix_file}")
        print(f'\t\tDirectory: {path_directory}')
        data_files += [[file, prefix_file, path_directory, file_type, n_samples, n_groups]]  #6
    
    #----------------------------------------------------------------
    #   I2- Check the output argument (-o)
    if args.output != None:
        output = check_output(args.output)

    #----------------------------------------------------------------
    #   I3- Check the list argument (-list)

    list_column_plot = args.list  

    if list_column_plot is not None:
        if data_folder != []:
            for sub in data_folder:

                if list_column_plot == 'partitions_summary':
                    file_summary = sub[3]
                    if file_summary is not None:
                        get_plot_columns(file_summary) 
                    else:
                        sys.exit(f"There is no partitions_summary file in the {sub[2]}. ")
                else:
                    file_s_interest=sub[4]
                    if file_s_interest is not None:
                        get_plot_columns(file_s_interest)   
                    else:
                        sys.exit(f"\nThere is no the sample_of_interest file in the {sub[2]}.")  
            sys.exit()  
        else:
            sys.exit('It is impossible to use the list argument (-list) when the input(s) (-i1, -i2) argument(s) have provided file(s).')

    #----------------------------------------------------------------
    #   I4- Check the column plot(s) (-cp) and plots thresholds (-pt) arguments
     
    columns_plots = args.columns_plots
    plots_thresholds = args.plots_threshold

    if plots_thresholds is not None:
        plots_thresholds = check_str_plots_threshold(plots_thresholds)

    #----------------------------------------------------------------
    #   I5- Check the threshold (-t) and score(-s) arguments

    score_value = check_score(args.score)
    threshold = check_threshold(args.threshold)

    if threshold != 'max':    
        
        for sub in data_files: 
            file_matrix = sub[0]
            identify_matrix = sub[3]
            if identify_matrix == False:
                if len(data_files) == 1:
                    print(f'\t\tWarning: The threshold argument (-t) is only applied to a partition matrix, so it is not applicable to the {file_matrix}.')
        
    #----------------------------------------------------------------
    #  I6- Arguments that do not require structural validation

    n_cluster = args.n_cluster
    plots_summary_arg = args.plots_summary
    plots_category_percentage = args.plots_category_percentage
    plots_category_number = args.plots_category_number
    n_stability = args.n_stability
    thr_stability = args.thr_stability

    #----------------------------------------------------------------
    #  I7- Check the threshold outbreak (-to)  and repeat_threshold_outbreak (-rto) arguments
    
    threshold_outbreak = args.threshold_outbreak   
    repeat_threshold_outbreak = args.repeat_threshold_outbreak   
    
    if threshold_outbreak is not None:
        valid_combinations = validate_combinations_outbreak(threshold_outbreak)
    
    #----------------------------------------------------------------
    # II- Validation of the argument combination (clustering, outbreaks)
    
    go_clustering, go_outbreaks = check_combinations_arguments(plots_summary_arg, data_folder, data_files)

    #----------------------------------------------------------------
    # III- Validation of file prefixes provided in different inputs
   
    data_folder, data_files, prefix_both = check_data_folders_file(data_folder, data_files)
           
    #---------------------------------------------------------
    # IV- Validation of partition matrix  FUNDAMENTAL
      
    inputs_variables = join_inputs_variables(data_folder,data_files)
   
    #--------------------------------------------------------------------------------------------------
    # V - Rename ouput folder if it was automatically created
    if args.output == None:
        output_folder = prefix_both 

        path_folder = os.path.abspath(output_folder)
        if os.path.exists(path_folder):
            sys.exit("Error: a folder with that name already exists. Please provide a folder name with different name using the -o argument to save the results.")

        os.makedirs(output_folder)
        path_folder=os.path.abspath(output_folder)
        if not os.path.isdir(path_folder):
            sys.exit("Critical error: the folder was not created successfully. Please provide a folder name using the -o argument to save the results.")
        
        output = path_folder

    #---------------------------------------------------------
    # VI- Validation of congruence
    go_congruence = False     
   
    if len(inputs_variables) == 2:

        i1,i2 = inputs_variables[0][0], inputs_variables[1][0]
        
        if i1 is not None and i2 is not None:       
            go_congruence = True

        else:
            print("Congruence analysis is not possible. It is necessary two *_partitions.tsv files.\n")


    #---------------------------------------------------------------------------------------------------
    # VII- Outbreaks (-rto) 

    if repeat_threshold_outbreak is not False:
        
        if args.output is None:
            sys.exit('Error: Please specify the output folder with the -o argument. It should contain the previous results (e.g outbreak analysis).')  
        
        file=glob.glob(os.path.join(output,'*_report.html'))
        if not file: 
            sys.exit("Error: The expected *_report.html file was not found. Please run the program first with the -to argument, and then with the -rto argument.")

        if not threshold_outbreak:
            print('\tDo not forget the double quotation marks!')
            sys.exit("Error: You must specify a new argument for the threshold_outbreak (-to).")   
    
    #---------------------------------------------------------------------------------------------------
    # VIII - Stable Regions (-thr_stab)

    if thr_stability != 0.99:
        if not (0 <= thr_stability <= 1):
            sys.exit("Error: thr_stability must be between 0 and 1.")

    #--------------------------------------------------------------------------------------------------
    # Starting logs	
    
    if not repeat_threshold_outbreak:
        log_name = (f'{output}/{prefix_both}.log')
        log = open(log_name, "w+")

    else:     
        log_name = (f'{output}/{prefix_both}_reanalyse.log')
        log = open(log_name, "w+")

    # -------------------------------------------------------------------------------------------------------------------------
    # INITIAL INFORMATIONS

    print("---------------------------------------------- Running EvalTree.py ----------------------------------------------\n")
    print_log(f"Version " + str(version) + " last updated on " + str(last_updated)+"\n", log)
    command_line = " ".join(sys.argv)
    print_log(f"Running EvalTree with the following command: {command_line}\n", log)
    print_log(f'Log file name: {log_name}\n', log)
    start = datetime.datetime.now()
    print_log("Start: " + str(start)+"\n", log)
    print_log(f'Output directory: {output}\n', log)
    
    #-----------------------------------------------
    # STAR HTML  

    if not repeat_threshold_outbreak:
        file_path_report = os.path.join(output, f'{prefix_both}_report.html') 
        html_content = create_html(log, file_path_report)
        html_content += body_html(start, command_line,version)  
    else:
        file_path_report = os.path.join(output, f'{prefix_both}_2ºRUN_report.html')
        html_content = create_html(log, file_path_report)
        html_content += body_html(start, command_line,version)    
        html_report = write_html(html_content,file_path_report, log)

    #-------------------------------------------------------------------------------------------------------------------------------

    if not repeat_threshold_outbreak: 

        #-------------------------------------------------------------------------------------------------------------------------------

        if inputs_variables:
            for sub in inputs_variables:

                #-------------------------------------------------------------------------------------------------------------------------------
                # MODULE 1 - SEQUENCE TYPE
                if len(sub) == 6:

                    if sub[3] == False:       
                        samples_st = sub[4]
                        groups_st = sub[5]
                        sequence_type_file = sub[0]
                        prefix_st = sub[1]
                        html_content += get_sequence_type(prefix_st,samples_st,groups_st,sequence_type_file)
                        fig_clusters = reading_sequence_type(sequence_type_file, output, prefix_st, log)
                        fig_html = pio.to_html(fig_clusters, include_plotlyjs='cdn', full_html=False)
                        html_content += sequence_type_image(fig_html)

        #-------------------------------------------------------------------------------------------------------------------------------       
        list_partition_by_threshold=[]
        category_colors = {'Others':'#000000'}

        if inputs_variables:
            for sub in inputs_variables:
                partition_matrix = sub[0]
                prefix = sub[1]
                directory = sub[2]

                #-------------------------------------------------------------------------------------------------------------------------------
                # MODULE 2 - Characterization of the ONE pipeline (Nr_partitions vs Nr_thresholds)
                if len(sub) == 7 or (len(sub) == 6 and sub[3] == True): 
                
                    print_log(f'\nPipeline characterization:  {directory}', log)
                    print_log(f'\tPipeline name: {prefix}', log)
                        
                    if partition_matrix is not None:

                        if threshold !='max':
                            start_threshold, end_threshold = check_range_threshold(partition_matrix,threshold,log)
                            input_filtered = filter_partition_matrix(partition_matrix, prefix, start_threshold, end_threshold, output, log)
                            sub[0] = input_filtered
                            partition_matrix = input_filtered

                        nr_lines_df, nr_columns_df = get_nr_lines_threshold(partition_matrix, log)
                        file_partition_by_threshold = get_file_partition_by_threshold (partition_matrix,  prefix, output, log)
                        list_partition_by_threshold.append(file_partition_by_threshold)
                        print_log(f'\tObtaining the number of partitions per threshold.', log)
                        yes_prefix_both=False
                        fig_partition_vs_threshols = get_graph_partition_by_threshold(file_partition_by_threshold, prefix, prefix_both, yes_prefix_both, output, threshold, log)
                        html_content += get_partitions_threshold(prefix, nr_lines_df, nr_columns_df, fig_partition_vs_threshols)
                        

                if go_clustering == False:
                    html_content += f'</div>\n'  

                #----------------------------------------------------------------------- 
                # MODULE 3 - REPORTREE clustering visualization
                if len(sub) == 7:  #folder
                    partitions_summary = sub[3]
                    sample_interest = sub[4]

                    if go_clustering == True:
                        plots_file = None

                        if plots_summary_arg == 'partitions_summary':  
                            if partitions_summary is not None:    
                                plots_file = partitions_summary
                        else:
                            if sample_interest is not None:
                                plots_file = sample_interest

                        print_log(f'\tPlotting cluster characterization ...', log)  

                        #----------------------------------------------------------------------- 
                        # Starting clustering
                        df_data=load_and_prepare_data(plots_file, log)
                        df_filtered=order_cluster_by_size(df_data, log)
                        
                        #----------------------------------------------------------------------- 
                        if df_filtered is not None:
                            method = check_plot_threshold(plots_thresholds, df_filtered, log)

                            if method != []:     
                                filtered_threshold = check_threshold_in_file(method, df_filtered, plots_file, log)  
                                
                                if filtered_threshold != []:  

                                    if plots_summary_arg == 'partitions_summary': 
                                        result_df = filter_df_by_plot_threshold(filtered_threshold, df_filtered, n_cluster, log)

                                    if plots_summary_arg == 'sample_of_interest':
                                        df_filtered_threshold = filtering_df_threshold(filtered_threshold, df_filtered, log)
                                        result_df = select_nomenclature_change(df_filtered_threshold, log)            
                                    
                                    if result_df is not None:
                                        check_columns = check_column_plots(columns_plots, result_df, log) 
                                        
                                        #----------------------------------------------------------------------- 
                                        # PLots
                                        if check_columns != []:
                                            
                                            results_list = check_structure_lines_column_plots(check_columns, result_df, plots_category_percentage, plots_category_number, output, prefix, plots_summary_arg, category_colors, log)

                                            if results_list is not None:
                                                mst_groups = organize_clusters(results_list)
                                                html_content += get_clusters(mst_groups, prefix)
                                            else:
                                                html_content += close_painel(prefix,"Error: Impossible to produce cluster plots.")
                                                print_log(f'\tError: Impossible to produce cluster plots.', log)
                                        else:
                                            html_content += close_painel(prefix,"Error: Invalid column plots, without clustering analysis.")
                                            print_log(f'\tError: Invalid column plots, without clustering analysis ...', log)                 
                                        #-------------------------------------------------------------------------
            
                                    else:
                                        html_content += close_painel(prefix,"Error: No data for processing, without clustering analysis.")
                                        print_log(f'\tError: No data for processing, without clustering analysis.', log)   
                                else:
                                    html_content += close_painel(prefix,"Error: The plot_threshold argument is invalid, without clustering analysis.")
                                    print_log(f'\tError: The plot_threshold argument is invalid, without clustering analysis. ', log)
                            else:
                                html_content += close_painel(prefix,"Error: The method provided is not available, without a clustering analysis.")
                                print_log(f"\tError: The method provided is not available, without a clustering analysis.",log)
                        else:
                            html_content += close_painel(prefix,"Error: Impossible to order the Dataframe by cluster length,  without clustering analysis.")
                            print_log(f'\tError: Impossible to order the Dataframe by cluster length, without clustering analysis.')
                    else:
                        html_content += f'</div>\n'

        #-------------------------------------------------------------------------------------------------------------------------------
            print_log(f"\nInter-pipeline cluster congruence analysis:\n", log)
            html_content += summary_congruence()
                
        #----------------------------------------------------------------------- 
        # MODULE 4.1 - Characterization of the BOTH pipelines (Nr_partitions vs Nr_thresholds) 
            if list_partition_by_threshold:
                if len(list_partition_by_threshold) == 2:
                    file1, file2 = list_partition_by_threshold
                    path = concatenation_files(file1, file2, output, prefix_both)
                    yes_prefix_both=True
                    fig = get_graph_partition_by_threshold(path, prefix, prefix_both, yes_prefix_both, output, threshold, log)
                    print_log(f"\tPlotting the number of partitions per threshold for the two pipelines ...", log)
                    fig_html = pio.to_html(fig, include_plotlyjs='cdn', full_html=False)
                    html_content += summary_partition_threshold(fig_html, prefix_both)

        #----------------------------------------------------------------------- 
        # MODULE 4.2 - Stability regions #or (len(sub)==6 and sub[3]==True):  
        print_log(f"\tIdentifying cluster stability regions for each pipeline ...", log)
        print_log(f"\t\tRunning comparing_partitions_v2.py in “stability” mode.", log)

        files_to_stability = []

        #----------------------------------------------------------------------- 
        for sub in inputs_variables:  
            partition_matrix = sub[0]
            prefix = sub[1]
            directory = sub[2] 

            if len(sub) == 7:   #folders
                stable_region = sub[6]     
                if stable_region is None or threshold !='max':
                    file_stability = stability_region(output, partition_matrix, prefix, comparing_partitions_script, n_stability, thr_stability, python, log) 
                    files_to_stability.append([file_stability,prefix])
                else:
                    files_to_stability.append([stable_region,prefix])

            if len(sub) == 6: #files
                type_file = sub[3]
                if type_file == True: #if true it is partition matrix
                    file_stability = stability_region(output, partition_matrix, prefix, comparing_partitions_script, n_stability, thr_stability, python ,log) 
                    files_to_stability.append([file_stability, prefix])
                else:
                    go_stability = False

        #----------------------------------------------------------------------- 
        all_dfs = []
        prefix_df = []
       
        if files_to_stability:

            for file, prefix in files_to_stability:
                
                try:
                    name_block = processing_block_names(file, prefix, log)
                    first_data, final_data = processing_data(file, log)
                    
                    df = pd.DataFrame({'Block_id': name_block, 'Start': first_data, 'Finish': final_data, 'Pipeline': prefix})
                    all_dfs.append(df)
                    prefix_df.append(prefix)
                    go_stability = True

                except Exception as e:
                    print(f'\t\tWarning: without stability reagions in the file {file}.')
                    go_stability = False

        if all_dfs:  
            df = pd.concat(all_dfs, ignore_index = True)
            if len(prefix_df) == 2:
                prefix=prefix_df[0]
                prefix_2=prefix_df[1]

            else:
                prefix_2 = None
                prefix = prefix_df[0]
               

        if  go_stability == True:
            fig_st = change_processing_data(df, prefix, prefix_2, output, log)
            print_log(f"\t\tDone.\n", log)
            fig_html_st = pio.to_html(fig_st, include_plotlyjs='cdn', full_html=False)
            html_content += congruence_stability(fig_html_st, prefix, prefix_2, n_stability, thr_stability)

        #----------------------------------------------------------------------- 
        #  MODULE 4.3 - Congruence between pipelines
        if go_congruence == True:

            i1_matrix=inputs_variables[0][0]
            i2_matrix=inputs_variables[1][0]
            i1_prefix=inputs_variables[0][1]
            i2_prefix=inputs_variables[1][1]

            path_all_correspondence_lower = management_main_scripts(comparing_partitions_script, get_best_part_correspondence_script, remove_hifen_script, i1_matrix, i2_matrix, prefix_both, output, score_value, python, log)

            #Final score
            fig_heatmap = get_heatmap(output, i1_prefix, i2_prefix, threshold, log)
            fig_html_heatmap = pio.to_html(fig_heatmap, include_plotlyjs='cdn',full_html=False)
            html_content += congruence_heatmap(fig_html_heatmap, prefix_both)
                
            #----------------------------------------------------------------------- 
            # Get best correspondence          
            
            if  not any(len(elem) == 6 and elem[3] is False for elem in inputs_variables): 
                fig_tendency, nr_point_method_1, nr_point_method_2 = get_tendency(output, prefix_both, threshold,log)
                fig_tendency_html = pio.to_html(fig_tendency,include_plotlyjs='cdn', full_html=False)
                html_content += congruence_tendency(fig_tendency_html, score_value, prefix_both, nr_point_method_1, nr_point_method_2)
                comparison = tendency_slop(path_all_correspondence_lower, i1_prefix, i2_prefix, output)
    #-------------------------------------------------------------------------------------------------------------------------------
    # MODULE 5 - OUTBREAK
    
    if go_outbreaks == True:
        
        #----------------------------------------------------------------------- 
        clusterComposition_1 = inputs_variables[0][5]
        clusterComposition_2 = inputs_variables[1][5]

        if valid_combinations != []:

            print_log(f"\tThreshold outbreaks was validated successfully.", log)
            values_outbreak = extract_integer_part(valid_combinations, log)
            print_log(f"\tAssessing the overlap of cluster composition.\n", log)
            df_stats_outbreak, path_stats_outbreak = creation_tsv_stats_outbreak(clusterComposition_1, clusterComposition_2, output, prefix_both, log) 

            #----------------------------------------------------------------------- 
            if values_outbreak:
                calling_script_outbreak(python, stats_outbreak_script, path_stats_outbreak, output, prefix_both, values_outbreak, log)
                process_files = read_files_outbreak(output)
                fig_result, thresholds = creation_overlap_clusters(process_files, output, values_outbreak)
                print_log(f"\tPlotting the matrices with the cluster overlap for each comparison", log)
                
                if not repeat_threshold_outbreak:
                    html_content += image_outbreak(fig_result)
                    html_content += summary_outbreak(prefix_both, thresholds)
                else:
                    final_files = find_html_outbreak(output, prefix_both, log)
                    path_temp = extration_section_original_file(output, final_files, log)
                    html_content += transfer_info_to_html_content(path_temp, html_content, log)
                    html_content += image_outbreak(fig_result)
                    html_content += summary_outbreak(prefix_both, thresholds)
        else:
            print_log(f'\tImpossible outbreaks analysis.', log)

    #--------------------------------------------------------------------------------------------------------------------------
    #4 - END HTML report
    html_content += references()
    html_content += javascript_function()
    html_content += create_html_footer()
    html_report = write_html(html_content, file_path_report, log)
    
    #path=f'{output}/html_all_modules.txt'
    #with open(path, 'w') as f:
    #    f.write(html_content)  

    #----------------------------------------------------------------------------------------------------------------------------
    #END INFORMATIONS

    print_log('Evaltree is done! If you found any issue please contact us.\n', log)
    end = datetime.datetime.now()
    elapsed = end - start
    print_log("\nEnd: " + str(end), log)
    print_log("Time elapsed: " + str(elapsed), log)
    log.close()


if __name__ == "__main__":
    main()


