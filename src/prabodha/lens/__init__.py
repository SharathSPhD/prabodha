"""prabodha.lens — public API for lens operations (fit, eval, vis).

Concept: ārambha (inception; the public gate to the instrument).
Source: docs/jspace_pratyabhijna_scoping.md; RULES R8 (public surface).
Primitive: public fit/eval/vis functions; internal modules for CLI dispatch.
"""

from .public_api import fit, eval, vis

__all__ = ["fit", "eval", "vis"]
