"""Random Forest analysis plugin.

Builds a random forest classifier for binary classification.
"""
from __future__ import annotations

from typing import Any, Dict, List

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder

from ..interfaces import AnalysisPlugin
from ..schemas import DatasetProfile


class RandomForestAnalysis(AnalysisPlugin):
    """Plugin that performs random forest classification."""

    name = "Random Forest"
    description = (
        "Builds a random forest classifier for binary classification."
    )

    def validate(self, profile: DatasetProfile) -> bool:
        """Return True when the dataset structure is valid for random forest classification."""
        numeric_columns = [cp for cp in profile.column_profiles if cp.can_average]
        binary_categorical_columns = [
            cp
            for cp in profile.column_profiles
            if cp.categorical and cp.unique_values == 2
        ]

        return bool(numeric_columns) and len(binary_categorical_columns) == 1

    def execute(self, dataset: pd.DataFrame) -> Dict[str, Any]:
        """Execute random forest classification on the dataset."""
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
            model = RandomForestClassifier(random_state=42)
            model.fit(complete_data[predictor_columns].values, encoded_target)
        except Exception:
            return results

        feature_importance = {
            feature: float(value)
            for feature, value in zip(predictor_columns, model.feature_importances_)
        }

        results = {
            "samples_used": int(complete_data.shape[0]),
            "predictors": predictor_columns,
            "target": target_column,
            "classes": encoder.classes_.tolist(),
            "accuracy": float(model.score(complete_data[predictor_columns].values, encoded_target)),
            "feature_importance": feature_importance,
            "n_estimators": int(model.n_estimators),
        }

        return results

    def explain(self, results: Dict[str, Any]) -> Dict[str, str]:
        """Return standardized explanations for random forest output keys."""
        return {
            "samples_used": "The number of complete observations used to train the random forest model.",
            "predictors": "The numeric predictor variables included in the random forest model.",
            "target": "The binary categorical target variable used for prediction.",
            "classes": "The encoded classes for the target variable.",
            "accuracy": "The classification accuracy on the training data.",
            "feature_importance": "The relative importance of each predictor feature for the random forest model.",
            "n_estimators": "The number of decision trees used by the random forest model.",
        }

    def observations(self, results: Dict[str, Any]) -> Dict[str, List[str]]:
        """Generate objective observations from random forest results."""
        if not results:
            return {"": ["Very small dataset used."]}

        observations: List[str] = []
        accuracy = results.get("accuracy", 0.0)
        feature_importance = results.get("feature_importance", {})

        if accuracy >= 0.8:
            observations.append("High classification accuracy observed.")
        else:
            observations.append("Low classification accuracy observed.")

        importance_values = list(feature_importance.values())
        if importance_values:
            max_importance = max(importance_values)
            if max_importance >= 0.7:
                observations.append("One predictor contributes most of the importance.")
            elif max_importance <= 0.5:
                observations.append("Feature importance is relatively balanced.")

        if results.get("samples_used", 0) < 5:
            observations.append("Very small dataset used.")

        return {"random_forest": observations}
