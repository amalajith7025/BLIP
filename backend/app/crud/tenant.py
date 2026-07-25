from uuid import UUID

from sqlalchemy.orm import Session

from app.models.tenant import Tenant
from app.schemas.tenant import TenantCreate, TenantUpdate


def get_all(db: Session):
    return db.query(Tenant).all()


def get_by_id(db: Session, tenant_id: UUID):
    return (
        db.query(Tenant)
        .filter(Tenant.tenant_id == tenant_id)
        .first()
    )


def create(db: Session, tenant: TenantCreate):
    db_tenant = Tenant(
        tenant_name=tenant.tenant_name,
        legal_name=tenant.legal_name,
        subscription_plan=tenant.subscription_plan,
        status=tenant.status,
    )

    db.add(db_tenant)
    db.commit()
    db.refresh(db_tenant)

    return db_tenant


def update(
    db: Session,
    tenant_id: UUID,
    tenant: TenantUpdate,
):
    db_tenant = get_by_id(db, tenant_id)

    if not db_tenant:
        return None

    updates = tenant.model_dump(exclude_unset=True)

    for key, value in updates.items():
        setattr(db_tenant, key, value)

    db.commit()
    db.refresh(db_tenant)

    return db_tenant


def delete(db: Session, tenant_id: UUID):
    db_tenant = get_by_id(db, tenant_id)

    if not db_tenant:
        return None

    db.delete(db_tenant)
    db.commit()

    return db_tenant