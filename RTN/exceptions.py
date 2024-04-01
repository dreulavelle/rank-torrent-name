"""
Custom exceptions for RTN.

Exceptions:
- `GarbageTorrent`: Raised when a torrent is considered garbage or invalid and should be ignored.

Refer to the respective docstrings for more information.
"""

class GarbageTorrent(Exception):
    """Raised when a torrent is considered garbage or invalid and should be ignored."""
