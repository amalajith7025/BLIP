from .catalog import default_analysis_capabilities
from .registry import AnalysisCapabilityRegistry


def build_default_capability_registry() -> AnalysisCapabilityRegistry:
    """
    Build the default metadata registry with built-in capability descriptors.
    """

    registry = AnalysisCapabilityRegistry()
    registry.register_many(default_analysis_capabilities())
    return registry