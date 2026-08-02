# Code Review Report: Authorization Refactor

## Overview

This change introduces a centralized authorization layer for the backend while preserving the existing FastAPI + SQLAlchemy architecture. The implementation reuses the existing authentication foundation, adds reusable authorization helpers, and applies them to selected routers and services without redesigning the application.

## 1. Modified files

### Router and service changes
- [backend/app/routers/investigation.py](backend/app/routers/investigation.py)
- [backend/app/routers/organization.py](backend/app/routers/organization.py)
- [backend/app/routers/organization_unit.py](backend/app/routers/organization_unit.py)
- [backend/app/routers/tenant.py](backend/app/routers/tenant.py)
- [backend/app/routers/workspace.py](backend/app/routers/workspace.py)
- [backend/app/services/organization.py](backend/app/services/organization.py)

### New support modules
- [backend/app/auth/authorization.py](backend/app/auth/authorization.py)
- [backend/app/auth/permissions.py](backend/app/auth/permissions.py)
- [backend/tests/test_authorization.py](backend/tests/test_authorization.py)
- [backend/verify_auth.py](backend/verify_auth.py)
- [PROJECT_STATE.md](PROJECT_STATE.md)

## 2. Why each file was modified

### [backend/app/routers/investigation.py](backend/app/routers/investigation.py)
- Added authorization checks before update and delete operations.
- Scoped listing to the authenticated user's organization.
- Kept the existing route structure intact while enforcing access control earlier in the flow.

### [backend/app/routers/organization.py](backend/app/routers/organization.py)
- Routed organization reads and mutations through the new centralized access helpers.
- Made organization listing depend on the current user's organization context.
- Preserved the existing API contract while tightening access behavior.

### [backend/app/routers/organization_unit.py](backend/app/routers/organization_unit.py)
- Applied organization-scoped authorization checks for create, read, update, and delete.
- Ensured updates and deletes are blocked before mutation when authorization fails.
- Reduced ad hoc access checks in the router layer.

### [backend/app/routers/tenant.py](backend/app/routers/tenant.py)
- Standardized the router to rely on the shared authenticated-user dependency.
- Kept tenant routes aligned with the new centralized auth pattern.

### [backend/app/routers/workspace.py](backend/app/routers/workspace.py)
- Switched workspace access handling to the new member/owner dependency helpers.
- Preserved the existing workspace-specific service behavior while making permission checks consistent.

### [backend/app/services/organization.py](backend/app/services/organization.py)
- Added organization scoping for list operations based on the current user.
- Ensured service-level behavior aligns with the authorization rules applied at the router layer.

### [backend/app/auth/authorization.py](backend/app/auth/authorization.py)
- Created the core authorization ruleset for authenticated users, workspace members, workspace owners, organization members, investigation access, and role checks.

### [backend/app/auth/permissions.py](backend/app/auth/permissions.py)
- Created dependency-style helpers so routers can enforce authorization in a thin and reusable way.

### [backend/tests/test_authorization.py](backend/tests/test_authorization.py)
- Added regression tests for the new authorization expectations.

### [backend/verify_auth.py](backend/verify_auth.py)
- Added a lightweight validation script to verify the authorization helpers directly.

### [PROJECT_STATE.md](PROJECT_STATE.md)
- Created as a workspace inventory and implementation-state summary for the backend.

## 3. Before vs. after summary

### Before
- Authorization logic was largely implicit or duplicated across routers.
- Some routes relied on the CRUD layer before authorization constraints were fully enforced.
- Listing endpoints could expose more data than the current user should see.
- The auth behavior was less centralized and harder to extend.

### After
- Authorization rules are centralized in [backend/app/auth/authorization.py](backend/app/auth/authorization.py).
- Dependency-based helpers in [backend/app/auth/permissions.py](backend/app/auth/permissions.py) keep routers thin.
- Access checks now happen before state-changing operations and before returning scoped resources.
- Organization-scoped listings now return only data the current user is allowed to see.

## 4. Architectural decisions

1. Reuse the existing authentication foundation instead of replacing it.
   - The implementation builds on the current-user dependency already present in the backend.

2. Keep the existing layering intact.
   - Routers remain thin, services preserve business logic, and CRUD remains responsible for persistence.

3. Centralize authorization rules.
   - Resource checks and reusable permission semantics are handled in dedicated auth modules rather than being scattered in route handlers.

4. Preserve API compatibility.
   - The public endpoints and response shapes were not redesigned; the primary change is the enforcement of access control.

5. Favor dependency-based enforcement.
   - FastAPI dependencies are used to keep authorization logic readable and consistent.

## 5. New dependencies introduced

### Production code
- No new third-party production dependencies were introduced.

### Internal dependencies
- Routers now depend on [backend/app/auth/permissions.py](backend/app/auth/permissions.py).
- Permission helpers depend on [backend/app/auth/authorization.py](backend/app/auth/authorization.py).
- Some routes now depend on service-level authorization-aware behavior in [backend/app/services/organization.py](backend/app/services/organization.py).

### Testing
- Pytest was installed in the local environment for verification of the new regression tests.

## 6. New authorization flow

The new access-control flow is:

1. A request reaches a route.
2. FastAPI resolves the current user via the existing authentication dependency.
3. A dedicated permission dependency validates the request context, such as:
   - authenticated user
   - workspace member
   - workspace owner
   - organization member
   - investigation access
   - required role
4. If the check passes, the route continues to the service or CRUD layer.
5. If the check fails, the request returns an appropriate HTTP response such as 401 Unauthorized or 403 Forbidden.
6. For mutations, the route checks access before performing the update or delete action.

## 7. Remaining TODOs

- Extend the same pattern to the remaining routers beyond the current set of updated modules.
- Add more end-to-end API tests with FastAPI TestClient for unauthorized, authorized, missing-resource, and list-scoping scenarios.
- Introduce reusable resource dependencies for additional entities beyond organizations, workspaces, investigations, and organization units.
- Refine RBAC support so role checks can scale beyond simple role-name matching.
- Expand list filtering and data scoping to all entities that should be tenant- or organization-restricted.

## 8. Files created

- [PROJECT_STATE.md](PROJECT_STATE.md)
- [backend/app/auth/authorization.py](backend/app/auth/authorization.py)
- [backend/app/auth/permissions.py](backend/app/auth/permissions.py)
- [backend/tests/test_authorization.py](backend/tests/test_authorization.py)
- [backend/verify_auth.py](backend/verify_auth.py)

## 9. Files deleted

- None.

## 10. Files renamed

- None.

## Verification note

The updated authorization behavior was verified locally with:

- `python -m pytest tests/test_authorization.py`

Result: 10 tests passed.
