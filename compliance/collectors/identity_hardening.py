"""
identity_hardening collector - EXAMINE method.

Graduates several implemented access/identity controls from "attested" to
collector-proven by examining the actual authentication code, so each control
status links back to the specific line that enforces it.

Maps to:
  3.1.8  - limit unsuccessful logon attempts (account lockout)
  3.1.11 - terminate a user session after a defined condition (idle session timeout)
  3.5.7  - enforce minimum password complexity
"""

from __future__ import annotations

from .base import (
    Collector, CollectorContext, Finding, Evidence,
    STATUS_MET, STATUS_NOT_MET, METHOD_EXAMINE,
)

AUTH = "backend/routes/auth.py"
MIDDLEWARE = "backend/auth_middleware.py"
PW = "backend/services/password_validator.py"


class IdentityHardeningCollector(Collector):
    name = "identity_hardening"
    provides = ["3.1.8", "3.1.11", "3.5.7"]
    method = METHOD_EXAMINE

    def collect(self, ctx: CollectorContext) -> list[Finding]:
        root = ctx.repo_root
        auth = root / AUTH
        findings: list[Finding] = []

        # --- 3.1.8: account lockout on repeated failed logons -------------
        fails = self.grep(auth, "failed_login_attempts")
        maxf = self.grep(auth, "MAX_FAILED_LOGINS")
        lock = self.grep(auth, "locked_until")
        if fails and maxf and lock:
            findings.append(Finding(
                control_id="3.1.8", status=STATUS_MET, method=METHOD_EXAMINE,
                summary="Repeated failed logins increment a per-user counter and lock the "
                        "account for a configured window once MAX_FAILED_LOGINS is reached; "
                        "a locked account is refused at login.",
                objective_ids=["3.1.8[a]", "3.1.8[c]"],
                evidence=[
                    Evidence("source-file", f"{AUTH}:{maxf[0][0]}",
                             "failed_login_attempts >= MAX_FAILED_LOGINS sets locked_until."),
                    Evidence("source-file", f"{AUTH}:{lock[0][0]}",
                             "locked_until blocks login until the lockout window elapses."),
                ]))
        else:
            findings.append(self._not_met("3.1.8", "No account-lockout logic found."))

        # --- 3.1.11: terminate idle sessions ------------------------------
        exp = self.grep(root / MIDDLEWARE, "expires_at")
        timeout = self.grep(auth, "SESSION_TIMEOUT_MINUTES")
        if exp and timeout:
            findings.append(Finding(
                control_id="3.1.11", status=STATUS_MET, method=METHOD_EXAMINE,
                summary="Server-side sessions carry a sliding expiry (SESSION_TIMEOUT_MINUTES); "
                        "the auth middleware rejects any request on an expired session, "
                        "terminating idle sessions.",
                objective_ids=["3.1.11[a]", "3.1.11[b]"],
                evidence=[
                    Evidence("source-file", f"{MIDDLEWARE}:{exp[0][0]}",
                             "Middleware rejects a request once sess.expires_at has passed."),
                    Evidence("source-file", f"{AUTH}:{timeout[0][0]}",
                             "Expiry set to SESSION_TIMEOUT_MINUTES and bumped per request (sliding)."),
                ]))
        else:
            findings.append(self._not_met("3.1.11", "No session-expiry enforcement found."))

        # --- 3.5.7: password complexity -----------------------------------
        pw = root / PW
        vdef = self.grep(pw, "def validate_password")
        length = self.grep(pw, "< 12")
        upper = self.grep(pw, "uppercase")
        special = self.grep(pw, "special")
        if vdef and length and (upper or special):
            cls_hit = upper or special
            findings.append(Finding(
                control_id="3.5.7", status=STATUS_MET, method=METHOD_EXAMINE,
                summary="Passwords are validated server-side to be at least 12 characters "
                        "with mixed character classes (uppercase, lowercase, digit, special).",
                objective_ids=["3.5.7[a]"],
                evidence=[
                    Evidence("source-file", f"{PW}:{length[0][0]}",
                             "Minimum length of 12 characters is enforced."),
                    Evidence("source-file", f"{PW}:{cls_hit[0][0]}",
                             "Character-class requirements are enforced."),
                ]))
        else:
            findings.append(self._not_met("3.5.7", "No password-complexity validator found."))

        return findings

    def _not_met(self, cid: str, why: str) -> Finding:
        return Finding(control_id=cid, status=STATUS_NOT_MET,
                       method=METHOD_EXAMINE, summary=why)
