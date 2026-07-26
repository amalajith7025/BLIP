DEFAULT_TENANT = {
    "tenant_name": "BLIP",
    "legal_name": "BLIP Technologies",
    "subscription_plan": "ENTERPRISE",
    "status": "ACTIVE",
}

DEFAULT_ORGANIZATION = {
    "name": "BLIP",
    "description": "Default organization",
    "status": "Active",
}

DEFAULT_ROLES = [
    {
        "role_name": "Platform Admin",
        "description": (
            "Full platform administration. Can manage tenants, organizations, "
            "platform settings, and all resources."
        ),
    },
    {
        "role_name": "Organization Admin",
        "description": (
            "Manages users, organization settings, and configuration within a "
            "single organization."
        ),
    },
    {
        "role_name": "Workspace Admin",
        "description": (
            "Manages workspaces, investigations, assignments, and operational "
            "administration."
        ),
    },
    {
        "role_name": "Contributor",
        "description": (
            "Creates and edits investigations, findings, analyses, and evidence."
        ),
    },
    {
        "role_name": "Reviewer",
        "description": (
            "Reviews, approves, rejects, and requests changes for investigations "
            "and findings."
        ),
    },
    {
        "role_name": "Viewer",
        "description": (
            "Read-only access to investigations, dashboards, reports, and "
            "analytics."
        ),
    },
]
