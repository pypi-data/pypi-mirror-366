"""
diagnostics.py

Provides diagnostic visualizations and metrics for evaluating regression
and classification models using scikit-learn pipelines.

Author: [Your Name]
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats
from scipy.stats import normaltest

from sklearn.linear_model import LinearRegression, Ridge, Lasso, ElasticNet
from sklearn.metrics import (
    roc_auc_score, confusion_matrix, RocCurveDisplay,
    precision_recall_curve, ConfusionMatrixDisplay
)
from sklearn.base import is_classifier


class ModelDiagnostics:
    """
    Diagnostic visualization and evaluation utilities for ML pipelines.

    Automatically detects whether the pipeline is for regression or classification,
    and generates appropriate plots such as ROC curve, residual plots, and more.
    """

    def __init__(self, pipeline):
        """
        Initialize with a fitted scikit-learn pipeline.

        Args:
            pipeline (Pipeline): Fitted scikit-learn pipeline with final estimator.
        """
        self.pipeline = pipeline
        self.model = self.pipeline.steps[-1][1]  # Final estimator

    def _check_fitted(self):
        """Check that pipeline has been fitted and is valid."""
        if not hasattr(self.pipeline, "predict"):
            raise ValueError("Pipeline is not fitted.")

    def plot_roc_curve(self, X_test, y_test):
        """Plot ROC curve for binary classifiers with AUC score."""
        self._check_fitted()
        if not is_classifier(self.model):
            raise ValueError("Only valid for classification models.")

        y_prob = self.pipeline.predict_proba(X_test)[:, 1]
        auc_score = roc_auc_score(y_test, y_prob)

        RocCurveDisplay.from_predictions(y_test, y_prob)
        plt.title(f'ROC Curve - Test Set (AUC = {auc_score:.2f})')
        plt.show()

    def plot_f1_threshold(self, X_test, y_test):
        """Plot F1 score across different decision thresholds."""
        self._check_fitted()
        if not is_classifier(self.model):
            raise ValueError("Only valid for classification models.")

        y_prob = self.pipeline.predict_proba(X_test)[:, 1]
        precision, recall, thresholds = precision_recall_curve(y_test, y_prob)
        f1_scores = 2 * (precision * recall) / (precision + recall + 1e-10)
        idx = np.argmax(f1_scores)

        plt.figure(figsize=(8, 6))
        plt.plot(thresholds, f1_scores[:-1], label='F1 Score')
        plt.plot(thresholds[idx], f1_scores[idx], 'ro',
                 label=f'Best = {thresholds[idx]:.2f} (F1={f1_scores[idx]:.2f})')
        plt.xlabel('Threshold')
        plt.ylabel('F1 Score')
        plt.title('F1 Score vs Threshold - Test Set')
        plt.legend()
        plt.show()

    def plot_confusion_matrix(self, X_test, y_test, normalize='true'):
        """Display normalized or raw confusion matrix."""
        self._check_fitted()
        if not is_classifier(self.model):
            raise ValueError("Only valid for classification models.")

        y_pred = self.pipeline.predict(X_test)
        cm = confusion_matrix(y_test, y_pred, normalize=normalize)
        disp = ConfusionMatrixDisplay(confusion_matrix=cm)
        disp.plot(cmap='Blues', values_format='.2f' if normalize else 'd')
        plt.title('Confusion Matrix - Test Set')
        plt.show()

    def plot_lift_chart(self, X_test, y_test, bins=10):
        """Create a lift chart to assess ranking performance."""
        self._check_fitted()
        if not is_classifier(self.model):
            raise ValueError("Only valid for classification models.")

        y_proba = self.pipeline.predict_proba(X_test)[:, 1]
        df = pd.DataFrame({'y': y_test, 'proba': y_proba})
        df['bin'] = pd.qcut(df['proba'], q=bins, duplicates='drop')

        lift = df.groupby('bin')['y'].mean() / df['y'].mean()
        lift.plot(kind='bar', figsize=(8, 6))
        plt.title('Lift Chart')
        plt.ylabel('Lift')
        plt.xlabel('Probability Decile')
        plt.grid(False)
        plt.show()

    def plot_cumulative_gain_chart(self, X_test, y_test):
        """Plot cumulative gain to visualize model ranking performance."""
        self._check_fitted()
        if not is_classifier(self.model):
            raise ValueError("Only valid for classification models.")

        y_proba = self.pipeline.predict_proba(X_test)[:, 1]
        data = pd.DataFrame({'y_true': y_test, 'y_score': y_proba})
        data.sort_values(by='y_score', ascending=False, inplace=True)
        data['cum_positive'] = data['y_true'].cumsum()
        data['percent_samples'] = np.arange(1, len(data) + 1) / len(data)
        data['percent_positive'] = data['cum_positive'] / data['y_true'].sum()

        plt.figure(figsize=(8, 6))
        plt.plot(data['percent_samples'], data['percent_positive'], label='Model')
        plt.plot([0, 1], [0, 1], 'k--', label='Baseline')
        plt.title('Cumulative Gain Chart')
        plt.xlabel('Proportion of Samples')
        plt.ylabel('Cumulative Positives')
        plt.legend()
        plt.grid(False)
        plt.show()

    def plot_predicted_vs_actual(self, X_test, y_test):
        """Plot predicted vs. actual values (regression only)."""
        self._check_fitted()
        if is_classifier(self.model):
            raise ValueError("Only valid for regression models.")

        y_pred = self.pipeline.predict(X_test)
        plt.figure(figsize=(8, 6))
        plt.scatter(y_test, y_pred, alpha=0.5)
        plt.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'r--', lw=2)
        plt.title('Predicted vs Actual - Test Set')
        plt.xlabel('Actual')
        plt.ylabel('Predicted')
        plt.grid(False)
        plt.show()

    def plot_residuals(self, X_test, y_test, check_normality=True):
        """
        Plot residuals and optionally check for normality (linear models only).
        """
        self._check_fitted()
        if is_classifier(self.model):
            raise ValueError("Only valid for regression models.")

        y_pred = self.pipeline.predict(X_test)
        residuals = y_test - y_pred
        is_linear = isinstance(self.model, (LinearRegression, Ridge, Lasso, ElasticNet))

        # Normality test
        if is_linear and check_normality:
            stat, p = normaltest(residuals)
            print(f"📊 Normality Test: stat={stat:.2f}, p={p:.3f} → {'✅ Normal' if p >= 0.05 else '❌ Not Normal'}")

        plt.figure(figsize=(8, 6))
        plt.scatter(y_pred, residuals, alpha=0.5)
        plt.axhline(0, color='red', linestyle='--')
        plt.title('Residuals vs Predicted')
        plt.xlabel('Predicted')
        plt.ylabel('Residuals')
        plt.grid(False)
        plt.show()

    def plot_error_distribution(self, X_test, y_test):
        """Plot histogram of residuals (regression only)."""
        self._check_fitted()
        if is_classifier(self.model):
            raise ValueError("Only valid for regression models.")

        residuals = y_test - self.pipeline.predict(X_test)
        plt.figure(figsize=(8, 6))
        plt.hist(residuals, bins=30, alpha=0.7)
        plt.title('Residuals Histogram')
        plt.xlabel('Residuals')
        plt.grid(False)
        plt.show()

    def plot_qq(self, X_test, y_test):
        """QQ plot to check normality of residuals."""
        self._check_fitted()
        if is_classifier(self.model):
            raise ValueError("Only valid for regression models.")

        residuals = y_test - self.pipeline.predict(X_test)
        plt.figure(figsize=(8, 6))
        stats.probplot(residuals, dist="norm", plot=plt)
        plt.title('QQ Plot of Residuals')
        plt.grid(False)
        plt.show()

    def auto_plot(self, X_test, y_test):
        """
        Automatically generate diagnostic plots based on task type.

        Args:
            X_test (array-like): Test features.
            y_test (array-like): True labels.
        """
        if is_classifier(self.model):
            self.plot_roc_curve(X_test, y_test)
            self.plot_f1_threshold(X_test, y_test)
            self.plot_confusion_matrix(X_test, y_test)
            self.plot_lift_chart(X_test, y_test)
            self.plot_cumulative_gain_chart(X_test, y_test)
        else:
            self.plot_predicted_vs_actual(X_test, y_test)
            self.plot_residuals(X_test, y_test)
            self.plot_error_distribution(X_test, y_test)
            self.plot_qq(X_test, y_test)


