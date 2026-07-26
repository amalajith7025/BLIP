from fastapi import FastAPI

from app.core.database import engine
from app.database.base import Base
from app.models import *

from app.routers import (
    tenant_router,
    organization_router,
    industry_router,
    organization_industry_router,
    organization_unit_router,
    investigation_router,
    business_question_router,
    artifact_router,
    fact_router,
    evidence_router,
    hypothesis_router,
    hypothesis_evidence_router,
    finding_router,
    recommendation_router,
    auth_router,
    user_router,
    workspace_router,
)

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="BLIP API",
    version="1.0.0",
)

app.include_router(tenant_router)
app.include_router(organization_router)
app.include_router(industry_router)
app.include_router(organization_industry_router)
app.include_router(organization_unit_router)
app.include_router(investigation_router)
app.include_router(business_question_router)
app.include_router(artifact_router)
app.include_router(fact_router)
app.include_router(evidence_router)
app.include_router(hypothesis_router)
app.include_router(hypothesis_evidence_router)
app.include_router(finding_router)
app.include_router(recommendation_router)
app.include_router(auth_router)
app.include_router(user_router)
app.include_router(workspace_router)


@app.get("/")
def root():
    return {
        "message": "BLIP API is running",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
    }
