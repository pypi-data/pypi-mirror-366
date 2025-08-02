import platform

class LazyModule:
    """
    Wrapper that delays importing a package until its attributes are accessed.
    We need this to keep the import time of the :mod:`ìmfusion` package reasonable.

    .. note::

        This wrapper is fairly basic and does not support assignments to the modules, i.e. no monkey-patching.

    """

    def __init__(self, name: str):
        from types import ModuleType
        from typing import Optional

        self._name_ = name
        self._module_: Optional[ModuleType] = None

    def __getattribute__(self, item):
        if item in ("_name_", "_module_"):
            return object.__getattribute__(self, item)
        if self._module_ is None:
            import importlib
            self._module_ = importlib.import_module(self._name_)
        return self._module_.__getattribute__(item)


try:
    from .onnxruntime_engine import PyOnnxRuntimeEngine
except ImportError:
    pass

try:
    from .openvino_engine import OpenVinoEngine
except ImportError:
    pass

try:
    from .pytorch_engine import PyTorchEngine
except ImportError:
    pass

if platform.system() == "Darwin" and platform.processor() == "arm":
    try:
        from .coreml_engine import CoreMLEngine
    except ImportError:
        pass
