CREATE TABLE organization_industries (

    organization_id UUID NOT NULL,
    industry_id UUID NOT NULL,

    primary_industry BOOLEAN DEFAULT FALSE,

    PRIMARY KEY (organization_id, industry_id),

    FOREIGN KEY (organization_id)
        REFERENCES organizations(organization_id)
        ON DELETE CASCADE,

    FOREIGN KEY (industry_id)
        REFERENCES industries(industry_id)
        ON DELETE CASCADE
);