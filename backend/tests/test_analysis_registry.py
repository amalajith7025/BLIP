import pandas as pd

from app.analysis.registry import AnalysisRegistry
from app.analysis.profiler import DataProfiler
from app.analysis.plugins.descriptive_statistics import DescriptiveStatistics


def test_register_and_get_plugin():
    registry = AnalysisRegistry()
    plugin = DescriptiveStatistics()

    registry.register(plugin)

    assert registry.get(plugin.name) is plugin
    assert registry.all() == [plugin]


def test_applicable_returns_matching_plugins():
    dataset = pd.DataFrame({"value": [1, 2, 3]})
    profile = DataProfiler().profile(dataset)
    registry = AnalysisRegistry()
    registry.register(DescriptiveStatistics())

    applicable = registry.applicable(profile)

    assert len(applicable) == 1
    assert applicable[0].name == "Descriptive Statistics"


def test_empty_registry_returns_empty_list():
    registry = AnalysisRegistry()
    profile = DataProfiler().profile(pd.DataFrame({"value": [1, 2]}))

    assert registry.applicable(profile) == []


def test_duplicate_registrations_replace_existing_plugin():
    registry = AnalysisRegistry()
    first_plugin = DescriptiveStatistics()
    second_plugin = DescriptiveStatistics()

    registry.register(first_plugin)
    registry.register(second_plugin)

    assert registry.get(first_plugin.name) is second_plugin
    assert len(registry.all()) == 1
