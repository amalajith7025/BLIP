from app.analysis.capabilities.registry import AnalysisCapabilityRegistry
from app.analysis.capabilities.schemas import AnalysisCapability

from .catalog import default_business_goals
from .registry import BusinessGoalRegistry


def build_default_goal_registry() -> BusinessGoalRegistry:
    """
    Build the default business-goal ontology registry.
    """

    registry = BusinessGoalRegistry()
    registry.register_many(default_business_goals())
    return registry


def build_goal_capability_blueprint(
    goal_id: str,
    goal_registry: BusinessGoalRegistry,
    capability_registry: AnalysisCapabilityRegistry,
) -> dict[str, list[AnalysisCapability]]:
    """
    Resolve required and optional capability metadata for a business goal.

    This is planner-facing contract preparation, not planner execution logic.
    """

    required_ids = goal_registry.get_required_capabilities(goal_id)
    optional_ids = goal_registry.get_optional_capabilities(goal_id)

    required_capabilities = [
        capability
        for capability in (capability_registry.get(capability_id) for capability_id in required_ids)
        if capability is not None
    ]
    optional_capabilities = [
        capability
        for capability in (capability_registry.get(capability_id) for capability_id in optional_ids)
        if capability is not None
    ]

    return {
        "required": required_capabilities,
        "optional": optional_capabilities,
    }