"""Collector registry for the Aeglero compliance engine.

To add a collector: implement a Collector subclass in its own module and append
an instance to ALL_COLLECTORS below. The runner iterates this list.
"""

from .audit_chain import AuditChainCollector
from .flaw_remediation import FlawRemediationCollector
from .access_control import AccessControlCollector
from .crypto_config import CryptoConfigCollector
from .aws_live import AwsLiveCollector
from .self_assessment import SelfAssessmentCollector
from .identity_hardening import IdentityHardeningCollector
from .network_config import NetworkConfigCollector

ALL_COLLECTORS = [
    AuditChainCollector(),
    FlawRemediationCollector(),
    AccessControlCollector(),
    CryptoConfigCollector(),
    SelfAssessmentCollector(),
    IdentityHardeningCollector(),
    NetworkConfigCollector(),
    # Runs AFTER crypto_config so its live TEST evidence merges into (and can flag
    # drift against) the Terraform EXAMINE evidence. Opt-in via COMPLIANCE_ENABLE_AWS.
    AwsLiveCollector(),
]
