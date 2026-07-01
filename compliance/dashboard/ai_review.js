window.AI_REVIEW = {
  "generated_at": "2026-07-01T19:10:56+00:00",
  "dry_run": false,
  "results": [
    {
      "control_id": "3.1.1",
      "engine_status": "met",
      "review": {
        "suggested_verdict": "partial",
        "confidence": "medium",
        "objective_assessments": [
          {
            "objective": "3.1.1[e] - access to the system is limited to authorized users and processes acting on behalf of authorized users",
            "met": false,
            "reason": "The require_auth() decorator (backend/auth_middleware.py:47) demonstrates a mechanism that validates the session and rejects unauthenticated requests with 401, and optionally enforces permission checks returning 403 when the user's role lacks the required permission. This shows a capability for limiting access. However, the evidence does not demonstrate that this decorator is actually applied to system endpoints/handlers, nor how sessions are validated (_validate_session is not shown), nor how permissions/roles are defined and assigned. Without evidence that the control is enforced across the system's access points, the objective is only partially supported.",
            "cites": [
              "backend/auth_middleware.py:47"
            ]
          }
        ],
        "gaps": [
          "No evidence that require_auth() is actually applied to route handlers/endpoints across the system.",
          "Implementation of _validate_session() and _get_session_id() is not shown, so session integrity/expiration cannot be assessed.",
          "No evidence of how user.has_permission() and roles are defined or assigned.",
          "No evidence covering process/service (non-interactive) access, which is part of the control scope."
        ],
        "injection_detected": false,
        "injection_note": ""
      },
      "provenance": {
        "model": "claude-opus-4-8",
        "prompt_sha256": "8ffc718847625cdc80753219593dcbe5ece20ee3586dbaa625be1dc02f922f2f",
        "evidence_sha256": "c052f0e419b984d466166797991efc9b9c7009f692386f9ad654eb59b9078dea",
        "reviewed_at": "2026-07-01T19:07:38+00:00"
      },
      "note": "AI-DRAFTED, PENDING HUMAN REVIEW. Advisory only; does not change any status."
    },
    {
      "control_id": "3.1.2",
      "engine_status": "met",
      "review": {
        "suggested_verdict": "partial",
        "confidence": "medium",
        "objective_assessments": [
          {
            "objective": "3.1.2[b]",
            "met": true,
            "reason": "The evidence demonstrates enforcement of access limits to permitted transactions and functions at two layers. In auth_middleware.py:71-85, require_auth denies requests when the user lacks the required permission (or any_of permissions), returning 403 and logging the denial. In patients.py:148-163, _apply_rbac() restricts data-row access so users without patients.view.all only see patients on their own care teams (or with no team). Together these enforce per-route function-level and row-level access controls.",
            "cites": [
              "backend/auth_middleware.py:71",
              "backend/routes/patients.py:148"
            ]
          }
        ],
        "gaps": [
          "Evidence shows the enforcement mechanism (require_auth decorator and _apply_rbac helper) but does not show that these are consistently applied across all routes/transactions \u2014 no inventory of routes confirming every sensitive endpoint declares a permission or invokes _apply_rbac.",
          "No evidence of how permissions are defined/assigned (role-to-permission mapping) to confirm the set of 'permitted transactions and functions' is authoritatively defined.",
          "The excerpts show two example routes/functions; there is no evidence that _apply_rbac is called in the query paths (the excerpt defines it but does not show it being invoked in the patient listing route)."
        ],
        "injection_detected": false,
        "injection_note": ""
      },
      "provenance": {
        "model": "claude-opus-4-8",
        "prompt_sha256": "2d1fa66d3e080be2a0a4f7b013da5e3372b934e6d6e6575ae780d764c927f34a",
        "evidence_sha256": "e03f1d4c6bf4772c036383d4e24596ed4de2691f8226ba1ca4f900b1a8c0bb2a",
        "reviewed_at": "2026-07-01T19:07:47+00:00"
      },
      "note": "AI-DRAFTED, PENDING HUMAN REVIEW. Advisory only; does not change any status."
    },
    {
      "control_id": "3.1.8",
      "engine_status": "met",
      "review": {
        "suggested_verdict": "satisfies",
        "confidence": "high",
        "objective_assessments": [
          {
            "objective": "3.1.8[a]",
            "met": true,
            "reason": "The code defines a limit on consecutive invalid logon attempts: on each failed password check, failed_login_attempts is incremented, and when it reaches config.MAX_FAILED_LOGINS the account is locked. This demonstrates a configured limit of unsuccessful logon attempts.",
            "cites": [
              "backend/routes/auth.py:61"
            ]
          },
          {
            "objective": "3.1.8[c]",
            "met": true,
            "reason": "When the limit is exceeded, locked_until is set to now + ACCOUNT_LOCKOUT_MINUTES, and the login flow blocks authentication while locked_until is in the future (returns 403 'account locked'). This shows the automated action taken when the limit is reached. Note the exact MAX_FAILED_LOGINS and ACCOUNT_LOCKOUT_MINUTES values are not shown, but the enforcement mechanism is clearly present.",
            "cites": [
              "backend/routes/auth.py:61",
              "backend/routes/auth.py:51"
            ]
          }
        ],
        "gaps": [
          "The concrete configured values for config.MAX_FAILED_LOGINS and config.ACCOUNT_LOCKOUT_MINUTES are not shown, so the actual threshold and lockout duration cannot be independently confirmed.",
          "On successful authentication failed_login_attempts resets to 0 (line 67), which counts consecutive rather than cumulative failures; whether this matches the intended policy is not evidenced.",
          "No evidence that failed_login_attempts is bounded or that repeated re-lock behavior after the window elapses is handled beyond re-incrementing."
        ],
        "injection_detected": false,
        "injection_note": ""
      },
      "provenance": {
        "model": "claude-opus-4-8",
        "prompt_sha256": "2fbf66293a432b96d43836a405a3a5ffad63abcc912cba3cf559d9735b7eb64e",
        "evidence_sha256": "c0d738400b4b24635bb8d9cb764b4233afd451932af6fe2bebef6636ff646e79",
        "reviewed_at": "2026-07-01T19:07:56+00:00"
      },
      "note": "AI-DRAFTED, PENDING HUMAN REVIEW. Advisory only; does not change any status."
    },
    {
      "control_id": "3.1.11",
      "engine_status": "met",
      "review": {
        "suggested_verdict": "partial",
        "confidence": "medium",
        "objective_assessments": [
          {
            "objective": "3.1.11[a]",
            "met": true,
            "reason": "A defined condition for session termination is established: sessions are created with an expires_at value of SESSION_TIMEOUT_MINUTES from creation (auth.py:146), and the cookie max_age matches (auth.py:189). This defines an inactivity/time-based condition that triggers termination.",
            "cites": [
              "backend/routes/auth.py:146",
              "backend/auth_middleware.py:35"
            ]
          },
          {
            "objective": "3.1.11[b]",
            "met": true,
            "reason": "The middleware enforces termination when the condition is met: _validate_session checks if sess.expires_at is past current UTC time and, if so, deletes the session and returns (None, None), causing the request to be rejected (auth_middleware.py:35-38). This automatically terminates the expired session.",
            "cites": [
              "backend/auth_middleware.py:35"
            ]
          }
        ],
        "gaps": [
          "The evidence detail claims expiry is 'bumped per request (sliding)' at auth.py:146, but the cited excerpt only shows session creation in _create_session; no code showing per-request expiry extension is provided. The sliding-renewal behavior is unverifiable from the excerpts.",
          "SESSION_TIMEOUT_MINUTES is a config reference; its actual value is not shown, so whether the defined condition uses an appropriate/organization-approved timeout cannot be confirmed.",
          "The termination logic depends on the session validation being invoked on every protected request; the middleware registration/wiring that guarantees _validate_session runs on all requests is not shown."
        ],
        "injection_detected": false,
        "injection_note": ""
      },
      "provenance": {
        "model": "claude-opus-4-8",
        "prompt_sha256": "ee6d0a1b54470e2a069c926f9f8a86dafd8d6cd16ebdfa94d3ab69b9f3b74865",
        "evidence_sha256": "bb57e54b2cfecd6fba4629a089e6d3981bc70e85cca36eef50ef144ca69cdd51",
        "reviewed_at": "2026-07-01T19:08:05+00:00"
      },
      "note": "AI-DRAFTED, PENDING HUMAN REVIEW. Advisory only; does not change any status."
    },
    {
      "control_id": "3.3.1",
      "engine_status": "met",
      "review": {
        "suggested_verdict": "partial",
        "confidence": "medium",
        "objective_assessments": [
          {
            "objective": "3.3.1[e]",
            "met": true,
            "reason": "Objective 3.3.1[e] requires that audit records be created (retained). The log_access() function constructs an AuditLog row capturing key event attributes (timestamp, user_id, action, resource, status, ip_address, description, tenant_id) and persists it via db.session.add(entry) followed by db.session.commit(), demonstrating creation and storage of an audit record per event.",
            "cites": [
              "backend/services/audit_logger.py:29"
            ]
          },
          {
            "objective": "3.3.1[f]",
            "met": false,
            "reason": "3.3.1[f] concerns retention of audit records for a defined time period to support after-the-fact investigations. The excerpt shows records are created and committed, and includes a hash-chain (prev_hash/entry_hash) which supports integrity, but there is no evidence of a defined retention period, retention policy, or mechanism ensuring records are retained for a required duration. Creation alone does not demonstrate retention duration compliance.",
            "cites": [
              "backend/services/audit_logger.py:29"
            ]
          }
        ],
        "gaps": [
          "No evidence of a defined audit log retention period or retention policy to satisfy 3.3.1[f].",
          "The single excerpt shows only creation/commit of one record; no evidence that log_access() is actually invoked across the relevant event types (login, access, admin actions, etc.).",
          "No evidence of protection against loss (backups) or configuration ensuring records persist for a required duration.",
          "The hash-chain is a per-tenant sequential lookup relying on AuditLog.id ordering; no evidence provided about concurrency handling, but this is tangential to the stated objectives."
        ],
        "injection_detected": false,
        "injection_note": ""
      },
      "provenance": {
        "model": "claude-opus-4-8",
        "prompt_sha256": "49c13eac3cb79ee21f7a8de1a6a1ed702f04626ba2e5b3d6615ccc7625e0fa84",
        "evidence_sha256": "f44ccc756422e990d90db7754db655b5445a7229fbabc0130fe7245abfff8311",
        "reviewed_at": "2026-07-01T19:08:15+00:00"
      },
      "note": "AI-DRAFTED, PENDING HUMAN REVIEW. Advisory only; does not change any status."
    },
    {
      "control_id": "3.3.2",
      "engine_status": "met",
      "review": {
        "suggested_verdict": "partial",
        "confidence": "medium",
        "objective_assessments": [
          {
            "objective": "3.3.2[a]",
            "met": true,
            "reason": "The evidence shows that user_id is included as a field in the audit record content and is part of the hash input (audit_logger.py:9, line 18), demonstrating that actions capture a user identity attribute. This supports the ability to trace an action to a specific user.",
            "cites": [
              "backend/services/audit_logger.py:9"
            ]
          },
          {
            "objective": "3.3.2[b]",
            "met": false,
            "reason": "The provided excerpt only shows a hash-computation helper that concatenates fields including user_id. There is no evidence demonstrating that user_id is guaranteed to be uniquely and reliably populated (e.g., non-null enforcement, mapping to authenticated identities, or non-shared accounts). The 'str(user_id or \"\")' construct actually allows an empty string when user_id is missing, which could undermine unique traceability. No evidence shows how records are written, validated, or how uniqueness of the user is ensured.",
            "cites": [
              "backend/services/audit_logger.py:9"
            ]
          }
        ],
        "gaps": [
          "No evidence that user_id is mandatory/non-null when audit records are created; the code tolerates an empty user_id via 'str(user_id or \"\")'.",
          "No evidence linking user_id to a uniquely authenticated identity (no account provisioning, no prohibition of shared/generic accounts).",
          "No evidence of the actual write path or schema showing user_id is persisted for every logged action.",
          "No evidence covering the full set of auditable actions \u2014 only the hash helper is shown."
        ],
        "injection_detected": false,
        "injection_note": ""
      },
      "provenance": {
        "model": "claude-opus-4-8",
        "prompt_sha256": "12c3ead7ea6a48fd0bb72351cacabe35e6b63b0dd6d2dc1ce7f66f655abaedd1",
        "evidence_sha256": "3041c5b18177bd668cd72539c862fcb13209630f70b6805d298e96d5da3c832f",
        "reviewed_at": "2026-07-01T19:08:24+00:00"
      },
      "note": "AI-DRAFTED, PENDING HUMAN REVIEW. Advisory only; does not change any status."
    },
    {
      "control_id": "3.3.8",
      "engine_status": "met",
      "review": {
        "suggested_verdict": "partial",
        "confidence": "medium",
        "objective_assessments": [
          {
            "objective": "3.3.8[b]",
            "met": true,
            "reason": "The evidence demonstrates a tamper-detection mechanism: _compute_hash() (audit_logger.py:9) builds a SHA-256 hash chain where each entry incorporates the previous entry's hash, so modifying any earlier row invalidates all subsequent hashes. The /api/audit/verify endpoint (audit.py:246) walks the chain, recomputes expected hashes, and reports broken/tampered entries. This provides detection of unauthorized modification to audit information.",
            "cites": [
              "backend/services/audit_logger.py:9",
              "backend/routes/audit.py:246"
            ]
          },
          {
            "objective": "3.3.8[c]",
            "met": false,
            "reason": "The provided material demonstrates DETECTION of modification via a hash chain, but does not clearly demonstrate protection against DELETION or unauthorized access-based prevention. Note a gap in the verification logic: when row.entry_hash is None the loop resets prev_hash to None and continues (audit.py:268-270), meaning entries can be null-hashed to escape the chain, and outright deletion of trailing rows would not necessarily be detected since the chain is rebuilt from remaining rows in id order. The verify endpoint only detects content modification of hashed rows, not deletion of whole entries. No evidence of access controls, WORM storage, or backups protecting against deletion is provided.",
            "cites": [
              "backend/routes/audit.py:246"
            ]
          }
        ],
        "gaps": [
          "No evidence of controls preventing or detecting deletion of entire audit entries (e.g., the chain is rebuilt from surviving rows, so removing trailing rows may go undetected).",
          "The verify logic treats entries with entry_hash == None as chain resets (audit.py:268-270), which could allow tampered/unhashed entries to bypass detection.",
          "No evidence of access controls restricting who can modify or delete audit records at the database/storage layer (require_auth only gates the verify endpoint, not write/delete paths).",
          "No evidence of alerting or automated response when tampering is detected \u2014 verification is on-demand via a GET endpoint only.",
          "No evidence the hash chain covers all fields that matter or that timestamps/IDs cannot be re-sequenced."
        ],
        "injection_detected": false,
        "injection_note": ""
      },
      "provenance": {
        "model": "claude-opus-4-8",
        "prompt_sha256": "eeed571e69ff4519ddfc12c9996f7a04695e09704f23b07fb2929f16175794f9",
        "evidence_sha256": "7e1ab282570bf134086265d971dbaf722f5bb6d65617ca09be6f92bee8c7b473",
        "reviewed_at": "2026-07-01T19:08:36+00:00"
      },
      "note": "AI-DRAFTED, PENDING HUMAN REVIEW. Advisory only; does not change any status."
    },
    {
      "control_id": "3.5.3",
      "engine_status": "met",
      "review": {
        "suggested_verdict": "partial",
        "confidence": "medium",
        "objective_assessments": [
          {
            "objective": "3.5.3[b]",
            "met": false,
            "reason": "The evidence shows pyotp TOTP is imported (mfa.py:4) and that login branches on tenant.mfa_required with user.mfa_enabled (auth.py:71-83), demonstrating a second-factor mechanism exists and is conditionally enforced. However, MFA is gated entirely on a per-tenant toggle (mfa_required) that may be OFF, and the excerpt is truncated before the actual TOTP verification logic, so it cannot be confirmed that MFA is enforced for the relevant account access scope this objective covers (e.g., local/network access to privileged accounts). The provided excerpts are consistent with a MFA capability but do not clearly demonstrate the objective for all required account types.",
            "cites": [
              "backend/routes/mfa.py:4",
              "backend/routes/auth.py:71"
            ],
            "met_note": ""
          },
          {
            "objective": "3.5.3[e]",
            "met": false,
            "reason": "The objective is not restated in the provided material, and the evidence only shows the beginning of the MFA enforcement branch (token creation is cut off) plus a TOTP import. There is no code demonstrating the full verification path, session/token validation completion, or the specific account-access condition this objective targets. The material is insufficient to confirm the objective is met.",
            "cites": [
              "backend/routes/auth.py:71",
              "backend/routes/mfa.py:4"
            ]
          }
        ],
        "gaps": [
          "The TOTP verify/setup logic in mfa.py is not included \u2014 only imports (line 4) are shown, so actual second-factor validation cannot be confirmed.",
          "The auth.py excerpt is truncated at line 83 (MfaPendingToken creation) before the token issuance and any secondary verification flow completes.",
          "MFA is contingent on the per-tenant mfa_required toggle; evidence does not show whether it is enabled for the relevant/privileged accounts, nor a policy requiring it.",
          "No evidence maps the code to which account types (privileged vs. non-privileged, local vs. network) the objectives 3.5.3[b] and 3.5.3[e] specifically require.",
          "The plain-language definitions of objectives 3.5.3[b] and 3.5.3[e] were not provided, limiting precise assessment."
        ],
        "injection_detected": false,
        "injection_note": ""
      },
      "provenance": {
        "model": "claude-opus-4-8",
        "prompt_sha256": "aa8ffb0a6f04a39aace57c77a8bb4abc4ee1a368d06b7fd79e9cde2cc8d9d015",
        "evidence_sha256": "3f070c86830d53df67302643edf23d6143dd603c3a20974a32c796a73c0e5477",
        "reviewed_at": "2026-07-01T19:08:49+00:00"
      },
      "note": "AI-DRAFTED, PENDING HUMAN REVIEW. Advisory only; does not change any status."
    },
    {
      "control_id": "3.5.7",
      "engine_status": "met",
      "review": {
        "suggested_verdict": "partial",
        "confidence": "medium",
        "objective_assessments": [
          {
            "objective": "3.5.7[a]",
            "met": true,
            "reason": "The validate_password function enforces password complexity requirements: minimum length of 12 characters (line 12), at least one uppercase letter (line 15), one lowercase letter (line 18), one number (line 21), and one special character (line 24). This clearly demonstrates minimum password complexity is enforced at the validation function level.",
            "cites": [
              "backend/services/password_validator.py:12",
              "backend/services/password_validator.py:16"
            ]
          }
        ],
        "gaps": [
          "The evidence shows the validate_password function exists and defines complexity rules, but there is no evidence that this function is actually invoked at password creation/change flows (e.g., registration, password reset, admin-set passwords). Without call-site evidence, enforcement across the system cannot be confirmed.",
          "No evidence of the organization-defined complexity policy this maps to (whether 12 chars + 4 character classes matches the required policy).",
          "No evidence covering related complexity aspects if defined by policy, such as prohibited/common-password checks or maximum length handling."
        ],
        "injection_detected": false,
        "injection_note": ""
      },
      "provenance": {
        "model": "claude-opus-4-8",
        "prompt_sha256": "0432c91b4f91a6e7cd3933be8d6a105412b2efe66d3cff3969ba818babef9a01",
        "evidence_sha256": "3156c2db5fd1c7755a3602e356d580f4b6cdb90c5eecbb08166a13dc81d248f3",
        "reviewed_at": "2026-07-01T19:08:56+00:00"
      },
      "note": "AI-DRAFTED, PENDING HUMAN REVIEW. Advisory only; does not change any status."
    },
    {
      "control_id": "3.11.2",
      "engine_status": "met",
      "review": {
        "suggested_verdict": "insufficient",
        "confidence": "high",
        "objective_assessments": [
          {
            "objective": "3.11.2[a]",
            "met": false,
            "reason": "The evidence only notes that a CI workflow has push, pull_request, and schedule triggers. No excerpt or detail shows that a vulnerability scan is actually run, nor what scanner or scope is used. Trigger events alone do not demonstrate that vulnerabilities are scanned.",
            "cites": [
              ".github/workflows/ci.yml"
            ]
          },
          {
            "objective": "3.11.2[d]",
            "met": false,
            "reason": "A 'schedule' trigger is mentioned but with no schedule frequency and no evidence that the scheduled job performs a scan. There is no showing of periodic scanning or scanning when new vulnerabilities arise. No code excerpts are provided to verify any of this.",
            "cites": [
              ".github/workflows/ci.yml"
            ]
          }
        ],
        "gaps": [
          "No code excerpts provided; only a one-line summary of trigger events.",
          "No evidence that any vulnerability scanning tool or step is invoked in the workflow.",
          "Schedule trigger frequency (e.g., cron expression) is not shown, so periodicity cannot be verified.",
          "No evidence linking scan execution to newly arising vulnerabilities (e.g., dependency/database updates)."
        ],
        "injection_detected": false,
        "injection_note": ""
      },
      "provenance": {
        "model": "claude-opus-4-8",
        "prompt_sha256": "9a84a6918e9557927857d6ed2606a3c24c8c3e4ea9d34bb4e87b6961559134ee",
        "evidence_sha256": "ae57d4aa537a4e19b3ad36d0ee2ab9862465f38b635e3b786e60d0263833d0e5",
        "reviewed_at": "2026-07-01T19:09:06+00:00"
      },
      "note": "AI-DRAFTED, PENDING HUMAN REVIEW. Advisory only; does not change any status."
    },
    {
      "control_id": "3.12.1",
      "engine_status": "met",
      "review": {
        "suggested_verdict": "insufficient",
        "confidence": "high",
        "objective_assessments": [
          {
            "objective": "3.12.1 - Periodically assess security controls for effectiveness.",
            "met": false,
            "reason": "The only evidence is a one-line description claiming run.py 'executes all collectors and scores the controls,' but no code excerpts were provided to verify this claim. There is no evidence demonstrating (a) that assessments actually occur, (b) that they are periodic/scheduled, or (c) that control effectiveness is evaluated. The description alone cannot be validated.",
            "cites": [
              "compliance/run.py"
            ]
          }
        ],
        "gaps": [
          "No code excerpts provided to substantiate the claim that run.py executes collectors and scores controls.",
          "No evidence of periodicity or scheduling (e.g., cron, CI schedule) to demonstrate assessments occur on a defined cadence.",
          "No evidence that the assessment evaluates control effectiveness, produces results, or triggers remediation.",
          "No evidence of assessment scope (which controls are covered) or of documented/retained results."
        ],
        "injection_detected": false,
        "injection_note": ""
      },
      "provenance": {
        "model": "claude-opus-4-8",
        "prompt_sha256": "5890e7db25846e572790c0c2143761545ef818cdcda47e697a99fa1062761f0c",
        "evidence_sha256": "c076dee48c67788e34213e6536ab1f8f332f4ac535fbc8fa24c2bea8a231ea2d",
        "reviewed_at": "2026-07-01T19:09:13+00:00"
      },
      "note": "AI-DRAFTED, PENDING HUMAN REVIEW. Advisory only; does not change any status."
    },
    {
      "control_id": "3.12.2",
      "engine_status": "met",
      "review": {
        "suggested_verdict": "insufficient",
        "confidence": "high",
        "objective_assessments": [
          {
            "objective": "3.12.2 - Develop and implement plans of action (POA&M) designed to correct deficiencies and reduce or eliminate vulnerabilities in systems.",
            "met": false,
            "reason": "The only evidence is a one-line description stating that generate_docs.py renders POAM.md and POAM.csv from status.json. No code excerpts were provided, so the actual content, logic, or output of the script cannot be verified. There is no evidence showing that the generated POA&M documents actually track deficiencies, remediation actions, responsible parties, milestones, or completion dates, nor that plans are implemented. The claim is unsubstantiated by any inspectable material.",
            "cites": [
              "compliance/generate_docs.py"
            ]
          }
        ],
        "gaps": [
          "No code excerpts were provided; the referenced generate_docs.py cannot be inspected to confirm it produces a valid POA&M.",
          "No evidence of the structure/content of POAM.md or POAM.csv (e.g., deficiency descriptions, remediation actions, responsible roles, milestones, target/completion dates).",
          "No evidence that status.json contains actual deficiency/vulnerability data feeding the plan.",
          "No evidence of the 'implement' aspect: tracking of remediation progress or closure of items."
        ],
        "injection_detected": false,
        "injection_note": ""
      },
      "provenance": {
        "model": "claude-opus-4-8",
        "prompt_sha256": "99a1900c3bdbf3f6762d07154cef22ac9109fdc6afc38f9bd214cd69b63ee907",
        "evidence_sha256": "fc90c8132923de8f926c4c00b6142281cf780fdc2455607dd764d185f706c5ec",
        "reviewed_at": "2026-07-01T19:09:20+00:00"
      },
      "note": "AI-DRAFTED, PENDING HUMAN REVIEW. Advisory only; does not change any status."
    },
    {
      "control_id": "3.12.3",
      "engine_status": "met",
      "review": {
        "suggested_verdict": "insufficient",
        "confidence": "high",
        "objective_assessments": [
          {
            "objective": "3.12.3 - Monitor security controls on an ongoing basis.",
            "met": false,
            "reason": "The only evidence is a one-line description asserting that a workflow file re-runs assessments daily and commits refreshed evidence. No code excerpts were provided (the excerpts array is empty), so there is nothing to verify the claim. I cannot confirm the schedule trigger, what commands run, that it monitors security controls, or that refreshed evidence is actually committed. The claim in the detail field is an unverified assertion.",
            "cites": [
              ".github/workflows/compliance.yml"
            ]
          }
        ],
        "gaps": [
          "No code excerpt from .github/workflows/compliance.yml is provided; the excerpts array is empty.",
          "No evidence of the actual schedule/cron trigger establishing 'daily' or 'ongoing' cadence.",
          "No evidence of what steps run (which controls are assessed) or that results are committed/retained.",
          "No evidence of alerting, review, or follow-up on findings that would constitute ongoing monitoring."
        ],
        "injection_detected": false,
        "injection_note": ""
      },
      "provenance": {
        "model": "claude-opus-4-8",
        "prompt_sha256": "fce6b14e744df9924e3433e3f2291a234fbcfda851dc05e50e1d5b8d9ee1bff7",
        "evidence_sha256": "8ec5b8a657efb90e9cad2aae36509cdd8620ff65a3663787001ff255e09e5ad1",
        "reviewed_at": "2026-07-01T19:09:27+00:00"
      },
      "note": "AI-DRAFTED, PENDING HUMAN REVIEW. Advisory only; does not change any status."
    },
    {
      "control_id": "3.12.4",
      "engine_status": "met",
      "review": {
        "suggested_verdict": "insufficient",
        "confidence": "high",
        "objective_assessments": [
          {
            "objective": "3.12.4 - Develop and maintain a System Security Plan (SSP) that describes system boundaries, environment of operation, security requirements implementation, and connections/relationships with other systems.",
            "met": false,
            "reason": "The only evidence is a summary claim that 'compliance/generate_docs.py renders SSP.md from status.json.' No code excerpts were provided (the excerpts array is empty), so I cannot verify what the script actually does, what content the generated SSP contains, whether it covers required SSP elements (system boundary, environment of operation, security requirements, system interconnections), or whether the SSP is maintained/updated. A description that a tool 'renders SSP.md' does not demonstrate the plan's content or maintenance."
          }
        ],
        "gaps": [
          "No code excerpt was provided for compliance/generate_docs.py; the claim cannot be verified.",
          "No evidence of the SSP's actual content (system boundary, environment of operation, security requirements implementation, interconnections).",
          "No evidence the SSP is maintained/updated over time (e.g., versioning, review cadence, change history).",
          "No sample or excerpt of the generated SSP.md to confirm it satisfies SSP requirements.",
          "status.json contents and how they map to SSP elements are not shown."
        ],
        "injection_detected": false,
        "injection_note": ""
      },
      "provenance": {
        "model": "claude-opus-4-8",
        "prompt_sha256": "47ffe47a7084dbaaf7b1490648188110c14bee2113e5619e3fb59a3f4961c74f",
        "evidence_sha256": "0514e8cfdd941f70939fd2b845079c895070344e3defa8d09f37b8732f94ffb6",
        "reviewed_at": "2026-07-01T19:09:36+00:00"
      },
      "note": "AI-DRAFTED, PENDING HUMAN REVIEW. Advisory only; does not change any status."
    },
    {
      "control_id": "3.13.1",
      "engine_status": "met",
      "review": {
        "suggested_verdict": "partial",
        "confidence": "medium",
        "objective_assessments": [
          {
            "objective": "3.13.1[a]",
            "met": false,
            "reason": "Objective 3.13.1[a] requires that the external system boundary be defined (in addition to key internal boundaries). The evidence demonstrates good boundary protection controls: a dedicated VPC forms the network boundary (network.tf:2), the ALB security group restricts HTTPS ingress to only the AWS-managed CloudFront origin-facing prefix list and scopes egress to the VPC CIDR (network.tf:178), and comments describe a chain of 3 security groups (ALB -> ECS -> RDS). This clearly shows monitoring/controlling/protecting communications at the ALB boundary. However, the underlying requirement for 3.13.1[a] is that the external system boundary is DEFINED, and the internal boundaries protecting the chain are only asserted in evidence detail (network.tf:168 says '3 security groups chain ALB -> ECS -> RDS') but the ECS and RDS security groups themselves are not shown in any excerpt. The ALB egress rule excerpt is truncated (cuts off at 'from_port = 0') so the egress destination scoping cannot be fully verified from the provided code. The provided material demonstrates the boundary is partially defined and controlled at the ALB, but does not fully substantiate the complete boundary definition claimed.",
            "cites": [
              "infra/network.tf:2",
              "infra/network.tf:178",
              "infra/network.tf:168"
            ]
          }
        ],
        "gaps": [
          "The ECS and RDS security groups referenced in the ALB->ECS->RDS chain (network.tf:168 detail) are not shown in any excerpt; the claim of 3 chained security groups cannot be verified.",
          "The ALB egress rule excerpt (network.tf:178) is truncated at 'from_port = 0'; the actual egress CIDR/destination scoping to the VPC is described in comments but not shown in the rule body.",
          "No evidence of monitoring (flow logs, traffic inspection) is provided\u2014only control/protection via security groups is shown, whereas the control title also references monitoring.",
          "The comment about the default SG allowing all intra-SG traffic (network.tf:12-14) is truncated; whether that default SG is actually locked down is not demonstrated."
        ],
        "injection_detected": false,
        "injection_note": ""
      },
      "provenance": {
        "model": "claude-opus-4-8",
        "prompt_sha256": "d856dc657e5f3120dfe1af87d06e07056fee1390fdc2a786a17211796b946b80",
        "evidence_sha256": "270bf169c3a7811ef8c7b82ccabae2f2a5ba0f242264cc4cad15e8006017ae22",
        "reviewed_at": "2026-07-01T19:09:49+00:00"
      },
      "note": "AI-DRAFTED, PENDING HUMAN REVIEW. Advisory only; does not change any status."
    },
    {
      "control_id": "3.13.5",
      "engine_status": "met",
      "review": {
        "suggested_verdict": "partial",
        "confidence": "medium",
        "objective_assessments": [
          {
            "objective": "3.13.5[a]",
            "met": false,
            "reason": "The evidence shows three distinct subnet tiers are defined in the VPC: a 'public' subnet intended for the ALB, a 'private' subnet for ECS tasks, and an 'isolated' subnet for RDS. This demonstrates that separate subnetworks exist that could physically or logically separate publicly accessible components from the internal network (infra/network.tf:50, :62, :74). However, defining tiers via subnet resources and tags alone does not demonstrate that publicly accessible system components are actually placed on the public subnet and separated from internal components. The excerpts do not include route tables, internet/NAT gateway associations, subnet-to-resource associations (ALB in public, ECS in private, RDS in isolated), or security group / NACL rules. The claim that the isolated subnet has 'no internet route' is asserted in the evidence detail but not shown in the provided code excerpts (the aws_route_table / route associations are not included). Therefore the actual separation of publicly accessible components onto subnetworks is not fully demonstrated.",
            "cites": [
              "infra/network.tf:50",
              "infra/network.tf:62",
              "infra/network.tf:74"
            ]
          }
        ],
        "gaps": [
          "No route table definitions or subnet route-table associations are provided to confirm the public subnet routes to an internet gateway and the isolated subnet has no internet route.",
          "No evidence associating the ALB (publicly accessible component) with the public subnet or the ECS/RDS components with the private/isolated subnets.",
          "No security group or network ACL configuration shown to demonstrate enforced separation between tiers.",
          "The 'no internet route' assertion for the isolated subnet is stated only in the evidence detail, not substantiated by the cited code."
        ],
        "injection_detected": false,
        "injection_note": ""
      },
      "provenance": {
        "model": "claude-opus-4-8",
        "prompt_sha256": "6c6a4c12c23ae099b652c0a4b908e8bff36a2fdc7bf20df50a85f59c3fd63a09",
        "evidence_sha256": "1a9b3c6aa97b7200f595932a7a0bf0f2360d00430d6cc696e3d950354e6d169d",
        "reviewed_at": "2026-07-01T19:09:59+00:00"
      },
      "note": "AI-DRAFTED, PENDING HUMAN REVIEW. Advisory only; does not change any status."
    },
    {
      "control_id": "3.13.6",
      "engine_status": "met",
      "review": {
        "suggested_verdict": "partial",
        "confidence": "medium",
        "objective_assessments": [
          {
            "objective": "3.13.6[a]",
            "met": false,
            "reason": "The excerpts show one security group (the ALB SG) with a single scoped ingress rule allowlisting only HTTPS from AWS's CloudFront origin-facing prefix list. AWS security groups are implicitly deny-by-default (only explicitly permitted traffic is allowed), and the ingress here is a narrow exception, which supports the 'deny by default, allow by exception' principle for this one component. However, the evidence only covers the ALB security group. There is no visibility into egress rules for this SG (the excerpt is truncated at line 185 before the egress block), nor into other security groups, NACLs, or the tiers referenced in the evidence detail ('allowlisted per tier'). The control applies to network traffic broadly, so the provided material does not clearly demonstrate deny-by-default across the environment.",
            "cites": [
              "infra/network.tf:168",
              "infra/network.tf:173"
            ]
          }
        ],
        "gaps": [
          "Egress rules for the ALB security group are not shown (excerpt truncated at line 185 before the egress block); cannot confirm egress is also deny-by-default/scoped.",
          "Only the ALB security group is shown. Evidence detail references 'allowlisting per tier' but no other tier/security group definitions are provided.",
          "No evidence of Network ACLs, which also affect subnet-level default traffic posture.",
          "No confirmation that AWS's implicit deny-all default has not been overridden by an explicit allow-all rule elsewhere in the configuration."
        ],
        "injection_detected": false,
        "injection_note": ""
      },
      "provenance": {
        "model": "claude-opus-4-8",
        "prompt_sha256": "88d8ec380ad1dd0d42dd1318ba92a1cb19425dcd744082c33ff5259582a53014",
        "evidence_sha256": "9f2c03d2347b7077f2eff6dfcebf76f5b1c114cf4e88e78f1e2a41a42aa04ac6",
        "reviewed_at": "2026-07-01T19:10:09+00:00"
      },
      "note": "AI-DRAFTED, PENDING HUMAN REVIEW. Advisory only; does not change any status."
    },
    {
      "control_id": "3.13.8",
      "engine_status": "met",
      "review": {
        "suggested_verdict": "satisfies",
        "confidence": "high",
        "objective_assessments": [
          {
            "objective": "3.13.8[c]",
            "met": true,
            "reason": "The evidence demonstrates cryptographic protection of data in transit across all transmission tiers. The RDS parameter group sets rds.force_ssl=1, rejecting non-TLS database connections (infra/rds.tf:23, lines 30-33). The ALB HTTPS listener on port 443 uses the ELBSecurityPolicy-TLS13-1-2-2021-06 policy, enforcing TLS 1.2/1.3 (infra/alb.tf:109). CloudFront enforces a minimum viewer protocol version of TLSv1.2_2021 (infra/cloudfront.tf:205) and redirects all viewer traffic to HTTPS via viewer_protocol_policy=redirect-to-https (infra/cloudfront.tf:149). The CloudFront-to-origin connection also uses https-only with TLSv1.2 (infra/cloudfront.tf:149, lines 137-138). Together these enforce cryptographic protection at the edge, load balancer, and database layers.",
            "cites": [
              "infra/rds.tf:23",
              "infra/alb.tf:109",
              "infra/cloudfront.tf:205",
              "infra/cloudfront.tf:149"
            ]
          }
        ],
        "gaps": [
          "Evidence does not confirm the ALB has no HTTP (port 80) listener beyond a code comment stating so; the absence is asserted but not directly verifiable from the provided excerpts.",
          "No evidence covers internal service-to-service or backend application-to-RDS traffic beyond the RDS force_ssl setting; client-side TLS certificate validation for the application connecting to RDS is not shown.",
          "The cited objective is only 3.13.8[c]; the specific text of objective [c] is not provided, so the mapping is inferred from the control title (use cryptography to protect CUI during transmission)."
        ],
        "injection_detected": false,
        "injection_note": ""
      },
      "provenance": {
        "model": "claude-opus-4-8",
        "prompt_sha256": "0319ff828df2c948ad70efe5bc501abd985e56abb9ae926e8a959067c6429b3e",
        "evidence_sha256": "2136645358e39391e3ab8a11eee4924e3a79e97531158c11a090bdaecc8e9f83",
        "reviewed_at": "2026-07-01T19:10:19+00:00"
      },
      "note": "AI-DRAFTED, PENDING HUMAN REVIEW. Advisory only; does not change any status."
    },
    {
      "control_id": "3.13.10",
      "engine_status": "met",
      "review": {
        "suggested_verdict": "satisfies",
        "confidence": "medium",
        "objective_assessments": [
          {
            "objective": "3.13.10[a]",
            "met": true,
            "reason": "The evidence demonstrates cryptographic keys are established and managed via IaC. The excerpt at infra/kms.tf:19 shows a customer-managed KMS key resource (aws_kms_key.rds) with a defined description, key policy (root-only), and deletion window. The excerpt at infra/kms.tf:21 shows enable_key_rotation = true, demonstrating key rotation (annual) is managed. Additional keys (e.g., aws_kms_key.secrets at line 32) confirm multiple managed keys. This satisfies establishing and managing cryptographic keys used for protection.",
            "cites": [
              "infra/kms.tf:19",
              "infra/kms.tf:21"
            ]
          }
        ],
        "gaps": [
          "The provided excerpts only fully show one key definition (rds) plus the start of a second (secrets); the claim of 4 KMS keys is not fully visible in the excerpts, only inferred.",
          "No evidence of key generation strength/algorithm selection or documented key management procedures beyond rotation and root-only policy.",
          "The root-only key policy grants kms:* on Resource '*' to the account root; while common, whether key access is appropriately restricted/managed is not fully demonstrated."
        ],
        "injection_detected": false,
        "injection_note": ""
      },
      "provenance": {
        "model": "claude-opus-4-8",
        "prompt_sha256": "cf931bac1e9c1fee7dd7b7c07d85ac6c81ba9e174271257eca30839e7e109bbf",
        "evidence_sha256": "b4d1b2c4bcd12b7599d936d31e6bc98ffee13207eeccfebcc5a7a0dac7ecdc34",
        "reviewed_at": "2026-07-01T19:10:28+00:00"
      },
      "note": "AI-DRAFTED, PENDING HUMAN REVIEW. Advisory only; does not change any status."
    },
    {
      "control_id": "3.13.11",
      "engine_status": "met",
      "review": {
        "suggested_verdict": "partial",
        "confidence": "medium",
        "objective_assessments": [
          {
            "objective": "3.13.11[a]",
            "met": false,
            "reason": "The evidence shows customer-managed AWS KMS keys are defined (infra/kms.tf:19), key rotation is enabled (infra/kms.tf:21), and RDS storage is encrypted at rest with a customer-managed KMS key (infra/rds.tf:85). AWS KMS is backed by FIPS 140-2 validated HSMs, which supports the encryption-at-rest use case. However, the objective requires FIPS-validated cryptography to protect CUI broadly. The evidence only demonstrates encryption at rest for RDS storage/snapshots and Secrets Manager. There is no evidence covering data in transit (TLS/FIPS-mode endpoints), the FIPS-validated status of client-side cryptographic modules, or that all systems processing/storing CUI use FIPS-validated modules. The claim that KMS HSMs are FIPS-validated is asserted in the evidence detail but not independently verifiable from the cited Terraform, and merely referencing a KMS key does not confirm FIPS mode is enforced. Partial coverage of the control."
          }
        ],
        "gaps": [
          "No evidence of FIPS-validated cryptography protecting CUI in transit (e.g., TLS with FIPS-approved ciphers or FIPS-endpoint enforcement).",
          "No independent confirmation of the FIPS 140-2/140-3 CMVP validation status of the KMS module beyond an asserted claim in the evidence detail.",
          "Scope limited to RDS at-rest and Secrets Manager encryption; no evidence covering other systems/data stores that may hold CUI (application servers, backups, object storage, logs).",
          "No evidence of client-side FIPS mode enforcement in the application (Flask app)."
        ],
        "injection_detected": false,
        "injection_note": ""
      },
      "provenance": {
        "model": "claude-opus-4-8",
        "prompt_sha256": "0e66dc622c5f92e286f64208fc1a7e5e9c6270b1877bbc37a0e36bb941dc1a96",
        "evidence_sha256": "9ad52e2681f2b5bce8d73db0981fdc48e0a3f8a8e5d1959fefa4013c6143b8d4",
        "reviewed_at": "2026-07-01T19:10:38+00:00"
      },
      "note": "AI-DRAFTED, PENDING HUMAN REVIEW. Advisory only; does not change any status."
    },
    {
      "control_id": "3.13.16",
      "engine_status": "met",
      "review": {
        "suggested_verdict": "satisfies",
        "confidence": "high",
        "objective_assessments": [
          {
            "objective": "3.13.16[a]",
            "met": true,
            "reason": "The RDS instance sets storage_encrypted=true and binds a customer-managed KMS key (kms_key_id = aws_kms_key.rds.arn) at infra/rds.tf:85-86. The referenced KMS key at infra/kms.tf:19 is defined specifically for RDS encryption at rest ('Encrypts RDS storage and snapshots') with key rotation enabled. Together these demonstrate that CUI stored in the RDS database (including snapshots) is encrypted at rest, satisfying the requirement to protect confidentiality of CUI at rest.",
            "cites": [
              "infra/rds.tf:85",
              "infra/kms.tf:19"
            ]
          }
        ],
        "gaps": [
          "Evidence covers RDS storage at rest only. Other CUI-bearing storage (e.g., S3 buckets, EBS volumes, backups outside RDS-managed snapshots, application logs) is not shown, so full coverage of all CUI at rest cannot be confirmed from this evidence.",
          "The KMS key policy grants kms:* to the account root only; while acceptable, the excerpt does not show whether encryption is enforced/prevented from being disabled, but storage_encrypted=true is set explicitly."
        ],
        "injection_detected": false,
        "injection_note": ""
      },
      "provenance": {
        "model": "claude-opus-4-8",
        "prompt_sha256": "3299d7c0dfabec7b20079da351b73713f36b90d1067ac93a916eeabb4919d053",
        "evidence_sha256": "6e4f84871e40348cdfb2cc354c02a0399c1068bd95fae0a8da51c64ac6b8e9ea",
        "reviewed_at": "2026-07-01T19:10:46+00:00"
      },
      "note": "AI-DRAFTED, PENDING HUMAN REVIEW. Advisory only; does not change any status."
    },
    {
      "control_id": "3.14.1",
      "engine_status": "met",
      "review": {
        "suggested_verdict": "insufficient",
        "confidence": "medium",
        "objective_assessments": [
          {
            "objective": "3.14.1[b]",
            "met": false,
            "reason": "Objective 3.14.1[b] concerns reporting system flaws in a timely manner. The evidence describes 5 scanners in ci.yml that identify flaws (SAST, dependency, IaC, container scanning), which supports identification and arguably surfaces/reports findings in the CI pipeline. However, no code excerpts were provided to corroborate the evidence claims, and there is no demonstration of a defined reporting mechanism or timeliness (e.g., notification, ticketing, or time-bound SLA). The claims cannot be verified against the cited file.",
            "cites": [
              ".github/workflows/ci.yml"
            ],
            "met_note": "unverifiable"
          },
          {
            "objective": "3.14.1[c]",
            "met": false,
            "reason": "Objective 3.14.1[c] concerns correcting system flaws in a timely manner. The evidence states a HIGH/CRITICAL finding fails the build (exit-code 1), blocking merge until corrected, which conceptually supports timely correction by preventing flawed code from merging. However, the excerpts array is empty, so the actual workflow configuration (exit-code gating, severity thresholds) is not provided and cannot be confirmed. No defined remediation timeframe is shown.",
            "cites": [
              ".github/workflows/ci.yml"
            ]
          }
        ],
        "gaps": [
          "No code excerpts were provided; the excerpts array is empty, so the ci.yml evidence claims (scanner configuration and build-failure gating) cannot be independently verified.",
          "No evidence of a timeliness definition or SLA for reporting or correcting flaws (e.g., required remediation window).",
          "No demonstration of a reporting/notification destination (who is notified and how) to satisfy the 'report' aspect of 3.14.1[b].",
          "No evidence of how flaws found outside the CI pipeline (e.g., in already-deployed/production systems) are identified and corrected."
        ],
        "injection_detected": false,
        "injection_note": ""
      },
      "provenance": {
        "model": "claude-opus-4-8",
        "prompt_sha256": "607113ccc4afaee327f5e1a0add949cebb3cb3f47341edad54404d232efb4784",
        "evidence_sha256": "3f153b6b1e8f5801eacdc225dba7cf952d9ba9eca384f2fa489fde367154ae62",
        "reviewed_at": "2026-07-01T19:10:56+00:00"
      },
      "note": "AI-DRAFTED, PENDING HUMAN REVIEW. Advisory only; does not change any status."
    }
  ]
};
