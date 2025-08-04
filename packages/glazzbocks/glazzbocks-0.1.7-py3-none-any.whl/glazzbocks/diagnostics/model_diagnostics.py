"""
model_diagnostics.py

Provides a comprehensive visual diagnostics toolkit for scikit-learn models.

Supports both classification and regression pipelines via intuitive plotting functions,
including:

- ROC and precision-recall curves (binary/multiclass)
- Confusion matrices and F1-threshold visualizations
- Lift and cumulative gain charts
- Residual analysis and QQ plots for regression models
- Automated plotting suite via `auto_plot()`

The module is designed for use with fitted sklearn `Pipeline` objects and
automatically detects model type and plot applicability.

Author: Joshua Thompson
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats
from scipy.stats import normaltest
from sklearn.base import is_classifier
from sklearn.linear_model import ElasticNet, Lasso, LinearRegression, Ridge
from sklearn.metrics import (
    ConfusionMatrixDisplay,
    RocCurveDisplay,
    confusion_matrix,
    precision_recall_curve,
    roc_auc_score,
    roc_curve,
)
from sklearn.preprocessing import label_binarize
import os
from sklearn.manifold import TSNE
import seaborn as sns

class ModelDiagnostics:
    """
    A visualization-based diagnostic toolkit for evaluating fitted scikit-learn pipelines.

    Supports both classification and regression pipelines:
    - For classification: ROC curves, confusion matrices, lift charts, etc.
    - For regression: residual plots, Q-Q plots, predicted vs actual, etc.

    Attributes:
        pipeline (Pipeline): A fitted sklearn pipeline with final estimator.
        model (estimator): Extracted model object from the pipeline.
    """

    def __init__(self, pipeline):
        """
        Initialize the diagnostic toolkit with a fitted sklearn pipeline.

        Args:
            pipeline (Pipeline): A trained scikit-learn pipeline.
        """
        self.pipeline = pipeline
        self.model = self.pipeline.steps[-1][1]

    def _check_fitted(self):
        """
        Internal utility to confirm that pipeline has been fitted.
        Raises:
            ValueError: If pipeline doesn't have a 'predict' method.
        """
        if not hasattr(self.pipeline, "predict"):
            raise ValueError("Pipeline is not fitted.")

    def plot_roc_curve(self, X_test, y_test):
        """
        Plot ROC curve for binary or multiclass classification.

        Args:
            X_test (np.ndarray or pd.DataFrame): Test features.
            y_test (np.ndarray or pd.Series): True test labels.

        Raises:
            ValueError: If model is not a classifier.
        """
        self._check_fitted()
        if not is_classifier(self.model):
            raise ValueError("Only valid for classification models.")

        y_proba = self.pipeline.predict_proba(X_test)
        classes = np.unique(y_test)
        plt.figure(figsize=(8, 6))

        if y_proba.shape[1] == 2:
            # Binary classification
            y_score = y_proba[:, 1]
            auc_score = roc_auc_score(y_test, y_score)
            RocCurveDisplay.from_predictions(y_test, y_score)
            plt.title(f"ROC Curve - Binary (AUC = {auc_score:.2f})")
        else:
            # Multiclass OvR
            y_test_bin = label_binarize(y_test, classes=classes)
            for i, cls in enumerate(classes):
                fpr, tpr, _ = roc_curve(y_test_bin[:, i], y_proba[:, i])
                auc_score = roc_auc_score(y_test_bin[:, i], y_proba[:, i])
                plt.plot(fpr, tpr, label=f"Class {cls} (AUC={auc_score:.2f})")
            plt.plot([0, 1], [0, 1], "k--")
            plt.title("ROC Curve - Multiclass OvR")
            plt.legend()

        plt.xlabel("False Positive Rate")
        plt.ylabel("True Positive Rate")
        plt.grid(True)
        plt.show()

    def plot_precision_recall_curve(self, X_test, y_test):
        """
        Plots the precision-recall curve (binary classification only).

        Args:
            X_test (np.ndarray): Test features.
            y_test (np.ndarray): True labels.
        """
        self._check_fitted()
        if not is_classifier(self.model):
            raise ValueError("Only valid for classification models.")

        y_proba = self.pipeline.predict_proba(X_test)
        if y_proba.shape[1] != 2:
            print("Precision-recall curve not supported for multiclass.")
            return

        precision, recall, _ = precision_recall_curve(y_test, y_proba[:, 1])
        plt.figure(figsize=(8, 6))
        plt.plot(recall, precision, label="PR Curve")
        plt.xlabel("Recall")
        plt.ylabel("Precision")
        plt.title("Precision-Recall Curve - Test Set")
        plt.grid(True)
        plt.tight_layout()
        plt.show()

    def plot_f1_threshold(self, X_test, y_test):
        """
        Plot F1 score across different probability thresholds (binary classification only).

        Args:
            X_test (np.ndarray): Test features.
            y_test (np.ndarray): True labels.
        """
        self._check_fitted()
        if not is_classifier(self.model):
            raise ValueError("Only valid for classification models.")

        y_proba = self.pipeline.predict_proba(X_test)

        if y_proba.shape[1] != 2:
            print("F1 vs Threshold not supported for multiclass. Skipping plot.")
            return

        y_score = y_proba[:, 1]
        precision, recall, thresholds = precision_recall_curve(y_test, y_score)
        f1_scores = 2 * (precision * recall) / (precision + recall + 1e-10)
        idx = np.argmax(f1_scores)

        plt.figure(figsize=(8, 6))
        plt.plot(thresholds, f1_scores[:-1], label="F1 Score")
        plt.plot(thresholds[idx], f1_scores[idx], "ro", label=f"Best = {thresholds[idx]:.2f}")
        plt.xlabel("Threshold")
        plt.ylabel("F1 Score")
        plt.title("F1 Score vs Threshold - Test Set")
        plt.legend()
        plt.grid(True)
        plt.show()

    def plot_confusion_matrix(self, X_test, y_test, normalize="true"):
        """
        Plot a confusion matrix for classification predictions.

        Args:
            X_test (np.ndarray): Test features.
            y_test (np.ndarray): True test labels.
            normalize (str): One of {'true', 'pred', 'all', None} for normalization.
        """
        self._check_fitted()
        if not is_classifier(self.model):
            raise ValueError("Only valid for classification models.")

        y_pred = self.pipeline.predict(X_test)
        cm = confusion_matrix(y_test, y_pred, normalize=normalize)
        disp = ConfusionMatrixDisplay(confusion_matrix=cm)
        disp.plot(cmap="Blues", values_format=".2f" if normalize else "d")
        plt.title("Confusion Matrix - Test Set")
        plt.grid(False)
        plt.show()

    def plot_lift_chart(self, X_test, y_test, bins=10):
        """
        Plot a lift chart showing predictive power by decile (binary classification only).

        Args:
            X_test (np.ndarray): Test features.
            y_test (np.ndarray): True labels.
            bins (int): Number of quantile bins to group predictions into.
        """
        self._check_fitted()
        if not is_classifier(self.model):
            raise ValueError("Only valid for classification models.")

        y_proba = self.pipeline.predict_proba(X_test)

        if y_proba.shape[1] != 2:
            print("Lift chart only supported for binary classification.")
            return

        df = pd.DataFrame({"y": y_test, "proba": y_proba[:, 1]})
        df["bin"] = pd.qcut(df["proba"], q=bins, duplicates="drop")
        lift = df.groupby("bin")["y"].mean() / df["y"].mean()
        lift.plot(kind="bar", figsize=(8, 6))
        plt.title("Lift Chart")
        plt.ylabel("Lift")
        plt.xlabel("Probability Decile")
        plt.grid(False)
        plt.show()

    def plot_cumulative_gain_chart(self, X_test, y_test):
        """
        Plot cumulative gain chart to visualize concentration of true positives (binary only).

        Args:
            X_test (np.ndarray): Test features.
            y_test (np.ndarray): True binary labels.
        """
        self._check_fitted()
        if not is_classifier(self.model):
            raise ValueError("Only valid for classification models.")

        y_proba = self.pipeline.predict_proba(X_test)

        if y_proba.shape[1] != 2:
            print("Cumulative gain chart only supported for binary classification.")
            return

        data = pd.DataFrame({"y_true": y_test, "y_score": y_proba[:, 1]})
        data.sort_values(by="y_score", ascending=False, inplace=True)
        data["cum_positive"] = data["y_true"].cumsum()
        data["percent_samples"] = np.arange(1, len(data) + 1) / len(data)
        data["percent_positive"] = data["cum_positive"] / data["y_true"].sum()

        plt.figure(figsize=(8, 6))
        plt.plot(data["percent_samples"], data["percent_positive"], label="Model")
        plt.plot([0, 1], [0, 1], "k--", label="Baseline")
        plt.title("Cumulative Gain Chart")
        plt.xlabel("Proportion of Samples")
        plt.ylabel("Cumulative Positives")
        plt.legend()
        plt.grid(False)
        plt.show()

    def plot_predicted_vs_actual(self, X_test, y_test):
        """
        Scatter plot of predicted vs actual values for regression.

        Args:
            X_test (np.ndarray): Test features.
            y_test (np.ndarray): True numeric values.
        """
        self._check_fitted()
        if is_classifier(self.model):
            raise ValueError("Only valid for regression models.")

        y_pred = self.pipeline.predict(X_test)
        plt.figure(figsize=(8, 6))
        plt.scatter(y_test, y_pred, alpha=0.5)
        plt.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], "r--", lw=2)
        plt.title("Predicted vs Actual - Test Set")
        plt.xlabel("Actual")
        plt.ylabel("Predicted")
        plt.grid(False)
        plt.show()

    def plot_residuals(self, X_test, y_test, check_normality=True):
        """
        Residuals plot for regression; optionally tests normality for linear models.

        Args:
            X_test (np.ndarray): Test features.
            y_test (np.ndarray): True values.
            check_normality (bool): If True, runs D’Agostino test on residuals.
        """
        self._check_fitted()
        if is_classifier(self.model):
            raise ValueError("Only valid for regression models.")

        y_pred = self.pipeline.predict(X_test)
        residuals = y_test - y_pred
        is_linear = isinstance(self.model, (LinearRegression, Ridge, Lasso, ElasticNet))

        if is_linear and check_normality:
            stat, p = normaltest(residuals)
            print(f"Normality Test: stat={stat:.2f}, p={p:.3f} → {'Normal' if p >= 0.05 else 'Not Normal'}")

        plt.figure(figsize=(8, 6))
        plt.scatter(y_pred, residuals, alpha=0.5)
        plt.axhline(0, color="red", linestyle="--")
        plt.title("Residuals vs Predicted")
        plt.xlabel("Predicted")
        plt.ylabel("Residuals")
        plt.grid(False)
        plt.show()

    def plot_error_distribution(self, X_test, y_test):
        """
        Histogram of residuals (errors) for regression models.

        Args:
            X_test (np.ndarray): Test data.
            y_test (np.ndarray): Actual values.
        """
        self._check_fitted()
        if is_classifier(self.model):
            raise ValueError("Only valid for regression models.")

        residuals = y_test - self.pipeline.predict(X_test)
        plt.figure(figsize=(8, 6))
        plt.hist(residuals, bins=30, alpha=0.7)
        plt.title("Residuals Histogram")
        plt.xlabel("Residuals")
        plt.grid(False)
        plt.show()

    def plot_qq(self, X_test, y_test):
        """
        Q-Q plot of residuals against a normal distribution.

        Args:
            X_test (np.ndarray): Test features.
            y_test (np.ndarray): True values.
        """
        self._check_fitted()
        if is_classifier(self.model):
            raise ValueError("Only valid for regression models.")

        residuals = y_test - self.pipeline.predict(X_test)
        plt.figure(figsize=(8, 6))
        stats.probplot(residuals, dist="norm", plot=plt)
        plt.title("QQ Plot of Residuals")
        plt.grid(False)
        plt.show()

    def auto_plot(self, X_test, y_test):
        """
        Run all applicable plots based on model type.

        Args:
            X_test (np.ndarray): Test set features.
            y_test (np.ndarray): True labels or values.
        """
        if is_classifier(self.model):
            n_classes = len(np.unique(y_test))
            self.plot_confusion_matrix(X_test, y_test)
            self.plot_roc_curve(X_test, y_test)
            if n_classes == 2:
                self.plot_f1_threshold(X_test, y_test)
                self.plot_lift_chart(X_test, y_test)
                self.plot_cumulative_gain_chart(X_test, y_test)
        else:
            self.plot_predicted_vs_actual(X_test, y_test)
            self.plot_residuals(X_test, y_test)
            self.plot_error_distribution(X_test, y_test)
            self.plot_qq(X_test, y_test)

    def plot_class_separation(self, X, y, method="tsne", perplexity=30):
        """
        Projects feature space into 2D and colors by class for visual separability.

        Args:
            X (pd.DataFrame or np.ndarray): Feature matrix.
            y (array-like): Class labels.
            method (str): 'tsne' or 'umap'.
            perplexity (int): t-SNE perplexity (ignored for UMAP).
        """
        try:
            if isinstance(self.pipeline, Pipeline):
                X_transformed = self.pipeline.named_steps['preprocessing'].transform(X)
            else:
                X_transformed = X

            if method == "tsne":
                reducer = TSNE(n_components=2, perplexity=perplexity, random_state=42)
            elif method == "umap":
                import umap
                reducer = umap.UMAP(n_components=2, random_state=42)
            else:
                raise ValueError("Method must be 'tsne' or 'umap'.")

            embedding = reducer.fit_transform(X_transformed)
            df_plot = pd.DataFrame(embedding, columns=["Dim1", "Dim2"])
            df_plot["Class"] = y

            plt.figure(figsize=(8, 6))
            sns.scatterplot(data=df_plot, x="Dim1", y="Dim2", hue="Class", alpha=0.7, palette="tab10")
            plt.title(f"{method.upper()} Class Separation")
            plt.tight_layout()
            plt.show()

        except Exception as e:
            print(f"Class separation plot failed: {e}")
