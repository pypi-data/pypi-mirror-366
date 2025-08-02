import pytest
from typer.testing import CliRunner

import typer

import typerhook

from typing import Annotated


class TestDefaultParams:
    """Test the decorator with actual typer.Typer applications."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

    def test_simple_command_with_extra_params(self):
        """Test a simple command with extra parameters."""
        app = typer.Typer()
        
        def debug_params(
            ctx: typer.Context,
            debug: Annotated[bool, typer.Option(help="Set log level to DEBUG")] = False,
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
            debug_status = ctx.obj.get('debug', False)
            verbose_status = ctx.obj.get('verbose', False)
            typer.echo(f"Hello {name}! Debug: {debug_status}, Verbose: {verbose_status}")
        
        # Test with default values
        result = self.runner.invoke(app, [])
        assert result.exit_code == 0
        assert "Hello World! Debug: False, Verbose: False" in result.stdout
        
        # Test with debug flag
        result = self.runner.invoke(app, ["--debug"])
        assert result.exit_code == 0
        assert "Hello World! Debug: True, Verbose: False" in result.stdout
        
        # Test with both flags and custom name
        result = self.runner.invoke(app, ["--debug", "--verbose", "--name", "Alice"])
        assert result.exit_code == 0
        assert "Hello Alice! Debug: True, Verbose: True" in result.stdout

    def test_subcommand_single_context_param(self):
        """Test the problematic case - subcommand with only context parameter."""
        app = typer.Typer()
        sub_app = typer.Typer()
        app.add_typer(sub_app, name="sub", help="Subcommands")
        
        def debug_params(
            ctx: typer.Context,
            debug: Annotated[bool, typer.Option(help="Set log level to DEBUG")] = False,
        ):
            ctx.ensure_object(dict)
            ctx.obj['debug'] = debug
        
        @sub_app.command()
        @typerhook.defaultparams(debug_params)
        def simple(ctx: typer.Context):
            debug_status = ctx.obj.get('debug', False)
            typer.echo(f"Simple command executed. Debug: {debug_status}")
        
        # This should not raise "TypeError: 'Context' object is not iterable"
        result = self.runner.invoke(app, ["sub", "simple"])
        assert result.exit_code == 0
        assert "Simple command executed. Debug: False" in result.stdout
        
        # Test with debug flag
        result = self.runner.invoke(app, ["sub", "simple", "--debug"])
        assert result.exit_code == 0
        assert "Simple command executed. Debug: True" in result.stdout

    def test_command_with_dropped_parameters(self):
        """Test command with dropped parameters."""
        app = typer.Typer()
        
        def debug_params(
            ctx: typer.Context,
            debug: Annotated[bool, typer.Option(help="Set log level to DEBUG")] = False,
            internal: Annotated[bool, typer.Option(help="Internal option")] = False,
        ):
            ctx.ensure_object(dict)
            ctx.obj['debug'] = debug
            # internal parameter should be processed but dropped from command signature
        
        @app.command()
        @typerhook.defaultparams(debug_params, drop=['internal'])
        def process(
            ctx: typer.Context,
            data: Annotated[str, typer.Argument(help="Data to process")]
        ):
            debug_status = ctx.obj.get('debug', False)
            typer.echo(f"Processing {data}. Debug: {debug_status}")
        
        # Test that the command works
        result = self.runner.invoke(app, ["test_data", "--debug"])
        assert result.exit_code == 0
        assert "Processing test_data. Debug: True" in result.stdout
        
        # Test that 'internal' option is not available in the command
        result = self.runner.invoke(app, ["process", "test_data", "--internal"])
        assert result.exit_code != 0  # Should fail because --internal is not recognized

    def test_ellipsis_parameter_replacement(self):
        """Test that ellipsis parameters are properly replaced."""
        app = typer.Typer()
        
        def config_params(
            ctx: typer.Context,
            config_file: Annotated[str, typer.Option(help="Config file path")] = "default.conf",
        ):
            ctx.ensure_object(dict)
            ctx.obj['config_file'] = config_file
        
        @app.command()
        @typerhook.defaultparams(config_params)
        def deploy(
            ctx: typer.Context,
            service: Annotated[str, typer.Argument(help="Service to deploy")],
            config_file=...,  # Should be replaced with default from config_params
        ):
            config = ctx.obj.get('config_file', 'none')
            typer.echo(f"Deploying {service} with config: {config}")
        
        # Test with default config
        result = self.runner.invoke(app, ["web-service"])
        assert result.exit_code == 0
        assert "Deploying web-service with config: default.conf" in result.stdout
        
        # Test with custom config
        result = self.runner.invoke(app, ["web-service", "--config-file", "custom.conf"])
        assert result.exit_code == 0
        assert "Deploying web-service with config: custom.conf" in result.stdout

    def test_help_output_includes_extra_params(self):
        """Test that help output includes parameters from extra function."""
        app = typer.Typer()
        
        def logging_params(
            ctx: typer.Context,
            debug: Annotated[bool, typer.Option(help="Enable debug logging")] = False,
            log_file: Annotated[str, typer.Option(help="Log file path")] = "",
        ):
            pass
        
        @app.command()
        @typerhook.defaultparams(logging_params)
        def run(
            ctx: typer.Context,
            task: Annotated[str, typer.Argument(help="Task to run")]
        ):
            typer.echo(f"Running task: {task}")
        
        # Test help output
        result = self.runner.invoke(app, ["run", "--help"])
        assert result.exit_code == 0
        assert "Enable debug logging" in result.stdout
        assert "Log file path" in result.stdout
        assert "Task to run" in result.stdout

    def test_multiple_commands_with_same_extra_params(self):
        """Test multiple commands using the same extra parameters."""
        app = typer.Typer()
        
        def common_params(
            ctx: typer.Context,
            verbose: Annotated[bool, typer.Option(help="Verbose output")] = False,
        ):
            ctx.ensure_object(dict)
            ctx.obj['verbose'] = verbose
        
        @app.command()
        @typerhook.defaultparams(common_params)
        def start(ctx: typer.Context):
            verbose = ctx.obj.get('verbose', False)
            typer.echo(f"Starting service. Verbose: {verbose}")
        
        @app.command()
        @typerhook.defaultparams(common_params)
        def stop(ctx: typer.Context):
            verbose = ctx.obj.get('verbose', False)
            typer.echo(f"Stopping service. Verbose: {verbose}")
        
        # Test both commands
        result = self.runner.invoke(app, ["start", "--verbose"])
        assert result.exit_code == 0
        assert "Starting service. Verbose: True" in result.stdout
        
        result = self.runner.invoke(app, ["stop", "--verbose"])
        assert result.exit_code == 0
        assert "Stopping service. Verbose: True" in result.stdout

    def test_nested_subcommands(self):
        """Test nested subcommands with extra parameters."""
        app = typer.Typer()
        db_app = typer.Typer()
        user_app = typer.Typer()
        
        app.add_typer(db_app, name="db", help="Database commands")
        db_app.add_typer(user_app, name="user", help="User management")
        
        def db_params(
            ctx: typer.Context,
            host: Annotated[str, typer.Option(help="Database host")] = "localhost",
            port: Annotated[int, typer.Option(help="Database port")] = 5432,
        ):
            ctx.ensure_object(dict)
            ctx.obj['host'] = host
            ctx.obj['port'] = port
        
        @user_app.command()
        @typerhook.defaultparams(db_params)
        def create(
            ctx: typer.Context,
            username: Annotated[str, typer.Argument(help="Username to create")]
        ):
            host = ctx.obj.get('host', 'unknown')
            port = ctx.obj.get('port', 0)
            typer.echo(f"Creating user {username} on {host}:{port}")
        
        result = self.runner.invoke(app, ["db", "user", "create", "alice"])
        assert result.exit_code == 0
        assert "Creating user alice on localhost:5432" in result.stdout
        
        result = self.runner.invoke(app, ["db", "user", "create", "bob", "--host", "prod.db", "--port", "3306"])
        assert result.exit_code == 0
        assert "Creating user bob on prod.db:3306" in result.stdout

    def test_command_with_no_extra_params_after_drop(self):
        """Test command where all extra params are dropped."""
        app = typer.Typer()
        
        def admin_params(
            ctx: typer.Context,
            admin_key: Annotated[str, typer.Option(help="Admin key")] = "secret",
        ):
            # This function processes admin_key but it's dropped from command signature
            pass
        
        @app.command()
        @typerhook.defaultparams(admin_params, drop=['admin_key'])
        def public_info(ctx: typer.Context):
            typer.echo("Public information accessed")
        
        result = self.runner.invoke(app, [])
        assert result.exit_code == 0
        assert "Public information accessed" in result.stdout
        
        # Admin key should not be available as an option
        result = self.runner.invoke(app, ["--admin-key", "test"])
        assert result.exit_code != 0

    def test_error_handling(self):
        """Test error handling in decorated commands."""
        app = typer.Typer()
        
        def validate_params(
            ctx: typer.Context,
            max_items: Annotated[int, typer.Option(help="Maximum items")] = 100,
        ):
            ctx.ensure_object(dict)
            if max_items <= 0:
                raise ValueError("max_items must be positive")
            ctx.obj['max_items'] = max_items
        
        @app.command()
        @typerhook.defaultparams(validate_params)
        def process_items(
            ctx: typer.Context,
            items: Annotated[str, typer.Argument(help="Items to process")]
        ):
            max_items = ctx.obj.get('max_items', 100)
            typer.echo(f"Processing {items} (max: {max_items})")
        
        # Test with valid parameters
        result = self.runner.invoke(app, ["data", "--max-items", "50"])
        assert result.exit_code == 0
        assert "Processing data (max: 50)" in result.stdout

    def test_original_use_case_reproduction(self):
        """Test that reproduces your original use case exactly."""
        app = typer.Typer()
        other_app = typer.Typer()
        app.add_typer(other_app, name='other', help='help me')
        
        def debug_params(
            ctx: typer.Context,
            debug: Annotated[bool, typer.Option(help="Set log level to DEBUG")] = False,
            drop: Annotated[bool, typer.Option(help="Drop option")] = False,
        ):
            ctx.ensure_object(dict)
            ctx.obj['debug'] = debug
            ctx.obj['drop'] = drop
        
        @other_app.command()
        @typerhook.defaultparams(debug_params, drop=('drop',))
        def ohman(ctx: typer.Context):
            debug_status = ctx.obj.get('debug', False)
            typer.echo(f'ohman executed, debug: {debug_status}')
        
        @app.command()
        @typerhook.defaultparams(debug_params, drop=('drop',))
        def hello(
            ctx: typer.Context,
            name: Annotated[str, typer.Option()],
            debug=...
        ):
            debug_status = ctx.obj.get('debug', False)
            typer.echo(f"hello {name}, debug: {debug_status}")
        
        # Test the problematic subcommand
        result = self.runner.invoke(app, ["other", "ohman"])
        assert result.exit_code == 0
        assert "ohman executed, debug: False" in result.stdout
        
        result = self.runner.invoke(app, ["other", "ohman", "--debug"])
        assert result.exit_code == 0
        assert "ohman executed, debug: True" in result.stdout
        
        # Test main command
        result = self.runner.invoke(app, ["hello", "--name", "world"])
        assert result.exit_code == 0
        assert "hello world, debug: False" in result.stdout
        
        result = self.runner.invoke(app, ["hello", "--name", "world", "--debug"])
        assert result.exit_code == 0
        assert "hello world, debug: True" in result.stdout
