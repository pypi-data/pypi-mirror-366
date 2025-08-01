from pathlib import Path
import uproot
import pandas as pd
import numpy as np

def load_data(path, tree, columns, weights_col=None):
    """
    Load data from a ROOT file and return a DataFrame with optional weights.
    
    Args:
        path (str): Path to the ROOT file.
        tree (str): Name of the tree to read from.
        columns (list): List of column names to extract.
        weights_col (str, optional): Name of the column containing weights. If None, no weights are returned.
    """
    with uproot.open(path) as f:
        df = f[tree].arrays(columns + ([weights_col] if weights_col else []), library="pd")
    weights = df.pop(weights_col).values if weights_col else np.ones(len(df))
    # Filter out negative weights from dataframe and weights
    df = df[weights >= 0]
    weights = weights[weights >= 0]
    return df, weights

def save_data(input_path, tree, output_path, output_tree, branch, weights):
    """
    Save weights to a ROOT file.
    
    Args:
        input_path (str): Path to the input ROOT file.
        tree (str): Name of the tree to read from.
        output_path (str): Path to the output ROOT file.
        output_tree (str): Name of the tree to write to.
        branch (str): Name of the branch to save weights under.
        weights (np.ndarray): Weights to save.
    """
    with uproot.open(input_path) as f:
        data = f[tree].arrays(library="pd")
    data[branch] = weights
    output_dir = Path(output_path).parent
    output_dir.mkdir(parents=True, exist_ok=True)
    with uproot.recreate(output_path) as f:
        f[output_tree] = data

def def_aliases(df, aliases):
    """
    Apply aliases to the DataFrame.
    
    Args:
        df (pd.DataFrame): DataFrame to apply aliases to.
        aliases (dict): Dictionary of aliases where keys are new names and values are expressions.
    
    Returns:
        pd.DataFrame: DataFrame with applied aliases.
    """
    for new_name, expr in aliases.items():
        try:
            if expr in df.columns:
                df[new_name] = df[expr]
            else:
                df[new_name] = df.eval(expr)
        except Exception as e:
            print(f"Error applying alias '{new_name}': {e}")    
    return df