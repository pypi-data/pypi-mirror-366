import inspect
import functools as ft

import typerhook.utils as utils

from typing import Any, Callable, NoReturn, Optional, Sequence


__all__ = ["defaultparams"]


def defaultparams(defaults: Callable, *, drop: Optional[Sequence[str]] = None) -> Callable | NoReturn:
    """
    Append defaults parameters to a Typer command.
    """
    def wrapper(command: Callable) -> Callable:
        nonlocal drop
        drop = drop or []
  
        default_sig = inspect.signature(defaults)
        command_sig = inspect.signature(command)
        new_sig = utils._combine_signatures(command_sig, default_sig, drop = drop)

        # correct dispatch with variadic args and po parameters would be more tricky.
        # don't konw if we have such use cases with typer.
        assert not any(
          p.kind in (inspect.Parameter.POSITIONAL_ONLY, inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD)
            for p in new_sig.parameters.values()
        )

        default_paramnames = [p.name for p in default_sig.parameters.values() if p.name not in drop]
        command_paramnames = [p.name for p in command_sig.parameters.values()]

        @ft.wraps(command)
        def wrapped(*args, **kwargs) -> Any:
            newly_bound = new_sig.bind(*args, **kwargs)
            newly_bound.apply_defaults()

            if default_paramnames:
                defaults(**{k: newly_bound.arguments[k] for k in default_paramnames if k in newly_bound.arguments})

            # invoke decorated command
            return command(**{k: newly_bound.arguments[k] for k in command_paramnames if k in newly_bound.arguments})

        setattr(wrapped, '__signature__', new_sig)
        return wrapped

    return wrapper
