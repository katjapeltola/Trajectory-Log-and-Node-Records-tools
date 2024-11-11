import pandas as pd 
import numpy as np
import os
import matplotlib.pyplot as plt

class NodeRecords:
    
    def __init__(self, path_to_file):
        """Initialize the cleaner with the file path and automatically clean the data."""
        self.path_to_file = path_to_file
        self.cleaned_dataframe = None
        self.new_filepath = self._create_new_filepath()
        self._clean()  # Automatically clean the data upon initialization
        print(f"Data from '{self.path_to_file}' has been cleaned.")
    
    def _create_new_filepath(self):
        """Generate the new file path for the cleaned CSV file."""
        dir_name = os.path.dirname(self.path_to_file)
        base_name, ext = os.path.splitext(os.path.basename(self.path_to_file))
        return os.path.join(dir_name, f"{base_name}_CLEAN.csv")
    
    def _clean(self):
        """Clean the Node Records CSV file and store the result in an attribute."""
        df = pd.read_csv(self.path_to_file, low_memory=False)
        split_dfs = self._split_dataframe(df)
        bankA, bankB = self._clean_banks(split_dfs)
        self.cleaned_dataframe = self._combine_banks(bankA, bankB)
    
    def _split_dataframe(self, df):
        """Split the DataFrame based on rows starting with 'Time'."""
        split_indices = [0]
        for j, row in df.iterrows():
            if row.iloc[0].startswith('Time'):
                split_indices.append(j)
        
        split_dfs = [df.iloc[split_indices[i]:split_indices[i + 1]] for i in range(len(split_indices) - 1)]
        split_dfs.append(df.iloc[split_indices[-1]:])
        return split_dfs
    
    def _clean_banks(self, split_dfs):
        """Process and clean bank DataFrames."""
        bankA1 = split_dfs[0]
        bankB1 = split_dfs[1].iloc[1:]  # Remove header row from bank B
        
        columns_to_keep = ['Time'] + [f'{prefix}{i}' for i in range(1, 61) for prefix in ['Exp', 'Prim', 'Sec']]
        bankA = bankA1[columns_to_keep]
        bankB = bankB1[columns_to_keep]
        
        bankA.columns = ['Time'] + [f'A{col}{i}' for i in range(1, 61) for col in ['Exp', 'Prim', 'Sec']]
        bankB.columns = ['Time'] + [f'B{col}{i}' for i in range(1, 61) for col in ['Exp', 'Prim', 'Sec']]
        
        return bankA, bankB
    
    def _combine_banks(self, bankA, bankB):
        """Concatenate bank A and B DataFrames side by side."""
        bankB.reset_index(drop=True, inplace=True)
        return pd.concat([bankA, bankB.iloc[:, 1:]], axis=1)
    
    def save(self):
        """Save the cleaned DataFrame to a CSV file."""
        if self.cleaned_dataframe is not None:
            self.cleaned_dataframe.to_csv(self.new_filepath, index=False)
            print(f"DataFrame saved in '{self.new_filepath}'")
        else:
            print("No cleaned data available.")
            
    def to_dataframe(self):
        """Return the cleaned data as a Pandas DataFrame."""
        if self.cleaned_dataframe is not None:
            return self.cleaned_dataframe
        else:
            print("No cleaned data available. Please ensure the file was loaded and cleaned correctly.")
            return None
        
        