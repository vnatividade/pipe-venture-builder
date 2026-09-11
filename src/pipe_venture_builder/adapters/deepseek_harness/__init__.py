"""Experimental DeepSeek Harness contract spike (ADR-004), synthetic and offline.

No DeepSeek Harness runtime, provider, model, process, or network is used,
and nothing here proves runtime compatibility. The package is not registered
with any CLI, runtime registry, or product manifest.
"""

from .adapter import DeepSeekHarnessRuntimeAdapter
from .checkpoint import CHECKPOINT_STATES, DeepSeekHarnessCheckpointStore
from .context import WORKFLOW_KINDS, DeepSeekHarnessRunContext
from .errors import BLOCKER_CODES, DeepSeekHarnessContractError
from .events import (
    EVENT_KINDS,
    READ_ONLY_TOOLS,
    DeepSeekHarnessEventSequence,
    DeepSeekHarnessRuntimeEvent,
)
from .normalizer import COMPATIBILITY_MATRIX, MAX_FRAME_BYTES, DeepSeekHarnessNormalizer
from .preflight import PREFLIGHT_FLAGS, validate_preflight
from .proposal import PROPOSAL_KINDS
from .session import (
    SYNTHETIC_MODEL_IDS,
    SYNTHETIC_ROUTE_IDS,
    SessionBinding,
    SessionRegistry,
)
from .transport import FakeNdjsonTransport, TransportSignal, drive_session

__all__ = [
    "BLOCKER_CODES",
    "CHECKPOINT_STATES",
    "COMPATIBILITY_MATRIX",
    "DeepSeekHarnessCheckpointStore",
    "DeepSeekHarnessContractError",
    "DeepSeekHarnessEventSequence",
    "DeepSeekHarnessNormalizer",
    "DeepSeekHarnessRunContext",
    "DeepSeekHarnessRuntimeAdapter",
    "DeepSeekHarnessRuntimeEvent",
    "drive_session",
    "EVENT_KINDS",
    "FakeNdjsonTransport",
    "MAX_FRAME_BYTES",
    "PREFLIGHT_FLAGS",
    "PROPOSAL_KINDS",
    "READ_ONLY_TOOLS",
    "SessionBinding",
    "SessionRegistry",
    "SYNTHETIC_MODEL_IDS",
    "SYNTHETIC_ROUTE_IDS",
    "TransportSignal",
    "validate_preflight",
    "WORKFLOW_KINDS",
]
