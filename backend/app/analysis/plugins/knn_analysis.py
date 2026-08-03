"""K-Nearest Neighbors analysis plugin.

Builds a K-Nearest Neighbors classifier for binary classification.
"""
from __future__ import annotations

from typing import Any, Dict, List

import numpy as np
import pandas as pd
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import LabelEncoder

from ..interfaces import AnalysisPlugin
from ..schemas import DatasetProfile


class KNNAnalysis(AnalysisPlugin):
    """Plugin that performs K-Nearest Neighbors classification."""

    name = "K-Nearest Neighbors"
    description = (
        "Builds a K-Nearest Neighbors classifier for binary classification."
    )

    def validate(self, profile: DatasetProfile) -> bool:
        """Return True when the dataset structure is valid for KNN classification."""
        numeric_columns = [cp for cp in profile.column_profiles if cp.can_average]
        binary_categorical_columns = [
            cp
            for cp in profile.column_profiles
            if cp.categorical and cp.unique_values == 2
        ]

        return bool(numeric_columns) and len(binary_categorical_columns) == 1

    def execute(self, dataset: pd.DataFrame) -> Dict[str, Any]:
        """Execute K-Nearest Neighbors classification on the dataset."""
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
            model = KNeighborsClassifier(n_neighbors=5)
            model.fit(complete_data[predictor_columns].values, encoded_target)
        except Exception:
            return results

        results = {
            "samples_used": int(complete_data.shape[0]),
            "predictors": predictor_columns,
            "target": target_column,
            "classes": encoder.classes_.tolist(),
            "accuracy": float(model.score(complete_data[predictor_columns].values, encoded_target)),
            "neighbors": int(model.n_neighbors),
        }

        return results

    def explain(self, results: Dict[str, Any]) -> Dict[str, str]:
        """Return standardized explanations for KNN output keys."""
        return {
            "samples_used": "The number of complete observations used to train the KNN model.",
            "predictors": "The numeric predictor variables included in the KNN model.",
            "target": "The binary categorical target variable used for prediction.",
            "classes": "The encoded classes for the target variable.",
            "accuracy": "The classification accuracy on the training data.",
            "neighbors": "The number of nearest neighbors used by the KNN model.",
        }

    def observations(self, results: Dict[str, Any]) -> Dict[str, List[str]]:
        """Generate objective observations from KNN results."""
        if not results:
            return {"": ["Very small dataset used."]}

        observations: List[str] = []
        accuracy = results.get("accuracy", 0.0)
        neighbors = results.get("neighbors", 0)

        if accuracy >= 0.8:
            observations.append("High classification accuracy observed.")
        else:
            observations.append("Low classification accuracy observed.")

        if neighbors == 1:
            observations.append("Model uses one nearest neighbor.")
        else:
            observations.append("Model uses multiple nearest neighbors.")

        if results.get("samples_used", 0) < 5:
            observations.append("Very small dataset used.")

        return {"knn": observations}
