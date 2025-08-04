"""
feature_diagnostics.py

Provides utilities for analyzing features prior to modeling.
This includes checks for multicollinearity (VIF), low variance,
redundant features, and basic statistical diagnostics.

Designed for use within the Glazzbocks framework.

Author: Joshua Thompson
"""

import pandas as pd
import numpy as np
from statsmodels.stats.outliers_influence import variance_inflation_factor
from statsmodels.tools.tools import add_constant
from .preprocessing import impute_numeric

def compute_vif(X, include_constant=False, impute_strategy="median", threshold=5.0, verbose=True):
    """
    Computes Variance Inflation Factor (VIF) for numeric features.

    Automatically imputes missing values using the given strategy.

    Args:
        X (pd.DataFrame): Numeric DataFrame with possible missing values.
        include_constant (bool): Whether to include intercept in VIF.
        impute_strategy (str): Strategy for imputing missing values. 
                               Options: "mean", "median", "most_frequent", etc.
        threshold (float): Threshold above which to flag VIF as high.
        verbose (bool): Whether to print warnings for high-VIF features.

    Returns:
        pd.DataFrame: Features and their VIF scores.
    """
    X_imputed = impute_numeric(X, strategy=impute_strategy)

    if include_constant:
        X_imputed = add_constant(X_imputed)

    vif_data = pd.DataFrame()
    vif_data["Feature"] = X_imputed.columns
    vif_data["VIF"] = [
        variance_inflation_factor(X_imputed.values, i)
        for i in range(X_imputed.shape[1])
    ]

    if not include_constant:
        vif_data = vif_data[vif_data["Feature"] != "const"]

    if verbose:
        high_vif = vif_data[vif_data["VIF"] > threshold].sort_values("VIF", ascending=False)
        if not high_vif.empty:
            print("\n⚠️  High multicollinearity detected (VIF > {}):".format(threshold))
            print(high_vif.head(5).to_string(index=False))

    return vif_data

def low_variance_features(X, threshold=0.01):
    """
    Identifies features with variance below a given threshold.

    Args:
        X (pd.DataFrame): Input features.
        threshold (float): Variance threshold.

    Returns:
        List[str]: Features with low variance.
    """
    return X.var()[X.var() < threshold].index.tolist()

def correlation_matrix(X, threshold=0.9):
    """
    Computes a correlation matrix and returns highly correlated feature pairs.

    Args:
        X (pd.DataFrame): Numeric DataFrame.
        threshold (float): Correlation threshold to flag.

    Returns:
        List[Tuple[str, str, float]]: Highly correlated feature pairs.
    """
    corr_matrix = X.corr().abs()
    upper = corr_matrix.where(np.triu(np.ones(corr_matrix.shape), k=1).astype(bool))
    return [(col1, col2, corr)
            for col1 in upper.columns
            for col2, corr in upper[col1].items()
            if pd.notnull(corr) and corr > threshold]

def describe_features(X):
    """
    Provides summary statistics and data types for features.

    Args:
        X (pd.DataFrame): Input DataFrame.

    Returns:
        pd.DataFrame: Combined describe() output with dtypes.
    """
    summary = X.describe(include="all").T
    summary["dtype"] = X.dtypes
    return summary

def run_feature_diagnostics(X, model_name=None, is_linear=False, vif_threshold=5.0, verbose=True):
    """
    Run feature diagnostics prior to modeling.

    Args:
        X (pd.DataFrame): Input feature DataFrame.
        model_name (str, optional): Name of the model.
        is_linear (bool): Whether the model is linear.
        vif_threshold (float): Threshold to trigger multicollinearity warning.
        verbose (bool): If True, prints VIF report.

    Returns:
        None
    """
    if is_linear:
        if verbose:
            model_info = f" for model '{model_name}'" if model_name else ""
            print(f"\n🔍 Running VIF check{model_info} (threshold = {vif_threshold})...")
        compute_vif(X, threshold=vif_threshold, verbose=verbose)
