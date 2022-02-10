import pandas as pd
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns


def read_raw_excel(path_to_excel_file:Path, sheet:int=0) -> pd.DataFrame:
    """Read raw data excel file output from analytical centrifuge
    Currently assumes a strict data format.

    Args:
        path_to_excel_file (Path): filepath
        sheet (int, optional): sheet number. Defaults to 0.

    Returns:
        pd.DataFrame: returns the read datafile
    
    TODO:
        - add plausibility checks on loading the data
    """
    return pd.read_excel(path_to_excel_file, sheet_name=sheet)


def get_array_for(string_to_search:str, d:pd.DataFrame) -> np.ndarray:
    """Function to extract the array from dataframe depending on queried value

    Args:
        string_to_search ([type]): the parameter in excel sheet for which we need the data as a vector
        d (DataFrame): the dataframe in which one has to search

    Returns:
        np.array: 1d numpy array of values corresponding to the parameter queried
    """
    return d[d.iloc[:, 0].str.contains(string_to_search, na=False)].values.ravel()[1:]


def get_value_for(string_to_search, d):
    """Utility function to get value corresponding to a string query

    Args:
        string_to_search (str): string corresponding to which the value has to be extracted
        d (DataFrame): raw data from analytical centrifuge

    Returns:
        float: value corresponding to the string query from dataframe
    """
    return d.iloc[:, 1]. \
        where(d.iloc[:, 0] == string_to_search). \
        dropna(). \
        to_string(index=False)


def get_profiles():
    pass

def gen_tgram_plot(transmission, power, xspacing, color, tmax=100):
    fig, ax = plt.subplots(figsize=(12, 7))
    if power == 1:
        ax = sns.heatmap(transmission, cmap=color, vmin=0, vmax=tmax, 
                            cbar_kws={'label': 'Transmission, %'},
                            xticklabels=xspacing, yticklabels=145)
    else:
        ax = sns.heatmap(transmission ** power, cmap=color, 
                            cbar_kws={'label': 'Transmission, %'},
                            xticklabels=xspacing, yticklabels=145)
    return ax
