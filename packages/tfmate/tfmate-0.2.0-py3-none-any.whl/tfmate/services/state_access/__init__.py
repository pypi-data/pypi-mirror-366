"""
State access package for tfmate.
"""

from .local import read_local_state
from .s3 import read_s3_state
from .http import read_http_state
from .tfe import read_tfe_state

__all__ = ["read_local_state", "read_s3_state", "read_http_state", "read_tfe_state"]
