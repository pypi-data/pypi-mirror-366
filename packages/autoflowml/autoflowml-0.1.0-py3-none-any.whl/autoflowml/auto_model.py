import pandas as pd
from evalml.automl import AutoMLSearch
from evalml.utils import infer_feature_types
from sklearn.model_selection import train_test_split

def run_tiny_automl(file_path, target_column, problem_type='regression', max_iterations=10):
    # Load dataset
    X = file_path.drop(columns=[target_column])
    y = file_path[target_column]

    # Infer EvalML feature types
    X = infer_feature_types(X)
    y = infer_feature_types(y)

    # Train-test split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Run AutoML Search
    automl = AutoMLSearch(
        X_train=X_train,
        y_train=y_train,
        problem_type=problem_type,
        objective='auto',
        max_iterations=max_iterations,
        optimize_thresholds=True,
        verbose=True
    )

    automl.search()

    # Best pipeline summary
    print("\nBest pipeline:")
    print(automl.best_pipeline.summary)

    # Evaluate on test set
    print("\nEvaluation on test data:")
    if problem_type == 'classification':
        print(automl.best_pipeline.score(X_test, y_test, objectives=["f1", "accuracy", "auc"]))
    else:
        print(automl.best_pipeline.score(X_test, y_test, objectives=["r2", "mae", "mse"]))

    # Export best model
    automl.best_pipeline.save("best_model_pipeline.pkl")
    print("\nBest model pipeline saved as 'best_model_pipeline.pkl'")

