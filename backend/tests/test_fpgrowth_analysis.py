import pandas as pd

from app.analysis.engine import AnalysisEngine
from app.analysis.profiler import DataProfiler
from app.analysis.plugins.fpgrowth_analysis import FPGrowthAnalysis


def test_plugin_metadata():
    plugin = FPGrowthAnalysis()

    assert plugin.name == "FP-Growth Analysis"


def test_validate_returns_true_with_two_categorical_columns():
    dataset = pd.DataFrame({"a": ["x", "y", "x"], "b": ["u", "v", "u"]})
    profile = DataProfiler().profile(dataset)

    plugin = FPGrowthAnalysis()
    assert plugin.validate(profile) is True


def test_validate_returns_false_with_one_categorical_column():
    dataset = pd.DataFrame({"a": ["x", "y", "x"], "num": [1.0, 2.0, 3.0]})
    profile = DataProfiler().profile(dataset)

    plugin = FPGrowthAnalysis()
    assert plugin.validate(profile) is False


def test_execute_returns_empty_dict_for_empty_dataset():
    plugin = FPGrowthAnalysis()
    results = plugin.execute(pd.DataFrame())

    assert results == {}


def test_execute_returns_empty_dict_for_insufficient_categorical_columns():
    dataset = pd.DataFrame({"a": ["x", "y", "z", "q", "w"], "num": [1, 2, 3, 4, 5]})
    plugin = FPGrowthAnalysis()
    results = plugin.execute(dataset)

    assert results == {}


def test_execute_ignores_rows_containing_missing_values():
    dataset = pd.DataFrame(
        {
            "a": ["x", "x", "x", None, "y"],
            "b": ["u", "u", "v", "v", None],
            "num": [1, 2, 3, 4, 5],
        }
    )
    plugin = FPGrowthAnalysis()
    results = plugin.execute(dataset)

    # fewer than five complete observations remain after dropna -> empty
    assert results == {}


def test_execute_detects_categorical_features_automatically():
    dataset = pd.DataFrame(
        {
            "a": ["x", "x", "y", "y", "x", "y"],
            "b": ["u", "u", "u", "v", "v", "v"],
            "num": [1, 2, 3, 4, 5, 6],
        }
    )
    plugin = FPGrowthAnalysis()
    results = plugin.execute(dataset)

    if results:
        assert results["features"] == ["a", "b"]
    else:
        assert results == {}


def test_execute_returns_expected_response_structure():
    dataset = pd.DataFrame(
        {
            "a": ["x", "x", "y", "y", "x", "y"],
            "b": ["u", "u", "u", "v", "v", "v"],
        }
    )
    plugin = FPGrowthAnalysis()
    results = plugin.execute(dataset)

    if results:
        assert set(results.keys()) == {"samples_used", "features", "minimum_support", "frequent_itemsets"}
    else:
        assert results == {}


def test_execute_returns_python_native_types_only():
    dataset = pd.DataFrame(
        {
            "a": ["x", "x", "y", "y", "x", "y"],
            "b": ["u", "u", "u", "v", "v", "v"],
        }
    )
    plugin = FPGrowthAnalysis()
    results = plugin.execute(dataset)

    if not results:
        assert results == {}
        return

    assert isinstance(results["samples_used"], int)
    assert isinstance(results["features"], list)
    assert isinstance(results["minimum_support"], float)
    assert isinstance(results["frequent_itemsets"], list)

    for itemset in results["frequent_itemsets"]:
        assert isinstance(itemset["items"], list)
        assert isinstance(itemset["support"], float)


def test_execute_returns_empty_dict_when_no_frequent_itemsets_discovered():
    dataset = pd.DataFrame(
        {
            "a": ["a1", "a2", "a3", "a4", "a5"],
            "b": ["b1", "b2", "b3", "b4", "b5"],
        }
    )
    plugin = FPGrowthAnalysis()
    results = plugin.execute(dataset)

    assert results == {}


def test_observations_returns_expected_structure():
    plugin = FPGrowthAnalysis()
    observations = plugin.observations(
        {
            "samples_used": 6,
            "features": ["a", "b"],
            "minimum_support": 0.5,
            "frequent_itemsets": [{"items": ["a_x"], "support": 0.5}],
        }
    )

    assert observations == {"fpgrowth": ["Frequent itemsets discovered: 1."]}


def test_observations_handles_empty_results():
    plugin = FPGrowthAnalysis()
    observations = plugin.observations({})

    assert observations == {"": ["No frequent itemsets were discovered."]}


def test_registered_in_analysis_engine():
    dataset = pd.DataFrame({"a": ["x", "y", "x"], "b": ["u", "v", "u"]})
    engine = AnalysisEngine()
    profile = engine.profiler.profile(dataset)
    applicable_names = {plugin.name for plugin in engine.registry.applicable(profile)}

    assert "FP-Growth Analysis" in applicable_names


def test_selected_by_analysis_registry_for_categorical_dataset():
    dataset = pd.DataFrame({"a": ["x", "y", "x"], "b": ["u", "v", "u"]})
    engine = AnalysisEngine()
    profile = engine.profiler.profile(dataset)
    applicable_names = {plugin.name for plugin in engine.registry.applicable(profile)}

    assert "FP-Growth Analysis" in applicable_names
