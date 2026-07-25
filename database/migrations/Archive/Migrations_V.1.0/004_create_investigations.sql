CREATE TABLE investigations (

    investigation_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    organization_id UUID NOT NULL,

    investigation_name VARCHAR(255) NOT NULL,

    purpose TEXT,

    status VARCHAR(20) NOT NULL DEFAULT 'OPEN',

    priority VARCHAR(20) NOT NULL DEFAULT 'MEDIUM',

    owner_name VARCHAR(255),

    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    completed_at TIMESTAMP,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_investigation_organization
        FOREIGN KEY (organization_id)
        REFERENCES organizations(organization_id)
        ON DELETE CASCADE
);