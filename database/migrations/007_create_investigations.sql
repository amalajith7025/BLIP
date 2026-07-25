CREATE TABLE investigations (

    investigation_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    organization_id UUID NOT NULL,

    unit_id UUID,

    investigation_name VARCHAR(255) NOT NULL,

    investigation_objective TEXT,

    description TEXT,

    status VARCHAR(20) NOT NULL DEFAULT 'OPEN'
        CHECK (status IN (
            'OPEN',
            'IN_PROGRESS',
            'COMPLETED',
            'ARCHIVED'
        )),

    priority VARCHAR(20) NOT NULL DEFAULT 'MEDIUM'
        CHECK (priority IN (
            'LOW',
            'MEDIUM',
            'HIGH',
            'CRITICAL'
        )),

    owner_name VARCHAR(255),

    started_at TIMESTAMP,

    completed_at TIMESTAMP,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_investigations_organization
        FOREIGN KEY (organization_id)
        REFERENCES organizations (organization_id)
        ON DELETE CASCADE,

    CONSTRAINT fk_investigations_unit
        FOREIGN KEY (unit_id)
        REFERENCES organization_units (unit_id)
        ON DELETE SET NULL
);

CREATE INDEX idx_investigations_organization
ON investigations (organization_id);

CREATE INDEX idx_investigations_unit
ON investigations (unit_id);

CREATE INDEX idx_investigations_status
ON investigations (status);

CREATE INDEX idx_investigations_priority
ON investigations (priority);