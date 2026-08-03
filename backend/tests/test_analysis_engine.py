import pandas as pd

from app.analysis.engine import AnalysisEngine
from app.analysis.profiler import DataProfiler
from app.analysis.plugins.random_forest_analysis import RandomForestAnalysis
from app.analysis.plugins.support_vector_machine_analysis import SupportVectorMachineAnalysis
from app.analysis.plugins.naive_bayes_analysis import NaiveBayesAnalysis
from app.analysis.plugins.knn_analysis import KNNAnalysis
from app.analysis.plugins.gradient_boosting_analysis import GradientBoostingAnalysis
from app.analysis.plugins.adaboost_analysis import AdaBoostAnalysis
from app.analysis.plugins.extra_trees_analysis import ExtraTreesAnalysis
from app.analysis.plugins.linear_discriminant_analysis import LinearDiscriminantAnalysis


def test_profiler_generates_dataset_profile():
    dataset = pd.DataFrame({"count": [1, 2], "label": ["a", "b"]})
    engine = AnalysisEngine()
    profile = engine.profiler.profile(dataset, name="TestDataset")

    assert profile.name == "TestDataset"
    assert profile.rows == 2
    assert profile.columns == 2
    assert len(profile.column_profiles) == 2
    assert profile.column_profiles[0].name == "count"
    assert profile.column_profiles[1].name == "label"


def test_plugin_selection_includes_all_applicable_plugins():
    dataset = pd.DataFrame({"value": [1, 2, 3], "category": ["a", "b", "a"]})
    engine = AnalysisEngine()
    profile = engine.profiler.profile(dataset)

    applicable_names = {plugin.name for plugin in engine.registry.applicable(profile)}

    expected_names = {
        "Descriptive Statistics",
        "Frequency Distribution",
        "Pareto Analysis",
        "Outlier Detection",
        "T-Test Analysis",
        "Normality Analysis",
        "Kruskal-Wallis Analysis",
        "Decision Tree",
    }

    if RandomForestAnalysis().validate(profile):
        expected_names.add("Random Forest")
    if SupportVectorMachineAnalysis().validate(profile):
        expected_names.add("Support Vector Machine")
    if NaiveBayesAnalysis().validate(profile):
        expected_names.add("Naive Bayes")
    if KNNAnalysis().validate(profile):
        expected_names.add("K-Nearest Neighbors")
    if GradientBoostingAnalysis().validate(profile):
        expected_names.add("Gradient Boosting")
    if AdaBoostAnalysis().validate(profile):
        expected_names.add("AdaBoost")
    if ExtraTreesAnalysis().validate(profile):
        expected_names.add("Extra Trees")
    if LinearDiscriminantAnalysis().validate(profile):
        expected_names.add("Linear Discriminant Analysis")

    assert applicable_names == expected_names


def test_analyze_executes_multiple_plugins_for_categorical_dataset():
    dataset = pd.DataFrame({"category": ["a", "a", "b", None]})
    engine = AnalysisEngine()
    result = engine.analyze(dataset, dataset_name="MyDataset")

    assert result["dataset_profile"].name == "MyDataset"
    assert result["dataset_profile"].rows == 4
    assert result["dataset_profile"].columns == 1

    analyses = result["analyses"]
    assert isinstance(analyses, list)
    assert len(analyses) == 2

    names = {analysis["analysis"] for analysis in analyses}
    assert names == {"Frequency Distribution", "Pareto Analysis"}

    for analysis in analyses:
        assert isinstance(analysis["results"], dict)
        assert isinstance(analysis["explanation"], dict)
        assert isinstance(analysis["observations"], dict)


def test_analyze_response_format_contains_expected_fields():
    dataset = pd.DataFrame({"category": ["x", "x", "y"]})
    engine = AnalysisEngine()
    result = engine.analyze(dataset)

    assert "dataset_profile" in result
    assert "analyses" in result
    assert isinstance(result["analyses"], list)
    assert all(
        set(item.keys()) == {"analysis", "results", "explanation", "observations"}
        for item in result["analyses"]
    )
