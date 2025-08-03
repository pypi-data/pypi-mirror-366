from copy import deepcopy
from functools import wraps
from inspect import currentframe
from inspect import iscoroutinefunction
from random import random
from typing import Any
from typing import Callable
from typing import Optional
from typing import overload
from typing import TypeVar


T = TypeVar("T")


class ChaosInjector:
    def __init__(self) -> None:
        raise NotImplementedError(
            "Use ChaosInjector.create_proxy(obj) for proxy instances "
            "or ChaosInjector.inject(obj) for in-place mutation."
        )

    @classmethod
    def create_proxy(
        cls,
        obj: T,
        probability: float = 0.5,
        decider: Optional[Callable[[str], bool]] = None,
        method_probs: Optional[dict[str, float]] = None,
    ) -> T:
        return cls.__inject(
            obj=obj,
            probability=probability,
            decider=decider,
            method_probs=method_probs,
            return_class=True,
        )

    @classmethod
    def inject(
        cls,
        obj: T,
        probability: float = 0.5,
        decider: Optional[Callable[[str], bool]] = None,
        method_probs: Optional[dict[str, float]] = None,
    ) -> None:
        return cls.__inject(
            obj=obj,
            probability=probability,
            decider=decider,
            method_probs=method_probs,
            return_class=False,
        )

    @overload
    @classmethod
    def __inject(
        cls,
        obj: T,
        probability: float = 0.5,
        decider: Optional[Callable[[str], bool]] = None,
        method_probs: Optional[dict[str, float]] = None,
        return_class: bool = True,
    ) -> T:
        ...

    @overload
    @classmethod
    def __inject(
        cls,
        obj: T,
        probability: float = 0.5,
        decider: Optional[Callable[[str], bool]] = None,
        method_probs: Optional[dict[str, float]] = None,
        return_class: bool = False,
    ) -> None:
        ...

    @classmethod
    def __inject(
        cls,
        obj: T,
        probability: float = 0.5,
        decider: Optional[Callable[[str], bool]] = None,
        method_probs: Optional[dict[str, float]] = None,
        return_class: bool = False,
    ) -> Optional[T]:
        cls.__validate_params(probability, method_probs)
        should_use_real = cls.__should_use_real(
            probability, decider, method_probs
        )
        ProxyCls = type(
            f"Proxy_{obj.__class__.__name__}",
            (obj.__class__,),
            {
                "__getattribute__": cls.__handle(should_use_real)
            }
        )

        if return_class:
            proxy_instance = ProxyCls.__new__(ProxyCls)

            if hasattr(obj, "__dict__"):
                proxy_instance.__dict__ = deepcopy(obj.__dict__)
            elif hasattr(obj.__class__, "__slots__"):
                for slot in obj.__class__.__slots__:
                    setattr(proxy_instance, slot, getattr(obj, slot))

            return proxy_instance
        else:
            obj.__class__ = ProxyCls
            return None

    @staticmethod
    def __validate_params(
        probability: float,
        method_probs: Optional[dict[str, float]],
    ) -> None:
        if not (0 <= probability <= 1):
            raise ValueError(
                f"Probability must be between 0 and 1, got {probability}"
            )

        if method_probs:
            invalid_probs = {
                k: v
                for k, v in method_probs.items()
                if not (0 <= v <= 1)
            }
            if invalid_probs:
                raise ValueError(
                    "Method probabilities must be between 0 and 1, "
                    f"invalid: {invalid_probs}"
                )

    @staticmethod
    def __should_use_real(
        probability: float = 0.5,
        decider: Optional[Callable[[str], bool]] = None,
        method_probs: Optional[dict[str, float]] = None,
    ) -> Callable[[str], bool]:
        def wrapper(name: str) -> bool:
            if decider:
                return decider(name)
            if method_probs and name in method_probs:
                return random() < method_probs[name]
            return random() < probability

        return wrapper

    @staticmethod
    def __handle(
        should_use_real: Callable[[str], bool],
    ) -> Callable[[object, str], Optional[Any]]:

        async def __async_stub() -> None:
            pass

        @wraps(object.__getattribute__)
        def wrapper(self, name: str) -> Any:
            _attr = object.__getattribute__(self, name)
            _f_name = currentframe().f_back.f_code.co_name
            if (
                should_use_real(name)
                or (_f_name.startswith("__") and _f_name.endswith("__"))
            ):
                return _attr

            if iscoroutinefunction(_attr):
                return lambda *args, **kwargs: __async_stub()
            elif callable(_attr):
                return lambda *args, **kwargs: None
            else:
                return None

        return wrapper
