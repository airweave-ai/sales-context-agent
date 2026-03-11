"""
Sales context agent pipeline components.
"""
from .decomposition import QueryDecomposer
from .search import ContextSearcher
from .synthesis import BriefSynthesizer
from .output import BriefOutputHandler

__all__ = [
    "QueryDecomposer",
    "ContextSearcher",
    "BriefSynthesizer",
    "BriefOutputHandler",
]
