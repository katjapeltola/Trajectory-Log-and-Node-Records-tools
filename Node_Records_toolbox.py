import pandas as pd 
import os

def clean_Node_Records_csv(path_to_file, save: bool = True, remove_stationaries: bool = True):
    
    """Cleans a Node Records csv-file (from COL node) to a contain only primary, secondary and expected values of the leaves in centimeters (cm). 
       Can either save the cleaned file as csv (default), or return the result as a Pandas DataFrame.

    Parameters
    ----------
    path_to_file : filepath
        Path to your Node Records csv-file, for example r"directory/filename.csv".
        
    save : boolean 
        If True (default), saves the cleaned csv-file in the same folder with the original, with _CLEANED added to the filename. 
        If False, does not save anything, but returns the cleaned file as a Pandas DataFrame.
        
    remove_stationaries : boolean
        If True (default), removes stationary data of each leaf and downsamples the data.
        If False, does not do anything.

    Returns (optional)
    -------
    dataframe : df
        A Pandas dataframe containing bank A and B leaves primary, secondary and expected values from your file. 
        
    """
    
    df = pd.read_csv(path_to_file, low_memory=False) # Reads the csv-file to a dataframe
    
    dir_name = os.path.dirname(path_to_file) # Specifies the directory name 
    base_name, ext = os.path.splitext(os.path.basename(path_to_file)) 
    
    new_filename = f"{base_name}_CLEAN{ext}" # Makes the new filename for the saving
    new_filepath = os.path.join(dir_name, new_filename) # Makes the new file path for the soon to saved csv

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
    
    if remove_stationaries:
        # Downsample the DataFrame
        df_downsampled = cleaned_dataframe.iloc[::2]
        
        # Next removing stationary datapoints
        # We have to go through every column (all 120 of them), and remove non-moving data and construct a new dataframe based on it
        
         # Iterate through each instance
        for i in range(1, 121):
            # Identify columns for this instance
            if i == 1: 
                first_column = df_downsampled.iloc[:, 0]
                
                # Creating a new dataframe with only the first column
                new_df = pd.DataFrame(first_column, columns=['Time'])
                cols = [f'AExp{i}', f'APrim{i}', f'ASec{i}'] 
            
            elif i > 1 and i <= 60:
                cols = [f'AExp{i}', f'APrim{i}', f'ASec{i}'] 
                
            else:
                cols = [f'BExp{i-60}', f'BPrim{i-60}', f'BSec{i-60}']  
            
            # Check for consecutive similarity in the selected columns
            # Initialize a list to track rows to drop
            rows_to_drop = []
            prev_value = None
            vals_df = pd.DataFrame(df[cols])
            
            # Iterate through the rows (assuming rows represent time steps)
            # Iterate through the 'movement1' column to find rows to drop
            
            for idx, value in vals_df[cols[0]].items():
                if prev_value is not None and value == prev_value:
                    rows_to_drop.append(idx)
                prev_value = value

            # Drop rows from 'movement1' where consecutive values are similar
            vals_df.drop(rows_to_drop, inplace=True)
            # Concatenate new_df and vals_df
            new_df = pd.concat([new_df, vals_df], axis=1, ignore_index=False)
            
            if save: 
                new_df.to_csv(new_filepath, index=False)
                print(f"DataFrame saved in '{new_filepath}'") 
    else:
        pass
    
    if save:
        cleaned_dataframe.to_csv(new_filepath, index=False)
        print(f"DataFrame saved in '{new_filepath}'")
        
    else:
        return cleaned_dataframe
    