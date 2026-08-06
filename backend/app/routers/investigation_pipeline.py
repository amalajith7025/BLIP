from __future__ import annotations

import io
import threading
from uuid import uuid4

import pandas as pd
from fastapi import APIRouter, BackgroundTasks, HTTPException, UploadFile

from app.analysis.profiler import DataProfiler
from app.business_goals.services import build_default_goal_registry
from app.planning.services import InvestigationPlannerService
from app.schemas.investigation_pipeline import (
    BusinessGoalResponse,
    DatasetUploadResponse,
    FindingCollectionResponse,
    FindingEvidenceResponse,
    FindingResponse,
    InvestigationFindingsResponse,
    InvestigationStatusResponse,
    SemanticColumnResponse,
    SemanticProfileResponse,
    StartInvestigationRequest,
    StartInvestigationResponse,
)
from app.investigation_workflow.services import InvestigationWorkflowService


router = APIRouter(
    prefix="/investigation-pipeline",
    tags=["Investigation Pipeline"],
)

_datasets: dict[str, dict] = {}
_investigations: dict[str, dict] = {}
_lock = threading.Lock()

_profiler = DataProfiler()
_goal_registry = build_default_goal_registry()
_workflow_service = InvestigationWorkflowService()
_planner_service = InvestigationPlannerService()


@router.post(
    "/datasets/upload",
    response_model=DatasetUploadResponse,
)
async def upload_dataset(file: UploadFile) -> DatasetUploadResponse:
    filename = file.filename or "uploaded_dataset"
    content = await file.read()

    try:
        dataframe = _read_dataframe(filename, content)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error

    dataset_id = str(uuid4())

    with _lock:
        _datasets[dataset_id] = {
            "filename": filename,
            "dataframe": dataframe,
            "profile": None,
        }

    return DatasetUploadResponse(
        dataset_id=dataset_id,
        filename=filename,
        rows=len(dataframe),
        columns=len(dataframe.columns),
    )


@router.post(
    "/datasets/{dataset_id}/semantic-profile",
    response_model=SemanticProfileResponse,
)
def generate_semantic_profile(dataset_id: str) -> SemanticProfileResponse:
    dataset_record = _datasets.get(dataset_id)
    if dataset_record is None:
        raise HTTPException(status_code=404, detail="Dataset not found")

    dataframe = dataset_record["dataframe"]
    profile = _profiler.profile(dataframe, name=dataset_record["filename"])

    with _lock:
        dataset_record["profile"] = profile

    measures = sum(
        1
        for column in profile.column_profiles
        if column.can_average or column.continuous or column.discrete
    )
    dimensions = sum(
        1
        for column in profile.column_profiles
        if column.categorical or column.boolean or column.datetime or column.text
    )

    total_cells = profile.rows * max(1, profile.columns)
    missing_values = sum(column.missing_values for column in profile.column_profiles)
    completeness = 1.0 - (missing_values / total_cells) if total_cells > 0 else 0.0
    health_score = round(max(0.0, min(1.0, completeness)), 3)

    columns_profile = [
        SemanticColumnResponse(
            name=column.name,
            data_type=column.data_type,
            primitive=_column_primitive(column),
            missing_values=column.missing_values,
            unique_values=column.unique_values,
        )
        for column in profile.column_profiles
    ]

    return SemanticProfileResponse(
        dataset_id=dataset_id,
        dataset_name=profile.name,
        rows=profile.rows,
        columns=profile.columns,
        measures=measures,
        dimensions=dimensions,
        health_score=health_score,
        warnings=list(profile.warnings),
        columns_profile=columns_profile,
    )


@router.get(
    "/business-goals",
    response_model=list[BusinessGoalResponse],
)
def get_business_goals() -> list[BusinessGoalResponse]:
    goals = _goal_registry.list_available()
    return [
        BusinessGoalResponse(
            goal_id=goal.goal_id,
            name=goal.name,
            description=goal.description,
            business_purpose=goal.business_purpose.value,
            tags=list(goal.tags),
        )
        for goal in goals
    ]


@router.post(
    "/investigations",
    response_model=StartInvestigationResponse,
)
def start_investigation(
    payload: StartInvestigationRequest,
    background_tasks: BackgroundTasks,
) -> StartInvestigationResponse:
    dataset_record = _datasets.get(payload.dataset_id)
    if dataset_record is None:
        raise HTTPException(status_code=404, detail="Dataset not found")

    goal = _goal_registry.get_by_id(payload.goal_id)
    if goal is None:
        raise HTTPException(status_code=404, detail="Business goal not found")

    profile = dataset_record.get("profile")
    if profile is None:
        raise HTTPException(status_code=400, detail="Generate semantic profile before starting investigation")

    investigation_id = str(uuid4())

    with _lock:
        _investigations[investigation_id] = {
            "dataset_id": payload.dataset_id,
            "goal_id": payload.goal_id,
            "status": "queued",
            "progress": 5,
            "current_step": "Investigation queued...",
            "warnings": [],
            "result": None,
        }

    background_tasks.add_task(_execute_investigation, investigation_id)

    return StartInvestigationResponse(
        investigation_id=investigation_id,
        status="queued",
        progress=5,
        current_step="Investigation queued...",
    )


@router.get(
    "/investigations/{investigation_id}/status",
    response_model=InvestigationStatusResponse,
)
def get_investigation_status(investigation_id: str) -> InvestigationStatusResponse:
    investigation = _investigations.get(investigation_id)
    if investigation is None:
        raise HTTPException(status_code=404, detail="Investigation not found")

    return InvestigationStatusResponse(
        investigation_id=investigation_id,
        status=investigation["status"],
        progress=investigation["progress"],
        current_step=investigation["current_step"],
        warnings=list(investigation.get("warnings", [])),
    )


@router.get(
    "/investigations/{investigation_id}/findings",
    response_model=InvestigationFindingsResponse,
)
def get_investigation_findings(investigation_id: str) -> InvestigationFindingsResponse:
    investigation = _investigations.get(investigation_id)
    if investigation is None:
        raise HTTPException(status_code=404, detail="Investigation not found")

    if investigation["status"] != "completed":
        raise HTTPException(status_code=409, detail="Investigation has not completed yet")

    result = investigation.get("result")
    if result is None or result.findings_collection is None:
        raise HTTPException(status_code=500, detail="Findings were not generated")

    findings = [
        FindingResponse(
            id=finding.id,
            title=finding.title,
            description=finding.description,
            category=finding.category,
            severity=finding.severity,
            confidence=finding.confidence,
            business_impact=finding.business_impact,
            supporting_analyses=list(finding.supporting_capabilities),
            supporting_evidence=[
                FindingEvidenceResponse(
                    capability_name=evidence.capability_name,
                    evidence_type=evidence.evidence_type,
                    confidence=evidence.confidence,
                    trace_reference=evidence.trace_reference,
                    evidence_value=str(evidence.evidence_value),
                )
                for evidence in finding.supporting_evidence
            ],
        )
        for finding in result.findings_collection.findings
    ]

    collection = FindingCollectionResponse(
        investigation_id=result.findings_collection.investigation_id,
        findings=findings,
        summary=dict(result.findings_collection.summary),
        statistics=dict(result.findings_collection.statistics),
        warnings=list(result.findings_collection.warnings),
        execution_metadata=dict(result.findings_collection.execution_metadata),
    )

    return InvestigationFindingsResponse(
        investigation_id=investigation_id,
        status="completed",
        confidence=result.confidence,
        findings_collection=collection,
    )


def _execute_investigation(investigation_id: str) -> None:
    investigation = _investigations.get(investigation_id)
    if investigation is None:
        return

    try:
        _update_investigation_state(
            investigation_id,
            status="running",
            progress=20,
            current_step="Understanding your dataset...",
        )

        dataset_record = _datasets[investigation["dataset_id"]]
        profile = dataset_record["profile"]
        goal = _goal_registry.get_by_id(investigation["goal_id"])
        if goal is None:
            raise ValueError("Business goal not found")

        _update_investigation_state(
            investigation_id,
            status="running",
            progress=45,
            current_step="Planning the investigation...",
        )

        _planner_service.plan(goal, profile)

        _update_investigation_state(
            investigation_id,
            status="running",
            progress=70,
            current_step="Executing analytical capabilities...",
        )

        result = _workflow_service.execute_investigation(
            dataset_profile=profile,
            business_goal=goal,
            dataset=dataset_record["dataframe"],
        )

        _update_investigation_state(
            investigation_id,
            status="running",
            progress=90,
            current_step="Building findings...",
            warnings=result.warnings,
            result=result,
        )

        _update_investigation_state(
            investigation_id,
            status="completed",
            progress=100,
            current_step="Investigation completed.",
            warnings=result.warnings,
            result=result,
        )
    except Exception as error:
        _update_investigation_state(
            investigation_id,
            status="failed",
            progress=100,
            current_step="Investigation failed.",
            warnings=[str(error)],
        )


def _update_investigation_state(
    investigation_id: str,
    status: str,
    progress: int,
    current_step: str,
    warnings: list[str] | None = None,
    result=None,
) -> None:
    with _lock:
        investigation = _investigations.get(investigation_id)
        if investigation is None:
            return

        investigation["status"] = status
        investigation["progress"] = progress
        investigation["current_step"] = current_step
        if warnings is not None:
            investigation["warnings"] = list(warnings)
        if result is not None:
            investigation["result"] = result


def _read_dataframe(filename: str, content: bytes) -> pd.DataFrame:
    lowered = filename.lower()

    if lowered.endswith(".csv"):
        dataframe = pd.read_csv(io.BytesIO(content))
    elif lowered.endswith(".xlsx") or lowered.endswith(".xls"):
        try:
            dataframe = pd.read_excel(io.BytesIO(content))
        except Exception as error:
            raise ValueError("Excel parsing failed. Ensure required parser dependency is installed.") from error
    else:
        raise ValueError("Unsupported file format. Upload CSV or Excel files.")

    if dataframe.empty:
        raise ValueError("Uploaded dataset is empty")

    return dataframe


def _column_primitive(column) -> str:
    if column.continuous or column.discrete or column.can_average:
        return "numeric"
    if column.categorical:
        return "categorical"
    if column.boolean:
        return "boolean"
    if column.datetime:
        return "datetime"
    if column.text:
        return "text"
    return "unknown"