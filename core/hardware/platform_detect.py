import os
import platform
from enum import Enum


class Platform(Enum):
    DESKTOP_MACOS = "desktop_macos"
    DESKTOP_LINUX = "desktop_linux"
    JETSON = "jetson"


def detect_platform() -> Platform:
    """Detect the runtime platform."""
    if os.path.exists("/etc/nv_tegra_release"):
        return Platform.JETSON
    if platform.system() == "Darwin":
        return Platform.DESKTOP_MACOS
    return Platform.DESKTOP_LINUX
