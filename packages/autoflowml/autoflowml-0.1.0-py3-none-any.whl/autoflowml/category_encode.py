import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder, OneHotEncoder
from category_encoders import TargetEncoder, BinaryEncoder
import warnings

warnings.filterwarnings("ignore")


class CategoricalMaster:
    def __init__(self, df: pd.DataFrame, target_column: str, model_type: str = 'tree'):
        self.df = df.copy()
        self.target_column = target_column
        self.model_type = model_type.lower()
        self.encoders = {}

    def detect_categoricals(self) -> list:
        """Detect columns with categorical data types."""
        return self.df.select_dtypes(include=['object', 'category']).columns.tolist()

    def encode_label(self, col: str):
        le = LabelEncoder()
        self.df[col] = le.fit_transform(self.df[col])
        self.encoders[col] = le
        print(f"Label encoded: {col}")

    def encode_onehot(self, col: str):
        ohe = OneHotEncoder(sparse_output=False, drop='first')
        transformed = ohe.fit_transform(self.df[[col]])
        df_ohe = pd.DataFrame(transformed, columns=[f"{col}_{cat}" for cat in ohe.categories_[0][1:]])
        df_ohe.index = self.df.index  # Maintain index alignment
        self.df = pd.concat([self.df.drop(columns=[col]), df_ohe], axis=1)
        self.encoders[col] = ohe
        print(f"One-hot encoded: {col}")

    def encode_target(self, col: str):
        te = TargetEncoder()
        self.df[col] = te.fit_transform(self.df[col], self.df[self.target_column])
        self.encoders[col] = te
        print(f"Target encoded: {col}")

    def encode_binary(self, col: str):
        be = BinaryEncoder(cols=[col])
        self.df = be.fit_transform(self.df)
        self.encoders[col] = be
        print(f"Binary encoded: {col}")

    def encode_auto(self) -> pd.DataFrame:
        """Automatically encode all categorical variables based on model type and cardinality."""
        # Encode target if it's categorical
        if self.df[self.target_column].dtype == 'object' or self.df[self.target_column].nunique() <= 10:
            le = LabelEncoder()
            self.df[self.target_column] = le.fit_transform(self.df[self.target_column])
            self.encoders[self.target_column] = le
            print(f"Target column '{self.target_column}' label encoded.")
        else:
            print(f"Target column '{self.target_column}' is already numeric. Skipping encoding.")

        cat_cols = self.detect_categoricals()
        cat_cols = [col for col in cat_cols if col != self.target_column]

        for col in cat_cols:
            cardinality = self.df[col].nunique()
            if cardinality == 2:
                self.encode_label(col)
            elif cardinality <= 10:
                self.encode_onehot(col)
            elif self.model_type == 'tree':
                self.encode_target(col)
            else:
                self.encode_binary(col)

        return self.df
