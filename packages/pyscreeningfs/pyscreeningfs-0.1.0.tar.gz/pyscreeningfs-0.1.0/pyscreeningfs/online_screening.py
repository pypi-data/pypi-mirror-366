# -*- coding: utf-8 -*-
"""
Created on Sun Jul 27 22:00:26 2025

Wang, M. and Barbu, A., 2022. 
Online feature screening for data streams with concept drift. 
IEEE Transactions on Knowledge and Data Engineering, 35(11), 
pp.11693-11707.

@author: Mingyuan Wang
"""

import numpy as np
from . import fsonline

def online_screening(is_sparse = None, X = None, Y = None, 
                     data_file_folder_path = '', main_data_file_name = '',
                     file_extension = 'svm', num_total_files = 0,
                     alpha = 1, beta = 1, batch_alpha = 1, batch_penalty_freq = 0,
                     num_bins = 5, base_engine = '', precision_factor = 5000,
                     batch_size = None):
    '''
    A comprehensive function to handle all scenarios mentioned in the paper.
    
    Parameters
    ----------
    base_engine: choose from {'moving_average', 'quantile'}. Engine type decides which type of feature
                importance scores to output. 'moving_average': moveing average based methods including 
                T-score and fisher score. 'quantile': quantile summary based methods including mutual 
                information, chi-square score, gini index score.
    
    is_sparse: a boolean flag to indicate if the data file should be loaded through
            direct array input or through .svm sparse data file.
                
    X : {numpy array-like} of shape (n_samples, n_features), only required if is_sparse is False.
    
    Y : {numpy array-like} of shape (n_samples, 1), only required if is_sparse is False.
    
    batch_size: the batch size used to iterate X and Y array, only required if is_sparse is False.
    
    data_file_folder_path: folder directory of .svm sparse data files, only required if is_sparse is True.
    
    main_data_file_name: main part of file names. E.g. for a set of .svm files "file1.svm", "file2.svm",
            "file3.svm", etc. the main_data_file_name will be "file".
    
    file_extension: usually file extension is default to "svm".
    
    num_total_files: number of total .svm files to process.
    
    -----exponential penalty-----
    When using only alpha and beta, historical records get penalized whenever a new sample arrives.
    
    alpha: range [0,1], penalty term for historical records. 1 indicates no penalty applied.
            0 indicates erasing all historical records which is rarely used.
    
    beta: range [0,1], penalty term for the current new record. 1 indicates no penalty 
            applied which is usually the choice. 0 indicates not counting the current new records 
            which is rarely used.
    ------------------------------
    
    -----more gradual batch/file wise penalty-----
    For some data, penalize historical records at each new sample's arrival is too extreme. Even if
    increasing the alpha value close to 1 is not enough. In this case, `bafreq` and `batchalpha` are 
    used to apply a more gradual penalization.
        1. When input is numpy array (not .svm files). Both `batch_penalty_freq` and `batch_alpha`
         are used to apply one `batch_alpha` penalty every `batch_penalty_freq` batchs.
        2. When input is sparse (.svm file), only `batch_alpha` is implemented to apply one `batch_alpha` 
        penalty every time a new .svm file arrives. `batch_penalty_freq` is not needed.
         
    batch_penalty_freq: how many batchs to apply a penalty. When input data is numpy array, 0 indicates
        not using batch penalty.
            
    batch_alpha: range [0,1], batch penalty term for historical records. 1 indicates no penalty applied.
        When input data is through .svm files, seting `batch_penalty_freq` to 0 will not turn off batch
        penalization. You have to set this parameter to 1 too. 0 indicates erasing all historical records
        which is rarely used.
    ------------------------------
    
    num_bins: the number of bins to discretize continuous data to when using `quantile` base engine. Default value is 5. 
    
    precision_factor: 1/epsilon. Epsilon is a precision parameter, see the paper for detail.
                
    Returns
    ----------
    T-score 
    fisher score
    mutual information
    chi-square score
    gini index
    indices of feature columns: only generate when input is sparse .svm files. It's of the same order as 
            output score arrays. It shows each score's corresponding column index in input sparse matrix.                    
    '''
    combination_status = []

    # engine check
    if base_engine not in ['moving_average', 'quantile']:
        raise ValueError("expected either 'moving_average' or 'quantile' for base_engine")
        
    if base_engine == 'moving_average':
        num_bins = 0
    else:
        if isinstance(num_bins, int):
            if num_bins < 2:
                raise ValueError("'num_bins' needs to >= 2")
    
    combination_status.append(">>"+base_engine)
    
    # sparse check
    if isinstance(is_sparse, bool):
        if is_sparse:
            if len(data_file_folder_path) == 0:
                raise ValueError("'data_file_folder_path' is expected as the data folder directory")
            
            if len(main_data_file_name) == 0:
                raise ValueError("'main_data_file_name' is expected as the main part of file names. E.g. for a set of .svm files 'file1.svm', 'file2.svm',\
                        'file3.svm', etc. the main_data_file_name will be 'file'")
            
            if file_extension != 'svm':
                raise ValueError("only 'svm' is supported file_extension")
                
            if isinstance(num_total_files, int):
                if num_total_files < 1:
                    raise ValueError("'num_total_files' needs to >= 1")
            combination_status.append(">>sparse file input")
        else:
            if isinstance(X, np.ndarray):
                X = X.astype(np.float64)
                if not X.flags['F_CONTIGUOUS']:
                    X = np.asfortranarray(X, dtype=np.float64)
            else:
                raise ValueError("expected X to be a numpy array")
                
            if isinstance(Y, np.ndarray):
                if Y.ndim==1:
                    raise ValueError(f"expected Y of shape (n_samples, 1), got {Y.shape}")
                if Y.shape[1]!=1:
                    raise ValueError(f"expected Y of shape (n_samples, 1), got {Y.shape}")
                Y = Y.astype(np.float64)
                if not Y.flags['F_CONTIGUOUS']:
                    Y = np.asfortranarray(Y, dtype=np.float64)
            else:
                raise ValueError("expected Y to be a numpy array")
                
            if batch_size is None:
                raise ValueError("batch_size is not assigned")
            elif isinstance(batch_size, int):
                if batch_size < 1:
                    raise ValueError("batch_size needs to >= 1")
            combination_status.append(">>numpy array input")
                
    # drifting check
    if isinstance(alpha, (int, float)):
        if alpha<0 or alpha>1:
            raise ValueError("expect 0 <= alpha <= 1")
            
    if isinstance(beta, (int, float)):
        if beta<0 or beta>1:
            raise ValueError("expect 0 <= beta <= 1")
        
    if isinstance(batch_alpha, (int, float)):
        if batch_alpha<0 or batch_alpha>1:
            raise ValueError("expect 0 <= batch_alpha <= 1")
            
    if isinstance(batch_penalty_freq, int):
        if batch_penalty_freq<0:
            raise ValueError("expect batch_penalty_freq >= 0")
    
    if is_sparse:
        if batch_alpha == 1:
            combination_status.append(">>no batch penalty")
        elif batch_alpha != 0:
            combination_status.append(">>use batch penalty")
        else:
            raise ValueError("batch penalty set to 0 which removes all historical record. If this is intended, directly modify this function's code to bypass")
    else:
        if batch_alpha >= 0 and batch_alpha < 1 and batch_penalty_freq == 0:
            raise ValueError(f"conflict: 'batch_alpha' is {batch_alpha} indicating the use of batch penalty, 'batch_penalty_freq' is {batch_penalty_freq} indicating no use of batch penalty")
        elif batch_alpha == 1 and batch_penalty_freq > 0:
            raise ValueError(f"conflict: 'batch_alpha' is {batch_alpha} indicating no use of batch penalty, 'batch_penalty_freq' is {batch_penalty_freq} indicating the use of batch penalty")
        elif batch_alpha == 1:
            combination_status.append(">>no batch penalty")
        elif batch_alpha > 0 and batch_alpha < 1 and batch_penalty_freq > 0:
            combination_status.append(">>use batch penalty")
        else:
            raise ValueError("batch penalty set to 0 which removes all historical record. If this is intended, directly modify this function's code to bypass")
            
    if alpha == 1 and beta == 1:
        combination_status.append(">>no exponential penalty")
    elif alpha < 1 and alpha >0 and beta == 1:
        combination_status.append(">>use exponential penalty on historic records only")
    elif alpha < 1 and alpha >0 and beta < 1 and beta >0:
        combination_status.append(">>use exponential penalty on both historic and new records")
    elif alpha == 1 and beta < 1 and beta >0:
        combination_status.append(">>use exponential penalty on new record only")
    elif alpha == 0 or beta == 0:
        raise ValueError("at least on of the exponential penalties is set to 0 which removes all historical or new records. If this is intended, directly modify this function's code to bypass")

    # display final mode
    combination_status = '\n'.join(combination_status)+'\n'
    print(combination_status, flush=True)
    # time.sleep(0.5)  
      
    if is_sparse:
        results = fsonline.OnlineDriftScreening(1, alpha, beta, batch_alpha, batch_penalty_freq, num_bins,
                        precision_factor, 0, data_file_folder_path, main_data_file_name, file_extension, num_total_files)
    else:
        results = fsonline.OnlineDriftScreening(0, alpha, beta, batch_alpha, batch_penalty_freq, num_bins, 
                        precision_factor, 0, X, Y, batch_size)
    
    output = {}
    if len(results) == 7:
        output['mutual information'] = results[1]
        output['chi-square score'] = results[2]
        output['gini index'] = results[3]
        output['indices of feature columns'] = results[6]
    elif len(results) == 6:
        output['mutual information'] = results[1]
        output['chi square score'] = results[2]
        output['gini index'] = results[3]
    elif len(results) == 5:
        output['fisher'] = results[0]
        output['T-score'] = results[1]
        output['indices of feature columns'] = results[4]
    elif len(results) == 4:
        output['fisher'] = results[0]
        output['T-score'] = results[1]
    
    return output

