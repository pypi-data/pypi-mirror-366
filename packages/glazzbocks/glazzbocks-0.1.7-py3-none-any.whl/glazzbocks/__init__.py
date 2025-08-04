"""
glazzbocks: Glassbox Machine Learning for Interpretable AI

Modules:
- DataExplorer: EDA, summaries, and professional PDF reports.
- MLPipeline: Modeling pipeline with transparent preprocessing.
- ModelDiagnostics: Visual diagnostics for regression/classification.
- ModelInterpreter: Post-hoc model explainability (e.g. SHAP).
"""

from .pipeline.ML_pipeline import MLPipeline
from .diagnostics.model_diagnostics import ModelDiagnostics
from .diagnostics.feature_diagnostics import run_feature_diagnostics
from .interpreters.modelinterpreter import ModelInterpreter
from .eda.data_explorer import DataExplorer 

__all__ = [
    "MLPipeline",
    "ModelDiagnostics",
    "ModelInterpreter",
    "run_feature_diagnostics",
    "DataExplorer"
]
