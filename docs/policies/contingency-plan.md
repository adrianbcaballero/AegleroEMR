# Contingency Plan

**Status:** Draft
**Owner:** Security Officer (system owner acts in this role for the current deployment)
**Effective date:** 2026-07-08
**Review cycle:** Annual; the plan is tested at least annually
**Regulatory basis:** HIPAA 45 CFR 164.308(a)(7); NIST SP 800-171 Rev 2

## 1. Purpose

This plan defines how Aeglero protects data against loss and keeps critical functions available
during and after a disruption, from a single failed component to the loss of an availability zone.

## 2. Scope

This plan covers the Aeglero application data, its database, its supporting AWS infrastructure, and
the deployment configuration needed to rebuild the system.

## 3. Plan

### 3.1 Data backup

- The database (RDS PostgreSQL) has automated backups with point-in-time recovery, retained for
  7 days, so the database can be restored to any moment within that window.
- The frontend bucket and the Terraform state bucket have versioning enabled, so prior versions can
  be recovered.
- The entire infrastructure is defined in Terraform, so the environment itself is reproducible from
  source rather than dependent on any single running machine.

### 3.2 Criticality analysis

The most critical function is availability of and integrity of the clinical record: the database and
the application that serves it. The database is the highest-criticality asset because it holds the
authoritative record. The static frontend and the compliance dashboard are lower criticality because
they are rebuildable from source and hold no authoritative data.

### 3.3 Recovery objectives

- **Recovery Point Objective (RPO):** within the database backup window, targeting minimal data loss
  through point-in-time recovery.
- **Recovery Time Objective (RTO):** restore core service within a few hours, bounded in practice by
  database restore time and infrastructure re-provisioning.

These are targets for the demonstration deployment and would be tightened and formally agreed for a
production clinical deployment.

### 3.4 Availability and resilience

- The database runs Multi-AZ in the production profile, with automatic failover to a synchronous
  standby in a second availability zone.
- The application runs on ECS Fargate, which restarts failed tasks automatically and is stateless,
  so a new task picks up immediately with no in-memory state to recover.
- Static content is served from S3 through CloudFront across multiple edge locations.

### 3.5 Emergency mode operation

During a major disruption, the priority is to preserve the confidentiality and integrity of PHI while
restoring the clinical record. Recovery proceeds from a known good backup, and integrity is verified
(including the audit-log hash chain) before the system is returned to normal use.

### 3.6 Testing

The plan is tested at least annually by exercising a restore from backup into an isolated environment
and confirming the restored data is complete and its integrity intact. Test results are recorded and
used to correct the plan and the recovery objectives.

## 4. Roles and responsibilities

- **Security Officer.** Owns the plan, declares emergency mode, and leads recovery.
- **System operators.** Execute backup restores and infrastructure re-provisioning.

In the current single-operator deployment the system owner performs all recovery roles.

## 5. Review and maintenance

Reviewed at least annually and after any event that required a restore. Test results are recorded in
version control.

## Control mapping

This plan supports the availability and recovery objectives of the framework and the HIPAA
contingency requirements. It is the recovery reference used by the Incident Response Policy.

HIPAA basis: 45 CFR 164.308(a)(7) (contingency plan: data backup, disaster recovery, emergency mode,
testing, criticality analysis).
