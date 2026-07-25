CREATE TABLE organizations (

    organization_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    tenant_id UUID NOT NULL,

    organization_name VARCHAR(255) NOT NULL,

    legal_name VARCHAR(255),

    website VARCHAR(255),

    headquarters VARCHAR(255),

    description TEXT,

    status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE'
        CHECK (status IN ('ACTIVE', 'INACTIVE')),

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_organizations_tenant
        FOREIGN KEY (tenant_id)
        REFERENCES tenants (tenant_id)
        ON DELETE CASCADE
);

CREATE INDEX idx_organizations_tenant
ON organizations (tenant_id);

CREATE INDEX idx_organizations_name
ON organizations (organization_name);