import numpy as np
import pandas as pd
import shap
import matplotlib.pyplot as plt

from sklearn.pipeline import Pipeline
from sklearn.base import is_classifier, is_regressor
from sklearn.exceptions import NotFittedError
from sklearn.inspection import PartialDependenceDisplay, permutation_importance


class ModelInterpreter:
    """
    Interpret trained ML models (linear, tree-based, pipelines) using:
        - Coefficients (linear models)
        - Feature importances (tree models)
        - SHAP values (all compatible models)

    Handles preprocessing pipelines and automatic feature name extraction.
    """

    def __init__(self, model, X_train, task='regression', logger=None):
        """
        Initialize the interpreter.

        Args:
            model: Trained scikit-learn model or pipeline.
            X_train (pd.DataFrame): Training data used to fit the model.
            task (str): 'regression' or 'classification'.
            logger (logging.Logger, optional): Logger for structured output.
        """
        self.X_train = X_train
        self.task = task
        self.logger = logger

        if isinstance(model, Pipeline):
            self.pipeline = model
            self.model = model.steps[-1][1]
            self.feature_names = self._extract_feature_names(model, X_train)
        else:
            self.pipeline = None
            self.model = model
            self.feature_names = list(X_train.columns)

    def _log(self, message):
        if self.logger:
            self.logger.warning(message)
        else:
            print(message)

    def _extract_feature_names(self, pipeline, X):
        """Safely extract transformed feature names from the pipeline."""
        try:
            preprocessor = pipeline.named_steps.get('preprocessing')
            if preprocessor and hasattr(preprocessor, 'get_feature_names_out'):
                return preprocessor.get_feature_names_out()
        except Exception as e:
            self._log(f"Feature name extraction failed: {e}")
        return list(X.columns)

    def summary(self):
        """
        Print a quick summary of what this interpreter can provide.
        """
        print("Model Interpreter Summary")
        print(f"Model type: {type(self.model).__name__}")
        print(f"Task: {self.task}")
        print(f"Feature count: {len(self.feature_names)}")
        print("Supports:")
        print(f" - Coefficients: {hasattr(self.model, 'coef_')}")
        print(f" - Feature Importances: {hasattr(self.model, 'feature_importances_')}")
        print(" - SHAP: (if model is compatible)")

    def feature_importance(self, return_fig=False):
        """
        Plot and return feature importances (tree-based models only).

        Returns:
            pd.Series or None: Feature importances, or None if unsupported.
        """
        if hasattr(self.model, "feature_importances_"):
            names = self.feature_names
            importances = pd.Series(self.model.feature_importances_, index=names)
            importances = importances.sort_values()

            fig, ax = plt.subplots(figsize=(8, 6))
            importances.plot(kind="barh", ax=ax)
            ax.set_title("Feature Importance")
            plt.tight_layout()
            if not return_fig:
                plt.show()

            return importances if not return_fig else (importances, fig, ax)
        else:
            self._log("Feature importances not available.")
            return None

    def coefficients(self, plot=True, return_fig=False):
        """
        Plot and return model coefficients (linear models only).
        """
        if not hasattr(self.model, "coef_"):
            self._log("Coefficients not available.")
            return None

        coefs = self.model.coef_
        if self.task == "classification" and coefs.ndim > 1:
            coefs = np.mean(np.abs(coefs), axis=0)

        names = self.feature_names
        coefs_series = pd.Series(coefs, index=names).sort_values()

        if plot:
            fig, ax = plt.subplots(figsize=(8, 6))
            coefs_series.plot(kind="barh", ax=ax)
            ax.set_title("Model Coefficients")
            plt.tight_layout()
            if return_fig:
                return coefs_series, fig, ax
            else:
                plt.show()

        return coefs_series

    def shap_summary(self, sample_size=500, plot_type="dot"):
        """
        Generate SHAP summary plot (works for most models).

        Args:
            sample_size (int): Sample size for SHAP computation.
            plot_type (str): Type of SHAP summary plot. One of 'dot', 'bar', 'violin'.

        Returns:
            shap.Explanation or None
        """
        try:
            X_transformed = self.X_train

            if self.pipeline:
                try:
                    preprocessor = self.pipeline.named_steps.get('preprocessing')
                    if preprocessor:
                        X_transformed = preprocessor.transform(self.X_train)
                        if hasattr(preprocessor, "get_feature_names_out"):
                            X_transformed = pd.DataFrame(
                                X_transformed, columns=preprocessor.get_feature_names_out()
                            )
                except Exception as e:
                    self._log(f"Pipeline preprocessing failed: {e}")

            X_sample = X_transformed if sample_size >= len(X_transformed) else X_transformed.sample(
                sample_size, random_state=42)

            explainer = shap.Explainer(self.model, X_sample)
            shap_values = explainer(X_sample)

            shap.summary_plot(shap_values, X_sample, plot_type=plot_type)
            return shap_values
        except Exception as e:
            self._log(f"SHAP interpretation failed: {e}")
            return None

    def partial_dependence(self, features, grid_resolution=50):
        """
        Plot partial dependence for one or more features.

        Args:
            features (list or str): Feature name(s) or column indices.
            grid_resolution (int): Number of grid points to evaluate.

        Notes:
            - Best for numeric features.
            - Supports regression and classification models.
        """
        estimator = self.pipeline if self.pipeline is not None else self.model
        X = self.X_train

        try:
            PartialDependenceDisplay.from_estimator(
                estimator, X, features=features, grid_resolution=grid_resolution
            )
            plt.tight_layout()
            plt.show()
        except Exception as e:
            self._log(f"⚠️ PDP failed: {e}")

    def permutation_importance(self, scoring=None, n_repeats=10, random_state=42, plot=True):
        """
        Compute and optionally plot permutation importance.

        Args:
            scoring (str): Scoring metric (e.g., 'r2', 'neg_mean_squared_error', 'accuracy').
            n_repeats (int): How many times to shuffle a feature.
            random_state (int): Reproducibility seed.
            plot (bool): If True, display horizontal bar chart.

        Returns:
            pd.Series: Feature importances ranked high to low.
        """
        estimator = self.pipeline if self.pipeline is not None else self.model
        X = self.X_train

        try:
            y_true = estimator.predict(X)
            result = permutation_importance(
                estimator, X, y_true,
                scoring=scoring, n_repeats=n_repeats, random_state=random_state
            )
            importances = pd.Series(result.importances_mean, index=self.feature_names).sort_values(ascending=False)

            if plot:
                importances.plot(kind='barh', figsize=(8, 6))
                plt.gca().invert_yaxis()
                plt.title('Permutation Feature Importance')
                plt.show()

            return importances
        except Exception as e:
            self._log(f"⚠️ Permutation importance failed: {e}")
            return None