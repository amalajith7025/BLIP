import pytest

from app.analysis.capabilities import (
    AnalysisCapability,
    AnalysisCapabilityRegistry,
    BusinessPurpose,
    CapabilityStage,
    ExecutionConstraints,
    MaturityLevel,
    SemanticPrimitive,
    build_default_capability_registry,
)


def test_build_default_capability_registry_discovers_capabilities():
    registry = build_default_capability_registry()
    capabilities = registry.discover_available()

    assert len(capabilities) >= 8
    assert any(capability.capability_id == "cap_descriptive_statistics" for capability in capabilities)


def test_register_and_get_capability_metadata():
    registry = AnalysisCapabilityRegistry()
    capability = AnalysisCapability(
        capability_id="cap_custom_demo",
        display_name="Custom Demo",
        description="Demo metadata capability",
        investigation_stage=CapabilityStage.OBSERVE,
        business_purpose=BusinessPurpose.DESCRIBE,
        required_input_types=["dataset_profile"],
        supported_semantic_primitives=[SemanticPrimitive.NUMERIC],
        expected_outputs=["demo_output"],
        execution_constraints=ExecutionConstraints(minimum_rows=1),
        dependencies=[],
        tags=["demo"],
        maturity_level=MaturityLevel.EXPERIMENTAL,
        version="0.1.0",
        plugin_key="Descriptive Statistics",
    )

    registry.register(capability)

    found = registry.get("cap_custom_demo")
    assert found is not None
    assert found.display_name == "Custom Demo"


def test_filter_by_investigation_stage():
    registry = build_default_capability_registry()

    explain_capabilities = registry.filter_by_stage(CapabilityStage.EXPLAIN)

    assert explain_capabilities
    assert all(capability.investigation_stage == CapabilityStage.EXPLAIN for capability in explain_capabilities)


def test_filter_by_supported_semantic_primitive():
    registry = build_default_capability_registry()

    categorical_capabilities = registry.filter_by_supported_primitive(SemanticPrimitive.CATEGORICAL)

    assert categorical_capabilities
    assert all(
        SemanticPrimitive.CATEGORICAL in capability.supported_semantic_primitives
        for capability in categorical_capabilities
    )


def test_filter_by_business_purpose():
    registry = build_default_capability_registry()

    diagnose_capabilities = registry.filter_by_business_purpose(BusinessPurpose.DIAGNOSE)

    assert diagnose_capabilities
    assert all(
        capability.business_purpose == BusinessPurpose.DIAGNOSE
        for capability in diagnose_capabilities
    )


def test_register_replaces_existing_capability_with_same_id():
    registry = AnalysisCapabilityRegistry()

    first = AnalysisCapability(
        capability_id="cap_replace",
        display_name="First",
        description="first",
        investigation_stage=CapabilityStage.OBSERVE,
        business_purpose=BusinessPurpose.DESCRIBE,
        required_input_types=[],
        supported_semantic_primitives=[SemanticPrimitive.NUMERIC],
        expected_outputs=[],
        execution_constraints=ExecutionConstraints(),
        dependencies=[],
        tags=[],
        maturity_level=MaturityLevel.BETA,
        version="1.0.0",
        plugin_key="Descriptive Statistics",
    )
    second = AnalysisCapability(
        capability_id="cap_replace",
        display_name="Second",
        description="second",
        investigation_stage=CapabilityStage.EXPLAIN,
        business_purpose=BusinessPurpose.DIAGNOSE,
        required_input_types=[],
        supported_semantic_primitives=[SemanticPrimitive.NUMERIC],
        expected_outputs=[],
        execution_constraints=ExecutionConstraints(),
        dependencies=[],
        tags=[],
        maturity_level=MaturityLevel.BETA,
        version="1.1.0",
        plugin_key="Correlation Analysis",
    )

    registry.register(first)
    registry.register(second)

    assert registry.get("cap_replace") == second
    assert len(registry.discover_available()) == 1


def test_register_validates_required_fields():
    registry = AnalysisCapabilityRegistry()

    with pytest.raises(ValueError, match="capability_id"):
        registry.register(
            AnalysisCapability(
                capability_id="",
                display_name="X",
                description="desc",
                investigation_stage=CapabilityStage.OBSERVE,
                business_purpose=BusinessPurpose.DESCRIBE,
                required_input_types=[],
                supported_semantic_primitives=[SemanticPrimitive.NUMERIC],
                expected_outputs=[],
                execution_constraints=ExecutionConstraints(),
                dependencies=[],
                tags=[],
                maturity_level=MaturityLevel.BETA,
                version="1.0.0",
                plugin_key="Descriptive Statistics",
            )
        )

    with pytest.raises(ValueError, match="plugin_key"):
        registry.register(
            AnalysisCapability(
                capability_id="cap_invalid",
                display_name="X",
                description="desc",
                investigation_stage=CapabilityStage.OBSERVE,
                business_purpose=BusinessPurpose.DESCRIBE,
                required_input_types=[],
                supported_semantic_primitives=[SemanticPrimitive.NUMERIC],
                expected_outputs=[],
                execution_constraints=ExecutionConstraints(),
                dependencies=[],
                tags=[],
                maturity_level=MaturityLevel.BETA,
                version="1.0.0",
                plugin_key="",
            )
        )