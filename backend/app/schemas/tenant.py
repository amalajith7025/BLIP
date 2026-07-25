from uuid import UUID

from pydantic import BaseModel, ConfigDict


class TenantCreate(BaseModel):
    tenant_name: str
    legal_name: str | None = None
    subscription_plan: str = "FREE"
    status: str = "ACTIVE"


class TenantUpdate(BaseModel):
    tenant_name: str | None = None
    legal_name: str | None = None
    subscription_plan: str | None = None
    status: str | None = None


class TenantResponse(BaseModel):
    tenant_id: UUID
    tenant_name: str
    legal_name: str | None
    subscription_plan: str
    status: str

    model_config = ConfigDict(from_attributes=True)