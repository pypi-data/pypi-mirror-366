from __future__ import annotations
import platform as platform
__all__ = ['LazyModule', 'platform']
class LazyModule:
    """
    
        Wrapper that delays importing a package until its attributes are accessed.
        We need this to keep the import time of the :mod:`ìmfusion` package reasonable.
    
        .. note::
    
            This wrapper is fairly basic and does not support assignments to the modules, i.e. no monkey-patching.
    
        
    """
    def __getattribute__(self, item):
        ...
    def __init__(self, name: str):
        ...
