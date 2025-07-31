import json
from pathlib import Path
from pydantic import ValidationError
from .schema import Config


DEFAULT_CONFIG_PATH = Path.home() / ".mktmp.config.json"


def validate_unix_absolute_path(path: str) -> str:
    """
    Validate and normalize a path to Unix-style path format.

    Args:
        path: Path string to validate

    Returns:
        str: Unix-style path (with / separators)

    Raises:
        ValueError: If path is empty or cannot be processed by pathlib
    """
    if not path:
        raise ValueError("Path cannot be empty")

    try:
        # Convert to Path object and resolve
        path_obj = Path(path).expanduser().resolve()

        # Convert to Unix-style path (replace \ with /)
        unix_path = path_obj.as_posix()

        return unix_path
    except Exception as e:
        raise ValueError(f"Invalid path: {path} - {e}")


def load_and_validate_config() -> Config:
    """
    Load configuration from the default config file and validate it against the Config schema.

    Returns:
        Config: Validated configuration object

    Raises:
        FileNotFoundError: If config file is not found at default location
        ValidationError: If config doesn't match schema
        json.JSONDecodeError: If config file is not valid JSON
    """
    config_file = DEFAULT_CONFIG_PATH

    if not config_file.exists():
        raise FileNotFoundError(
            f"Config file not found at default location: {config_file}")

    # Load and parse JSON
    with open(config_file, 'r') as f:
        config_data = json.load(f)

    # Validate against schema
    try:
        config = Config(**config_data)
        return config
    except ValidationError as e:
        raise ValidationError(f"Config validation failed: {e}")


def save_config(config: Config) -> None:
    """
    Save a Config object to the default config file location.

    Args:
        config: Config object to save

    Raises:
        OSError: If unable to write to the config file
        json.JSONEncodeError: If config cannot be serialized to JSON
        ValueError: If mountpoint is not a valid Unix-style absolute path
    """
    # Validate mountpoint before saving
    validated_mountpoint = validate_unix_absolute_path(config.mountpoint)

    # Create a new config with validated mountpoint
    validated_config = Config(mountpoint=validated_mountpoint)

    config_file = DEFAULT_CONFIG_PATH

    # Ensure the parent directory exists
    config_file.parent.mkdir(parents=True, exist_ok=True)

    # Convert config to dict and save as JSON
    with open(config_file, 'w') as f:
        json.dump(validated_config.model_dump(), f, indent=2)


def create_validated_config(mountpoint: str) -> Config:
    """
    Create a Config object with validated mountpoint.

    Args:
        mountpoint: Path string for the mountpoint

    Returns:
        Config: Config object with validated Unix-style absolute mountpoint

    Raises:
        ValueError: If mountpoint is not a valid path
    """
    validated_mountpoint = validate_unix_absolute_path(mountpoint)
    return Config(mountpoint=validated_mountpoint)
