import typer
from .config import save_config, load_and_validate_config, create_validated_config

app = typer.Typer(no_args_is_help=True)


@app.command()
def init():
    """Interactively initialize configuration by changing each value."""
    typer.echo("Initializing mktmp configuration...")

    # Get current mountpoint value or use default
    try:
        current_config = load_and_validate_config()
        current_mountpoint = current_config.mountpoint
    except FileNotFoundError:
        current_mountpoint = None

    # Interactively get mountpoint value
    if current_mountpoint:
        mountpoint = typer.prompt(
            "Enter mountpoint path",
            default=current_mountpoint
        )
    else:
        mountpoint = typer.prompt(
            "Enter mountpoint path"
        )
        default = current_mountpoint

    # Create new config with validated mountpoint
    try:
        new_config = create_validated_config(mountpoint)

        # Save the configuration
        save_config(new_config)

        typer.echo("Configuration saved successfully!")
        typer.echo(
            f"Mountpoint: {typer.style(new_config.mountpoint, fg=typer.colors.GREEN)}")
    except ValueError as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=1)


@app.command()
def mountpoint(mountpoint: str):
    """Set the mountpoint and overwrite the config file."""
    # Create new config with validated mountpoint
    try:
        new_config = create_validated_config(mountpoint)

        # Save the configuration (overwriting existing)
        save_config(new_config)

        typer.echo("Configuration updated successfully!")
        typer.echo(
            f"Mountpoint set to: {typer.style(new_config.mountpoint, fg=typer.colors.GREEN)}")
    except ValueError as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=1)


def main():
    app()
