ALTER TABLE organizations
    RENAME COLUMN organization_name TO name;

ALTER TABLE organizations
    ADD COLUMN IF NOT EXISTS industry VARCHAR(100),
    ADD COLUMN IF NOT EXISTS timezone VARCHAR(100);

ALTER TABLE organizations
    DROP CONSTRAINT IF EXISTS organizations_status_check;

UPDATE organizations
SET status = CASE status
    WHEN 'ACTIVE' THEN 'Active'
    WHEN 'INACTIVE' THEN 'Archived'
    ELSE status
END;

ALTER TABLE organizations
    ALTER COLUMN status SET DEFAULT 'Active';

ALTER TABLE organizations
    ADD CONSTRAINT organizations_status_check
        CHECK (status IN ('Active', 'Suspended', 'Archived'));

CREATE UNIQUE INDEX IF NOT EXISTS uq_organizations_name
    ON organizations (name);