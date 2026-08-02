from typing import Any

import pandas as pd

from .schemas import ColumnProfile, DatasetProfile


class DataProfiler:
    """
    Profiles a dataset and generates metadata
    required by the Scientific Analysis Engine.
    """

    def profile(self, dataset: pd.DataFrame, name: str = "Dataset") -> DatasetProfile:
        column_profiles = []

        for column in dataset.columns:
            series = dataset[column]

            profile = ColumnProfile(
                name=column,
                data_type=str(series.dtype),
                nullable=series.isnull().any(),
                missing_values=int(series.isnull().sum()),
                unique_values=int(series.nunique()),
                sample_values=series.dropna().unique()[:5].tolist(),
            )

            self._detect_characteristics(series, profile)

            column_profiles.append(profile)

        return DatasetProfile(
            name=name,
            rows=len(dataset),
            columns=len(dataset.columns),
            column_profiles=column_profiles,
        )

    def _detect_characteristics(
        self,
        series: pd.Series,
        profile: ColumnProfile,
    ) -> None:

        if pd.api.types.is_numeric_dtype(series):

            profile.can_average = True
            profile.can_correlate = True
            profile.can_count = True

            profile.continuous = True

            profile.recommended_analyses.extend([
                "descriptive_statistics",
                "outlier_detection",
                "correlation",
            ])

        elif pd.api.types.is_bool_dtype(series):

            profile.boolean = True
            profile.can_count = True
            profile.can_group = True

            profile.recommended_analyses.extend([
                "frequency_distribution",
            ])

        elif pd.api.types.is_datetime64_any_dtype(series):

            profile.datetime = True
            profile.can_forecast = True

            profile.recommended_analyses.extend([
                "trend_analysis",
                "forecasting",
            ])

        else:

            profile.categorical = True

            profile.can_group = True
            profile.can_count = True
            profile.can_pareto = True

            profile.recommended_analyses.extend([
                "frequency_distribution",
                "pareto_analysis",
            ])