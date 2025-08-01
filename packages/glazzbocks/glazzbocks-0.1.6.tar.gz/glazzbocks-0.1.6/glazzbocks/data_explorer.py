import pandas as pd
import numpy as np

from statsmodels.tools.tools import add_constant
from statsmodels.stats.outliers_influence import variance_inflation_factor
from scipy.stats import normaltest, entropy
from sklearn.impute import SimpleImputer

import matplotlib.pyplot as plt
import seaborn as sns
import missingno as msno

from IPython.display import display


class DataExplorer:
    """
    Enhanced EDA tool with datetime and entropy support for better modeling decisions.
    """

    def __init__(self, df, target_col):
        self.df = df.copy()
        self.target_col = target_col
        self.task_type = 'classification' if self.df[target_col].nunique() <= 10 else 'regression'
        self.datetime_cols = df.select_dtypes(include='datetime').columns.tolist()
        self.extract_datetime_features()

    def extract_datetime_features(self):
        """Expands datetime columns into useful features."""
        for col in self.datetime_cols:
            self.df[f'{col}_year'] = self.df[col].dt.year
            self.df[f'{col}_month'] = self.df[col].dt.month
            self.df[f'{col}_day'] = self.df[col].dt.day
            self.df[f'{col}_weekday'] = self.df[col].dt.weekday
        self.df.drop(columns=self.datetime_cols, inplace=True)

    def summary(self):
        print("Dataset Shape:", self.df.shape)
        print("Data Types:\n", self.df.dtypes)
        print("Missing Values:\n", self.df.isnull().sum().sort_values(ascending=False))
        display(self.df.head())

    def plot_target(self):
        if self.task_type == 'regression':
            sns.histplot(self.df[self.target_col], kde=True)
        else:
            self.df[self.target_col].value_counts().plot(kind='bar')
        plt.title(f"Target Distribution: {self.target_col}")
        plt.show()

    def get_imputed_numeric_df(self):
        X = self.df.drop(columns=[self.target_col], errors='ignore')
        X_numeric = X.select_dtypes(include=np.number)
        imputer = SimpleImputer(strategy='median')
        X_imputed = pd.DataFrame(imputer.fit_transform(X_numeric), columns=X_numeric.columns)
        return X_imputed

    def correlation_heatmap(self, exclude_cols=None):
        data = self.df.drop(columns=exclude_cols, errors='ignore') if exclude_cols else self.df
        corr = data.select_dtypes(include='number').corr()
        sns.heatmap(corr, annot=True, fmt=".3f", cmap='coolwarm', annot_kws={"size": 8})
        plt.title("Correlation Heatmap")
        plt.show()

    def calculate_vif(self):
        X_imputed = self.get_imputed_numeric_df()
        X_imputed = add_constant(X_imputed)
        vif = pd.DataFrame()
        vif["Feature"] = X_imputed.columns
        vif["VIF"] = [variance_inflation_factor(X_imputed.values, i) for i in range(X_imputed.shape[1])]
        return vif[vif["Feature"] != "const"]

    def skewness_summary(self, threshold=1.0):
        X = self.get_imputed_numeric_df()
        skewness = X.skew().sort_values(ascending=False)
        return skewness[abs(skewness) > threshold]

    def test_normality(self, alpha=0.05):
        X = self.get_imputed_numeric_df()
        results = {}
        for col in X.columns:
            try:
                stat, p = normaltest(X[col])
                results[col] = {"statistic": stat, "p_value": p, "normal": p >= alpha}
            except Exception as e:
                results[col] = {"statistic": None, "p_value": None, "normal": None}
        return pd.DataFrame(results).T.sort_values("p_value", na_position='last')

    def detect_outliers(self, z_thresh=3.0):
        X = self.get_imputed_numeric_df()
        z_scores = ((X - X.mean()) / X.std()).abs()
        outliers = (z_scores > z_thresh).sum().sort_values(ascending=False)
        return outliers[outliers > 0]

    def class_balance_summary(self):
        if self.task_type != 'classification':
            print("Only valid for classification tasks.")
            return
        return self.df[self.target_col].value_counts(normalize=True).to_frame("Proportion")

    def class_entropy(self):
        """Compute entropy of the target variable (for classification tasks)."""
        if self.task_type != 'classification':
            print("Only applicable to classification tasks.")
            return
        probs = self.df[self.target_col].value_counts(normalize=True)
        return entropy(probs)

    def plot_missing_matrix(self):
        msno.matrix(self.df)
        plt.show()

    def suggest_modeling_approach(self):
        print("Modeling Hints Based on EDA:")
        if self.task_type == 'regression':
            skewed = self.skewness_summary()
            print(f"- Skewed numeric features: {list(skewed.index)}")
            normality = self.test_normality()
            non_normal = normality[normality['normal'] == False]
            print(f"- Non-normal features: {list(non_normal.index)}")
            print("- Consider log-transforming skewed features for linear models.")
        else:
            imbalance = self.class_balance_summary()
            print("- Class distribution:")
            display(imbalance)
            if imbalance.iloc[0, 0] > 0.8:
                print("Severe class imbalance detected — consider SMOTE or class weighting.")
            print(f"- Entropy of classes: {self.class_entropy():.4f}")

