CREATE TABLE organization_units (

    unit_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    organization_id UUID NOT NULL,

    parent_unit_id UUID,

    unit_name VARCHAR(255) NOT NULL,

    unit_type VARCHAR(50) NOT NULL
        CHECK (unit_type IN (
            'REGION',
            'COUNTRY',
            'STATE',
            'CITY',
            'SITE',
            'DIVISION',
            'DEPARTMENT',
            'BUSINESS_UNIT',
            'PROGRAM',
            'TEAM',
            'OTHER'
        )),

    description TEXT,

    status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE'
        CHECK (status IN ('ACTIVE', 'INACTIVE')),

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_organization_units_organization
        FOREIGN KEY (organization_id)
        REFERENCES organizations (organization_id)
        ON DELETE CASCADE,

    CONSTRAINT fk_organization_units_parent
        FOREIGN KEY (parent_unit_id)
        REFERENCES organization_units (unit_id)
        ON DELETE CASCADE
);

CREATE INDEX idx_organization_units_organization
ON organization_units (organization_id);

CREATE INDEX idx_organization_units_parent
ON organization_units (parent_unit_id);

CREATE INDEX idx_organization_units_type
ON organization_units (unit_type);