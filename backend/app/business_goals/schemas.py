from dataclasses import dataclass, field

from app.analysis.capabilities.schemas import BusinessPurpose, SemanticPrimitive
from app.investigation_framework.schemas import InvestigationStageName


@dataclass(frozen=True)
class BusinessGoal:
    goal_id: str
    name: str
    description: str
    business_purpose: BusinessPurpose
    common_business_questions: list[str] = field(default_factory=list)
    applicable_investigation_stages: list[InvestigationStageName] = field(default_factory=list)
    required_analytical_capabilities: list[str] = field(default_factory=list)
    optional_analytical_capabilities: list[str] = field(default_factory=list)
    supported_semantic_primitives: list[SemanticPrimitive] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    version: str = "1.0.0"