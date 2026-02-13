"""
DI Container.

Core dependency injection container.
Resolves dependencies and manages component lifecycles.
"""
import logging
import inspect
from typing import Type, TypeVar, Any, Dict, Callable

from .registry import ComponentRegistry

logger = logging.getLogger(__name__)

T = TypeVar("T")

class DIContainer:
    """
    Dependency Injection Container.
    
    Responsibilities:
    - Hold the ComponentRegistry
    - Resolve dependencies recursively
    - Manage Singleton instances
    """

    def __init__(self, registry: ComponentRegistry):
        self.registry = registry
        self._instances: Dict[Type, Any] = {}

    def resolve(self, interface: Type[T], **overrides) -> T:
        """
        Resolve an interface to a concrete instance.
        
        Args:
            interface: The Port or Class to resolve
            overrides: Runtime arguments to override injection (e.g., per-request params)
        
        Returns:
            Instance of T
        """
        # 1. Check if it's a registered interface
        registration = self.registry.get_registration(interface)
        
        if registration:
            impl = registration["impl"]
            is_singleton = registration["singleton"]

            # Singleton Check
            if is_singleton and interface in self._instances:
                return self._instances[interface]

            # Instantiate
            instance = self._create_instance(impl, overrides)
            
            # Cache if Singleton
            if is_singleton:
                self._instances[interface] = instance
                
            return instance

        # 2. If not registered, try to instantiate the class directly (Auto-wiring)
        if inspect.isclass(interface):
             return self._create_instance(interface, overrides)
             
        raise ValueError(f"Cannot resolve interface: {interface}")

    def _create_instance(self, factory_or_class: Any, overrides: dict) -> Any:
        """
        Instantiate a class or call a factory, injecting dependencies.
        """
        # Case A: It's an already instantiated object (Manual registration)
        if not callable(factory_or_class):
            return factory_or_class

        # Case B: It's a Class or Function
        try:
            sig = inspect.signature(factory_or_class)
            params = sig.parameters
            injectable_kwargs = {}

            for name, param in params.items():
                # 1. Check Overrides (Runtime params)
                if name in overrides:
                    injectable_kwargs[name] = overrides[name]
                    continue
                
                # 2. Check Annotation (Type Hint)
                if param.annotation != inspect.Parameter.empty:
                    # Attempt recursive resolution
                    try:
                        dependency = self.resolve(param.annotation)
                        injectable_kwargs[name] = dependency
                    except ValueError:
                        # If cannot resolve, skip (might be optional or primitive)
                        pass
                
                # 3. If still missing and has default, let it use default
                if name not in injectable_kwargs and param.default == inspect.Parameter.empty:
                     # If we can't find it and no default, we might have an issue unless it's handled inside the class
                     pass

            return factory_or_class(**injectable_kwargs)

        except Exception as e:
            logger.error(f"DI Injection failed for {factory_or_class}: {e}")
            raise
