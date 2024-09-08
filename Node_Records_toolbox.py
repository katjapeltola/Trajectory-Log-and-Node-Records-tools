import pandas as pd 
import numpy as np
import os

def clean_Node_Records_csv(path_to_file, save: bool = True):
    
    """Cleans a Node Records csv-file (from COL node) to a contain only primary, secondary and expected values of the leaves in cm. Can either save the cleaned file as csv (default), or return the result as a Pandas DataFrame.

    Parameters
    ----------
    path_to_file : filepath
        Path to your Node Records csv-file, for example r"directory/filename.csv".
        
    save : boolean 
        If True (default), saves the cleaned csv-file in the same folder with the original, with _CLEANED added to the filename. 
        If False, does not save anything, but returns the cleaned file as a Pandas DataFrame.

    Returns (optional)
    -------
    dataframe : df
        Dataframe containing bank A and B leaves primary, secondary and expected values from your file. 
        
    """
    
    df = pd.read_csv(path_to_file, low_memory=False)
    
    dir_name = os.path.dirname(path_to_file)
    base_name, ext = os.path.splitext(os.path.basename(path_to_file))
    
    new_filename = f"{base_name}_CLEAN{ext}"
    new_filepath = os.path.join(dir_name, new_filename)

    # Initialize lists to store the split DataFrames
    split_dfs = []

    # Find the indices where the rows start with 'Time'
    split_indices = [0]  # Start with the first index
    for j, row in df.iterrows():
        if row.iloc[0].startswith('Time'):  # Using .iloc to access by position
            split_indices.append(j)

    # Split the DataFrame based on the indices
    for k in range(len(split_indices) - 1):
        start_index = split_indices[k]
        end_index = split_indices[k + 1]
        split_dfs.append(df.iloc[start_index:end_index])

    # Add the last split (from the last 'Time' row to the end)
    split_dfs.append(df.iloc[split_indices[-1]:])

    # Now split_dfs contains all the split DataFrames
    # Remove first row from bank B dataframe (contains Time CarExp CarPrim...)
    # Rename the split_dfs
    bankA1 = split_dfs[0]
    bankB1 = split_dfs[1].iloc[1:]

    # Cleaning the DataFrames
    # Generate the list of columns to retain
    columns_to_keep = ['Time'] + [f'{prefix}{i}' for i in range(1, 61) for prefix in ['Exp', 'Prim', 'Sec']]

    # Filter the DataFrame to retain only the specified columns
    bankA = bankA1[columns_to_keep]
    bankB = bankB1[columns_to_keep]
    
    # Rename bankA and bankB column heads
    # Generate new column names
    new_columns = []
    for i in range(1, 61):
        new_columns.append(f'AExp{i}')
        new_columns.append(f'APrim{i}')
        new_columns.append(f'ASec{i}')

    # Update the DataFrame with the new column names
    bankA.columns = ['Time'] + new_columns

    new_columns = []
    for i in range(1, 61):
        new_columns.append(f'BExp{i}')
        new_columns.append(f'BPrim{i}')
        new_columns.append(f'BSec{i}')
    
    bankB.columns = ['Time'] + new_columns
    
    
    # Combine these and remove first 55 rows
    
    bankB.reset_index(drop=True, inplace=True)
    # Concatenate dataframes side by side
    cleaned_dataframe = pd.concat([bankA, bankB.iloc[:, 1:]], axis=1)
    
    if save:
        cleaned_dataframe.to_csv(new_filepath, index=False)
        print(f"DataFrame saved in '{new_filepath}'")
        
    else:
        return cleaned_dataframe