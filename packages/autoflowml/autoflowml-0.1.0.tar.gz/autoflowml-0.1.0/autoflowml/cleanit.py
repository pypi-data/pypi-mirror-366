import pandas as pd
import re

class CleanIt:
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()

    # Function to remove duplicate rows from the DataFrame
    def remove_duplicates(self): 
        before = self.df.shape[0]
        self.df = self.df.drop_duplicates()
        after = self.df.shape[0]
        print(f"Removed {before - after} duplicate rows.")
        return self.df

    # Function to fix column names by removing special characters and extra spaces
    def fix_column_names(self):
        self.df.columns = [re.sub(r'\W+', '_', col.strip()) for col in self.df.columns]
        print("Fixed column names.")
        return self.df

    # Function to attempt standardizing data types in object columns
    def standardize_dtypes(self):
        for col in self.df.select_dtypes(include='object'):
            self.df[col] = self.df[col].str.strip('"').str.strip("'")
            try:
                self.df[col] = pd.to_numeric(self.df[col])
            except:
                try:
                    self.df[col] = pd.to_datetime(self.df[col])
                except:
                    pass
        return self.df
    
    # Run all cleaning steps in sequence
    def full_clean(self):
        self.fix_column_names()
        self.remove_duplicates()
        self.standardize_dtypes()
        print("Full cleaning completed.")
        return self.df