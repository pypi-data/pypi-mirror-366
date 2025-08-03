# -*- coding: utf-8 -*-

import threading
from abc import ABC, abstractmethod
from inspect import isabstract
from typing import Type, Dict, Set, Optional

try:
    from typing import Self

except ImportError:
    # For earlier versions...
    from typing_extensions import Self


class IFactory(ABC):
    """
    Base interface for classes that acts like
    factories. The IFactory pattern
    allows you to:

      - Automatically register concrete implementations.
      - Discover available implementations at runtime.
      - Create instances by string reference.
      - Maintain separate registries for different factory types.
    """

    _impls: Dict[str, Type[Self]] = {}
    _lock = threading.Lock()

    def __init_subclass__(cls, **kwargs) -> None:
        """
        Automatically register concrete subclasses in both the global and
        per-abstract-class registries. Each abstract subclass gets its own
        _impls dict.
        """
        super().__init_subclass__(**kwargs)

        if isabstract(cls):
            # Each abstract (new base) class will have its own
            # register. This way each new base interface does not need
            # to redefine `_impls`...
            cls._impls = {}

        else:
            with IFactory._lock:
                for base in cls.__mro__:
                    if issubclass(base, IFactory) and isabstract(base) and hasattr(base, "_impls"):
                        key = cls.registration_key()
                        if key in base._impls:
                            raise ValueError(
                                f"Registration key '{key}' already exists in {base.__name__} registry. "
                                f"Existing class: {base._impls[key].__name__}, "
                                f"Attempting to register: {cls.__name__}"
                            )

                        base._impls[key] = cls

    @classmethod
    @abstractmethod
    def registration_key(cls) -> str:
        """
        It returns the name (reference) for the key used
        to register, like: return `self.__name__`
        """

    @classmethod
    def get_registered_classes(cls) -> Set[str]:
        """ It returns the current registered implementations """
        return set(cls._impls)

    @classmethod
    def get_class(cls, cls_reference: str) -> Optional[Type[Self]]:
        """ It returns the reference (class type) by reference """
        return cls._impls.get(cls_reference, None)
