import pandas as pd
import numpy as np
from sklearn.impute import KNNImputer
from sklearn.experimental import enable_iterative_imputer 
from sklearn.impute import IterativeImputer  


class NullFixer:
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()

    def nullfix_knn(self, n_neighbors=5):
        imputer = KNNImputer(n_neighbors=n_neighbors)
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns
        self.df[numeric_cols] = imputer.fit_transform(self.df[numeric_cols])
        print("KNN imputation applied.")
        return self.df

    def nullfix_mice(self):
        imputer = IterativeImputer()
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns
        self.df[numeric_cols] = imputer.fit_transform(self.df[numeric_cols])
        print("MICE imputation applied.")
        return self.df

    def nullfix_timeseries(self, method='ffill'):
        self.df = self.df.fillna(method=method)
        print(f"Time-series imputation ({method}) applied.")
        return self.df

