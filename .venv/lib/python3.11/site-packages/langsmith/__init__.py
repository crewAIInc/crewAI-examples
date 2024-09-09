"""LangSmith Client."""
from importlib import metadata

try:
    __version__ = metadata.version(__package__)
except metadata.PackageNotFoundError:
    # Case where package metadata is not available.
    __version__ = ""

from langsmith.client import Client
from langsmith.evaluation.evaluator import EvaluationResult, RunEvaluator
from langsmith.run_helpers import trace, traceable
from langsmith.run_trees import RunTree

__all__ = [
    "Client",
    "RunTree",
    "__version__",
    "EvaluationResult",
    "RunEvaluator",
    "traceable",
    "trace",
]
