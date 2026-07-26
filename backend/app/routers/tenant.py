from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth.permissions import require_authenticated_user_dependency
from app.core.database import get_db
from app.crud import tenant as tenant_crud
from app.models.user import User
from app.schemas.tenant import (
    TenantCreate,
    TenantUpdate,
    TenantResponse,
)

router = APIRouter(
    prefix="/tenants",
    tags=["Tenants"],
)


@router.get("/", response_model=list[TenantResponse])
def get_all_tenants(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_authenticated_user_dependency),
):
    return tenant_crud.get_all(db)


@router.get("/{tenant_id}", response_model=TenantResponse)
def get_tenant(
    tenant_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_authenticated_user_dependency),
):
    tenant = tenant_crud.get_by_id(db, tenant_id)

    if tenant is None:
        raise HTTPException(status_code=404, detail="Tenant not found")

    return tenant


@router.post("/", response_model=TenantResponse, status_code=201)
def create_tenant(
    tenant: TenantCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_authenticated_user_dependency),
):
    return tenant_crud.create(db, tenant)


@router.put("/{tenant_id}", response_model=TenantResponse)
def update_tenant(
    tenant_id: UUID,
    tenant: TenantUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_authenticated_user_dependency),
):
    updated = tenant_crud.update(db, tenant_id, tenant)

    if updated is None:
        raise HTTPException(status_code=404, detail="Tenant not found")

    return updated


@router.delete("/{tenant_id}")
def delete_tenant(
    tenant_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_authenticated_user_dependency),
):
    deleted = tenant_crud.delete(db, tenant_id)

    if deleted is None:
        raise HTTPException(status_code=404, detail="Tenant not found")

    return {"message": "Tenant deleted successfully"}