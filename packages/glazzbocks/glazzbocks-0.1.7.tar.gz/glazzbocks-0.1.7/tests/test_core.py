
import pytest
from tests.glazzbocks import DataExplorer, MLPipeline, ModelDiagnostics, ModelInterpreter
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

@pytest.fixture
def sample_data():
    df = pd.DataFrame({
        'feature1': [1, 2, 3, 4],
        'feature2': [5, 6, 7, 8],
        'target': [10, 20, 30, 40]
    })
    return df

def test_dataexplorer_init(sample_data):
    explorer = DataExplorer(sample_data, target_col='target')
    assert explorer is not None

def test_mlpipeline_basic(sample_data):
    pipeline = MLPipeline(sample_data, target_column='target')
    pipeline.build_pipeline(model=LinearRegression())
    pipeline.train_model()
    results = pipeline.evaluate_model()
    assert results is not None

def test_modeldiagnostics_auto(sample_data):
    pipeline = MLPipeline(sample_data, target_column='target')
    pipeline.build_pipeline(model=LinearRegression())
    pipeline.train_model()
    diagnostics = ModelDiagnostics(pipeline.pipeline)
    assert diagnostics is not None

def test_modelinterpreter_shap(sample_data):
    X = sample_data[['feature1', 'feature2']]
    y = sample_data['target']
    model = LinearRegression().fit(X, y)
    interpreter = ModelInterpreter(model, X, y)
    assert interpreter is not None
