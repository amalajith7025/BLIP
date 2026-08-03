"""Linear Discriminant analysis plugin.

Builds a Linear Discriminant Analysis classifier for binary classification.
"""
from __future__ import annotations

from typing import Any, Dict, List

import numpy as np
import pandas as pd
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis as SklearnLinearDiscriminantAnalysis
from sklearn.preprocessing import LabelEncoder

from ..interfaces import AnalysisPlugin
from ..schemas import DatasetProfile


class LinearDiscriminantAnalysis(AnalysisPlugin):
    """Plugin that performs Linear Discriminant Analysis classification."""

    name = "Linear Discriminant Analysis"
    description = "Builds a Linear Discriminant Analysis classifier for binary classification."

    def validate(self, profile: DatasetProfile) -> bool:
        """Return True when the dataset structure is valid for LDA classification."""
        numeric_columns = [cp for cp in profile.column_profiles if cp.can_average]
        binary_categorical_columns = [
            cp
            for cp in profile.column_profiles
            if cp.categorical and cp.unique_values == 2
        ]

        return bool(numeric_columns) and len(binary_categorical_columns) == 1

    def execute(self, dataset: pd.DataFrame) -> Dict[str, Any]:
        """Execute Linear Discriminant Analysis classification on the dataset."""
        results: Dict[str, Any] = {}

        if dataset is None or dataset.empty:
            return results

        predictor_columns = dataset.select_dtypes(include=[np.number]).columns.tolist()
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

        if not predictor_columns or not binary_targets:
            return results

        target_column = binary_targets[0]
        complete_data = dataset[predictor_columns + [target_column]].dropna()
        if complete_data.shape[0] < 5:
            return results

        target_values = complete_data[target_column]
        if target_values.nunique() < 2:
            return results

        encoder = LabelEncoder()
        encoded_target = encoder.fit_transform(target_values)

        try:
            model = SklearnLinearDiscriminantAnalysis()
            model.fit(complete_data[predictor_columns].values, encoded_target)
        except Exception:
            return results

        coefficients = {
            feature: float(value)
            for feature, value in zip(predictor_columns, model.coef_.flatten())
        }

        explained_variance_ratio = [float(value) for value in model.explained_variance_ratio_]

        results = {
            "samples_used": int(complete_data.shape[0]),
            "predictors": predictor_columns,
            "target": target_column,
            "classes": encoder.classes_.tolist(),
            "accuracy": float(model.score(complete_data[predictor_columns].values, encoded_target)),
            "coefficients": coefficients,
            "explained_variance_ratio": explained_variance_ratio,
        }

        return results

    def explain(self, results: Dict[str, Any]) -> Dict[str, str]:
        """Return standardized explanations for LDA output keys."""
        return {
            "samples_used": "The number of complete observations used to train the LDA model.",
            "predictors": "The numeric predictor variables included in the LDA model.",
            "target": "The binary categorical target variable used for prediction.",
            "classes": "The encoded classes for the target variable.",
            "accuracy": "The classification accuracy on the training data.",
            "coefficients": "The linear coefficients used by the LDA classification model.",
            "explained_variance_ratio": "The explained variance ratio for each linear discriminant component.",
        }

    def observations(self, results: Dict[str, Any]) -> Dict[str, List[str]]:
        """Generate objective observations from LDA results."""
        if not results:
            return {"": ["Very small dataset used."]}

        observations: List[str] = []
        accuracy = results.get("accuracy", 0.0)
        coefficients = results.get("coefficients", {})

        if accuracy >= 0.8:
            observations.append("High classification accuracy observed.")
        else:
            observations.append("Low classification accuracy observed.")

        if coefficients:
            observations.append("Model coefficients were computed for predictor variables.")

        if results.get("samples_used", 0) < 5:
            observations.append("Very small dataset used.")

        return {"linear_discriminant_analysis": observations}
