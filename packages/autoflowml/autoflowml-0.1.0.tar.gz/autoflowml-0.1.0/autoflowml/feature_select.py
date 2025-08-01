import pandas as pd
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.feature_selection import RFE
from sklearn.model_selection import train_test_split

class FeatureSelector:
    def __init__(self, df: pd.DataFrame, target_column: str, problem_type='regression'):
        self.df = df.copy()
        self.target_column = target_column
        self.problem_type = problem_type.lower()
        self.X = self.df.drop(columns=[target_column])
        self.y = self.df[target_column]

        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
            self.X, self.y, test_size=0.2, random_state=42
        )

    def select_features(self, model_type='linear', n_features=10):
        
        if self.problem_type == 'classification':
            model = RandomForestClassifier(n_estimators=30)
        elif self.problem_type == 'regression':
            model = RandomForestRegressor(n_estimators=30)
        
        rfe = RFE(model, n_features_to_select=n_features)
        rfe.fit(self.X_train, self.y_train)

        selected_features = self.X.columns[rfe.support_]
        print(f"Top {n_features} features selected using RFE with {model_type} for {self.problem_type}:")
        print(selected_features.tolist())

        return self.df[selected_features.tolist() + [self.target_column]]
