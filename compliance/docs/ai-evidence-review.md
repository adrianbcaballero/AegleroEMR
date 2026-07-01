# AI Evidence Review: Design and Threat Model

Status: design (not yet implemented). This document is written before code so the
feature is built to a defined threat model. The capability is opt-in and off by
default.

## 1. Purpose

The compliance engine gathers structured evidence for each control. The AI evidence
review layer applies a large language model to that evidence in two modes:

1. Review mode: given a control, its NIST SP 800-171A objectives, the collected
   evidence, and the specific code excerpts the evidence cites, judge whether the
   evidence actually satisfies each objective, cite the supporting evidence, and flag
   gaps. This is a second, skeptical opinion that checks the collectors for over-claims.
2. Narrative mode: draft an assessor-ready System Security Plan implementation
   statement for a control from its structured evidence.

The layer is advisory. It never sets or changes a control status, an SPRS score, or the
catalog. Its output is a draft that a human reviews and approves.

## 2. Frameworks adopted

This feature is governed by two established frameworks, chosen to cover both AI
governance and application security.

- NIST AI Risk Management Framework 1.0 (AI 100-1) for governance and lifecycle risk,
  using its four functions: Govern, Map, Measure, Manage.
- OWASP Top 10 for LLM Applications (2025) for the security threat model specific to
  LLM-backed features.

Section 6 maps the design to specific subcategories of each.

## 3. Design principles (mandatory)

1. Advisory only. The agent writes to a separate, labeled artifact. It cannot change a
   status, score, or catalog entry. This single constraint bounds the impact of nearly
   every threat below.
2. Human in the loop. Every output is marked draft, pending review. A person approves
   before anything flows into the SSP.
3. Least privilege. Read-only on the generated status file, write-only to one advisory
   output file. No repo write, no filesystem access beyond its inputs and output, no
   network beyond the model API.
4. Data minimization. Only control metadata (id, title, objectives) and evidence
   strings (reference and short detail) leave the machine. Never raw files, secrets,
   environment variables, credentials, or protected health information.
5. Grounded and auditable. Judge strictly from the provided evidence, cite references or
   return insufficient, and record full provenance for every call.
6. Fail safe. If the key is absent, the API errors, or a budget cap is reached, the step
   skips cleanly and the core assessment is unaffected.

## 4. Architecture and data flow

```
collectors -> catalog -> scorer -> generators
                                     |
                                     +-> ai_review (opt-in)
                                           reads:  output/status.json + cited code excerpts
                                           calls:  model API (minimized payload)
                                           writes: output/ai_review.json, .md
```

- The module runs after scoring, as an opt-in step controlled by COMPLIANCE_ENABLE_AI.
- Input is the already-generated status file plus the specific code lines its evidence
  cites (the referenced line plus limited context, never whole files or the repository).
  Output is two advisory files in output/, which is gitignored like the rest of the
  generated evidence.
- The only external call is to the model API, with a minimized, scrubbed payload.

## 5. Data classification and handling

| Data element | Classification | Leaves the machine | Control |
|---|---|---|---|
| Control id, title, objectives | Public framework text | Yes | Allowlisted |
| Evidence reference (path:line) and detail string | Internal, non-sensitive | Yes | Allowlisted |
| Collector summary | Internal, non-sensitive | Yes | Allowlisted |
| Cited code excerpts (referenced line plus limited context) | Internal, from a public repo | Yes | Bounded to evidence references; scrubbed |
| Whole source files, .env, secrets, credentials | Sensitive | No | Blocked by allowlist and scrubber |
| Protected health information | Regulated | No | Not present in evidence; blocked by scrubber |

A pre-send scrubber runs on every payload. It enforces the field allowlist (control
metadata, evidence strings, and bounded cited code excerpts only), rejects whole-file or
directory content, and rejects the call if the payload matches secret or credential
patterns (keys, tokens, connection strings) or known sensitive markers. The model API should be configured for zero data
retention where available. No PHI is ever in scope because the evidence consists of
control metadata and code references, not patient data.

## 6. Control mapping

### 6.1 OWASP Top 10 for LLM Applications (2025)

| Risk | Addressed | How |
|---|---|---|
| LLM01 Prompt injection | Yes | Evidence is treated as untrusted data, delimited and labeled as data not instructions. Advisory-only output means an injected instruction cannot change any status. Structured tool-schema output constrains the response. |
| LLM02 Sensitive information disclosure | Yes | Field allowlist plus pre-send scrubber. No raw files, secrets, or PHI in payloads. Zero-retention API configuration preferred. |
| LLM03 Supply chain | Yes | The model SDK is a pinned dependency already covered by the project's pip-audit and Trivy scans, and is optional to the core engine. |
| LLM04 Data and model poisoning | Not applicable | No training or fine-tuning. A hosted, vendor-maintained model is used. |
| LLM05 Improper output handling | Yes | Output is validated against a JSON schema and is never executed, rendered as trusted HTML, or used to drive control status. It is displayed as labeled advisory text. |
| LLM06 Excessive agency | Yes | Least privilege and advisory-only. The module cannot import the scorer or catalog writers, cannot write outside its one output file, and has a mandatory human approval gate. |
| LLM07 System prompt leakage | Yes | The system prompt contains no secrets or sensitive data, so leakage carries no confidentiality impact. |
| LLM08 Vector and embedding weaknesses | Not applicable | No retrieval, vector store, or embeddings are used. |
| LLM09 Misinformation | Yes | Grounding prompt with cite-or-insufficient, schema validation, and a human review gate. Verdicts are suggested, never authoritative. |
| LLM10 Unbounded consumption | Yes | Opt-in only, with hard caps on controls per run, per-call timeout, retry with backoff, and a token budget guard that halts the run. |

### 6.2 NIST AI Risk Management Framework 1.0

| Subcategory | Addressed | How |
|---|---|---|
| GOVERN 1.1 Legal and regulatory requirements understood | Yes | Purpose and data handling documented here; no regulated data in scope. |
| GOVERN 1.3 Risk management processes in place | Yes | This threat model and its mitigations; opt-in rollout. |
| GOVERN 4.1 Risk culture, critical thinking encouraged | Yes | Output framed as a draft to challenge; separation of duties between evidence gathering and approval. |
| GOVERN 6.1 and 6.2 Third-party and contingency for third-party failure | Yes | Pinned model provider, recorded model id, and graceful degradation if the provider is unavailable. |
| MAP 1.1 Intended purpose and context established | Yes | Purpose, scope, and out-of-scope stated. |
| MAP 4.1 Third-party risks mapped | Yes | Model provider dependency and data-sharing risk documented. |
| MEASURE 2.5 Validity and reliability | Yes | Model pinning plus a recorded prompt hash and evidence hash per review, giving reproducible advisory records. |
| MEASURE 2.7 Security and resilience | Yes | Prompt-injection handling, least privilege, scrubber, and fail-safe behavior. |
| MEASURE 2.8 Transparency and accountability | Yes | Every output labeled AI-generated with model id, prompt hash, evidence hash, and timestamp. |
| MEASURE 2.10 Privacy | Yes | Data minimization and scrubber; no PHI in scope. |
| MANAGE 1.3 Responses to high-priority risks | Yes | Advisory-only design and human approval as the primary risk response. |
| MANAGE 2.4 Mechanisms to supersede or deactivate | Yes | Off by default; a single flag disables it; failures skip cleanly. |
| MANAGE 3.1 Third-party risks monitored | Yes | Model id recorded per review; a model change invalidates prior reviews and triggers re-review. |
| MANAGE 4.1 Post-deployment monitoring | Yes | Reviews are logged with provenance; the AI's suggested verdicts can be compared against human decisions over time. |

Subcategories concerning workforce composition, broad societal impact, and bias in
protected classes (for example GOVERN 3 and several MEASURE 2.11 bias items) are noted
as lower relevance for a code-evidence review task and are not primary here.

## 7. Human oversight and governance

- The output is a draft. A human reads output/ai_review.md, considers the confidence and
  gaps, and approves before any narrative is promoted into the SSP.
- Separation of duties: the collectors gather evidence; the AI reviews it; a human
  approves. No single actor both produces and blesses the result.
- Automation bias is countered by surfacing confidence and gaps prominently and by
  framing the AI output as a position to be challenged.

## 8. Provenance and auditability

Each review record stores: control id, suggested verdict, confidence, objective-level
assessment with citations, gaps, the model id, a hash of the prompt, the evidence hash
it reviewed, and a timestamp. This makes each review a fixed, reproducible artifact and
supports after-the-fact review.

## 9. Operational guardrails

- Secret management: the API key lives only in an environment secret. It is never
  committed and never logged. In CI it is injected as a masked secret. Rotation is
  documented.
- Budget and rate control: caps on controls per run, per-call timeout, retry with
  backoff, and a token budget guard.
- Graceful degradation: any missing key, API error, or cap breach results in a clean
  skip. The core assessment always completes.
- Model selection and provider: the module is provider-agnostic, so the endpoint,
  provider, and credentials are configuration (see section 10). By default it uses a
  strong model for review (for example claude-opus-4-8) and a lighter model for narrative
  drafting (for example claude-sonnet-5). The exact model id is pinned and recorded.

## 10. AI provider and deployment governance

The choice of model backend is a procurement and data governance decision, not a
developer default. Sending code or evidence to a third-party model service must go
through a channel the organization has approved. The module is therefore
provider-agnostic: the endpoint, provider, and credentials are configuration, so it can
be pointed at whatever backend is approved.

Approved options, in increasing order of control:

- A commercial agreement with the model provider that contractually guarantees zero data
  retention and no training on submitted data, backed by a data processing agreement, and
  a business associate agreement where health data is in scope.
- The model hosted inside the organization's own cloud boundary, for example Claude
  through AWS Bedrock or Google Vertex AI, so data stays within the existing cloud tenancy
  and its agreements. Government and FedRAMP-authorized paths exist through these providers
  for regulated and public-sector workloads.
- A self-hosted or private model for the most sensitive material, keeping all data inside
  the organization's boundary.

For defense or export-controlled work, source code can itself be controlled technical
data, for example under ITAR or as CUI, and may not be permitted to reach a commercial
software-as-a-service endpoint at all. Those settings require an in-tenancy or self-hosted
model within the appropriate government cloud boundary.

The default in this project is the public model API used only against a public,
non-sensitive repository for demonstration. A non-public or regulated deployment must
select an approved channel above before the feature is enabled on that code.

## 11. Out of scope and residual risk

- Out of scope: training or fine-tuning, retrieval or embeddings, autonomous action,
  any write to control status or score.
- Residual risk: evidence and cited code excerpts are shared with the configured model
  provider. For the default demo this is accepted because the repository is public and the
  data is minimized and scrubbed. For any non-public or regulated deployment, the
  approved-channel requirement in section 10 applies before the feature is enabled.

## 12. Build plan

1. Implement review mode against this document, on a small scope (a single control or
   the automated set), with the scrubber and provenance in place from the start.
2. Validate the guardrails: key-absent skip, budget cap, schema rejection, and a
   prompt-injection test using a benign planted instruction in evidence.
3. Add narrative mode.
4. Add an optional, human-gated path for approved narratives to flow into the SSP.
