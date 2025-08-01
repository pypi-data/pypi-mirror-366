__title__ = "discord.ext.track_edits"
__author__ = "beerpsi"
__license__ = "MIT"
__copyright__ = "Copyright 2025-present beerpsi"
__version__ = "0.1.1"

from typing import Literal, NamedTuple

from .cog import EditTrackerCog
from .context import EditTrackableContext

__all__ = ("EditTrackableContext", "EditTrackerCog")


class VersionInfo(NamedTuple):
    major: int
    minor: int
    micro: int
    releaselevel: Literal["alpha", "beta", "candidate", "final"]
    serial: int


version_info: VersionInfo = VersionInfo(
    major=0, minor=1, micro=1, releaselevel="final", serial=0
)

del NamedTuple, Literal, VersionInfo
