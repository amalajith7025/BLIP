from app.core.database import SessionLocal
from app.database.seed_data import (
    DEFAULT_ORGANIZATION,
    DEFAULT_ROLES,
    DEFAULT_TENANT,
)
from app.models.organization import Organization
from app.models.role import Role
from app.models.tenant import Tenant


def seed():

    db = SessionLocal()

    try:

        tenant = (
            db.query(Tenant)
            .filter(
                Tenant.tenant_name == DEFAULT_TENANT["tenant_name"]
            )
            .first()
        )

        if tenant is None:

            tenant = Tenant(**DEFAULT_TENANT)

            db.add(tenant)

            db.commit()

            db.refresh(tenant)

            print("✅ Tenant created")

        else:

            print("✔ Tenant already exists")

        organization = (
            db.query(Organization)
            .filter(
                Organization.name
                == DEFAULT_ORGANIZATION["name"]
            )
            .first()
        )

        if organization is None:

            organization = Organization(
                tenant_id=tenant.tenant_id,
                **DEFAULT_ORGANIZATION,
            )

            db.add(organization)

            db.commit()

            db.refresh(organization)

            print("✅ Organization created")

        else:

            print("✔ Organization already exists")

        for role_data in DEFAULT_ROLES:

            role = (
                db.query(Role)
                .filter(
                    Role.role_name == role_data["role_name"]
                )
                .first()
            )

            if role is None:

                db.add(Role(**role_data))

                print(f"✅ Created role: {role_data['role_name']}")

        db.commit()

        print("\n🎉 Database seeded successfully!")

        print(f"\nOrganization ID: {organization.organization_id}")

    finally:

        db.close()


if __name__ == "__main__":

    seed()
