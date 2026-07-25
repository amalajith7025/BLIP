CREATE TABLE organization_industries (

    organization_id UUID NOT NULL,

    industry_id UUID NOT NULL,

    is_primary BOOLEAN NOT NULL DEFAULT FALSE,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (organization_id, industry_id),

    CONSTRAINT fk_org_industry_organization
        FOREIGN KEY (organization_id)
        REFERENCES organizations (organization_id)
        ON DELETE CASCADE,

    CONSTRAINT fk_org_industry_industry
        FOREIGN KEY (industry_id)
        REFERENCES industries (industry_id)
        ON DELETE CASCADE
);

CREATE INDEX idx_org_industry_organization
ON organization_industries (organization_id);

CREATE INDEX idx_org_industry_industry
ON organization_industries (industry_id);