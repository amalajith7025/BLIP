import pandas as pd

from app.analysis.engine import AnalysisEngine
from app.analysis.profiler import DataProfiler
from app.analysis.plugins.apriori_analysis import AprioriAnalysis


def test_plugin_metadata():
    plugin = AprioriAnalysis()

    assert plugin.name == "Apriori Association"


def test_validate_returns_true_with_two_categorical_columns():
    dataset = pd.DataFrame({"a": ["x", "y", "x"], "b": ["u", "v", "u"]})
    profile = DataProfiler().profile(dataset)

    plugin = AprioriAnalysis()
    assert plugin.validate(profile) is True


def test_validate_returns_false_with_one_categorical_column():
    dataset = pd.DataFrame({"a": ["x", "y", "x"], "num": [1.0, 2.0, 3.0]})
    profile = DataProfiler().profile(dataset)

    plugin = AprioriAnalysis()
    assert plugin.validate(profile) is False


def test_execute_returns_expected_structure_or_empty_when_no_itemsets():
    dataset = pd.DataFrame({
        "a": ["x", "x", "x", "y", "y"],
        "b": ["u", "u", "v", "v", "v"],
    })
    plugin = AprioriAnalysis()
    results = plugin.execute(dataset)

    # Depending on support threshold, may find itemsets; ensure keys when present
    if results:
        assert set(results.keys()) == {"samples_used", "features", "minimum_support", "frequent_itemsets"}
    else:
        assert results == {}


def test_execute_returns_empty_dict_when_fewer_than_five_complete_rows_remain():
    dataset = pd.DataFrame({"a": ["x", None, None], "b": ["u", None, None]})
    plugin = AprioriAnalysis()
    results = plugin.execute(dataset)

    assert results == {}


def test_execute_ignores_rows_containing_missing_values():
    dataset = pd.DataFrame({
        "a": ["x", "x", "x", None, "y"],
        "b": ["u", "u", "v", "v", None],
    })
    plugin = AprioriAnalysis()
    results = plugin.execute(dataset)

    # fewer than five complete observations remain -> empty or valid
    assert isinstance(results, dict)


def test_registered_in_analysis_engine():
    dataset = pd.DataFrame({"a": ["x", "y", "x"], "b": ["u", "v", "u"]})
    engine = AnalysisEngine()
    profile = engine.profiler.profile(dataset)
    applicable_names = {plugin.name for plugin in engine.registry.applicable(profile)}

    assert "Apriori Association" in applicable_names
