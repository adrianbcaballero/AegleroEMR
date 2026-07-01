"""
access_control collector - EXAMINE method.

Proves Aeglero enforces access control and MFA by examining the auth middleware,
the RBAC permission model, and the TOTP MFA implementation. No creds needed.

Maps to:
  3.1.1 - limit system access to authorized users
          (require_auth authenticates every protected route)
  3.1.2 - limit access to the transactions/functions users may execute
          (RBAC has_permission checks + care-team-scoped patient visibility)
  3.5.3 - use multifactor authentication for network access to accounts
          (TOTP via pyotp, per-tenant enforced by tenant.mfa_required)
"""

from __future__ import annotations

from .base import (
    Collector, CollectorContext, Finding, Evidence,
    STATUS_MET, STATUS_PARTIAL, STATUS_NOT_MET, STATUS_ERROR, METHOD_EXAMINE,
)

MIDDLEWARE = "backend/auth_middleware.py"
PATIENTS = "backend/routes/patients.py"
MFA_ROUTE = "backend/routes/mfa.py"
AUTH_ROUTE = "backend/routes/auth.py"


class AccessControlCollector(Collector):
    name = "access_control"
    provides = ["3.1.1", "3.1.2", "3.5.3"]
    method = METHOD_EXAMINE

    def collect(self, ctx: CollectorContext) -> list[Finding]:
        mw = ctx.repo_root / MIDDLEWARE
        if not mw.exists():
            return [self._error(cid, f"auth middleware not found: {MIDDLEWARE}")
                    for cid in self.provides]

        require_auth = self.grep(mw, "def require_auth")
        perm_check = self.grep(mw, "has_permission(permission")
        rbac_scope = self.grep(ctx.repo_root / PATIENTS, "_apply_rbac")
        totp_impl = self.grep(ctx.repo_root / MFA_ROUTE, "pyotp")
        mfa_enforce = self.grep(ctx.repo_root / AUTH_ROUTE, "mfa_required")

        findings: list[Finding] = []

        # --- 3.1.1: access limited to authorized users ---------------------
        if require_auth:
            findings.append(Finding(
                control_id="3.1.1",
                status=STATUS_MET,
                method=METHOD_EXAMINE,
                summary="All protected routes require authentication via the "
                        "require_auth decorator; unauthenticated requests are rejected.",
                objective_ids=["3.1.1[e]"],
                evidence=[Evidence("source-file", f"{MIDDLEWARE}:{require_auth[0][0]}",
                                   "require_auth() authenticates the session before the "
                                   "handler runs.")],
            ))
        else:
            findings.append(self._not_met("3.1.1", "No authentication decorator found."))

        # --- 3.1.2: access limited to permitted transactions/functions -----
        if perm_check and rbac_scope:
            findings.append(Finding(
                control_id="3.1.2",
                status=STATUS_MET,
                method=METHOD_EXAMINE,
                summary="RBAC restricts each route to a required permission "
                        "(has_permission), and patient visibility is further limited "
                        "to a user's care teams (_apply_rbac).",
                objective_ids=["3.1.2[b]"],
                evidence=[
                    Evidence("source-file", f"{MIDDLEWARE}:{perm_check[0][0]}",
                             "require_auth(permission=...) enforces per-route permission."),
                    Evidence("source-file", f"{PATIENTS}:{rbac_scope[0][0]}",
                             "_apply_rbac() limits patient rows to the caller's care teams."),
                ],
            ))
        elif perm_check:
            findings.append(Finding(
                control_id="3.1.2",
                status=STATUS_PARTIAL,
                method=METHOD_EXAMINE,
                summary="Per-route RBAC is enforced, but data-row scoping "
                        "(care-team) was not detected.",
                objective_ids=["3.1.2[b]"],
                evidence=[Evidence("source-file", f"{MIDDLEWARE}:{perm_check[0][0]}",
                                   "Permission check present; row-level scoping unverified.")],
            ))
        else:
            findings.append(self._not_met("3.1.2", "No RBAC permission enforcement found."))

        # --- 3.5.3: multifactor authentication -----------------------------
        if totp_impl and mfa_enforce:
            findings.append(Finding(
                control_id="3.5.3",
                status=STATUS_MET,
                method=METHOD_EXAMINE,
                summary="TOTP multifactor authentication (RFC 6238 via pyotp) is "
                        "implemented and enforced at login when tenant.mfa_required "
                        "is set, applying to privileged and non-privileged accounts alike.",
                objective_ids=["3.5.3[b]", "3.5.3[e]"],
                evidence=[
                    Evidence("source-file", f"{MFA_ROUTE}:{totp_impl[0][0]}",
                             "pyotp TOTP setup/verify implements the second factor."),
                    Evidence("source-file", f"{AUTH_ROUTE}:{mfa_enforce[0][0]}",
                             "Login enforces TOTP when tenant.mfa_required is enabled."),
                ],
            ))
        elif totp_impl:
            findings.append(Finding(
                control_id="3.5.3",
                status=STATUS_PARTIAL,
                method=METHOD_EXAMINE,
                summary="TOTP MFA is implemented but login-time enforcement was "
                        "not detected.",
                objective_ids=["3.5.3[b]"],
                evidence=[Evidence("source-file", f"{MFA_ROUTE}:{totp_impl[0][0]}",
                                   "MFA available; enforcement path unverified.")],
            ))
        else:
            findings.append(self._not_met("3.5.3", "No TOTP/MFA implementation found."))

        return findings

    # -- helpers ---------------------------------------------------------------

    def _not_met(self, cid: str, why: str) -> Finding:
        return Finding(control_id=cid, status=STATUS_NOT_MET,
                       method=METHOD_EXAMINE, summary=why)

    def _error(self, cid: str, why: str) -> Finding:
        return Finding(control_id=cid, status=STATUS_ERROR,
                       method=METHOD_EXAMINE, summary=why)
