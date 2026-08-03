"""Principal Component Analysis plugin.

Performs PCA on numeric variables.
"""
from __future__ import annotations

from typing import Any, Dict, List

import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

from ..interfaces import AnalysisPlugin
from ..schemas import DatasetProfile


class PCAAnalysis(AnalysisPlugin):
    """Plugin that performs principal component analysis."""

    name = "Principal Component Analysis"
    description = (
        "Performs Principal Component Analysis (PCA) on numeric variables."
    )

    def validate(self, profile: DatasetProfile) -> bool:
        """Return True when the dataset contains at least two numeric columns."""
        numeric_columns = [cp for cp in profile.column_profiles if cp.can_average]
        return len(numeric_columns) >= 2

    def execute(self, dataset: pd.DataFrame) -> Dict[str, Any]:
        """Execute PCA on all numeric columns in the dataset."""
        results: Dict[str, Any] = {}

        if dataset is None or dataset.empty:
            return results

        numeric_columns = dataset.select_dtypes(include=[np.number]).columns.tolist()

        if len(numeric_columns) < 2:
            return results

        numeric_frame = dataset[numeric_columns].dropna()

        if numeric_frame.shape[0] < 2:
            return results

        scaler = StandardScaler()
        scaled_values = scaler.fit_transform(numeric_frame.values)

        pca = PCA()
        pca.fit(scaled_values)

        explained_variance_ratio = [float(x) for x in pca.explained_variance_ratio_]
        cumulative_variance: List[float] = []
        cumulative_sum = 0.0
        for ratio in explained_variance_ratio:
            cumulative_sum += ratio
            cumulative_variance.append(float(cumulative_sum))

        eigenvalues = [float(x) for x in pca.explained_variance_]
        components: List[Dict[str, Any]] = []

        for index, component_loadings in enumerate(pca.components_, start=1):
            loadings = {
                column: float(value)
                for column, value in zip(numeric_columns, component_loadings)
            }
            components.append(
                {
                    "component": f"PC{index}",
                    "loadings": loadings,
                }
            )

        results = {
            "explained_variance_ratio": explained_variance_ratio,
            "cumulative_variance": cumulative_variance,
            "eigenvalues": eigenvalues,
            "components": components,
            "number_of_components": int(pca.n_components_),
            "samples_used": int(numeric_frame.shape[0]),
            "features_used": int(len(numeric_columns)),
        }

        return results

    def explain(self, results: Dict[str, Any]) -> Dict[str, str]:
        """Return standardized explanations for PCA output keys."""
        return {
            "explained_variance_ratio": "The proportion of total variance explained by each principal component.",
            "cumulative_variance": "The cumulative proportion of variance explained by the principal components.",
            "eigenvalues": "The eigenvalues associated with each principal component, indicating explained variance.",
            "components": "The principal components and their feature loadings.",
            "number_of_components": "The number of principal components computed.",
            "samples_used": "The number of rows used for PCA after dropping missing values.",
            "features_used": "The number of numeric features included in PCA.",
        }

    def observations(self, results: Dict[str, Any]) -> Dict[str, List[str]]:
        """Generate objective observations from PCA results."""
        if not results:
            return {"": ["PCA could not be performed."]}

        observations: Dict[str, List[str]] = {}
        explained_variance_ratio = results.get("explained_variance_ratio", [])
        samples_used = results.get("samples_used", 0)

        component_observations: List[str] = []

        if samples_used < 3:
            component_observations.append("Limited observations available for PCA.")

        if explained_variance_ratio:
            if explained_variance_ratio[0] >= 0.7:
                component_observations.append(
                    "The first principal component explains most of the variance."
                )
            elif explained_variance_ratio[0] < 0.4:
                component_observations.append("No dominant principal component is present.")
            else:
                component_observations.append("Variance is distributed across multiple components.")

            if len(explained_variance_ratio) > 1 and explained_variance_ratio[0] >= 0.5:
                component_observations.append("Dimensionality reduction is likely to be effective.")

        observations["pca"] = component_observations
        return observations
