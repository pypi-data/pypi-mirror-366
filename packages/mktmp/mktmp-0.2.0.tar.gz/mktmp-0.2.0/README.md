# MKTMP

MKTMP is a command-line tool for creating temporary directories along with symbolic links to them — enabling centralized, consistent management of ephemeral files.

## Setup

Add your user to the "Create symbolic links" user right in Windows to avoid permission issues when creating symbolic links.

```
Security Settings > Local Policies > User Rights Assignment > Create symbolic links
安全设置 > 本地策略 > 用户权限分配 > 创建符号链接
```

## Usage

### Initial Configuration

Before using MKTMP, you need to configure the mountpoint (directory where temporary folders will be created):

```bash
# Interactive configuration setup
python -m mktmp.config_cli init

# Or set mountpoint directly
python -m mktmp.config_cli mountpoint /path/to/temp/directory
```

The configuration will be saved to `~/.mktmp.config.json`.

### Creating Temporary Directories

```bash
# Create a temporary directory with a symbolic link
mktmp myproject

# This creates:
# - A unique temporary directory in your configured mountpoint
# - A symbolic link named 'myproject' in your current directory pointing to the temp directory
```
