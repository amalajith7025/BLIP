CREATE TABLE tenants (
    tenant_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    tenant_name VARCHAR(255) NOT NULL,

    legal_name VARCHAR(255),

    subscription_plan VARCHAR(50) DEFAULT 'FREE',

    status VARCHAR(20) DEFAULT 'ACTIVE',

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);