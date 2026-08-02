# PROJECT_STATE

This document is derived from the implemented code in the workspace and reflects the current backend state as of 2026-07-26.

## 1. Workspace inventory

### Backend
- The active application implementation is in [backend/app](backend/app).
- The API entrypoint is [backend/app/main.py](backend/app/main.py).
- The frontend directory exists but is empty, so there is no frontend implementation in the workspace at this time.

### Key backend modules
- Models: [backend/app/models](backend/app/models)
- Schemas: [backend/app/schemas](backend/app/schemas)
- Routers: [backend/app/routers](backend/app/routers)
- Services: [backend/app/services](backend/app/services)
- CRUD: [backend/app/crud](backend/app/crud)

---

## 2. SQLAlchemy models

The codebase defines the following SQLAlchemy models:

- [backend/app/models/tenant.py](backend/app/models/tenant.py) — Tenant
- [backend/app/models/organization.py](backend/app/models/organization.py) — Organization
- [backend/app/models/industry.py](backend/app/models/industry.py) — Industry
- [backend/app/models/organization_industry.py](backend/app/models/organization_industry.py) — OrganizationIndustry
- [backend/app/models/organization_unit.py](backend/app/models/organization_unit.py) — OrganizationUnit
- [backend/app/models/investigation.py](backend/app/models/investigation.py) — Investigation
- [backend/app/models/business_question.py](backend/app/models/business_question.py) — BusinessQuestion
- [backend/app/models/artifact.py](backend/app/models/artifact.py) — Artifact
- [backend/app/models/fact.py](backend/app/models/fact.py) — Fact
- [backend/app/models/evidence.py](backend/app/models/evidence.py) — Evidence
- [backend/app/models/hypothesis.py](backend/app/models/hypothesis.py) — Hypothesis
- [backend/app/models/hypothesis_evidence.py](backend/app/models/hypothesis_evidence.py) — HypothesisEvidence
- [backend/app/models/finding.py](backend/app/models/finding.py) — Finding
- [backend/app/models/recommendation.py](backend/app/models/recommendation.py) — Recommendation
- [backend/app/models/role.py](backend/app/models/role.py) — Role
- [backend/app/models/user.py](backend/app/models/user.py) — User
- [backend/app/models/workspace.py](backend/app/models/workspace.py) — Workspace
- [backend/app/models/membership.py](backend/app/models/membership.py) — Membership

### Model coverage notes
- The model layer is present for a multi-tenant operational investigation domain.
- Workspace and membership models are implemented, but the surrounding feature set is still narrower than the rest of the CRUD surface.

---

## 3. Pydantic schemas

The codebase defines the following Pydantic schemas:

- [backend/app/schemas/tenant.py](backend/app/schemas/tenant.py) — TenantCreate, TenantUpdate, TenantResponse
- [backend/app/schemas/organization.py](backend/app/schemas/organization.py) — OrganizationCreate, OrganizationUpdate, OrganizationStatusUpdate, OrganizationResponse
- [backend/app/schemas/industry.py](backend/app/schemas/industry.py) — IndustryCreate, IndustryUpdate, IndustryResponse
- [backend/app/schemas/organization_industry.py](backend/app/schemas/organization_industry.py) — OrganizationIndustryCreate, OrganizationIndustryUpdate, OrganizationIndustryResponse
- [backend/app/schemas/organization_unit.py](backend/app/schemas/organization_unit.py) — OrganizationUnitCreate, OrganizationUnitUpdate, OrganizationUnitResponse
- [backend/app/schemas/investigation.py](backend/app/schemas/investigation.py) — InvestigationCreate, InvestigationUpdate, InvestigationResponse
- [backend/app/schemas/business_question.py](backend/app/schemas/business_question.py) — BusinessQuestionCreate, BusinessQuestionUpdate, BusinessQuestionResponse
- [backend/app/schemas/artifact.py](backend/app/schemas/artifact.py) — ArtifactCreate, ArtifactUpdate, ArtifactResponse
- [backend/app/schemas/fact.py](backend/app/schemas/fact.py) — FactCreate, FactUpdate, FactResponse
- [backend/app/schemas/evidence.py](backend/app/schemas/evidence.py) — EvidenceCreate, EvidenceUpdate, EvidenceResponse
- [backend/app/schemas/hypothesis.py](backend/app/schemas/hypothesis.py) — HypothesisCreate, HypothesisUpdate, HypothesisResponse
- [backend/app/schemas/hypothesis_evidence.py](backend/app/schemas/hypothesis_evidence.py) — HypothesisEvidenceCreate, HypothesisEvidenceUpdate, HypothesisEvidenceResponse
- [backend/app/schemas/finding.py](backend/app/schemas/finding.py) — FindingCreate, FindingUpdate, FindingResponse
- [backend/app/schemas/recommendation.py](backend/app/schemas/recommendation.py) — RecommendationCreate, RecommendationUpdate, RecommendationResponse
- [backend/app/schemas/role.py](backend/app/schemas/role.py) — RoleBase, RoleCreate, RoleUpdate, RoleResponse
- [backend/app/schemas/user.py](backend/app/schemas/user.py) — UserBase, UserCreate, UserUpdate, UserResponse
- [backend/app/schemas/auth.py](backend/app/schemas/auth.py) — LoginRequest, TokenResponse
- [backend/app/schemas/workspace.py](backend/app/schemas/workspace.py) — WorkspaceCreate, WorkspaceUpdate, WorkspaceResponse, WorkspaceListResponse

---

## 4. Routers

The application registers the following routers in [backend/app/main.py](backend/app/main.py):

- [backend/app/routers/tenant.py](backend/app/routers/tenant.py) — /tenants
- [backend/app/routers/organization.py](backend/app/routers/organization.py) — /organizations
- [backend/app/routers/industry.py](backend/app/routers/industry.py) — /industries
- [backend/app/routers/organization_industry.py](backend/app/routers/organization_industry.py) — /organization-industries
- [backend/app/routers/organization_unit.py](backend/app/routers/organization_unit.py) — /organization-units
- [backend/app/routers/investigation.py](backend/app/routers/investigation.py) — /investigations
- [backend/app/routers/business_question.py](backend/app/routers/business_question.py) — /business-questions
- [backend/app/routers/artifact.py](backend/app/routers/artifact.py) — /artifacts
- [backend/app/routers/fact.py](backend/app/routers/fact.py) — /facts
- [backend/app/routers/evidence.py](backend/app/routers/evidence.py) — /evidence
- [backend/app/routers/hypothesis.py](backend/app/routers/hypothesis.py) — /hypotheses
- [backend/app/routers/hypothesis_evidence.py](backend/app/routers/hypothesis_evidence.py) — /hypothesis-evidence
- [backend/app/routers/finding.py](backend/app/routers/finding.py) — /findings
- [backend/app/routers/recommendation.py](backend/app/routers/recommendation.py) — /recommendations
- [backend/app/routers/auth.py](backend/app/routers/auth.py) — /auth
- [backend/app/routers/user.py](backend/app/routers/user.py) — /users
- [backend/app/routers/workspace.py](backend/app/routers/workspace.py) — /workspaces

### Router status
- CRUD-style routers are implemented for most domain entities.
- Role-based router support is not present; role CRUD exists in the code but is not exposed through a router.

---

## 5. Services

Implemented services:

- [backend/app/services/auth.py](backend/app/services/auth.py) — user registration, authentication, and token issuance.
- [backend/app/services/organization.py](backend/app/services/organization.py) — organization create/list/get/update/status orchestration.
- [backend/app/services/workspace.py](backend/app/services/workspace.py) — workspace create/list/get/update/delete with owner and conflict handling.

### Service observations
- Services are used for authentication and the workspace feature.
- The rest of the CRUD modules are implemented directly through router-to-CRUD calls rather than dedicated services.

---

## 6. CRUD modules

CRUD modules exist for:

- [backend/app/crud/tenant.py](backend/app/crud/tenant.py)
- [backend/app/crud/organization.py](backend/app/crud/organization.py)
- [backend/app/crud/industry.py](backend/app/crud/industry.py)
- [backend/app/crud/organization_industry.py](backend/app/crud/organization_industry.py)
- [backend/app/crud/organization_unit.py](backend/app/crud/organization_unit.py)
- [backend/app/crud/investigation.py](backend/app/crud/investigation.py)
- [backend/app/crud/business_question.py](backend/app/crud/business_question.py)
- [backend/app/crud/artifact.py](backend/app/crud/artifact.py)
- [backend/app/crud/fact.py](backend/app/crud/fact.py)
- [backend/app/crud/evidence.py](backend/app/crud/evidence.py)
- [backend/app/crud/hypothesis.py](backend/app/crud/hypothesis.py)
- [backend/app/crud/hypothesis_evidence.py](backend/app/crud/hypothesis_evidence.py)
- [backend/app/crud/finding.py](backend/app/crud/finding.py)
- [backend/app/crud/recommendation.py](backend/app/crud/recommendation.py)
- [backend/app/crud/role.py](backend/app/crud/role.py)
- [backend/app/crud/user.py](backend/app/crud/user.py)
- [backend/app/crud/workspace.py](backend/app/crud/workspace.py)
- [backend/app/crud/membership.py](backend/app/crud/membership.py)

### CRUD pattern
- Most CRUD modules follow the same pattern: get-all/get-by-id/create/update/delete.
- Workspace and membership access are slightly more specialized and are handled by the workspace service.

---

## 7. Implemented API endpoints

The implemented routes are:

### Authentication
- POST /auth/register
- POST /auth/login

### Users
- GET /users/me

### Tenants
- GET /tenants/
- GET /tenants/{tenant_id}
- POST /tenants/
- PUT /tenants/{tenant_id}
- DELETE /tenants/{tenant_id}

### Organizations
- GET /organizations/
- GET /organizations/{organization_id}
- POST /organizations/
- PUT /organizations/{organization_id}
- PATCH /organizations/{organization_id}/status

### Industries
- GET /industries/
- GET /industries/{industry_id}
- POST /industries/
- PUT /industries/{industry_id}
- DELETE /industries/{industry_id}

### Organization industries
- GET /organization-industries/
- GET /organization-industries/{organization_industry_id}
- POST /organization-industries/
- PUT /organization-industries/{organization_industry_id}
- DELETE /organization-industries/{organization_industry_id}

### Organization units
- GET /organization-units/
- GET /organization-units/{organization_unit_id}
- POST /organization-units/
- PUT /organization-units/{organization_unit_id}
- DELETE /organization-units/{organization_unit_id}

### Investigations
- GET /investigations/
- GET /investigations/{investigation_id}
- POST /investigations/
- PUT /investigations/{investigation_id}
- DELETE /investigations/{investigation_id}

### Business questions
- GET /business-questions/
- GET /business-questions/{business_question_id}
- POST /business-questions/
- PUT /business-questions/{business_question_id}
- DELETE /business-questions/{business_question_id}

### Artifacts
- GET /artifacts/
- GET /artifacts/{artifact_id}
- POST /artifacts/
- PUT /artifacts/{artifact_id}
- DELETE /artifacts/{artifact_id}

### Facts
- GET /facts/
- GET /facts/{fact_id}
- POST /facts/
- PUT /facts/{fact_id}
- DELETE /facts/{fact_id}

### Evidence
- GET /evidence/
- GET /evidence/{evidence_id}
- POST /evidence/
- PUT /evidence/{evidence_id}
- DELETE /evidence/{evidence_id}

### Hypotheses
- GET /hypotheses/
- GET /hypotheses/{hypothesis_id}
- POST /hypotheses/
- PUT /hypotheses/{hypothesis_id}
- DELETE /hypotheses/{hypothesis_id}

### Hypothesis evidence
- GET /hypothesis-evidence/
- GET /hypothesis-evidence/{hypothesis_evidence_id}
- POST /hypothesis-evidence/
- PUT /hypothesis-evidence/{hypothesis_evidence_id}
- DELETE /hypothesis-evidence/{hypothesis_evidence_id}

### Findings
- GET /findings/
- GET /findings/{finding_id}
- POST /findings/
- PUT /findings/{finding_id}
- DELETE /findings/{finding_id}

### Recommendations
- GET /recommendations/
- GET /recommendations/{recommendation_id}
- POST /recommendations/
- PUT /recommendations/{recommendation_id}
- DELETE /recommendations/{recommendation_id}

### Workspaces
- POST /workspaces/
- GET /workspaces/
- GET /workspaces/{workspace_id}
- PATCH /workspaces/{workspace_id}
- DELETE /workspaces/{workspace_id}

---

## 8. Authentication status

Authentication is implemented in the codebase.

### What exists
- JWT-based authentication is implemented in [backend/app/auth/jwt.py](backend/app/auth/jwt.py).
- Login and registration endpoints are implemented in [backend/app/routers/auth.py](backend/app/routers/auth.py).
- A current-user dependency is implemented in [backend/app/auth/dependencies.py](backend/app/auth/dependencies.py).
- Password hashing and verification are implemented in [backend/app/auth/security.py](backend/app/auth/security.py).

### Current status
- Authentication is functional at the API boundary for auth endpoints and for the user/workspace routes that depend on the current user.
- Most domain CRUD routers do not require authentication yet.

---

## 9. Authorization status

Authorization is only partially implemented.

### What exists
- Workspace routes enforce authentication via the current-user dependency.
- Workspace update/delete operations enforce owner-only access in [backend/app/services/workspace.py](backend/app/services/workspace.py).
- User and role models exist, and seed roles are defined in [backend/app/database/seed_data.py](backend/app/database/seed_data.py).

### What is missing
- No general role-based access control enforcement is applied across domain routers.
- No per-resource permission checks are implemented for tenants, organizations, investigations, findings, or other entities.
- The role CRUD exists, but there is no exposed role-management API in the current router layer.

---

## 10. Completed features

Based on the current source, the following features are implemented:

- Full backend CRUD scaffolding for a broad set of investigation-related entities.
- Pydantic schema layer for request and response validation.
- SQLAlchemy models and database initialization from [backend/app/main.py](backend/app/main.py).
- JWT-based registration/login flow.
- Authenticated workspace management with owner-based update/delete rules.
- Seed data and role definitions for a future RBAC system.
- Basic health and root endpoints in [backend/app/main.py](backend/app/main.py).

---

## 11. Partially completed features

The following areas are present but not yet complete:

- Authorization framework: present as a foundation, but not enforced consistently across the API.
- Workspace feature: implemented, but appears to be a focused early implementation rather than a full multi-tenant collaboration system.
- Role management: CRUD exists in code, but no router exposes it.
- Frontend: no implementation exists in the workspace.
- Tests: the [backend/tests](backend/tests) directory is empty.
- Multi-tenant enforcement: tenant/organization relationships exist in the model layer, but the current routers do not enforce tenant-scoped access rules.

---

## 12. Next logical development phase

The next logical phase is to move from scaffolded CRUD to a secured, domain-oriented backend foundation:

1. Enforce authentication across all resource routers.
2. Implement role-based access control and tenant-aware authorization for every domain entity.
3. Add tests for auth, workspaces, and core CRUD flows.
4. Introduce explicit business rules for investigations, findings, and recommendations rather than keeping them as generic CRUD endpoints.
5. Build the missing frontend around the authenticated API surface.

In short, the project is currently in an API scaffolding and foundation-authentication stage, and the next phase should focus on secure, role-aware, tenant-scoped business functionality.
