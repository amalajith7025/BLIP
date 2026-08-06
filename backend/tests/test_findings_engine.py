from app.findings.services import FindingsBuilderService
from app.investigation_framework.schemas import InvestigationStatus, StageStatus
from app.investigation_workflow.schemas import (
    ExecutedCapabilityResult,
    InvestigationExecutionSummary,
    InvestigationResult,
)


def _base_result(
    executed_capabilities: list[ExecutedCapabilityResult],
    warnings: list[str] | None = None,
    dataset_rows: int = 100,
    dataset_columns: int = 4,
    missing_ratio: float = 0.05,
) -> InvestigationResult:
    return InvestigationResult(
        investigation_metadata={
            "goal_id": "goal_test",
            "goal_name": "Test Goal",
            "dataset_name": "test_dataset",
            "dataset_rows": str(dataset_rows),
            "dataset_columns": str(dataset_columns),
            "dataset_missing_ratio": str(missing_ratio),
            "workflow_version": "1.0.0",
        },
        execution_summary=InvestigationExecutionSummary(
            framework_status=InvestigationStatus.COMPLETED,
            stage_statuses={
                "understand": StageStatus.COMPLETED,
                "observe": StageStatus.COMPLETED,
            },
            total_selected=len(executed_capabilities),
            total_executed=sum(1 for item in executed_capabilities if item.status == "executed"),
            total_failed=sum(1 for item in executed_capabilities if item.status == "failed"),
            total_skipped=sum(1 for item in executed_capabilities if item.status == "skipped"),
        ),
        executed_capabilities=executed_capabilities,
        skipped_capabilities=[],
        analysis_results={},
        execution_duration_ms=10.0,
        warnings=warnings or [],
        planner_decisions=None,
        confidence=0.8,
    )


def test_finding_creation_from_executed_capability():
    builder = FindingsBuilderService()
    result = _base_result(
        executed_capabilities=[
            ExecutedCapabilityResult(
                capability_id="cap_descriptive_statistics",
                plugin_name="Descriptive Statistics",
                stage="observe",
                status="executed",
                results={
                    "value": {
                        "mean": 10.0,
                        "median": 9.0,
                        "missing_values": 0,
                    }
                },
            )
        ]
    )

    collection = builder.build(result)

    assert len(collection.findings) >= 1
    finding = collection.findings[0]
    assert finding.supporting_capabilities == ["cap_descriptive_statistics"]
    assert finding.category in {"metric", "quality", "indicator", "relationship"}


def test_evidence_aggregation_groups_related_evidence():
    builder = FindingsBuilderService()
    result = _base_result(
        executed_capabilities=[
            ExecutedCapabilityResult(
                capability_id="cap_descriptive_statistics",
                plugin_name="Descriptive Statistics",
                stage="observe",
                status="executed",
                results={
                    "value": {
                        "mean": 10.0,
                        "median": 9.0,
                        "variance": 2.0,
                    }
                },
            )
        ]
    )

    collection = builder.build(result)

    metric_findings = [finding for finding in collection.findings if finding.category == "metric"]
    assert metric_findings
    assert any(len(finding.supporting_evidence) >= 2 for finding in metric_findings)


def test_duplicate_finding_prevention():
    builder = FindingsBuilderService()
    duplicated = ExecutedCapabilityResult(
        capability_id="cap_descriptive_statistics",
        plugin_name="Descriptive Statistics",
        stage="observe",
        status="executed",
        results={
            "value": {
                "mean": 10.0,
            }
        },
    )
    result = _base_result(executed_capabilities=[duplicated, duplicated])

    collection = builder.build(result)
    ids = [finding.id for finding in collection.findings]

    assert len(ids) == len(set(ids))


def test_confidence_calculation_reflects_support_and_quality():
    builder = FindingsBuilderService()

    high_support_result = _base_result(
        executed_capabilities=[
            ExecutedCapabilityResult(
                capability_id="cap_a",
                plugin_name="A",
                stage="observe",
                status="executed",
                results={"value": {"mean": 10.0}},
            ),
            ExecutedCapabilityResult(
                capability_id="cap_b",
                plugin_name="B",
                stage="explain",
                status="executed",
                results={"value": {"mean": 11.0}},
            ),
        ],
        dataset_rows=500,
        dataset_columns=10,
        missing_ratio=0.01,
    )

    low_support_result = _base_result(
        executed_capabilities=[
            ExecutedCapabilityResult(
                capability_id="cap_a",
                plugin_name="A",
                stage="observe",
                status="executed",
                results={"value": {"mean": 10.0}},
            ),
        ],
        dataset_rows=10,
        dataset_columns=1,
        missing_ratio=0.8,
    )

    high_collection = builder.build(high_support_result)
    low_collection = builder.build(low_support_result)

    high_avg = high_collection.statistics["average_finding_confidence"]
    low_avg = low_collection.statistics["average_finding_confidence"]

    assert high_avg > low_avg


def test_traceability_preserved_in_findings():
    builder = FindingsBuilderService()
    result = _base_result(
        executed_capabilities=[
            ExecutedCapabilityResult(
                capability_id="cap_correlation_analysis",
                plugin_name="Correlation Analysis",
                stage="explain",
                status="executed",
                results={
                    "revenue": {
                        "cost": {
                            "coefficient": -0.9,
                            "direction": "Negative",
                        }
                    }
                },
            )
        ]
    )

    collection = builder.build(result)

    assert collection.findings
    first = collection.findings[0]
    assert first.supporting_capabilities
    assert all(evidence.trace_reference.startswith("cap_correlation_analysis:") for evidence in first.supporting_evidence)


def test_empty_investigation_returns_empty_findings_with_warning():
    builder = FindingsBuilderService()
    result = _base_result(executed_capabilities=[])

    collection = builder.build(result)

    assert collection.findings == []
    assert any("No findings produced" in warning for warning in collection.warnings)


def test_partial_investigation_uses_only_executed_capabilities():
    builder = FindingsBuilderService()
    result = _base_result(
        executed_capabilities=[
            ExecutedCapabilityResult(
                capability_id="cap_ok",
                plugin_name="OK",
                stage="observe",
                status="executed",
                results={"value": {"mean": 1.0}},
            ),
            ExecutedCapabilityResult(
                capability_id="cap_failed",
                plugin_name="Failed",
                stage="observe",
                status="failed",
                reason="execution error",
            ),
        ],
        warnings=["capability failed"],
    )

    collection = builder.build(result)

    assert collection.findings
    assert all("cap_failed" not in finding.supporting_capabilities for finding in collection.findings)
    assert "capability failed" in collection.warnings


def test_multiple_supporting_analyses_in_single_finding():
    builder = FindingsBuilderService()
    result = _base_result(
        executed_capabilities=[
            ExecutedCapabilityResult(
                capability_id="cap_one",
                plugin_name="One",
                stage="observe",
                status="executed",
                results={"value": {"mean": 12.0}},
            ),
            ExecutedCapabilityResult(
                capability_id="cap_two",
                plugin_name="Two",
                stage="explain",
                status="executed",
                results={"value": {"mean": 12.5}},
            ),
        ]
    )

    collection = builder.build(result)

    assert any(len(finding.supporting_capabilities) >= 2 for finding in collection.findings)


def test_deterministic_output_for_same_input():
    builder = FindingsBuilderService()
    result = _base_result(
        executed_capabilities=[
            ExecutedCapabilityResult(
                capability_id="cap_descriptive_statistics",
                plugin_name="Descriptive Statistics",
                stage="observe",
                status="executed",
                results={"value": {"mean": 10.0, "median": 9.0}},
            )
        ]
    )

    first = builder.build(result)
    second = builder.build(result)

    assert first == second