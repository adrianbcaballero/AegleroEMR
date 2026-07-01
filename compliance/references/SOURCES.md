# Framework Sources of Authority

This compliance engine maps Aeglero's controls to several frameworks. This file is
the single citation list: what each framework is, the authoritative source, and how
it's used here. We **link** the authoritative sources rather than mirroring PDFs, so
the reference is always the current, correct version (regulations get amended).

All of these are **US federal government works and therefore public domain**
(17 U.S.C. 105) — the requirement text may be quoted freely. The `controls.json`
catalog embeds the relevant requirement text per control so the dashboard/SSP are
self-contained; this file points to where each requirement comes from.

---

## Primary spine

### NIST SP 800-171 Rev 2 — "Protecting CUI in Nonfederal Systems"
The 110 security requirements. The scored spine of this engine.
- Publication: https://csrc.nist.gov/pubs/sp/800/171/r2/upd1/final
- Machine-readable (OSCAL) catalog: https://github.com/usnistgov/oscal-content
- Note: CMMC currently uses **Rev 2** (not Rev 3), so we track Rev 2.

### NIST SP 800-171A — Assessment Objectives
The `[a]`,`[b]`,`[c]` determination statements graded during an assessment.
- Publication: https://csrc.nist.gov/pubs/sp/800/171/a/final

### DoD Assessment Methodology (SPRS scoring)
The −1 / −3 / −5 point weights per control used to compute the SPRS score from 110.
- DoD Procurement Toolbox: https://dodprocurementtoolbox.com/site-pages/nist-sp-800-171
- DPC Safeguarding page: https://www.acq.osd.mil/asda/dpc/cp/cyber/safeguarding.html

---

## Frameworks mapped via crosswalk (`mappings` field in controls.json)

### CMMC Level 2 (Cybersecurity Maturity Model Certification)
Practices are 1:1 with NIST 800-171 Rev 2, referenced by practice ID (e.g. `AU.L2-3.3.8`).
- CMMC program: https://dodcio.defense.gov/CMMC/
- Final rule (32 CFR Part 170): https://www.ecfr.gov/current/title-32/subtitle-A/chapter-I/subchapter-M/part-170

### HIPAA Security Rule (45 CFR Part 164, Subpart C)
Aeglero's actual legal obligation as an EHR. Referenced by section (e.g. `164.312(b)`).
- Regulation text (eCFR): https://www.ecfr.gov/current/title-45/subtitle-A/subchapter-C/part-164
- HHS overview: https://www.hhs.gov/hipaa/for-professionals/security/index.html
- HIPAA↔NIST crosswalk source: NIST SP 800-66 Rev 2 — https://csrc.nist.gov/pubs/sp/800/66/r2/final

### ONC Health IT Certification Criteria (45 CFR 170.315)
Certification criteria for certified health IT; the `(d)` criteria are privacy/security
(e.g. `170.315(d)(2)` auditable events & tamper-resistance — Aeglero's hash chain).
- Regulation text (eCFR): https://www.ecfr.gov/current/title-45/subtitle-A/subchapter-D/part-170/subpart-C/section-170.315
- Certification Companion Guides (ONC/ASTP): https://www.healthit.gov/topic/certification-ehrs/certification-companion-guides

### 42 CFR Part 2 (Confidentiality of SUD Patient Records)
Consent-based disclosure and redisclosure restrictions for substance-use records —
Aeglero's consent management. Referenced by section (e.g. `2.16` security for records).
- Regulation text (eCFR): https://www.ecfr.gov/current/title-42/chapter-I/subchapter-A/part-2

---

## How to use this file

- Each control in `../catalog/controls.json` carries a `mappings` object citing the
  equivalent requirement in each framework above.
- When a mapping is added or changed, confirm it against the source linked here.
- The mappings in this engine were drafted from knowledge and **should be
  spot-checked against these authoritative sources** before being treated as final —
  especially the SPRS weights and the HIPAA/ONC section numbers.
