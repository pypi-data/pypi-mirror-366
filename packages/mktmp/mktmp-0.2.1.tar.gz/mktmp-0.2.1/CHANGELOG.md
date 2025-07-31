# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.1]

### Added
- Configuration CLI `show` command to display current configuration settings

## [0.2.0]

### Added
- Configuration management system with JSON-based config file
- Interactive configuration CLI (`mktmp-config`) with `init` and `mountpoint` commands
- Path validation and normalization to Unix-style format
- Automatic mountpoint directory creation
- Pydantic-based configuration schema validation
- Configuration file stored at `~/.mktmp.config.json`

### Changed
- **BREAKING**: Replaced environment variable (`MKTMP_DIR`) with configuration file system
- Main CLI now reads mountpoint from configuration instead of environment variables

## [0.1.0] - Initial Release

### Added
- Basic temporary directory creation with symbolic links
- Typer-based CLI interface
