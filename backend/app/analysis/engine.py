from typing import Dict

import pandas as pd

from .profiler import DataProfiler
from .registry import AnalysisRegistry

from .plugins.descriptive_statistics import DescriptiveStatistics
from .plugins.frequency_distribution import FrequencyDistribution
from .plugins.pareto_analysis import ParetoAnalysis
from .plugins.correlation_analysis import CorrelationAnalysis
from .plugins.regression_analysis import RegressionAnalysis
from .plugins.outlier_detection import OutlierDetection
from .plugins.ttest_analysis import TTestAnalysis
from .plugins.chi_square_analysis import ChiSquareAnalysis
from .plugins.anova_analysis import AnovaAnalysis
from .plugins.normality_analysis import NormalityAnalysis
from .plugins.kruskal_wallis_analysis import KruskalWallisAnalysis
from .plugins.pca_analysis import PCAAnalysis
from .plugins.kmeans_analysis import KMeansAnalysis
from .plugins.hierarchical_clustering_analysis import HierarchicalClusteringAnalysis
from .plugins.dbscan_analysis import DBSCANAnalysis
from .plugins.gaussian_mixture_analysis import GaussianMixtureAnalysis
from .plugins.logistic_regression_analysis import LogisticRegressionAnalysis
from .plugins.decision_tree_analysis import DecisionTreeAnalysis
from .plugins.random_forest_analysis import RandomForestAnalysis
from .plugins.support_vector_machine_analysis import SupportVectorMachineAnalysis
from .plugins.naive_bayes_analysis import NaiveBayesAnalysis
from .plugins.knn_analysis import KNNAnalysis
from .plugins.gradient_boosting_analysis import GradientBoostingAnalysis
from .plugins.adaboost_analysis import AdaBoostAnalysis
from .plugins.extra_trees_analysis import ExtraTreesAnalysis
from .plugins.linear_discriminant_analysis import LinearDiscriminantAnalysis
from .plugins.mean_shift_analysis import MeanShiftAnalysis
from .plugins.spectral_clustering_analysis import SpectralClusteringAnalysis
from .plugins.optics_analysis import OPTICSAnalysis
from .plugins.birch_analysis import BirchAnalysis
from .plugins.quadratic_discriminant_analysis import QuadraticDiscriminantAnalysis


class AnalysisEngine:
    """
    Orchestrates the complete scientific analysis pipeline.
    """

    def __init__(self):
        self.profiler = DataProfiler()
        self.registry = AnalysisRegistry()

        # Register built-in analysis plugins explicitly.
        self.registry.register(DescriptiveStatistics())
        self.registry.register(FrequencyDistribution())
        self.registry.register(ParetoAnalysis())
        self.registry.register(CorrelationAnalysis())
        self.registry.register(RegressionAnalysis())
        self.registry.register(OutlierDetection())
        self.registry.register(TTestAnalysis())
        self.registry.register(ChiSquareAnalysis())
        self.registry.register(AnovaAnalysis())
        self.registry.register(NormalityAnalysis())
        self.registry.register(KruskalWallisAnalysis())
        self.registry.register(PCAAnalysis())
        self.registry.register(KMeansAnalysis())
        self.registry.register(HierarchicalClusteringAnalysis())
        self.registry.register(DBSCANAnalysis())
        self.registry.register(GaussianMixtureAnalysis())
        self.registry.register(LogisticRegressionAnalysis())
        self.registry.register(DecisionTreeAnalysis())
        self.registry.register(RandomForestAnalysis())
        self.registry.register(SupportVectorMachineAnalysis())
        self.registry.register(NaiveBayesAnalysis())
        self.registry.register(KNNAnalysis())
        self.registry.register(GradientBoostingAnalysis())
        self.registry.register(AdaBoostAnalysis())
        self.registry.register(ExtraTreesAnalysis())
        self.registry.register(LinearDiscriminantAnalysis())
        self.registry.register(MeanShiftAnalysis())
        self.registry.register(SpectralClusteringAnalysis())
        self.registry.register(OPTICSAnalysis())
        self.registry.register(BirchAnalysis())
        self.registry.register(QuadraticDiscriminantAnalysis())

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