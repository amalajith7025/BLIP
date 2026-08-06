from __future__ import annotations

from collections import defaultdict
from typing import TYPE_CHECKING
from uuid import NAMESPACE_DNS, uuid5

from .schemas import Evidence, Finding, FindingCollection

if TYPE_CHECKING:
    from app.investigation_workflow.schemas import InvestigationResult


class FindingsBuilderService:
    """
    Deterministic converter from completed investigation outputs to findings.
    """

    def build(self, investigation_result: InvestigationResult) -> FindingCollection:
        evidence_items = self._normalize_evidence(investigation_result)
        grouped = self._group_evidence(evidence_items)
        findings = self._build_findings(grouped, investigation_result)
        findings = self._deduplicate(findings)

        investigation_id = self._build_investigation_id(investigation_result)

        summary = {
            "total_findings": len(findings),
            "high_severity": sum(1 for finding in findings if finding.severity == "high"),
            "medium_severity": sum(1 for finding in findings if finding.severity == "medium"),
            "low_severity": sum(1 for finding in findings if finding.severity == "low"),
        }

        statistics = {
            "total_evidence_items": len(evidence_items),
            "unique_capabilities": len({item.capability_id for item in evidence_items}),
            "average_finding_confidence": round(
                sum(finding.confidence for finding in findings) / len(findings),
                3,
            ) if findings else 0.0,
        }

        warnings = list(investigation_result.warnings)
        if not findings:
            warnings.append("No findings produced from investigation evidence")

        return FindingCollection(
            investigation_id=investigation_id,
            findings=findings,
            summary=summary,
            statistics=statistics,
            warnings=warnings,
            execution_metadata={
                "workflow_confidence": investigation_result.confidence,
                "execution_duration_ms": investigation_result.execution_duration_ms,
                "workflow_version": investigation_result.investigation_metadata.get("workflow_version", "1.0.0"),
            },
        )

    def _normalize_evidence(self, investigation_result: InvestigationResult) -> list[Evidence]:
        evidence_items: list[Evidence] = []

        for executed in investigation_result.executed_capabilities:
            if executed.status != "executed":
                continue

            for key, value in executed.results.items():
                evidence_items.extend(
                    self._extract_evidence_values(
                        capability_id=executed.capability_id,
                        capability_name=executed.plugin_name,
                        source_analysis=executed.plugin_name,
                        parent_key=str(key),
                        value=value,
                        stage=executed.stage,
                    )
                )

        return evidence_items

    def _extract_evidence_values(
        self,
        capability_id: str,
        capability_name: str,
        source_analysis: str,
        parent_key: str,
        value,
        stage: str,
    ) -> list[Evidence]:
        items: list[Evidence] = []

        if isinstance(value, dict):
            for child_key, child_value in value.items():
                trace = f"{capability_id}:{parent_key}.{child_key}"
                if isinstance(child_value, dict):
                    items.extend(
                        self._extract_evidence_values(
                            capability_id=capability_id,
                            capability_name=capability_name,
                            source_analysis=source_analysis,
                            parent_key=f"{parent_key}.{child_key}",
                            value=child_value,
                            stage=stage,
                        )
                    )
                else:
                    evidence_type = self._classify_evidence_type(parent_key, child_key)
                    items.append(
                        Evidence(
                            capability_id=capability_id,
                            capability_name=capability_name,
                            source_analysis=source_analysis,
                            evidence_type=evidence_type,
                            evidence_value=child_value,
                            confidence=self._evidence_confidence(child_value),
                            trace_reference=trace,
                        )
                    )
            return items

        items.append(
            Evidence(
                capability_id=capability_id,
                capability_name=capability_name,
                source_analysis=source_analysis,
                evidence_type="scalar",
                evidence_value=value,
                confidence=self._evidence_confidence(value),
                trace_reference=f"{capability_id}:{parent_key}",
            )
        )
        return items

    @staticmethod
    def _classify_evidence_type(parent_key: str, child_key: str) -> str:
        lowered = f"{parent_key}.{child_key}".lower()

        if "correlation" in lowered or "coefficient" in lowered or "direction" in lowered:
            return "relationship"
        if "missing" in lowered or "count" in lowered:
            return "quality"
        if any(token in lowered for token in ("mean", "median", "variance", "std", "quartile", "range")):
            return "metric"
        return "indicator"

    @staticmethod
    def _evidence_confidence(value) -> float:
        if value is None:
            return 0.0
        if isinstance(value, bool):
            return 0.7
        if isinstance(value, (int, float)):
            return 0.9
        if isinstance(value, str):
            return 0.75
        return 0.6

    def _group_evidence(self, evidence_items: list[Evidence]) -> dict[str, list[Evidence]]:
        grouped: dict[str, list[Evidence]] = defaultdict(list)

        for item in evidence_items:
            concept_key = self._concept_key(item)
            grouped[concept_key].append(item)

        return grouped

    @staticmethod
    def _concept_key(evidence: Evidence) -> str:
        trace = evidence.trace_reference.split(":", 1)[-1]
        path = trace.split(".")

        if evidence.evidence_type == "relationship" and len(path) >= 2:
            return f"relationship:{path[0]}"
        if evidence.evidence_type == "quality" and len(path) >= 2:
            return f"quality:{path[0]}"
        if evidence.evidence_type == "metric" and len(path) >= 2:
            return f"metric:{path[0]}"

        return f"indicator:{path[0]}"

    def _build_findings(
        self,
        grouped: dict[str, list[Evidence]],
        investigation_result: InvestigationResult,
    ) -> list[Finding]:
        findings: list[Finding] = []
        dataset_quality = self._dataset_quality(investigation_result)

        for concept_key in sorted(grouped.keys()):
            evidence_list = grouped[concept_key]
            supporting_capabilities = sorted({e.capability_id for e in evidence_list})
            category = concept_key.split(":", 1)[0]

            confidence = self._finding_confidence(
                evidence=evidence_list,
                dataset_quality=dataset_quality,
            )

            severity = self._severity_from_confidence(confidence)
            business_impact = self._business_impact_from_severity(severity)

            finding_id = str(uuid5(NAMESPACE_DNS, concept_key))
            title = self._title_for_concept(concept_key)
            description = self._description_for_concept(concept_key, evidence_list)

            related_metrics, related_dimensions = self._extract_related_fields(evidence_list)

            findings.append(
                Finding(
                    id=finding_id,
                    title=title,
                    description=description,
                    category=category,
                    severity=severity,
                    confidence=confidence,
                    business_impact=business_impact,
                    supporting_capabilities=supporting_capabilities,
                    supporting_evidence=evidence_list,
                    related_metrics=related_metrics,
                    related_dimensions=related_dimensions,
                    metadata={
                        "concept_key": concept_key,
                        "evidence_count": len(evidence_list),
                        "dataset_quality": dataset_quality,
                    },
                    created_at="1970-01-01T00:00:00Z",
                )
            )

        return findings

    def _finding_confidence(self, evidence: list[Evidence], dataset_quality: float) -> float:
        support_factor = min(1.0, len({item.capability_id for item in evidence}) / 3.0)
        agreement_factor = self._agreement_score(evidence)
        completeness_factor = self._completeness_score(evidence)

        confidence = (
            (0.35 * support_factor)
            + (0.30 * agreement_factor)
            + (0.20 * completeness_factor)
            + (0.15 * dataset_quality)
        )
        return round(max(0.0, min(1.0, confidence)), 3)

    @staticmethod
    def _agreement_score(evidence: list[Evidence]) -> float:
        values: list[float] = []
        for item in evidence:
            if isinstance(item.evidence_value, (int, float)):
                values.append(float(item.evidence_value))

        if len(values) <= 1:
            return 1.0

        signs = [1 if value > 0 else -1 if value < 0 else 0 for value in values]
        dominant = max(signs.count(-1), signs.count(0), signs.count(1))
        return dominant / len(signs)

    @staticmethod
    def _completeness_score(evidence: list[Evidence]) -> float:
        if not evidence:
            return 0.0
        complete = sum(1 for item in evidence if item.evidence_value is not None)
        return complete / len(evidence)

    @staticmethod
    def _severity_from_confidence(confidence: float) -> str:
        if confidence >= 0.75:
            return "high"
        if confidence >= 0.5:
            return "medium"
        return "low"

    @staticmethod
    def _business_impact_from_severity(severity: str) -> str:
        if severity == "high":
            return "priority"
        if severity == "medium":
            return "monitor"
        return "informational"

    @staticmethod
    def _title_for_concept(concept_key: str) -> str:
        category, _, subject = concept_key.partition(":")
        subject_title = subject.replace("_", " ").strip()
        return f"{category.title()} finding for {subject_title}"

    @staticmethod
    def _description_for_concept(concept_key: str, evidence: list[Evidence]) -> str:
        _, _, subject = concept_key.partition(":")
        return (
            f"Deterministic finding generated for '{subject}' with "
            f"{len(evidence)} supporting evidence item(s)."
        )

    @staticmethod
    def _extract_related_fields(evidence: list[Evidence]) -> tuple[list[str], list[str]]:
        metrics: set[str] = set()
        dimensions: set[str] = set()

        for item in evidence:
            trace = item.trace_reference.split(":", 1)[-1]
            parts = trace.split(".")
            if parts:
                dimensions.add(parts[0])
            if len(parts) >= 2:
                metrics.add(parts[-1])

        return sorted(metrics), sorted(dimensions)

    @staticmethod
    def _deduplicate(findings: list[Finding]) -> list[Finding]:
        seen: set[str] = set()
        deduped: list[Finding] = []

        for finding in findings:
            if finding.id in seen:
                continue
            seen.add(finding.id)
            deduped.append(finding)

        return deduped

    @staticmethod
    def _dataset_quality(investigation_result: InvestigationResult) -> float:
        rows_raw = investigation_result.investigation_metadata.get("dataset_rows", "0")
        columns_raw = investigation_result.investigation_metadata.get("dataset_columns", "0")
        missing_ratio_raw = investigation_result.investigation_metadata.get("dataset_missing_ratio", "1.0")

        try:
            rows = max(0, int(rows_raw))
            columns = max(0, int(columns_raw))
            missing_ratio = min(1.0, max(0.0, float(missing_ratio_raw)))
        except ValueError:
            return 0.5

        shape_score = min(1.0, (rows * max(1, columns)) / 1000.0)
        completeness_score = 1.0 - missing_ratio
        return round((0.4 * shape_score) + (0.6 * completeness_score), 3)

    @staticmethod
    def _build_investigation_id(investigation_result: InvestigationResult) -> str:
        goal_id = investigation_result.investigation_metadata.get("goal_id", "unknown_goal")
        dataset_name = investigation_result.investigation_metadata.get("dataset_name", "unknown_dataset")
        identity = f"{goal_id}:{dataset_name}"
        return str(uuid5(NAMESPACE_DNS, identity))