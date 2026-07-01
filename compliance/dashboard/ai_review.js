window.AI_REVIEW = {
  "generated_at": "2026-07-01T19:30:25+00:00",
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
            "objective": "3.1.1[e]",
            "met": false,
            "reason": "Objective 3.1.1[e] concerns limiting system access to authorized processes (i.e., ensuring the types of transactions and functions authorized processes/users are permitted to execute are defined and enforced). The excerpt shows require_auth() authenticates the session (calls _validate_session, returns 401 if no valid user) and optionally enforces per-permission and any_of role-based authorization before running the handler. This demonstrates access is limited to authenticated users and, where a permission is specified, to authorized users. However, the evidence only shows the decorator definition; it does not show that authorized *processes* (system-to-system/service accounts) are covered, nor that the decorator is actually applied to protected endpoints, nor how the authorized transactions/functions are defined per role. The specific '[e]' authorized-processes aspect is not clearly demonstrated.",
            "cites": [
              "backend/auth_middleware.py:47"
            ]
          }
        ],
        "gaps": [
          "No evidence that require_auth() is actually applied to endpoints/handlers \u2014 only the decorator definition is shown, not its usage.",
          "No evidence addressing 'authorized processes' (service/system accounts, machine-to-machine access) as distinct from interactive users.",
          "No definition of how permissions/roles map to authorized transactions and functions (has_permission implementation and role definitions not provided).",
          "Implementation of _validate_session is not shown, so the strength of authentication cannot be assessed."
        ],
        "injection_detected": false,
        "injection_note": ""
      },
      "provenance": {
        "model": "claude-opus-4-8",
        "prompt_sha256": "8ffc718847625cdc80753219593dcbe5ece20ee3586dbaa625be1dc02f922f2f",
        "evidence_sha256": "c052f0e419b984d466166797991efc9b9c7009f692386f9ad654eb59b9078dea",
        "reviewed_at": "2026-07-01T19:27:01+00:00"
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
            "met": false,
            "reason": "Objective 3.1.2[b] requires that the types of transactions and functions that authorized users are permitted to execute be limited (enforced). The evidence shows two enforcement mechanisms: (1) require_auth applies a per-route permission check that returns 403 when the user lacks the required permission or any_of permissions (auth_middleware.py:71-85), and (2) _apply_rbac restricts patient row visibility to the caller's care teams unless they hold patients.view.all (patients.py:148-163). These demonstrate that access to functions/data is programmatically limited by permission. However, the provided material does not clearly demonstrate the full scope: there is no evidence identifying WHICH transactions/functions are defined as permitted (i.e., how permissions map to routes across the system), no route decorator examples showing require_auth being applied with specific permissions, and no evidence that this enforcement is applied comprehensively rather than to isolated endpoints. The excerpts show the enforcement primitives but not that they are consistently and completely applied to limit permitted transactions and functions. Marking as not fully met pending that coverage evidence.",
            "cites": [
              "backend/auth_middleware.py:71",
              "backend/routes/patients.py:148"
            ]
          }
        ],
        "gaps": [
          "No evidence showing which specific transactions/functions require which permissions (no route decorator usage examples applying require_auth with a permission).",
          "No evidence of comprehensive application across all routes/functions; only the enforcement primitives and one row-level filter are shown.",
          "No definition of the permission/role model showing that permitted transactions are explicitly enumerated and limited.",
          "No evidence that _apply_rbac is actually invoked in the patient query path (only its definition is shown)."
        ],
        "injection_detected": false,
        "injection_note": ""
      },
      "provenance": {
        "model": "claude-opus-4-8",
        "prompt_sha256": "2d1fa66d3e080be2a0a4f7b013da5e3372b934e6d6e6575ae780d764c927f34a",
        "evidence_sha256": "e03f1d4c6bf4772c036383d4e24596ed4de2691f8226ba1ca4f900b1a8c0bb2a",
        "reviewed_at": "2026-07-01T19:27:11+00:00"
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
            "reason": "The code defines a limit on consecutive invalid logon attempts. Each failed password check increments failed_login_attempts (line 60), and when the count reaches config.MAX_FAILED_LOGINS the account is locked (lines 61-62). This demonstrates a configured limit is enforced.",
            "cites": [
              "backend/routes/auth.py:61"
            ]
          },
          {
            "objective": "3.1.8[c]",
            "met": true,
            "reason": "When the limit is exceeded, the system takes a defined action: locked_until is set to now + ACCOUNT_LOCKOUT_MINUTES (line 62), and subsequent login attempts are blocked while locked_until is in the future (lines 51-53), returning 403. Successful authentication resets the counter and clears the lock (lines 67-68).",
            "cites": [
              "backend/routes/auth.py:61",
              "backend/routes/auth.py:51"
            ]
          }
        ],
        "gaps": [
          "The actual values of MAX_FAILED_LOGINS and ACCOUNT_LOCKOUT_MINUTES are not shown, so it cannot be confirmed the configured thresholds match organizational policy.",
          "No evidence that the counter is only reset on successful auth over a defined period (though line 67 shows reset on success); reset-window semantics are not fully documented."
        ],
        "injection_detected": false,
        "injection_note": ""
      },
      "provenance": {
        "model": "claude-opus-4-8",
        "prompt_sha256": "2fbf66293a432b96d43836a405a3a5ffad63abcc912cba3cf559d9735b7eb64e",
        "evidence_sha256": "c0d738400b4b24635bb8d9cb764b4233afd451932af6fe2bebef6636ff646e79",
        "reviewed_at": "2026-07-01T19:27:18+00:00"
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
            "reason": "The condition for terminating a session is defined: a session is considered expired when sess.expires_at is earlier than the current UTC time. The expiry is set at session creation to SESSION_TIMEOUT_MINUTES from now (auth.py:146), establishing an inactivity/timeout condition as the defined termination trigger.",
            "cites": [
              "backend/routes/auth.py:146",
              "backend/auth_middleware.py:35"
            ]
          },
          {
            "objective": "3.1.11[b]",
            "met": true,
            "reason": "The session is actually terminated when the defined condition is met: on validation, if sess.expires_at has passed, the session is deleted from the database and (None, None) is returned so the request is rejected (auth_middleware.py:35-38). This demonstrates enforcement of termination.",
            "cites": [
              "backend/auth_middleware.py:35"
            ]
          }
        ],
        "gaps": [
          "The evidence detail for auth.py:146 states expiry is 'bumped per request (sliding)', but the provided _create_session excerpt only sets expiry at session creation and does not show any per-request update of expires_at. No excerpt demonstrates the sliding-renewal logic, so the actual timeout behavior (idle vs. absolute) cannot be confirmed from the code provided.",
          "The actual value of SESSION_TIMEOUT_MINUTES is not shown, so whether the defined condition is reasonable/appropriate cannot be verified.",
          "No evidence shows where _validate_session is invoked in the middleware chain to confirm it runs on every protected request; the excerpt is labeled auth_middleware.py but only shows the helper function."
        ],
        "injection_detected": false,
        "injection_note": ""
      },
      "provenance": {
        "model": "claude-opus-4-8",
        "prompt_sha256": "ee6d0a1b54470e2a069c926f9f8a86dafd8d6cd16ebdfa94d3ab69b9f3b74865",
        "evidence_sha256": "bb57e54b2cfecd6fba4629a089e6d3981bc70e85cca36eef50ef144ca69cdd51",
        "reviewed_at": "2026-07-01T19:27:28+00:00"
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
            "reason": "Objective 3.3.1[e] requires that audit records are created (generated). The log_access() function at backend/services/audit_logger.py:29 constructs an AuditLog row capturing timestamp, user_id, action, resource, status, ip_address, and description, and adds it via db.session.add(entry), demonstrating creation of audit records for each event.",
            "cites": [
              "backend/services/audit_logger.py:29"
            ]
          },
          {
            "objective": "3.3.1[f]",
            "met": true,
            "reason": "Objective 3.3.1[f] requires that audit records are retained. The function commits the entry to the database (db.session.commit() at line 60), persisting each record. The per-tenant hash chain (prev_hash/entry_hash) additionally supports integrity of retained records. However, no evidence of a defined retention period or protection against deletion/overwrite is provided, so retention is only partially demonstrated.",
            "cites": [
              "backend/services/audit_logger.py:29"
            ]
          }
        ],
        "gaps": [
          "No evidence that log_access() is actually invoked across the required event types; only the function definition is shown, not its callers.",
          "No evidence of a defined audit record retention period or retention policy enforcement.",
          "No evidence of error handling/durability if db.session.commit() fails (records could be lost silently).",
          "The hash chain suggests integrity intent, but there is no evidence of chain verification or tamper detection being enforced."
        ],
        "injection_detected": false,
        "injection_note": ""
      },
      "provenance": {
        "model": "claude-opus-4-8",
        "prompt_sha256": "49c13eac3cb79ee21f7a8de1a6a1ed702f04626ba2e5b3d6615ccc7625e0fa84",
        "evidence_sha256": "f44ccc756422e990d90db7754db655b5445a7229fbabc0130fe7245abfff8311",
        "reviewed_at": "2026-07-01T19:27:37+00:00"
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
            "reason": "The excerpt at audit_logger.py:9 shows user_id is included as a content field in each audit record (line 18) and is part of the hashed payload. This demonstrates that audit records capture the individual user associated with an action, supporting unique traceability of actions to users.",
            "cites": [
              "backend/services/audit_logger.py:9"
            ]
          },
          {
            "objective": "3.3.2[b]",
            "met": false,
            "reason": "The provided code shows only the hash computation function. There is no evidence demonstrating that user_id values are themselves unique or bound to distinct authenticated individuals (e.g., that user IDs are non-reusable, mapped to real identities, or protected against shared/generic accounts). The hash chain provides tamper-detection but does not by itself establish that each action is uniquely traceable to a specific user. Additional evidence (user identity management, unique account enforcement, actual record-writing code populating user_id) is needed.",
            "cites": [
              "backend/services/audit_logger.py:9"
            ]
          }
        ],
        "gaps": [
          "No evidence that user_id uniquely identifies a distinct individual (no user account uniqueness/non-reuse controls shown).",
          "No evidence of the code that actually writes audit records and reliably populates user_id for every action.",
          "user_id is coerced with str(user_id or \"\") meaning a null/empty user_id is permitted and hashes to an empty string, which could allow non-attributable actions.",
          "No evidence covering all auditable action types are captured with user attribution."
        ],
        "injection_detected": false,
        "injection_note": ""
      },
      "provenance": {
        "model": "claude-opus-4-8",
        "prompt_sha256": "12c3ead7ea6a48fd0bb72351cacabe35e6b63b0dd6d2dc1ce7f66f655abaedd1",
        "evidence_sha256": "3041c5b18177bd668cd72539c862fcb13209630f70b6805d298e96d5da3c832f",
        "reviewed_at": "2026-07-01T19:27:46+00:00"
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
            "reason": "The evidence demonstrates a tamper-detection mechanism protecting against unauthorized modification. _compute_hash() builds a SHA-256 hash chain where each entry incorporates the previous entry's hash (audit_logger.py:9), so altering any earlier row invalidates every subsequent hash. GET /api/audit/verify walks the chain and reports modification of any recorded field (audit.py:246). This provides detection of unauthorized modification.",
            "cites": [
              "backend/services/audit_logger.py:9",
              "backend/routes/audit.py:246"
            ]
          },
          {
            "objective": "3.3.8[c]",
            "met": true,
            "reason": "The verify endpoint documentation states it detects deletion of rows anywhere except the tail, because the following row's prev_hash stops matching, and treats a NULL entry_hash as an anomaly rather than a legitimate reset (audit.py:246). The hash chain design inherently exposes deletions. However, the excerpt is truncated mid-sentence, and there is no evidence of protection against tail deletion/truncation, which is a residual gap.",
            "cites": [
              "backend/services/audit_logger.py:9",
              "backend/routes/audit.py:246"
            ]
          }
        ],
        "gaps": [
          "The audit.py:246 excerpt is truncated mid-sentence; the actual chain-walking and verification logic (loop, comparison, response) is not shown, so the claim that verify correctly reports tampering is not fully demonstrated by code.",
          "By its own documentation, the mechanism only detects deletions 'anywhere except the tail' \u2014 deletion/truncation of the most recent rows is not detected, and no compensating control (e.g., external anchoring, sequence counters, write-once storage) is shown.",
          "No evidence shows the audit records themselves are stored on protected/immutable/access-controlled storage; the hash chain only provides detection, not prevention of modification or deletion.",
          "No evidence that the verify endpoint is actually invoked/monitored, so tampering detection depends on someone running it; no automated alerting shown."
        ],
        "injection_detected": false,
        "injection_note": ""
      },
      "provenance": {
        "model": "claude-opus-4-8",
        "prompt_sha256": "3aea10f438c17433d51f5cc65bc47a1ad18cded03538cf604008e2837b38d835",
        "evidence_sha256": "7e1ab282570bf134086265d971dbaf722f5bb6d65617ca09be6f92bee8c7b473",
        "reviewed_at": "2026-07-01T19:27:58+00:00"
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
            "reason": "The excerpts show a TOTP second factor exists (pyotp import at mfa.py:4) and that login enforces TOTP when tenant.mfa_required is set and user.mfa_enabled (auth.py:75). However, MFA is governed entirely by a per-tenant toggle (auth.py:70-73), so MFA is only conditionally enforced. Without evidence of how account types are classified (e.g., local/network access, privileged vs non-privileged) or that the required accounts actually have the toggle enabled, the provided material does not clearly demonstrate that MFA is established/implemented for the required accounts.",
            "cites": [
              "backend/routes/mfa.py:4",
              "backend/routes/auth.py:71"
            ]
          },
          {
            "objective": "3.5.3[e]",
            "met": false,
            "reason": "The excerpts partially support enforcement of MFA at login (auth.py:75 branches to TOTP when tenant.mfa_required and user.mfa_enabled). But the comments note that MFA is skipped when the tenant toggle is off even if the user configured it (auth.py:72), and the excerpt is cut off before the actual verification path completes. The full TOTP verify logic (mfa.py verify endpoint) is not shown, so successful second-factor verification enforcement cannot be confirmed from the provided evidence.",
            "cites": [
              "backend/routes/auth.py:71",
              "backend/routes/mfa.py:4"
            ]
          }
        ],
        "gaps": [
          "No mapping between the two cited objectives (3.5.3[b], [e]) and the account categories (local/network, privileged/non-privileged) they govern, so it cannot be confirmed MFA applies to the required accounts.",
          "The mfa.py excerpt only shows imports (lines 1-16); the actual TOTP setup and verify logic that would demonstrate second-factor validation is not included.",
          "The auth.py excerpt is truncated at line 83 before the MfaPendingToken creation and the TOTP verification flow completes.",
          "No evidence that tenant.mfa_required is actually enabled for any tenant/account; enforcement is entirely conditional on an operator-controlled toggle.",
          "No evidence of TOTP secret storage security, code window/validity, or replay protection."
        ],
        "injection_detected": false,
        "injection_note": ""
      },
      "provenance": {
        "model": "claude-opus-4-8",
        "prompt_sha256": "aa8ffb0a6f04a39aace57c77a8bb4abc4ee1a368d06b7fd79e9cde2cc8d9d015",
        "evidence_sha256": "3f070c86830d53df67302643edf23d6143dd603c3a20974a32c796a73c0e5477",
        "reviewed_at": "2026-07-01T19:28:11+00:00"
      },
      "note": "AI-DRAFTED, PENDING HUMAN REVIEW. Advisory only; does not change any status."
    },
    {
      "control_id": "3.5.7",
      "engine_status": "met",
      "review": {
        "suggested_verdict": "satisfies",
        "confidence": "medium",
        "objective_assessments": [
          {
            "objective": "3.5.7[a]",
            "met": true,
            "reason": "The validate_password function enforces minimum password complexity: a minimum length of 12 characters (line 12), and character-class requirements for uppercase (line 15), lowercase (line 18), digits (line 21), and special characters (line 24). Each unmet requirement returns False with an error message, demonstrating enforcement of complexity rules as required by the control.",
            "cites": [
              "backend/services/password_validator.py:12",
              "backend/services/password_validator.py:16"
            ]
          }
        ],
        "gaps": [
          "Evidence shows the validation function exists but does not demonstrate it is actually invoked at all password-setting entry points (e.g., registration, password change, admin reset). Enforcement in code paths is not verified.",
          "No evidence of the organization's defined complexity policy to confirm these specific rules (length 12, four character classes) match the required minimum."
        ],
        "injection_detected": false,
        "injection_note": ""
      },
      "provenance": {
        "model": "claude-opus-4-8",
        "prompt_sha256": "0432c91b4f91a6e7cd3933be8d6a105412b2efe66d3cff3969ba818babef9a01",
        "evidence_sha256": "3156c2db5fd1c7755a3602e356d580f4b6cdb90c5eecbb08166a13dc81d248f3",
        "reviewed_at": "2026-07-01T19:28:18+00:00"
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
            "reason": "The evidence only lists trigger types (push, pull_request, schedule) for a CI workflow file. There are no code excerpts showing that any vulnerability scanning tool or step actually runs. A schedule trigger alone does not demonstrate that vulnerabilities are scanned periodically.",
            "cites": [
              ".github/workflows/ci.yml"
            ]
          },
          {
            "objective": "3.11.2[d]",
            "met": false,
            "reason": "No evidence shows scanning is performed when new vulnerabilities are identified. The push/pull_request/schedule triggers do not establish a scan on new-vulnerability events, and no scanning step or tool is provided in any excerpt.",
            "cites": [
              ".github/workflows/ci.yml"
            ]
          }
        ],
        "gaps": [
          "No code excerpts provided; the excerpts array is empty, so the actual workflow content cannot be verified.",
          "No evidence identifying a vulnerability scanning tool or step (e.g., dependency scanner, SAST, container scan).",
          "Schedule trigger cadence (frequency of periodic scans) is not specified.",
          "No evidence linking scanning to the emergence of newly identified vulnerabilities.",
          "No evidence of scan results, reporting, or remediation tracking."
        ],
        "injection_detected": false,
        "injection_note": ""
      },
      "provenance": {
        "model": "claude-opus-4-8",
        "prompt_sha256": "9a84a6918e9557927857d6ed2606a3c24c8c3e4ea9d34bb4e87b6961559134ee",
        "evidence_sha256": "ae57d4aa537a4e19b3ad36d0ee2ab9862465f38b635e3b786e60d0263833d0e5",
        "reviewed_at": "2026-07-01T19:28:25+00:00"
      },
      "note": "AI-DRAFTED, PENDING HUMAN REVIEW. Advisory only; does not change any status."
    },
    {
      "control_id": "3.12.1",
      "engine_status": "met",
      "review": {
        "suggested_verdict": "satisfies",
        "confidence": "high",
        "objective_assessments": [
          {
            "objective": "3.12.1",
            "met": true,
            "reason": "The evidence demonstrates a periodic, automated assessment of security controls for effectiveness. run_collectors() iterates over the full collector registry (ALL_COLLECTORS) each run, evaluating every registered control against the system (run.py:73, 77). The collected findings are then scored via scorer.score() to compute the SPRS summary (run.py:144), which measures control posture/effectiveness. The scheduled GitHub workflow re-runs the assessment on a defined cadence (daily at 07:17 UTC) plus on push and manual dispatch, establishing the periodic nature (compliance.yml:9). Together these show controls are periodically assessed and results scored.",
            "cites": [
              "compliance/run.py:73",
              "compliance/run.py:77",
              "compliance/run.py:144",
              ".github/workflows/compliance.yml:9"
            ]
          }
        ],
        "gaps": [
          "Evidence shows assessments run and are scored, but does not directly show remediation or human review of ineffective controls (though the workflow comment mentions failing on posture drift, that logic is not in the provided excerpts).",
          "The definition of 'effectiveness' rests on the scorer's computation, but the scoring logic itself (scorer.score) is not included in the excerpts, so the depth/rigor of the effectiveness evaluation cannot be fully verified.",
          "For controls without a real collector, a disposition finding is synthesized from the catalog type (run.py:142); such controls are not actively tested each run, only assigned a static disposition."
        ],
        "injection_detected": false,
        "injection_note": ""
      },
      "provenance": {
        "model": "claude-opus-4-8",
        "prompt_sha256": "d4b47a54ac07e11469a326ef994dc35be2dd03d9632f5142c66f5a478dfdc2dc",
        "evidence_sha256": "f0036b6e3f957c19fbc371883979882aff50a4a6d22b028b4b6b98937e691ce1",
        "reviewed_at": "2026-07-01T19:28:35+00:00"
      },
      "note": "AI-DRAFTED, PENDING HUMAN REVIEW. Advisory only; does not change any status."
    },
    {
      "control_id": "3.12.2",
      "engine_status": "met",
      "review": {
        "suggested_verdict": "satisfies",
        "confidence": "medium",
        "objective_assessments": [
          {
            "objective": "3.12.2",
            "met": true,
            "reason": "The evidence demonstrates both development and implementation of a POA&M process. _poam_rows() (line 197) selects open/unmet controls and builds structured rows that include each weakness, its status, a remediation hint, and a milestone/scheduled completion date (lines 204-218) \u2014 this is the substance of a plan of action. render_poam() (line 223) produces a human-readable POA&M.md that lists open items, SPRS points at risk, weaknesses, remediation, and scheduled completion dates in a table (lines 244-250). write_poam_csv() (line 254) exports the same fields to POAM.csv for assessor/spreadsheet tooling. Together these cover developing the plan (identifying deficiencies, remediation, and milestones) and implementing it via generated, regenerable artifacts.",
            "cites": [
              "compliance/generate_docs.py:197",
              "compliance/generate_docs.py:223",
              "compliance/generate_docs.py:254"
            ]
          }
        ],
        "gaps": [
          "Evidence shows generation of the POA&M artifacts but not that they are actually reviewed, tracked to closure, or assigned to a responsible owner over time (the text at line 236-238 references an 'owner' but no code confirms owner assignment).",
          "The definitions of POAM_STATUSES, _remediation_hint(), and _milestone() are not included, so the correctness of which controls become POA&M items and how milestone dates are derived cannot be independently verified.",
          "No evidence that the generated POA&M is periodically updated/regenerated as part of an operational process beyond the code capability itself."
        ],
        "injection_detected": false,
        "injection_note": ""
      },
      "provenance": {
        "model": "claude-opus-4-8",
        "prompt_sha256": "30648c7b16612bde7871d4b65c19cff6ec4d905de5a7eb79fb740cc4942b4665",
        "evidence_sha256": "bc136ce903bfb4db34736ecfbdc61ab85dbdc4df09914d069852359b5d23ca1e",
        "reviewed_at": "2026-07-01T19:28:45+00:00"
      },
      "note": "AI-DRAFTED, PENDING HUMAN REVIEW. Advisory only; does not change any status."
    },
    {
      "control_id": "3.12.3",
      "engine_status": "met",
      "review": {
        "suggested_verdict": "partial",
        "confidence": "medium",
        "objective_assessments": [
          {
            "objective": "3.12.3",
            "met": true,
            "reason": "The workflow is configured with a schedule trigger (cron '17 7 * * *', daily at 07:17 UTC) plus push-on-main and manual dispatch triggers, demonstrating that a compliance assessment runs on an ongoing/recurring basis rather than only on demand. This provides evidence of automated ongoing monitoring cadence. However, the excerpts only show the trigger configuration (the 'on:' block); the actual job steps that perform the assessment, evaluate control posture, and report/act on results are not included in the provided evidence, so full verification of what is monitored and how results are handled is not possible from this material alone.",
            "cites": [
              ".github/workflows/compliance.yml:9",
              ".github/workflows/compliance.yml:8"
            ]
          }
        ],
        "gaps": [
          "Evidence shows only the workflow trigger configuration (the 'on:' block), not the job steps that actually perform the security control assessment.",
          "No evidence of what specific security controls are monitored, how drift is detected, or how/where results are reported or acted upon (the 'jobs:' section header appears at line 21 but its contents are not provided).",
          "No evidence confirming the scheduled workflow is enabled/active and actually executing successfully on the stated cadence (e.g., run history or logs)."
        ],
        "injection_detected": false,
        "injection_note": ""
      },
      "provenance": {
        "model": "claude-opus-4-8",
        "prompt_sha256": "2603e5b988694ec0331d110f04276ac194e7a4abed8a97cef2d54e4568d9ee09",
        "evidence_sha256": "6c04f2b22be01d264147c0168746bd7cf6784a9ae7624b79f4829d1cf9c5e550",
        "reviewed_at": "2026-07-01T19:28:54+00:00"
      },
      "note": "AI-DRAFTED, PENDING HUMAN REVIEW. Advisory only; does not change any status."
    },
    {
      "control_id": "3.12.4",
      "engine_status": "met",
      "review": {
        "suggested_verdict": "partial",
        "confidence": "medium",
        "objective_assessments": [
          {
            "objective": "3.12.4 - Develop and maintain a System Security Plan (SSP).",
            "met": false,
            "reason": "The evidence shows an SSP is *developed* (generated): render_ssp() at compliance/generate_docs.py:115 renders SSP.md with a header, scope note, and (per the detail) one implementation statement per satisfied control, drawing on human-approved narratives via _load_approved(). SSP_STATUSES at :38 defines which control dispositions (met, partial, inherited, na, manual, attested, policy) are included. This demonstrates the generation/development mechanism. However, the objective also requires that the SSP be *maintained* and that it describe the required content elements (system boundary, environment of operation, security requirements, and relationships/connections with other systems). The excerpts only show the document header, an auto-generated/regenerate note, and a scope note; they do not show the body content covering system boundary, operating environment, connections, or evidence that the plan is periodically updated/reviewed. The mechanism to regenerate from status.json suggests maintainability but is not itself demonstrated as an ongoing maintenance process.",
            "cites": [
              "compliance/generate_docs.py:115",
              "compliance/generate_docs.py:38"
            ]
          }
        ],
        "gaps": [
          "No evidence of the SSP's required content elements: system boundary, environment of operation, and relationships/connections with other systems.",
          "No evidence that the SSP is periodically reviewed/updated (the 'maintain' half of the objective) beyond a comment instructing regeneration.",
          "The cited code excerpts show only the SSP document header/preamble, not the per-control implementation statements described in the evidence detail.",
          "No evidence showing an actual generated SSP.md output or that render_ssp is invoked on a defined cadence."
        ],
        "injection_detected": false,
        "injection_note": ""
      },
      "provenance": {
        "model": "claude-opus-4-8",
        "prompt_sha256": "0dc725db54795297445be556ef32942f32bd52609e03375dbb5c16e85b534555",
        "evidence_sha256": "78b988023c79a52fe6740775964c4defc2dc03095ba6023120740afda502d898",
        "reviewed_at": "2026-07-01T19:29:03+00:00"
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
            "reason": "Objective 3.13.1[a] requires that the external system boundary and key internal boundaries be defined/identified, and that communications at those boundaries be monitored, controlled, and protected. The evidence demonstrates good boundary controls: a dedicated VPC forms the network boundary (network.tf:2), the ALB ingress is restricted to the AWS-managed CloudFront origin-facing prefix list so only CloudFront can reach it (network.tf:178, network.tf:159-160), and the excerpts reference a security-group chain ALB->ECS->RDS (network.tf:168). This clearly shows communications being *controlled and protected* at the external boundary. However, the provided material only fully shows the ALB security group ingress and a partial egress rule; the actual ECS and RDS security groups claimed in the ALB->ECS->RDS chain are not included in the excerpts (evidence at network.tf:168 asserts '3 security groups chain' but the excerpt only contains the ALB SG). There is also no evidence of *monitoring* at the boundary (e.g., VPC flow logs, WAF, IDS/IPS, logging), which 3.13.1 explicitly requires ('monitor'). The ALB egress rule is also truncated mid-definition. Because the monitoring aspect is unsupported and the internal-boundary security groups are asserted but not shown, the objective is not fully demonstrated.",
            "cites": [
              "infra/network.tf:2",
              "infra/network.tf:178",
              "infra/network.tf:168"
            ]
          }
        ],
        "gaps": [
          "No evidence of monitoring at the boundary (e.g., VPC flow logs, WAF, IDS/IPS, or logging) as required by 3.13.1's 'monitor' element.",
          "The ALB->ECS->RDS security-group chain is asserted in evidence (network.tf:168) but the ECS and RDS security groups themselves are not included in any excerpt; only the ALB SG is shown.",
          "The ALB egress rule (network.tf:188-190) is truncated, so scoping of egress to the VPC CIDR cannot be fully verified from the provided code.",
          "The comment at network.tf:12-14 notes a default VPC security group that allows all intra-SG traffic; the excerpt is cut off before confirming its rules are replaced/locked down, leaving a potential unaddressed path."
        ],
        "injection_detected": false,
        "injection_note": ""
      },
      "provenance": {
        "model": "claude-opus-4-8",
        "prompt_sha256": "d856dc657e5f3120dfe1af87d06e07056fee1390fdc2a786a17211796b946b80",
        "evidence_sha256": "270bf169c3a7811ef8c7b82ccabae2f2a5ba0f242264cc4cad15e8006017ae22",
        "reviewed_at": "2026-07-01T19:29:15+00:00"
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
            "objective": "3.13.5[a] - publicly accessible system components are separated (via subnetworks) from internal networks",
            "met": false,
            "reason": "The evidence demonstrates that three distinct subnet tiers are defined: a public subnet tagged Tier=public with map_public_ip_on_launch=false (network.tf:39-52), a private subnet tier for ECS tasks (network.tf:54-64), and an isolated subnet tier for RDS (network.tf:66-76). This shows structural separation of subnetworks by tier. However, the objective requires that publicly accessible components are actually placed in the public subnet and separated from internal ones. The excerpts only show subnet resource definitions and tags; they do not show route tables, internet/NAT gateway associations, or which components (ALB, ECS, RDS) are actually deployed into each subnet. The claim that the isolated subnet has 'no internet route' (evidence detail for network.tf:74) is not substantiated by any route-table code in the excerpts. Thus separation is defined by naming/tags but the enforcing configuration (routing and resource-to-subnet placement) is not shown.",
            "cites": [
              "infra/network.tf:50",
              "infra/network.tf:62",
              "infra/network.tf:74"
            ]
          }
        ],
        "gaps": [
          "No route table definitions or associations shown to confirm the public subnet routes to an internet gateway and the private/isolated subnets do not.",
          "No evidence showing which components are actually deployed into each subnet (ALB in public, ECS in private, RDS in isolated) \u2014 placement is only implied by tag names and comments.",
          "The 'no internet route' claim for the isolated subnet is asserted in the evidence detail but not backed by any routing code in the excerpts.",
          "No internet gateway resource shown to confirm the public tier is the internet-facing boundary."
        ],
        "injection_detected": false,
        "injection_note": ""
      },
      "provenance": {
        "model": "claude-opus-4-8",
        "prompt_sha256": "6c6a4c12c23ae099b652c0a4b908e8bff36a2fdc7bf20df50a85f59c3fd63a09",
        "evidence_sha256": "1a9b3c6aa97b7200f595932a7a0bf0f2360d00430d6cc696e3d950354e6d169d",
        "reviewed_at": "2026-07-01T19:29:26+00:00"
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
            "reason": "The excerpts show one security group (the ALB SG) using deny-by-default behavior: AWS security groups implicitly deny all ingress not explicitly allowed, and here only a single scoped HTTPS (443) ingress rule restricted to the CloudFront managed prefix list is added. This demonstrates deny-by-default/allow-by-exception for the ALB tier. However, the objective requires the deny-by-default posture across network traffic generally, and the evidence only covers one SG's ingress. There is no evidence for egress rules (the excerpt is cut off at the egress comment), no evidence for other tiers/SGs (ECS tasks, databases), no evidence of the VPC-level default security group being locked down, and no evidence of network ACLs. The single-tier evidence is insufficient to conclude the environment-wide default-deny posture.",
            "cites": [
              "infra/network.tf:168",
              "infra/network.tf:173"
            ]
          }
        ],
        "gaps": [
          "No evidence of egress rules for the ALB SG (excerpt truncated at line 185 before the egress block).",
          "No evidence for other network tiers (ECS tasks, databases) or their security groups.",
          "No evidence that the VPC's default security group is restricted to deny all.",
          "No evidence of Network ACLs or subnet-level default-deny configuration.",
          "Cannot confirm the CloudFront prefix list scoping is applied at the actual point of enforcement beyond this single SG."
        ],
        "injection_detected": false,
        "injection_note": ""
      },
      "provenance": {
        "model": "claude-opus-4-8",
        "prompt_sha256": "88d8ec380ad1dd0d42dd1318ba92a1cb19425dcd744082c33ff5259582a53014",
        "evidence_sha256": "9f2c03d2347b7077f2eff6dfcebf76f5b1c114cf4e88e78f1e2a41a42aa04ac6",
        "reviewed_at": "2026-07-01T19:29:35+00:00"
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
            "reason": "Objective 3.13.8[c] concerns implementing cryptographic mechanisms to prevent unauthorized disclosure of CUI during transmission. The evidence demonstrates TLS enforcement across all major transmission paths: the RDS parameter group sets rds.force_ssl=1, rejecting non-TLS database connections (infra/rds.tf:23, lines 30-33); the ALB HTTPS listener uses a modern TLS 1.2/1.3 security policy 'ELBSecurityPolicy-TLS13-1-2-2021-06' (infra/alb.tf:109); CloudFront enforces a minimum viewer protocol of TLSv1.2_2021 (infra/cloudfront.tf:205) and redirects all viewer traffic to HTTPS via 'redirect-to-https' (infra/cloudfront.tf:149). The CloudFront-to-origin path also uses https-only with TLSv1.2 (infra/cloudfront.tf:149, lines 137-138). Together these cover data-in-transit at the edge, load balancer, and database tiers.",
            "cites": [
              "infra/rds.tf:23",
              "infra/alb.tf:109",
              "infra/cloudfront.tf:205",
              "infra/cloudfront.tf:149"
            ]
          }
        ],
        "gaps": [
          "No evidence that the ALB-to-backend-target traffic (target group / backend application) is encrypted; the HTTPS listener terminates TLS at the ALB and forwards to a target group without shown backend protocol configuration.",
          "No evidence of TLS enforcement for internal service-to-service or application-to-RDS client configuration beyond the RDS server-side force_ssl setting (e.g., certificate validation on the client side)."
        ],
        "injection_detected": false,
        "injection_note": ""
      },
      "provenance": {
        "model": "claude-opus-4-8",
        "prompt_sha256": "0319ff828df2c948ad70efe5bc501abd985e56abb9ae926e8a959067c6429b3e",
        "evidence_sha256": "2136645358e39391e3ab8a11eee4924e3a79e97531158c11a090bdaecc8e9f83",
        "reviewed_at": "2026-07-01T19:29:45+00:00"
      },
      "note": "AI-DRAFTED, PENDING HUMAN REVIEW. Advisory only; does not change any status."
    },
    {
      "control_id": "3.13.10",
      "engine_status": "met",
      "review": {
        "suggested_verdict": "partial",
        "confidence": "medium",
        "objective_assessments": [
          {
            "objective": "3.13.10[a]",
            "met": false,
            "reason": "The evidence demonstrates that cryptographic keys are established (customer-managed KMS keys defined in IaC at infra/kms.tf:19 and :32) and that rotation is managed (enable_key_rotation = true at infra/kms.tf:21, plus deletion_window_in_days at :22 and key policy at :23). This addresses the 'establish' and part of the 'manage' aspects of the objective. However, the objective 3.13.10[a] concerns cryptographic keys used in the system when cryptography is employed to protect the confidentiality of CUI. The excerpts only show two of the four claimed keys (rds and secrets, partially), with a root-only key policy. There is no evidence tying these keys to CUI-protecting cryptography, no evidence of the other two claimed keys, and no documented key management procedures/lifecycle beyond rotation and deletion window. The provided material is incomplete relative to the claim of 4 keys."
          }
        ],
        "gaps": [
          "Evidence cites 4 customer-managed KMS keys but excerpts only fully show one (rds) and partially a second (secrets); the other keys are not shown for verification.",
          "No evidence linking these KMS keys to cryptography employed to protect the confidentiality of CUI (the objective's scope).",
          "Key policy shown grants 'kms:*' on Resource '*' to the account root only (EnableRootPermissions); no evidence of least-privilege key usage grants or separation of duties for key management.",
          "No documentation of key management procedures/lifecycle (generation, distribution, storage, access, destruction) beyond automated rotation and deletion window."
        ],
        "injection_detected": false,
        "injection_note": ""
      },
      "provenance": {
        "model": "claude-opus-4-8",
        "prompt_sha256": "cf931bac1e9c1fee7dd7b7c07d85ac6c81ba9e174271257eca30839e7e109bbf",
        "evidence_sha256": "b4d1b2c4bcd12b7599d936d31e6bc98ffee13207eeccfebcc5a7a0dac7ecdc34",
        "reviewed_at": "2026-07-01T19:29:56+00:00"
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
            "reason": "The evidence shows customer-managed AWS KMS keys are defined (infra/kms.tf:19) with key rotation enabled (infra/kms.tf:21), and that RDS storage at rest is encrypted using a customer-managed KMS key (infra/rds.tf:85: storage_encrypted = true, kms_key_id = aws_kms_key.rds.arn). AWS KMS does use FIPS 140-2 validated HSMs, which supports encryption at rest for one data store. However, the control requires employing FIPS-validated cryptography to protect CUI broadly. The provided material only demonstrates at-rest encryption for RDS storage/snapshots and references (but does not show) Secrets Manager encryption. There is no evidence that the AWS KMS FIPS-validated endpoints are enforced (KMS also offers non-FIPS endpoints), no evidence of CUI encryption in transit (TLS/FIPS mode), and no evidence covering other data stores (e.g., S3, EBS, backups). Coverage of CUI is therefore incomplete."
          }
        ],
        "gaps": [
          "No evidence that FIPS-validated KMS endpoints (kms-fips.*) are specifically enforced; standard KMS endpoints exist and the scanner's blanket 'FIPS 140-2 validated' claim is not proven for the configuration used.",
          "No evidence of FIPS-validated cryptography protecting CUI in transit (e.g., TLS configuration, rds.force_ssl, HTTPS/ALB TLS policy).",
          "Encryption coverage is only demonstrated for RDS storage at rest; Secrets Manager KMS key is referenced in comments/excerpt tail but no confirming evidence line is provided, and other potential CUI stores (S3, EBS, backups, logs) are not covered.",
          "No mapping showing which data stores actually contain CUI, so completeness of protection cannot be assessed.",
          "Key policy grants kms:* on Resource '*' to account root only; while not disqualifying, no evidence of scoped access controls to the key."
        ],
        "injection_detected": false,
        "injection_note": ""
      },
      "provenance": {
        "model": "claude-opus-4-8",
        "prompt_sha256": "0e66dc622c5f92e286f64208fc1a7e5e9c6270b1877bbc37a0e36bb941dc1a96",
        "evidence_sha256": "9ad52e2681f2b5bce8d73db0981fdc48e0a3f8a8e5d1959fefa4013c6143b8d4",
        "reviewed_at": "2026-07-01T19:30:08+00:00"
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
            "reason": "The RDS instance sets storage_encrypted=true and binds a customer-managed KMS key (kms_key_id = aws_kms_key.rds.arn) at infra/rds.tf:85-86. The referenced KMS key at infra/kms.tf:19-24 is a dedicated customer-managed key for RDS storage and snapshots with enable_key_rotation=true. Together these demonstrate that CUI at rest in the database (and its snapshots) is encrypted, satisfying protection of confidentiality of CUI at rest for this data store.",
            "cites": [
              "infra/rds.tf:85",
              "infra/kms.tf:19"
            ]
          }
        ],
        "gaps": [
          "Evidence covers only the RDS database store. Other potential CUI-at-rest locations (e.g., S3 buckets, EBS volumes, backups outside RDS, application file storage) are not shown, so full-system coverage cannot be confirmed from this evidence.",
          "The KMS key policy shown grants kms:* to the account root principal only; while typical, no evidence demonstrates restriction of decrypt access to specific authorized roles."
        ],
        "injection_detected": false,
        "injection_note": ""
      },
      "provenance": {
        "model": "claude-opus-4-8",
        "prompt_sha256": "3299d7c0dfabec7b20079da351b73713f36b90d1067ac93a916eeabb4919d053",
        "evidence_sha256": "6e4f84871e40348cdfb2cc354c02a0399c1068bd95fae0a8da51c64ac6b8e9ea",
        "reviewed_at": "2026-07-01T19:30:16+00:00"
      },
      "note": "AI-DRAFTED, PENDING HUMAN REVIEW. Advisory only; does not change any status."
    },
    {
      "control_id": "3.14.1",
      "engine_status": "met",
      "review": {
        "suggested_verdict": "insufficient",
        "confidence": "high",
        "objective_assessments": [
          {
            "objective": "3.14.1[b]",
            "met": false,
            "reason": "Objective 3.14.1[b] concerns reporting of system flaws. While the evidence summary claims 5 scanners are configured to identify flaws and that findings can fail a build, no code excerpts were provided to verify these claims. The 'excerpts' array is empty, so there is nothing to confirm that any reporting mechanism (e.g., uploading results, notifying personnel, or surfacing findings) actually exists.",
            "cites": [
              ".github/workflows/ci.yml"
            ]
          },
          {
            "objective": "3.14.1[c]",
            "met": false,
            "reason": "Objective 3.14.1[c] concerns correcting flaws in a timely manner. The evidence claims a HIGH/CRITICAL finding fails the build (exit-code 1) to block merges, which would support timely correction. However, no supporting code excerpt was provided to verify the exit-code/blocking configuration. The empty 'excerpts' array means the claim cannot be substantiated.",
            "cites": [
              ".github/workflows/ci.yml"
            ]
          }
        ],
        "gaps": [
          "No code excerpts were provided; the 'excerpts' array is empty, so the evidence detail claims cannot be verified against actual workflow configuration.",
          "No demonstration of a reporting/notification path for identified flaws (needed for 3.14.1[b]).",
          "No verifiable proof of the exit-code/build-failure gate or which severities trigger it (needed for 3.14.1[c]).",
          "No evidence of 'timely' criteria such as SLAs, remediation timelines, or scheduled/recurring scans (only merge-time gating is claimed)."
        ],
        "injection_detected": false,
        "injection_note": ""
      },
      "provenance": {
        "model": "claude-opus-4-8",
        "prompt_sha256": "607113ccc4afaee327f5e1a0add949cebb3cb3f47341edad54404d232efb4784",
        "evidence_sha256": "3f153b6b1e8f5801eacdc225dba7cf952d9ba9eca384f2fa489fde367154ae62",
        "reviewed_at": "2026-07-01T19:30:25+00:00"
      },
      "note": "AI-DRAFTED, PENDING HUMAN REVIEW. Advisory only; does not change any status."
    }
  ]
};
