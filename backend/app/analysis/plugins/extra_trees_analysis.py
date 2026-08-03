"""Extra Trees analysis plugin.

Builds an Extra Trees classifier for binary classification.
"""
from __future__ import annotations

from typing import Any, Dict, List

import numpy as np
import pandas as pd
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.preprocessing import LabelEncoder

from ..interfaces import AnalysisPlugin
from ..schemas import DatasetProfile


class ExtraTreesAnalysis(AnalysisPlugin):
    """Plugin that performs Extra Trees classification."""

    name = "Extra Trees"
    description = "Builds an Extra Trees classifier for binary classification."

    def validate(self, profile: DatasetProfile) -> bool:
        """Return True when the dataset structure is valid for Extra Trees classification."""
        numeric_columns = [cp for cp in profile.column_profiles if cp.can_average]
        binary_categorical_columns = [
            cp
            for cp in profile.column_profiles
            if cp.categorical and cp.unique_values == 2
        ]

        return bool(numeric_columns) and len(binary_categorical_columns) == 1

    def execute(self, dataset: pd.DataFrame) -> Dict[str, Any]:
        """Execute Extra Trees classification on the dataset."""
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
            model = ExtraTreesClassifier(random_state=42)
            model.fit(complete_data[predictor_columns].values, encoded_target)
        except Exception:
            return results

        feature_importances = {
            feature: float(value)
            for feature, value in zip(predictor_columns, model.feature_importances_)
        }

        results = {
            "samples_used": int(complete_data.shape[0]),
            "predictors": predictor_columns,
            "target": target_column,
            "classes": encoder.classes_.tolist(),
            "accuracy": float(model.score(complete_data[predictor_columns].values, encoded_target)),
            "feature_importances": feature_importances,
            "estimators": int(model.n_estimators),
        }

        return results

    def explain(self, results: Dict[str, Any]) -> Dict[str, str]:
        """Return standardized explanations for Extra Trees output keys."""
        return {
            "samples_used": "The number of complete observations used to train the Extra Trees model.",
            "predictors": "The numeric predictor variables included in the Extra Trees model.",
            "target": "The binary categorical target variable used for prediction.",
            "classes": "The encoded classes for the target variable.",
            "accuracy": "The classification accuracy on the training data.",
            "feature_importances": "The relative importance of each predictor feature for the Extra Trees model.",
            "estimators": "The number of decision trees used by the Extra Trees model.",
        }

    def observations(self, results: Dict[str, Any]) -> Dict[str, List[str]]:
        """Generate objective observations from Extra Trees results."""
        if not results:
            return {"": ["Very small dataset used."]}

        observations: List[str] = []
        accuracy = results.get("accuracy", 0.0)
        feature_importances = results.get("feature_importances", {})

        if accuracy >= 0.8:
            observations.append("High classification accuracy observed.")
        else:
            observations.append("Low classification accuracy observed.")

        if feature_importances:
            observations.append("Feature importances were computed for predictor variables.")

        if results.get("samples_used", 0) < 5:
            observations.append("Very small dataset used.")

        return {"extra_trees": observations}
