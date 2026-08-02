from abc import ABC, abstractmethod

import pandas as pd

from .schemas import DatasetProfile


class AnalysisPlugin(ABC):
    """
    Base interface for every scientific analysis module.
    """

    name: str
    description: str

    @abstractmethod
    def validate(self, profile: DatasetProfile) -> bool:
        """
        Determines whether this analysis is applicable
        for the supplied dataset profile.
        """
        pass

    @abstractmethod
    def execute(self, dataset: pd.DataFrame) -> dict:
        """
        Executes the statistical analysis.
        """
        pass

    @abstractmethod
    def explain(self, results: dict) -> dict:
        """
        Converts raw statistical results into
        universal explanations.
        """
        pass

    @abstractmethod
    def observations(self, results: dict) -> list[str]:
        """
        Generates objective observations from
        the statistical output.
        """
        pass