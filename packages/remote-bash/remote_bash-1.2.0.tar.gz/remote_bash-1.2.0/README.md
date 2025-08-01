# Remote Bash Shell (remote_bash)

[![PyPI version](https://badge.fury.io/py/remote-bash.svg)](https://badge.fury.io/py/remote-bash)
[![Python Version](https://img.shields.io/pypi/pyversions/remote-bash.svg)](https://pypi.org/project/remote-bash/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)


## 🚀 Make Your Remote Server Feel Local

Tired of complex file sync setups? Confused by `rsync`, `scp`, or NFS exports?  
Frustrated when local computing isn't enough — but sharing data with a remote server feels like a nightmare?

**`remote_bash` solves this with one simple command.**

With `rbash` or `remote_bash`, you can:

- 🔄 **Mount your local folder** directly into a remote server using a **reverse `sshfs` tunnel**
- 🖥️ **Run remote code on your data**, just like it's local — ideal for training, compiling, debugging, or experimentation
- 🔐 Skip the hassle of SSH key sharing — everything is temporary and secure
- 🧼 Automatic cleanup after session ends (including keys and mount points)

All without:

- ❌ NFS configuration
- ❌ Manual SSH forwarding
- ❌ Sharing full system access

Whether you're a developer, data scientist, or systems engineer —  
**`rbash` makes remote environments feel just like home.**

## Features

- **Automatic local directory mounting** to remote workspace via reverse SSHFS
- **Reverse SSH tunnel** + `sshfs` (no NFS configuration or port forwarding required)
- **Temporary key exchange** with automatic cleanup (no permanent SSH key setup needed)
- **Seamless integration** with your existing `~/.ssh/config`
- **Auto-cleanup** of mounts, keys, and temporary files after session ends
- **Host discovery** from SSH config with tabular output

## Installation

```bash
pip install remote-bash
```

## Quick Start

List available remote hosts from your SSH config:

```bash
rbash
# or
remote_bash
```

Connect to a specific host:

```bash
rbash <hostname>
# or
remote_bash <hostname>
```

The `<hostname>` must be a valid Host entry in your `~/.ssh/config`.

## Example Usage

```bash
rbash myserver
```

This command will:

1. Create a temporary SSH keypair on the remote machine
2. Add the remote public key to your local `authorized_keys`
3. Establish a reverse SSH tunnel to your local machine
4. Mount your current directory to `/home/remote_user/workspaceXXXXXX` on the remote server
5. Drop you into an interactive bash shell on the remote machine

## Requirements

### Local Machine
- Python 3.8+
- `ssh` client
- `sshfs` (FUSE filesystem)

### Remote Machine
- SSH server
- `sshfs` (FUSE filesystem)
- FUSE support enabled

### Installation of Dependencies

**Ubuntu/Debian:**
```bash
sudo apt install sshfs
```

**macOS:**
```bash
brew install sshfs
```

**CentOS/RHEL/Fedora:**
```bash
sudo yum install sshfs  # CentOS/RHEL
sudo dnf install sshfs  # Fedora
```

## SSH Configuration

Ensure your `~/.ssh/config` contains the target hosts. Example:

```
Host myserver
    HostName 192.168.1.100
    User myuser
    IdentityFile ~/.ssh/id_rsa

Host production
    HostName prod.example.com
    User deploy
    Port 2222
    IdentityFile ~/.ssh/prod_key
```

## How It Works

1. **Host Discovery**: Parses your `~/.ssh/config` to find available hosts
2. **Temporary Key Generation**: Creates a temporary SSH keypair on the remote machine
3. **Reverse Tunnel Setup**: Establishes a reverse SSH connection from remote to local
4. **Directory Mounting**: Uses SSHFS to mount your local directory on the remote machine
5. **Interactive Shell**: Drops you into a bash shell with your local files accessible
6. **Automatic Cleanup**: Removes temporary keys, unmounts directories, and cleans up on exit

## Security

- Uses temporary SSH keys that are automatically removed after the session
- No permanent modifications to SSH configurations
- All connections use your existing SSH config and key authentication
- Reverse tunnel is automatically torn down on exit

## Troubleshooting

### Permission Denied
Ensure your SSH key has proper permissions and the remote user has sudo access for FUSE mounting.

### SSHFS Not Found
Install `sshfs` on both local and remote machines using your system's package manager.

### Connection Refused
Verify the host configuration in your `~/.ssh/config` and ensure you can connect manually with `ssh <hostname>`.

## Contributing

Contributions are welcome! Please ensure:

- Scripts remain portable across Unix-like systems
- SSH compatibility is maintained
- Include tests for new features
- Follow existing code style

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Changelog

### [1.2.0] - 2025-08-01

#### Bug Fix
- Update remote system check with sshf and fuse


### [1.1.0] - 2025-07-31

#### Bug Fix
- Update path of bash.sh

### [1.0.1] - 2025-07-31

#### Added
- Update the pip install remote-bash

### [1.0.0] - 2025-07-31

#### Added
- Initial release of `remote_bash`
- CLI commands: `rbash` and `remote_bash`
- Reverse SSHFS mounting with local → remote path mapping
- Remote temporary SSH key exchange
- Automatic cleanup of keys, mounts, and workspace
- Host listing from `~/.ssh/config` in table formatere’s a complete README.md for your PyPI package Remote Bash Shell (rbash), along with a CHANGELOG.md to track versions.

