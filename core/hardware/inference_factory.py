from core.hardware.base import InferenceBackend
from core.hardware.platform_detect import Platform


def create_inference_backend(plat: Platform) -> InferenceBackend:
    """Create the appropriate inference backend for the current platform."""
    if plat == Platform.JETSON:
        from core.hardware.inference_cuda import CUDAInferenceBackend
        return CUDAInferenceBackend()

    from core.hardware.inference_cpu import CPUInferenceBackend
    return CPUInferenceBackend()
