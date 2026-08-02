from typing import Dict

import pandas as pd

from .profiler import DataProfiler
from .registry import AnalysisRegistry
from .plugins.descriptive_statistics import DescriptiveStatistics
from .plugins.frequency_distribution import FrequencyDistribution


class AnalysisEngine:
    """
    Orchestrates the complete scientific analysis pipeline.
    """

    def __init__(self):
        self.profiler = DataProfiler()
        self.registry = AnalysisRegistry()
        # Register built-in analysis plugins explicitly so they
        # are available to the engine at runtime.
        self.registry.register(DescriptiveStatistics())
        self.registry.register(FrequencyDistribution())

    def analyze(
        self,
        dataset: pd.DataFrame,
        dataset_name: str = "Dataset",
    ) -> Dict:

        profile = self.profiler.profile(
            dataset,
            name=dataset_name,
        )

        plugins = self.registry.applicable(profile)

        analyses = []

        for plugin in plugins:

            results = plugin.execute(dataset)

            analyses.append(
                {
                    "analysis": plugin.name,
                    "results": results,
                    "explanation": plugin.explain(results),
                    "observations": plugin.observations(results),
                }
            )

        return {
            "dataset_profile": profile,
            "analyses": analyses,
        }