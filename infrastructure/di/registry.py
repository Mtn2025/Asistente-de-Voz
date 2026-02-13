"""
DI Registry.

Maps abstract Ports to concrete Adapter implementations.
"""
from typing import Type, Any, Dict

from app_nuevo.domain.ports import (
    LLMPort,
    STTPort,
    TTSPort,
    CallRepositoryPort,
    ConfigRepositoryPort,
    TranscriptRepositoryPort
)

class ComponentRegistry:
    """
    Central registry for component configuration.
    Maps Port Types to Configured Implementation Factories or Classes.
    """
    
    def __init__(self):
        self._registry: Dict[Type, Any] = {}
        self._singletons: Dict[Type, Any] = {}

    def register(self, interface: Type, implementation: Any, is_singleton: bool = False):
        """
        Register an implementation for an interface.
        
        Args:
            interface: The abstract Port/Interface class
            implementation: The concrete class or factory function
            is_singleton: If True, the container will instantiate once and reuse
        """
        self._registry[interface] = {
            "impl": implementation,
            "singleton": is_singleton
        }

    def get_registration(self, interface: Type) -> dict | None:
        return self._registry.get(interface)
