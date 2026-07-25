CREATE TABLE tenants (

    tenant_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    tenant_name VARCHAR(255) NOT NULL,

    legal_name VARCHAR(255),

    subscription_plan VARCHAR(50) NOT NULL DEFAULT 'FREE'
        CHECK (subscription_plan IN ('FREE', 'PRO', 'ENTERPRISE')),

    status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE'
        CHECK (status IN ('ACTIVE', 'INACTIVE')),

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_tenants_name
ON tenants (tenant_name);