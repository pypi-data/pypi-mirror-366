# === Required Imports ===
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder

from sklearn.linear_model import LinearRegression
from sklearn.metrics import (
    mean_squared_error, mean_absolute_error, r2_score,
    accuracy_score, precision_score, recall_score, f1_score
)

from sklearn.model_selection import cross_validate, KFold
from sklearn.base import is_classifier

from diagnostics import ModelDiagnostics

# === MLPipeline Class ===
class MLPipeline:
    """
    A machine learning pipeline for regression and classification tasks.

    This class automates:
        - Data splitting (train/test)
        - Feature preprocessing (numeric scaling, categorical encoding)
        - Model training and prediction
        - Cross-validation (regression & classification)
        - Evaluation and diagnostic visualization

    Attributes:
        model: The ML model (default: LinearRegression).
        pipeline: Full scikit-learn Pipeline (preprocessing + model).
        numeric_cols (list): List of detected numeric column names.
        categorical_cols (list): List of detected categorical column names.
    """
    def __init__(self, model=None):
        self.model = model if model else LinearRegression()
        self.pipeline = None
        self.numeric_cols = []
        self.categorical_cols = []

    def set_model(self, model):
        """
        Set the ML model directly as an initialized scikit-learn instance.
        """
        self.model = model
        self.pipeline = None
        print(f"Model set to: {self.model}")

    def split_data(self, df, target_col, test_size=0.2, random_state=42):
        X = df.drop(columns=[target_col])
        y = df[target_col]
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=random_state)
        return X_train, X_test, y_train, y_test 

    def build_pipeline(self, X):
        """
        Build a preprocessing and modeling pipeline based on the input features.

        Args:
            X (pd.DataFrame): Input feature dataset used to determine numeric and 
                            categorical columns.

        Raises:
            ValueError: If no numeric or categorical columns are detected in `X`.

        Notes:
            - Automatically detects numeric and categorical columns:
                * Numeric columns: dtype `number` (int or float).
                * Categorical columns: dtype `object` (string-based).
            - For numeric features:
                * Missing values are imputed using the median.
                * Features are standardized using StandardScaler.
            - For categorical features:
                * Missing values are imputed with the most frequent value.
                * Features are one-hot encoded (unknown categories ignored at prediction time).
            - The final pipeline is stored in `self.pipeline` as:
                Pipeline([
                    ('preprocessing', ColumnTransformer),
                    ('model', self.model)
                ])
            - Call this method before `fit()` if the pipeline is not already built.
        """
        # Select only non-null column names
        self.numeric_cols = [col for col in X.select_dtypes(include='number').columns if col is not None]
        self.categorical_cols = [col for col in X.select_dtypes(include='object').columns if col is not None]

        numeric_pipeline = Pipeline([
            ('imputer', SimpleImputer(strategy='median')),
            ('scaler', StandardScaler())
        ])

        transformers = []

        if self.numeric_cols:
            transformers.append(('num', numeric_pipeline, self.numeric_cols))

        if self.categorical_cols:
            categorical_pipeline = Pipeline([
                ('imputer', SimpleImputer(strategy='most_frequent')),
                ('encoder', OneHotEncoder(handle_unknown='ignore'))
            ])
            transformers.append(('cat', categorical_pipeline, self.categorical_cols))

        if not transformers:
            raise ValueError("No columns to transform. Check your input data.")

        preprocessor = ColumnTransformer(transformers)

        self.pipeline = Pipeline([
            ('preprocessing', preprocessor),
            ('model', self.model)
        ])

    def cross_validate(self, X_train, y_train):
        """
        Perform cross-validation for regression or classification tasks.
        Stores results in self.cv_results_ for later access.

        Args:
            X_train (pd.DataFrame or np.ndarray): Training feature set.
            y_train (pd.Series or np.ndarray): Training target values.

        Raises:
            ValueError: If the pipeline is not built and no features are available.
        """
        if self.pipeline is None:
            self.build_pipeline(X_train)
        
        model = self.pipeline.steps[-1][1]
        is_classification = is_classifier(model)

        # === REGRESSION ===
        if not is_classification:
            scoring = {
                'neg_mean_squared_error': 'neg_mean_squared_error',
                'neg_mean_absolute_error': 'neg_mean_absolute_error',
                'r2': 'r2'
            }

            cv = KFold(n_splits=10, shuffle=True, random_state=42)
            cv_results = cross_validate(
                self.pipeline, X_train, y_train,
                cv=cv, scoring=scoring, return_train_score=False
            )

            fold_results = {
                f'fold_{i}': {
                    'mse': -cv_results['test_neg_mean_squared_error'][i],
                    'rmse': np.sqrt(-cv_results['test_neg_mean_squared_error'][i]),
                    'mae': -cv_results['test_neg_mean_absolute_error'][i],
                    'r2': cv_results['test_r2'][i]
                }
                for i in range(10)
            }

            metrics_df = pd.DataFrame(fold_results).T
            metrics_df.index.name = 'fold'

            # Store internally
            self.cv_results_ = {
                'metrics': metrics_df,
                'roc_data': None,
                'f1_threshold_data': None,
                'X_test_folds': None,
                'y_test_folds': None
            }
            return  # No need to return anything — stored internally

        # === CLASSIFICATION ===
        scoring = {
            'accuracy': 'accuracy',
            'precision': 'precision_weighted',
            'recall': 'recall_weighted',
            'f1': 'f1_weighted'
        }

        cv = KFold(n_splits=10, shuffle=True, random_state=42)
        cv_results = cross_validate(
            self.pipeline, X_train, y_train,
            cv=cv, scoring=scoring, return_train_score=False, return_estimator=True
        )

        fold_results = {}
        roc_data = {}
        f1_threshold_data = {}
        X_test_folds = {}
        y_test_folds = {}

        for fold, (train_idx, test_idx) in enumerate(cv.split(X_train, y_train)):
            X_test_fold = X_train.iloc[test_idx] if isinstance(X_train, pd.DataFrame) else X_train[test_idx]
            y_test_fold = y_train.iloc[test_idx] if isinstance(y_train, pd.Series) else y_train[test_idx]

            X_test_folds[f'fold_{fold}'] = X_test_fold
            y_test_folds[f'fold_{fold}'] = y_test_fold

            estimator = cv_results['estimator'][fold]
            y_prob = estimator.predict_proba(X_test_fold)[:, 1]

            fpr, tpr, roc_thresholds = roc_curve(y_test_fold, y_prob)
            roc_data[f'fold_{fold}'] = {'fpr': fpr, 'tpr': tpr, 'thresholds': roc_thresholds}

            precision, recall, thresholds = precision_recall_curve(y_test_fold, y_prob)
            f1_scores = 2 * (precision * recall) / (precision + recall + 1e-10)
            optimal_idx = np.argmax(f1_scores)
            f1_threshold_data[f'fold_{fold}'] = {
                'threshold': thresholds[optimal_idx],
                'f1': f1_scores[optimal_idx]
            }

            fold_results[f'fold_{fold}'] = {
                'accuracy': cv_results['test_accuracy'][fold],
                'precision': cv_results['test_precision'][fold],
                'recall': cv_results['test_recall'][fold],
                'f1': cv_results['test_f1'][fold]
            }

        metrics_df = pd.DataFrame(fold_results).T
        metrics_df.index.name = 'fold'

        # Store internally
        self.cv_results_ = {
            'metrics': metrics_df,
            'roc_data': roc_data,
            'f1_threshold_data': pd.DataFrame(f1_threshold_data).T,
            'X_test_folds': X_test_folds,
            'y_test_folds': y_test_folds
        }

    @staticmethod
    def summarize_cv_results(results_dict, metrics=('accuracy', 'precision', 'recall', 'f1', 'r2', 'rmse', 'mae')):
        """
        Summarize and compare average CV metrics across multiple models.

        Args:
            results_dict (dict): Dictionary where each key is a model name, and each value
                                is the pipeline.cv_results_ dict (with 'metrics' DataFrame).
            metrics (tuple): Metrics to extract and compare. Only those found in each DataFrame will be included.

        Returns:
            pd.DataFrame: A summary table comparing average metrics across models.
        """
        summary = {}

        for model_name, cv_data in results_dict.items():
            model_metrics = cv_data['metrics']
            available_metrics = [m for m in metrics if m in model_metrics.columns]
            summary[model_name] = model_metrics[available_metrics].mean()

        summary_df = pd.DataFrame(summary).T
        summary_df.index.name = 'Model'
        return summary_df

def get_diagnostics(self):
        return ModelDiagnostics(self.pipeline)