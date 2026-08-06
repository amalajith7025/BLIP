from __future__ import annotations

from collections import OrderedDict

from .schemas import AnalysisCapability, BusinessPurpose, CapabilityStage, SemanticPrimitive


class AnalysisCapabilityRegistry:
    """
    Deterministic metadata registry for all available analytical capabilities.
    """

    def __init__(self):
        self._capabilities: OrderedDict[str, AnalysisCapability] = OrderedDict()

    def register(self, capability: AnalysisCapability) -> None:
        self._validate_capability(capability)
        self._capabilities[capability.capability_id] = capability

    def register_many(self, capabilities: list[AnalysisCapability]) -> None:
        for capability in capabilities:
            self.register(capability)

    def discover_available(self) -> list[AnalysisCapability]:
        return list(self._capabilities.values())

    def get(self, capability_id: str) -> AnalysisCapability | None:
        return self._capabilities.get(capability_id)

    def filter_by_stage(self, stage: CapabilityStage) -> list[AnalysisCapability]:
        return [
            capability
            for capability in self._capabilities.values()
            if capability.investigation_stage == stage
        ]

    def filter_by_supported_primitive(
        self,
        primitive: SemanticPrimitive,
    ) -> list[AnalysisCapability]:
        return [
            capability
            for capability in self._capabilities.values()
            if primitive in capability.supported_semantic_primitives
        ]

    def filter_by_business_purpose(
        self,
        business_purpose: BusinessPurpose,
    ) -> list[AnalysisCapability]:
        return [
            capability
            for capability in self._capabilities.values()
            if capability.business_purpose == business_purpose
        ]

    @staticmethod
    def _validate_capability(capability: AnalysisCapability) -> None:
        if not capability.capability_id.strip():
            raise ValueError("capability_id is required")

        if not capability.display_name.strip():
            raise ValueError("display_name is required")

        if not capability.plugin_key.strip():
            raise ValueError("plugin_key is required")