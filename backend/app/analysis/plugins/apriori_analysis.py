"""Apriori association rule mining analysis plugin.

Uses mlxtend.frequent_patterns.apriori to find frequent itemsets.
"""
from __future__ import annotations

from typing import Any, Dict, List

import numpy as np
import pandas as pd

from ..interfaces import AnalysisPlugin
from ..schemas import DatasetProfile


class AprioriAnalysis(AnalysisPlugin):
    """Plugin that performs Apriori frequent itemset mining."""

    name = "Apriori Association"
    description = "Finds frequent itemsets in categorical data using the Apriori algorithm." 

    def validate(self, profile: DatasetProfile) -> bool:
        categorical_columns = [cp for cp in profile.column_profiles if cp.categorical]
        return len(categorical_columns) >= 2

    def execute(self, dataset: pd.DataFrame) -> Dict[str, Any]:
        results: Dict[str, Any] = {}

        if dataset is None or dataset.empty:
            return results

        categorical_columns = [c for c in dataset.columns if not pd.api.types.is_numeric_dtype(dataset[c])]
        if len(categorical_columns) < 2:
            return results

        df = dataset[categorical_columns].dropna()
        if df.shape[0] < 5:
            return results


        # One-hot encode categorical columns into indicator matrix
        # Use string conversion to avoid dtype issues
        encoded = pd.get_dummies(df.astype(str))

        # sensible default min_support
        min_support = 0.5
        try:
            from mlxtend.frequent_patterns import apriori
        except Exception:
            # mlxtend is optional; return empty results if not installed
            return results

        try:
            itemsets = apriori(encoded, min_support=min_support, use_colnames=True)
        except Exception:
            return results

        if itemsets.empty:
            return results

        frequent = []
        for _, row in itemsets.iterrows():
            items = sorted([str(x) for x in list(row["itemsets"])])
            frequent.append({"items": items, "support": float(row["support"])})

        results = {
            "samples_used": int(df.shape[0]),
            "features": categorical_columns,
            "minimum_support": float(min_support),
            "frequent_itemsets": frequent,
        }

        return results

    def explain(self, results: Dict[str, Any]) -> Dict[str, str]:
        return {
            "samples_used": "The number of observations used after dropping missing values.",
            "features": "Categorical features evaluated for frequent itemsets.",
            "minimum_support": "The minimum support threshold used by Apriori.",
            "frequent_itemsets": "List of discovered frequent itemsets and their support.",
        }

    def observations(self, results: Dict[str, Any]) -> Dict[str, List[str]]:
        if not results:
            return {"": ["Very small dataset used or no frequent itemsets found."]}

        count = len(results.get("frequent_itemsets", []))
        observations: List[str] = []

        if count == 0:
            observations.append("No frequent itemsets were discovered.")
        else:
            observations.append(f"{count} frequent itemsets discovered.")

        return {"apriori": observations}
