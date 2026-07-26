CREATE TABLE workspaces (

    workspace_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    name VARCHAR(255) NOT NULL,

    slug VARCHAR(100) NOT NULL UNIQUE,

    description TEXT,

    owner_id UUID NOT NULL,

    organization_id UUID,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_workspaces_owner
        FOREIGN KEY (owner_id)
        REFERENCES users (user_id)
        ON DELETE RESTRICT,

    CONSTRAINT fk_workspaces_organization
        FOREIGN KEY (organization_id)
        REFERENCES organizations (organization_id)
        ON DELETE SET NULL
);

CREATE INDEX idx_workspaces_owner
ON workspaces (owner_id);

CREATE INDEX idx_workspaces_organization
ON workspaces (organization_id);

CREATE TABLE memberships (

    membership_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    workspace_id UUID NOT NULL,

    user_id UUID NOT NULL,

    role VARCHAR(20) NOT NULL DEFAULT 'OWNER',

    status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',

    joined_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT uq_memberships_workspace_user
        UNIQUE (workspace_id, user_id),

    CONSTRAINT fk_memberships_workspace
        FOREIGN KEY (workspace_id)
        REFERENCES workspaces (workspace_id)
        ON DELETE CASCADE,

    CONSTRAINT fk_memberships_user
        FOREIGN KEY (user_id)
        REFERENCES users (user_id)
        ON DELETE CASCADE
);

CREATE INDEX idx_memberships_user
ON memberships (user_id);

CREATE INDEX idx_memberships_workspace
ON memberships (workspace_id);
