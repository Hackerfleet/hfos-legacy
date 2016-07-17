"""Version Module

Unified HFOS wide version number.
"""

version_info = (1, 1, 0, "dev")  # (major, minor, patch, dev?)
version = (
    ".".join(map(str, version_info))
    if version_info[-1] != "dev"
    else "dev"
)
