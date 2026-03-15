from core.hardware.base import CameraBackend
from core.hardware.platform_detect import Platform


def create_camera(plat: Platform) -> CameraBackend:
    """Create the appropriate camera backend for the current platform."""
    if plat == Platform.JETSON:
        from core.hardware.camera_jetson import JetsonCamera
        return JetsonCamera()

    from core.hardware.camera_desktop import DesktopCamera
    return DesktopCamera()
