"""prabodha.steer — public API for steering operations (write, gate, verify).

Concept: likhita (writing; the steering write interface).
Source: docs/jspace_pratyabhijna_scoping.md; RULES R8 (public surface).
Primitive: public write/gate/verify functions; internal modules for e4 dispatch.
"""

from prabodha.steering.public_api import write, gate, verify

__all__ = ["write", "gate", "verify"]
