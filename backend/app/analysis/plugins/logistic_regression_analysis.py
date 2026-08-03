"""Logistic Regression analysis plugin.

Builds a logistic regression model for binary classification.
"""
from __future__ import annotations

from typing import Any, Dict, List

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import LabelEncoder

from ..interfaces import AnalysisPlugin
from ..schemas import DatasetProfile


class LogisticRegressionAnalysis(AnalysisPlugin):
    """Plugin that performs logistic regression analysis."""

    name = "Logistic Regression"
    description = (
        "Builds a logistic regression model for binary classification."
    )
    minimum_samples = 5

    def validate(self, profile: DatasetProfile) -> bool:
        """Return True when the dataset is structurally appropriate for logistic regression."""
        numeric_columns = [cp for cp in profile.column_profiles if cp.can_average]
        binary_categorical_columns = [
            cp
            for cp in profile.column_profiles
            if cp.categorical and cp.unique_values == 2
        ]

        return bool(numeric_columns) and len(binary_categorical_columns) == 1

    def execute(self, dataset: pd.DataFrame) -> Dict[str, Any]:
        """Execute logistic regression using the first binary categorical target."""
        results: Dict[str, Any] = {}

        if dataset is None or dataset.empty:
            return results

        numeric_columns = dataset.select_dtypes(include=[np.number]).columns.tolist()
        categorical_columns = [
            column
            for column in dataset.columns
            if not pd.api.types.is_numeric_dtype(dataset[column])
        ]
        binary_targets = [
            column
            for column in categorical_columns
            if dataset[column].dropna().nunique() == 2
        ]

        if not numeric_columns or not binary_targets:
            return results

        target_column = binary_targets[0]
        feature_columns = numeric_columns

        complete_data = dataset[feature_columns + [target_column]].dropna()
        if complete_data.shape[0] < 2:
            return results

        target_values = complete_data[target_column]
        if target_values.nunique() < 2:
            return results

        encoder = LabelEncoder()
        encoded_target = encoder.fit_transform(target_values)

        try:
            model = LogisticRegression(max_iter=1000, random_state=42)
            model.fit(complete_data[feature_columns].values, encoded_target)
        except Exception:
            return results

        coefficients = {
            feature: float(value)
            for feature, value in zip(feature_columns, model.coef_[0])
        }

        results = {
            "samples_used": int(complete_data.shape[0]),
            "features_used": feature_columns,
            "target": target_column,
            "classes": encoder.classes_.tolist(),
            "coefficients": coefficients,
            "intercept": float(model.intercept_[0]),
            "accuracy": float(model.score(complete_data[feature_columns].values, encoded_target)),
            "iterations": int(model.n_iter_[0]),
            "converged": bool(model.n_iter_[0] < model.max_iter),
        }

        return results

    def explain(self, results: Dict[str, Any]) -> Dict[str, str]:
        """Return standardized explanations for logistic regression output keys."""
        return {
            "samples_used": "The number of complete observations used to train the logistic regression model.",
            "features_used": "The numeric predictor variables included in the logistic regression model.",
            "target": "The binary categorical target variable used for prediction.",
            "classes": "The encoded classes for the target variable.",
            "coefficients": "The learned weights for each predictor variable.",
            "intercept": "The model intercept term.",
            "accuracy": "The classification accuracy on the training data.",
            "iterations": "The number of iterations the solver required to fit the model.",
            "converged": "Whether the logistic regression solver converged successfully.",
        }

    def observations(self, results: Dict[str, Any]) -> Dict[str, List[str]]:
        """Generate objective observations from logistic regression results."""
        if not results:
            return {"": ["Very small dataset used."]}

        observations: List[str] = []
        accuracy = results.get("accuracy", 0.0)
        feature_count = len(results.get("features_used", []))
        converged = results.get("converged", False)

        if converged:
            observations.append("Model converged successfully.")
        if accuracy >= 0.8:
            observations.append("High classification accuracy observed.")
        elif accuracy < 0.8:
            observations.append("Low classification accuracy observed.")
        if feature_count > 1:
            observations.append("Multiple predictor variables were included.")
        if results.get("samples_used", 0) < 5:
            observations.append("Very small dataset used.")

        return {"logistic_regression": observations}
