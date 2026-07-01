# Aeglero Continuous Compliance

A continuous controls monitoring subsystem for the Aeglero EMR. It assesses the running
system against NIST SP 800-171 Rev 2, generates the two artifacts an assessor works from
(a System Security Plan and a Plan of Action and Milestones), computes an SPRS score, and
crosswalks every control to HIPAA, ONC Health IT, CMMC, and 42 CFR Part 2. It runs on a
schedule, so compliance posture is measured continuously rather than reconstructed in the
weeks before an audit.

The approach is "compliance as code". Evidence is gathered by small, testable collectors
that read the actual application source, infrastructure, and CI configuration, so each
control status links back to the specific line of code or config that supports it.

## What it produces

One command runs the whole pipeline and writes four things:

- `output/status.json` is a machine-readable scorecard: every control with a status, a
  disposition, cited evidence, and a SHA-256 provenance hash.
- `output/SSP.md` is a System Security Plan: a per-control implementation statement with
  linked evidence.
- `output/POAM.md` and `output/POAM.csv` are the Plan of Action and Milestones: the open
  items with milestone dates.
- `dashboard/data.js` feeds `dashboard/index.html`, a self-contained page with an SPRS
  gauge, a browsable control list, and a framework switcher.

## How it works

```
collectors  ->  catalog  ->  scorer  ->  generators
(evidence)     (controls)    (SPRS)      (dashboard, SSP, POA&M, JSON)
```

1. Collectors in `collectors/` gather evidence for specific controls. Each returns
   findings with a status, an assessment method (Examine or Test, per NIST SP 800-171A),
   cited evidence, and a hash of that evidence.
2. The catalog in `catalog/controls.json` (built by `catalog/build_catalog.py`) defines
   all 110 NIST 800-171 Rev 2 controls, their SPRS weight, their disposition type, and
   their cross-framework mappings.
3. The scorer in `scorer.py` computes the SPRS score and automation coverage from the
   merged findings and the catalog.
4. The generators in `generate_docs.py` render the SSP, the POA&M, and the dashboard feed.

Run it:

```
python compliance/run.py
```

The core engine uses only the Python standard library. The single optional collector that
queries a live AWS account uses boto3 (see `requirements.txt`) and is off by default.

## Control dispositions

Not every control can, or should, be proven by scanning code. Each control carries a
disposition that states plainly how it is satisfied:

| Disposition | Meaning | Count |
|---|---|---|
| Implemented (automated) | Proven now by a collector that reads source, infra, or CI | 14 |
| Attested | Implemented in the application; a collector for it is a roadmap item | 46 |
| Policy | Satisfied by an organizational policy or process document | 22 |
| Inherited | Provided by the cloud platform (AWS), evidenced by its attestations | 13 |
| Not applicable | Out of scope for this system, with a stated rationale | 15 |

Current posture is SPRS 105 of 110, with about 17 percent of applicable controls verified
automatically. That automated share is designed to grow over time: adding a collector for
an Attested control moves it to Implemented and raises the coverage number.

## Collectors

| Collector | Method | Area |
|---|---|---|
| `audit_chain` | Examine | Audit generation, traceability, tamper-evidence (3.3.x) |
| `access_control` | Examine | Authentication, RBAC, MFA (3.1.x, 3.5.3) |
| `flaw_remediation` | Examine | Vulnerability scanning and merge gating in CI (3.11.2, 3.14.1) |
| `crypto_config` | Examine | Encryption in transit and at rest, read from Terraform (3.13.x) |
| `self_assessment` | Examine | The engine itself satisfies the assessment family (3.12.x) |
| `aws_live` | Test | Optional live check of the running AWS account (opt-in) |

Adding a collector is the primary extension point. Implement a `Collector` subclass that
returns findings for one or more controls, then register it in `collectors/__init__.py`.

## Frameworks

Controls are assessed against NIST 800-171 and crosswalked to other frameworks, so a
single piece of evidence can satisfy several at once. The dashboard switches between these
views, showing each control by its framework reference next to its NIST 800-171 control.

| Framework | Mapped controls |
|---|---|
| NIST SP 800-171 Rev 2 | 110 |
| CMMC Level 2 | 110 |
| HIPAA Security Rule | 36 |
| ONC Health IT Certification | 16 |
| 42 CFR Part 2 | 6 |

## Continuous operation

A scheduled GitHub Actions workflow (`.github/workflows/compliance.yml`) re-runs the
assessment daily, uploads the refreshed evidence as an artifact, and fails the run if the
SPRS score falls below a threshold or a control regresses. The regression and threshold
logic lives in `check_drift.py`. A second workflow runs the optional live AWS checks
through a read-only role assumed via GitHub OIDC, so no cloud credentials are stored.

## Layout

```
compliance/
  run.py                 pipeline entry point
  scorer.py              SPRS scoring
  generate_docs.py       SSP, POA&M, and dashboard feed
  check_drift.py         drift detection and score gate
  catalog/
    build_catalog.py     builds controls.json
    controls.json        the 110-control catalog (generated)
  collectors/            evidence collectors
  dashboard/             self-contained dashboard (index.html)
  output/                generated artifacts (regenerated each run)
  references/
    SOURCES.md           authoritative source for every framework and mapping
```

## Scope and caveats

The control dispositions, SPRS weights, and cross-framework mappings are drafted and
should be verified against the authoritative sources listed in `references/SOURCES.md`
before being relied upon.
