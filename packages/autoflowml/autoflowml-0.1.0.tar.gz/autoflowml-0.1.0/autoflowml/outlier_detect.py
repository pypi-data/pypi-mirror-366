import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest

class AutoOutlier:
    def __init__(self, method='zscore', strategy='remove', threshold=3.0):
        self.method = method
        self.strategy = strategy
        self.threshold = threshold
        self.report = {}

    def fit_transform(self, df, numeric_cols=None):
        if numeric_cols is None:
            numeric_cols = df.select_dtypes(include=np.number).columns.tolist()

        df_clean = df.copy()

        for col in numeric_cols:
            original_count = df.shape[0]
            if self.method == 'zscore':
                df_clean = self._zscore(df_clean, col)
            elif self.method == 'iqr':
                df_clean = self._iqr(df_clean, col)
            elif self.method == 'isolation_forest':
                df_clean = self._isolation_forest(df_clean, col)
            new_count = df_clean.shape[0]
            self.report[col] = original_count - new_count

        return df_clean

    def _zscore(self, df, col):
        z_scores = (df[col] - df[col].mean()) / df[col].std()
        outliers = np.abs(z_scores) > self.threshold
        return self._handle_outliers(df, col, outliers)

    def _iqr(self, df, col):
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        outliers = (df[col] < (Q1 - self.threshold * IQR)) | (df[col] > (Q3 + self.threshold * IQR))
        return self._handle_outliers(df, col, outliers)

    def _isolation_forest(self, df, col):
        clf = IsolationForest(contamination=0.05, random_state=42)
        reshaped = df[col].values.reshape(-1, 1)
        preds = clf.fit_predict(reshaped)
        outliers = preds == -1
        return self._handle_outliers(df, col, outliers)

    def _handle_outliers(self, df, col, outliers):
        if self.strategy == 'remove':
            return df[~outliers]
        elif self.strategy == 'cap':
            capped = df.copy()
            if self.method == 'zscore':
                capped[col] = np.where(outliers, df[col].median(), df[col])
            else:
                lower = df[col].quantile(0.05)
                upper = df[col].quantile(0.95)
                capped[col] = np.clip(df[col], lower, upper)
            return capped
        else:
            raise ValueError("Unsupported strategy: choose 'remove' or 'cap'")

    def get_report(self):
        return pd.DataFrame.from_dict(self.report, orient='index', columns=['Outliers Removed'])

