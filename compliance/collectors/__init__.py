"""Collector registry for the Aeglero compliance engine.

To add a collector: implement a Collector subclass in its own module and append
an instance to ALL_COLLECTORS below. The runner iterates this list.
"""

from .audit_chain import AuditChainCollector
from .flaw_remediation import FlawRemediationCollector
from .access_control import AccessControlCollector
from .crypto_config import CryptoConfigCollector

ALL_COLLECTORS = [
    AuditChainCollector(),
    FlawRemediationCollector(),
    AccessControlCollector(),
    CryptoConfigCollector(),
]
