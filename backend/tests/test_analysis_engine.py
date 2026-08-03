import pandas as pd

from app.analysis.engine import AnalysisEngine
from app.analysis.profiler import DataProfiler


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

    assert applicable_names == {
        "Descriptive Statistics",
        "Frequency Distribution",
        "Pareto Analysis",
        "Outlier Detection",
        "T-Test Analysis",
    }


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
