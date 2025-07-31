import typer
from pathlib import Path
from dotenv import load_dotenv
import os
import hashlib
from datetime import datetime

app = typer.Typer()


def build_unique_tmp_folder_name(path: Path) -> str:
    """
    Build a unique temporary folder name based on the symbolic link path.
    """
    resolved_path = path.expanduser().resolve()
    hashed = hashlib.sha256(str(resolved_path).encode()).hexdigest()
    timestamp = datetime.now().strftime("%y%m%d_%H%M%S")
    return f"{timestamp}_{hashed[:8]}"


@app.command()
def mktmp(name: str):
    """
    create a temporary directory and a symbolic link to it.
    """
    # retrieve the temporary directory.
    tmp_dir = os.getenv('MKTMP_DIR')
    if not tmp_dir:
        typer.echo("MKTMP_DIR environment variable is not set.")
        raise typer.Exit(code=1)
    assert tmp_dir
    tmp_dir = Path(tmp_dir).expanduser().resolve()

    # build the symbolic link path.
    cwd = Path.cwd()
    symlink_path = cwd / name
    if symlink_path.exists():
        typer.echo(f'Symbolic link "{symlink_path}" already exists.')
        raise typer.Exit(code=1)

    # create the tmporary directory.
    tmp_folder_name = build_unique_tmp_folder_name(symlink_path)
    tmp_folder_path = tmp_dir / tmp_folder_name
    if tmp_folder_path.exists():
        typer.echo(f'Temporary folder "{tmp_folder_path}" already exists.')
        raise typer.Exit(code=1)
    try:
        tmp_folder_path.mkdir(parents=True, exist_ok=False)
    except FileExistsError:
        typer.echo(f'Temporary folder "{tmp_folder_path}" already exists.')
        raise typer.Exit(code=1)

    # create the symbolic link.
    try:
        symlink_path.symlink_to(tmp_folder_path)
        typer.echo("Symlink created:")
        typer.echo(typer.style(symlink_path, fg=typer.colors.GREEN))
        typer.echo(f"pointing to:")
        typer.echo(typer.style(tmp_folder_path, fg=typer.colors.GREEN))
    except FileExistsError:
        typer.echo(f'Symbolic link "{symlink_path}" already exists.')
        raise typer.Exit(code=1)


def main():
    load_dotenv()
    app()
