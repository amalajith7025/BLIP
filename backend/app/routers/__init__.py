from .tenant import router as tenant_router
from .organization import router as organization_router
from .industry import router as industry_router
from .organization_industry import (
    router as organization_industry_router,
)
from .organization_unit import router as organization_unit_router
from .investigation import router as investigation_router
from .business_question import router as business_question_router
from .artifact import router as artifact_router
from .fact import router as fact_router
from .evidence import router as evidence_router
from .hypothesis import (
    router as hypothesis_router,
)
from .hypothesis_evidence import (
    router as hypothesis_evidence_router,
)
from .finding import (
    router as finding_router,
)
from .recommendation import (
    router as recommendation_router,
)
from .auth import router as auth_router
from .user import router as user_router
from .workspace import router as workspace_router
from .investigation_pipeline import router as investigation_pipeline_router
