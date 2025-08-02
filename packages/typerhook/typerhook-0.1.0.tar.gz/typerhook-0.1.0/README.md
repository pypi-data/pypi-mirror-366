# TyperHook

## Overview

Hook decorators to enhance Typer CLIs. Current hooks:

1. defaultparams: adapted from GitHub user Antoine adm271828,
shares parameters between typer commands

## Installation

```bash
pip install typerhook
```

## Quick Start

```python
import typer
import typerhook
from typing import Annotated

app = typer.Typer()

def debug_params(
    ctx: typer.Context,
    debug: Annotated[bool, typer.Option(help="Enable debug mode")] = False,
    verbose: Annotated[bool, typer.Option(help="Verbose output")] = False,
):
    ctx.ensure_object(dict)
    ctx.obj['debug'] = debug
    ctx.obj['verbose'] = verbose

@app.command()
@typerhook.defaultparams(debug_params)
def hello(
    ctx: typer.Context,
    name: Annotated[str, typer.Option(help="Name to greet")] = "World"
):
    debug_mode = ctx.obj.get('debug', False)
    typer.echo(f"Hello {name}! Debug mode: {debug}; Verbose mode: {verbose}")

@app.command()
@typerhook.defaultparams(debug_params)
def bye(
    ctx: typer.Context,
    name: Annotated[str, typer.Option(help="Name to greet")] = "World"
):
    debug = ctx.obj.get('debug', False)
    verbose = ctx.obj.get('verbose', False)
    typer.echo(f"Goodbye {name}! Debug mode: {debug}; Verbose mode: {verbose}")

if __name__ == "__main__":
    app()
```

## API Reference

### `defaultparams(extra: Callable, *, drop: Optional[Sequence[str]]=None)`

Decorator factory that adds extra parameters to a Typer command.

**Parameters:**
- `extra`: Function containing the extra parameters to inject
- `drop`: List of parameter names to exclude from the final signature

## License

MIT License - see LICENSE file for details.
