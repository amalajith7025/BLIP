CREATE TABLE organization_units (

    unit_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    organization_id UUID NOT NULL,

    parent_unit_id UUID,

    unit_name VARCHAR(255) NOT NULL,

    unit_type VARCHAR(100) NOT NULL,

    description TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (organization_id)
        REFERENCES organizations(organization_id)
        ON DELETE CASCADE,

    FOREIGN KEY (parent_unit_id)
        REFERENCES organization_units(unit_id)
        ON DELETE CASCADE
);