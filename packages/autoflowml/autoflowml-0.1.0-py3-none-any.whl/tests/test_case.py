import pandas as pd
import numpy as np
from autoflowml import CleanIt, NullFixer, AutoOutlier, CategoricalMaster

# Sample test data
def test_data():
    return pd.DataFrame({
        'numeric': [1, 2, np.nan, 4, 100],  # Contains outlier (100) and missing value
        'categorical': ['A', 'B', 'A', 'C', 'B'],
        'target': [10, 20, 30, 40, 50]
    })

def test_full_workflow(test_data):
    # 1. Test CleanIt
    cleaner = CleanIt(test_data)
    cleaned = cleaner.full_clean()
    assert cleaned.shape[0] == 5  # No duplicates in this case
    assert '_' in cleaned.columns[0]  # Columns should be standardized

    # 2. Test NullFixer
    fixer = NullFixer(cleaned)
    fixed = fixer.nullfix_knn(n_neighbors=2)
    assert fixed.isna().sum().sum() == 0  # No missing values

    # 3. Test AutoOutlier
    outlier_handler = AutoOutlier(method='iqr', strategy='cap')
    processed = outlier_handler.fit_transform(fixed)
    assert (processed['numeric'] < 10).all()  # Outlier capped

    # 4. Test CategoricalMaster
    encoder = CategoricalMaster(processed, target_column='target')
    encoded = encoder.encode_auto()
    assert 'categorical_B' in encoded.columns  # One-hot encoding applied
    assert encoded.select_dtypes('object').empty  # No string columns left

    # 5. Test model training (smoke test)
    from autoflowml import run_tiny_automl
    results = run_tiny_automl(
        encoded,
        target_column='target',
        problem_type='regression',
        max_iterations=3
    )
    assert 'pipeline' in results
    assert results['scores']['r2'] > -1  # Basic sanity check