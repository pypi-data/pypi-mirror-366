"""
ML_pipeline.py - Glazzbocks Core

This module defines the MLPipeline class used to automate the modeling workflow,
including preprocessing, cross-validation, and scoring for both regression and
classification tasks.

Features:
- Auto-handling of numerical and categorical features
- Binary and multiclass classification support
- Integrated cross-validation with scoring and metrics
- Compatible with any scikit-learn-compatible model

Part of the Glazzbocks interpretability framework.

Author: Joshua Thompson
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os
from .diagnostics import ModelDiagnostics
from sklearn.base import is_classifier
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LinearRegression
from sklearn.metrics import (
    accuracy_score, f1_score, mean_absolute_error, roc_curve,
    precision_recall_curve, mean_squared_error, precision_score, r2_score,
    recall_score
)
from sklearn.model_selection import KFold, cross_validate, train_test_split
from sklearn.pipeline import Pipeline
from .utils.preprocessing import (
    create_numeric_pipeline,
    create_categorical_pipeline,
    create_transformer,
)
from .utils.feature_diagnostics import run_feature_diagnostics
import time

class MLPipeline:
    def __init__(self, model=None):
        self.model = model if model else LinearRegression()
        self.pipeline = None
        self.numeric_cols = []
        self.categorical_cols = []

    def set_model(self, model):
        self.model = model
        self.pipeline = None
        print(f"Model set to: {self.model}")

    def split_data(self, df, target_col, test_size=0.2, random_state=42):
        X = df.drop(columns=[target_col])
        y = df[target_col]
        return train_test_split(X, y, test_size=test_size, random_state=random_state)

    def _build_transformers(self, X_train, transform_config=None):
        self.numeric_cols = X_train.select_dtypes(include="number").columns.tolist()
        self.categorical_cols = X_train.select_dtypes(include="object").columns.tolist()

        transformers = []

        if self.numeric_cols:
            transformers.append(("num", create_numeric_pipeline(), self.numeric_cols))

        if transform_config:
            for transform_type, columns in transform_config.items():
                transformers.append(create_transformer(transform_type, columns))

        if self.categorical_cols:
            transformers.append(("cat", create_categorical_pipeline(), self.categorical_cols))

        if not transformers:
            raise ValueError("No columns to transform. Check your input data.")

        return transformers

    def build_pipeline(self, X_train, transform_config=None):
        transformers = self._build_transformers(X_train, transform_config)
        preprocessor = ColumnTransformer(transformers, remainder="passthrough")

        self.pipeline = Pipeline([
            ("preprocessing", preprocessor),
            ("model", self.model),
        ])

    def cross_validate(self, X_train, y_train, n_splits=10):
        """
        Performs cross-validation with metrics.

        Args:
            X_train (pd.DataFrame or np.ndarray): Training features.
            y_train (pd.Series or np.ndarray): Training target.
            n_splits (int): Number of cross-validation folds (default: 10).

        Stores:
            self.cv_results_ (dict): Metrics, ROC data, F1 thresholds, and test folds.
        """
        if self.pipeline is None:
            self.build_pipeline(X_train)

        model = self.pipeline.steps[-1][1]
        is_classification = is_classifier(model)

        if not is_classification:
            # Regression scoring
            scoring = {
                "neg_mean_squared_error": "neg_mean_squared_error",
                "neg_mean_absolute_error": "neg_mean_absolute_error",
                "r2": "r2",
            }
            cv = KFold(n_splits=n_splits, shuffle=True, random_state=42)
            cv_results = cross_validate(self.pipeline, X_train, y_train, cv=cv, scoring=scoring)

            metrics_df = pd.DataFrame({
                f"fold_{i}": {
                    "mse": -cv_results["test_neg_mean_squared_error"][i],
                    "rmse": np.sqrt(-cv_results["test_neg_mean_squared_error"][i]),
                    "mae": -cv_results["test_neg_mean_absolute_error"][i],
                    "r2": cv_results["test_r2"][i],
                }
                for i in range(n_splits)
            }).T
            metrics_df.index.name = "fold"

            self.cv_results_ = {
                "metrics": metrics_df,
                "roc_data": None,
                "f1_threshold_data": None,
                "X_test_folds": None,
                "y_test_folds": None,
            }
            return

        # Classification scoring
        scoring = {
            "accuracy": "accuracy",
            "precision": "precision_weighted",
            "recall": "recall_weighted",
            "f1": "f1_weighted",
        }

        cv = KFold(n_splits=n_splits, shuffle=True, random_state=42)
        cv_results = cross_validate(
            self.pipeline, X_train, y_train,
            cv=cv, scoring=scoring, return_estimator=True
        )

        fold_results = {}
        roc_data, f1_data = {}, {}
        X_folds, y_folds = {}, {}

        for i, (train_idx, test_idx) in enumerate(cv.split(X_train, y_train)):
            X_test_fold = X_train.iloc[test_idx] if isinstance(X_train, pd.DataFrame) else X_train[test_idx]
            y_test_fold = y_train.iloc[test_idx] if isinstance(y_train, pd.Series) else y_train[test_idx]

            X_folds[f"fold_{i}"] = X_test_fold
            y_folds[f"fold_{i}"] = y_test_fold

            est = cv_results["estimator"][i]

            if hasattr(est, "predict_proba"):
                y_prob = est.predict_proba(X_test_fold)
                if y_prob.shape[1] == 2:
                    y_score = y_prob[:, 1]
                    fpr, tpr, thresholds = roc_curve(y_test_fold, y_score)
                    roc_data[f"fold_{i}"] = {
                        "fpr": fpr, "tpr": tpr, "thresholds": thresholds
                    }

                    precision, recall, thresh = precision_recall_curve(y_test_fold, y_score)
                    f1s = 2 * (precision * recall) / (precision + recall + 1e-10)
                    best_idx = np.argmax(f1s)
                    f1_data[f"fold_{i}"] = {
                        "threshold": thresh[best_idx],
                        "f1": f1s[best_idx],
                    }

            fold_results[f"fold_{i}"] = {
                "accuracy": cv_results["test_accuracy"][i],
                "precision": cv_results["test_precision"][i],
                "recall": cv_results["test_recall"][i],
                "f1": cv_results["test_f1"][i],
            }

        metrics_df = pd.DataFrame(fold_results).T
        metrics_df.index.name = "fold"

        self.cv_results_ = {
            "metrics": metrics_df,
            "roc_data": roc_data,
            "f1_threshold_data": pd.DataFrame(f1_data).T,
            "X_test_folds": X_folds,
            "y_test_folds": y_folds,
        }

    def evaluate_on_test(self, X_test, y_test):
        """
        Evaluate the trained pipeline on a held-out test set.

        Args:
            X_test (pd.DataFrame): Test features.
            y_test (pd.Series): True test target values.

        Returns:
            dict: Classification report (dict) or regression metrics.
        """
        from sklearn.metrics import classification_report
        import json

        if self.pipeline is None:
            raise ValueError("Pipeline has not been built.")

        is_classification = is_classifier(self.pipeline.named_steps["model"])
        y_pred = self.pipeline.predict(X_test)

        if is_classification:
            report = classification_report(y_test, y_pred, output_dict=True)
            return report
        else:
            mse = mean_squared_error(y_test, y_pred)
            mae = mean_absolute_error(y_test, y_pred)
            r2 = r2_score(y_test, y_pred)
            rmse = np.sqrt(mse)
            return {"test_mse": mse, "test_mae": mae, "test_rmse": rmse, "test_r2": r2}

    def get_diagnostics(self):
        """
        Wraps the current pipeline in a ModelDiagnostics instance.

        Returns:
            ModelDiagnostics: Diagnostics object for the pipeline.
        """
        return ModelDiagnostics(self.pipeline)

    @staticmethod
    def summarize_cv_results(results_dict, metrics=("accuracy", "precision", "recall", "f1", "r2", "rmse", "mae")):
        """
        Creates a summary table of average CV metrics from multiple models.

        Args:
            results_dict (dict): Dictionary of model names and their cv_results_ outputs.
            metrics (tuple): Metrics to extract from each model.

        Returns:
            pd.DataFrame: Summary table of mean metrics per model.
        """
        summary = {}
        for model_name, cv_data in results_dict.items():
            model_metrics = cv_data["metrics"]
            available_metrics = [m for m in metrics if m in model_metrics.columns]
            row = model_metrics[available_metrics].mean().to_dict()
            row["inference_time"] = cv_data.get("inference_time", np.nan)
            summary[model_name] = row

        summary_df = pd.DataFrame(summary).T
        summary_df.index.name = "Model"
        return summary_df

    @staticmethod
    def compare_models(model_dict, X_train, y_train, run_feature_diagnostics_flag=True, vif_threshold=5.0):
        """
        Compares multiple models using MLPipeline cross-validation.

        Args:
            model_dict (dict): Dictionary of {name: estimator}.
            X_train (pd.DataFrame): Training features.
            y_train (pd.Series): Training target.

        Returns:
            pd.DataFrame: Summary of CV metrics and inference time per model.
            dict: Dictionary of fitted MLPipeline instances (for diagnostics, plotting, etc.)
        """
        results = {}
        pipelines = {}

        for name, model in model_dict.items():
            print(f"\U0001f501 Cross-validating model: {name}")
            pipe = MLPipeline(model)
            pipe.build_pipeline(X_train)
            pipe.cross_validate(X_train, y_train, run_feature_diagnostics_flag=run_feature_diagnostics_flag, vif_threshold=vif_threshold)

            X_sample = X_train.sample(n=min(100, len(X_train)), random_state=42)
            start = time.time()
            pipe.pipeline.predict(X_sample)
            end = time.time()
            latency = (end - start) / len(X_sample) * 1000

            results[name] = pipe.cv_results_
            results[name]["inference_time_ms"] = latency
            pipelines[name] = pipe

        summary = MLPipeline.summarize_cv_results(results)
        return summary, pipelines

        
       