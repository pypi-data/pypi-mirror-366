import inspect

from typing import NoReturn, Optional, Sequence

def _combine_signatures(
    first: inspect.Signature,
    second: inspect.Signature,
    *,
    drop: Optional[Sequence[str]] = None,
    ) -> inspect.Signature | NoReturn:
    """
    Combine two signatures.
  
    Returns a new signature where the parameters of the second signature have been
    injected in the first if they weren't already there (i.e. same name not found).

    The following rules are used:
      - parameter order is preserved, with parameter from first signature coming
        first, and parameters from second one coming after
      - when a parameter (same name) is found in both signatures, parameter from
        first signature is kept, but if its annotation or default value is Ellipsis
        they are replaced with annotation and default value coming from second
        parameter.
      - parameters in second signature whose name appear in drop list are not 
        taken into account

    Once this is done, we do not have a valid signature. The following extra step
    are performed:
      - move all positional only parameter first. Positional only parameters will
        still be ordered together, but some parameters from second signature will
        now appear before parameters from first signature (the non positional only
        ones).
      - make sure we have at most one variadic parameter of each kind (keyword and
        non keyword). They can appear in both original signature but under same
        name. Otherwise a ValueError is raised.
      - move keyword only parameters last (just before variadic keyword perameter)
      - keyword only parameters are left as is. It does not seem to be a problem is
        some of have default values and appear before other keyword only parameters
        without default value.

    Result is still not a valid signature as we could have some positional only
    parameter with a default value, followed by non keyword or positional without
    default value. In this case, a ValueError will be raised.
    """
    drop = drop or []

    params = dict(first.parameters)

    for n, p1 in second.parameters.items():
      if n in drop:
        continue

      if (p0 := params.get(n)):
        if p0.default is Ellipsis or p0.default is inspect.Parameter.empty:
          p0 = p0.replace(default = p1.default)
        if p0.annotation is inspect.Parameter.empty:
          p0 = p0.replace(annotation = p1.annotation)
        params[n] = p0
      else:
        params[n] = p1

    # Sort params by kind, moving params with default value after params without
    # default value within each kind group.
    params = sorted(
      params.values(), key = lambda p: 2 * p.kind + bool(p.default != inspect.Parameter.empty)
    )

    # Will raise if signature not valid
    return first.replace(parameters = params)
