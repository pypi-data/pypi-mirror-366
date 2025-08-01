
# Glazzbocks

_A transparent, interpretable machine learning framework_

**Glazzbocks** (pronounced "glass box") provides a modular and fully auditable pipeline for building, diagnosing, and interpreting machine learning models. Designed to comply with real-world regulatory and interpretability demands—particularly in finance, healthcare, and insurance—Glazzbocks enables practitioners to go beyond accuracy and deliver insights that are explainable, defensible, and production-ready.

---

## Why "Glass Box" ML?

Modern machine learning offers unprecedented predictive power, but too often at the cost of transparency. In high-stakes or regulated environments, this trade-off is unacceptable.

**Glazzbocks** is built on the principle that powerful models should also be interpretable. Every component—from preprocessing to diagnostics and interpretation—is designed to remain visible, explainable, and auditable.

Rather than obscuring internal logic behind black-box pipelines, this framework promotes **transparent, modular ML development** where every decision and output can be inspected, traced, and justified.

---

## Industry Relevance

Many domains face legal, ethical, or operational requirements that demand model explainability. Glazzbocks is particularly suited for:

### Finance and Credit Risk
- Explain loan decisions using coefficients, SHAP, or PDP
- Comply with fair lending regulations (e.g., ECOA, FCRA)
- Audit model outputs for disparate impact

### Healthcare and Life Sciences
- Support clinical decision-making with interpretable diagnostics
- Align with FDA guidance on algorithmic risk and bias
- Validate performance without opaque heuristics

### Insurance Underwriting and Claims
- Reveal why customers are rated differently
- Justify risk assessments during regulatory reviews
- Provide human-interpretable justifications to customers

---

## Key Advantages of Glazzbocks

- **Full Interpretability**: Native support for feature importances, coefficients, SHAP values, PDPs, and permutation importances
- **Auditable Pipelines**: Clear step-by-step ML workflows using modular, scikit-learn-compatible structures
- **Built for Compliance**: Enables traceability for data transformations, model decisions, and performance metrics
- **Diagnostic Depth**: Includes error distributions, lift charts, cumulative gain, VIF analysis, and more
- **Human-Centric Development**: Designed for data scientists, analysts, and auditors who need to understand and explain model behavior—not just optimize accuracy

---

## Components

### `ML_Pipeline.py`
> End-to-end automation for classification and regression:
- Handles preprocessing of numerical and categorical features
- Supports any scikit-learn compatible model
- Includes train/test split and pipeline building
- Performs cross-validation with detailed fold-wise metrics
- Stores ROC, precision-recall, and threshold analysis (for classifiers)
- Summarizes cross-validated performance across models

### `diagnostics.py`
> Automated performance diagnostics after training:
- Classification: ROC, Confusion Matrix, F1 vs Threshold, Lift Chart, Gain Chart
- Regression: Predicted vs Actual, Residual Plot, Error Distribution, Q-Q Plot
- Auto-detects task type and generates all relevant visuals

### `modelinterpreter.py`
> Model interpretation & explainability utilities:
- Tree-based models: Feature importances
- Linear models: Coefficients (with plot support)
- SHAP summary plots (supports pipelines)
- Partial Dependence Plots (PDP)
- Permutation Importance

### `dataexplorer.py`
> Exploratory Data Analysis (EDA) for modeling decisions:
- Auto-detects task type (regression/classification)
- Displays shape, dtypes, missing values (via `missingno` matrix)
- Visualizes target distribution
- Correlation heatmap
- VIF for multicollinearity detection
- Skewness and normality testing
- Outlier detection (via z-score)
- Entropy calculation (classification only)
- Automatically extracts datetime features (year, month, day, weekday)
- Provides modeling guidance (e.g., transformation hints, imbalance warning)

---

## Example Usage

```python
from pipeline import MLPipeline
from diagnostics import odelDiagnostics
from interpreter import ModelInterpreter
from eda import DataExplorer
```

## Notes

- All components are sklearn-compatible and designed to integrate seamlessly.
- All visualizations are built using `matplotlib`, `seaborn`, or `shap`.
- Logging is optionally supported in `ModelInterpreter` for production.
- Pipelines auto-handle transformed features for compatibility with SHAP/PDP.
