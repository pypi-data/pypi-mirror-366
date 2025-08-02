# Pakto

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

>_(pronounced "pack-toe")_

**Pakto** is a command-line tool for bundling and distributing software as OCI (Open Container Initiative) artifacts. It provides a comprehensive solution for creating, managing, and deploying software bundles with enterprise-grade security and compliance features.

Pakto is designed for both developers building bespoke systems (particularly in airgapped environments) and their customers who need reliable, reproducible software deployments. It enables seamless software distribution from development environments to production systems, ensuring consistency and traceability across the entire deployment pipeline.

## 🚀 Features

- **OCI-Native Bundling**: Create and manage software bundles as OCI artifacts
- **Multi-Artifact Support**: Bundle containers, files, and other artifacts in a single package
- **Registry Integration**: Push and pull bundles from OCI-compatible registries
- **Security & Compliance**: Built-in SBOM generation and integrity verification
- **Offline Capabilities**: Build and verify bundles without network access
- **Template System**: Scaffold new bundles with predefined templates
- **Variable Substitution**: Dynamic configuration with templating support
- **Airgapped Deployment**: Designed for secure, isolated environments

## 📋 Requirements

- Python 3.11 or higher
- `uv` package manager (recommended) or `pip`

## 🛠️ Installation

### Using uv (Recommended)

```bash
# Install from PyPI
uv tool install pakto

# Or install from source
git clone https://github.com/wixregiga/pakto.git
cd pakto
uv pip install -e .
```

### Using pip

```bash
pip install pakto
```

## 🎯 Quick Start

### 1. Initialize a New Bundle

```bash
# Create a new bundle project
pakto bundle init my-application

# Or initialize in current directory
pakto bundle init
```

### 2. Build Your Bundle

```bash
# Build from manifest file
pakto bundle build -f my-application.pakto.yml

# Or build from lockfile
pakto bundle build -f my-application.lock
```

### 3. Push to Registry

```bash
# Push to registry
pakto bundle push my-application.bundle registry.example.com/my-application:v1.0.0
```

### 4. Pull and Apply

```bash
# Pull from registry
pakto bundle pull registry.example.com/my-application:v1.0.0

# Apply bundle (extract and execute)
pakto bundle apply my-application.bundle
```

## 📖 Usage

### Bundle Commands

| Command | Description |
|---------|-------------|
| `init` | Scaffold a starter manifest file |
| `build` | Build a .bundle file from manifest or lockfile |
| `verify` | Verify bundle integrity and contents |
| `push` | Push a bundle to an OCI registry |
| `pull` | Pull a bundle from an OCI registry |
| `extract` | Extract bundle contents |
| `info` | Show bundle information |
| `apply` | Extract artifacts and execute entrypoints |

### Bundle Management

```bash
# List bundle contents (inclide `--json` for more detailed output)
pakto bundle info my-application.bundle

# Extract bundle to directory
pakto bundle extract my-application.bundle ./extracted/

# Verify bundle integrity
pakto bundle verify my-application.bundle
```

### Configuration

```bash
# View current configuration
pakto config show

# Set registry default
pakto config set registry.default registry.example.com
```

## 📝 Manifest Format

Pakto uses YAML manifests to define bundle contents and metadata:

```yaml
apiVersion: pakto.warrical.com/v1alpha1
kind: Manifest
metadata:
  name: my-application
  version: 1.0.0
  description: "My application bundle"
  category: application

variables:
  app_version: 2.1.0
  base_image: alpine:3.18

entrypoint:
  script: "install.sh"
  mode: "0755"

artifacts:
  - name: my-app-{{metadata.version}}
    origin: oci://docker.io/myorg/myapp:{{variables.app_version}}
    target: my-app-{{metadata.version}}.tar
  - name: config-files
    origin: local://./config/
    target: config/
```

## 🔧 Configuration

Pakto can be configured via environment variables or a configuration file (`/etc/pakto/pakto.yaml` or `~/.config/pakto/pakto.yaml`):

```yaml
registry:
  default: registry.example.com
  auth:
    username: ${PAKTO_REGISTRY_USERNAME}
    password: ${PAKTO_REGISTRY_PASSWORD}

security:
  verify_signatures: true
  verify_hashes: true
  attach_sbom: true
  attach_attest: true

build:
  workers: 4
  offline: false
```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `PAKTO_REGISTRY_DEFAULT` | Default registry host | - |
| `PAKTO_REGISTRY_USERNAME` | Registry username | - |
| `PAKTO_REGISTRY_PASSWORD` | Registry password | - |
| `PAKTO_BUILD_OFFLINE` | Disable network during build | false |

## 🔒 Security Features

- **Hash Verification**: SHA-256 integrity checks for all artifacts
- **SBOM Generation**: Automatic Software Bill of Materials creation
- **Content Verification**: Verify bundle contents and metadata
- **Offline Security**: Secure operation in airgapped environments

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
uv run pytest -v --tb=short --disable-warnings

# Run specific test file
uv run pytest -v --tb=short --disable-warnings tests/test_pack_service_integration.py
```

**Note**: The full test suite requires a running zot-registry instance for integration tests. Some tests will be skipped if zot-registry is not available.

## 📚  Documentation *[WIP]*

## 🤝 Contributing *[WIP]*

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Setup

```bash
# Clone repository
git clone https://github.com/wixregiga/pakto.git
cd pakto

# Install development dependencies
uv sync --group dev

# Install in development mode
uv pip install -e .

# Run tests
uv run pytest -v
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👤 Author

**wixregiga** - [kecyojagi@protonmail.com](mailto:kecyojagi@protonmail.com)

## 🙏 Acknowledgments

- OCI (Open Container Initiative) for the artifact specification
- The Python packaging community for inspiration and tools