# TorManager

TorManager is a macOS menu-bar application written in Python that controls a local Tor service, configures the system SOCKS proxy, and reports the current public IP address.

![Python](https://img.shields.io/badge/Language-Python-3776AB?style=flat-square&logo=python&logoColor=white)
![macOS](https://img.shields.io/badge/Platform-macOS-000000?style=flat-square&logo=apple&logoColor=white)
![Menu bar app](https://img.shields.io/badge/Interface-Menu_bar_app-555555?style=flat-square)
![Tor](https://img.shields.io/badge/Network-Tor-7D4698?style=flat-square&logo=torproject&logoColor=white)
![Year](https://img.shields.io/badge/Year-2025-6c757d?style=flat-square)

## Overview

TorManager provides a native menu-bar interface for a Tor daemon running locally on the machine. The application detects whether Tor is listening on its local SOCKS port, starts or stops the Tor service through Homebrew, enables or disables the macOS SOCKS proxy for each network service, and displays the public IP obtained from `api.ipify.org`.

The implementation is contained in [`tor_menu.py`](tor_menu.py), with [`setup.py`](setup.py) providing a `py2app` configuration for building a macOS application bundle.

## Features

- **Control Tor:** Start or stop the Tor service through the Homebrew service manager.
- **Configure the system proxy:** Set or clear the SOCKS proxy at `127.0.0.1:9050` for the network services reported by macOS `networksetup`.
- **Inspect status and IP:** Show whether Tor is active and retrieve the public IP directly or through Tor.
- **Request a new identity:** Send `SIGNAL NEWNYM` to Tor's control port at `127.0.0.1:9051`.
- **Run from the menu bar:** Present actions through a `rumps` menu-bar application and use the bundled `icon_def.png` icon.

## Technology stack

- **Language:** Python 3
- **User interface:** `rumps`
- **HTTP client:** `requests`
- **Application packaging:** `py2app`
- **macOS integration:** `networksetup` and Homebrew services
- **Network service:** A locally running Tor daemon

## Prerequisites

The source code assumes:

- macOS, including `/usr/sbin/networksetup`;
- Python 3;
- the Python packages `rumps` and `requests`;
- `py2app` for application packaging;
- Tor installed and managed by Homebrew at `/opt/homebrew/bin/brew`.

The repository does not include a dependency manifest or automated environment setup. Install the prerequisites using the package-management workflow appropriate for your machine before running the application.

## Getting started

From the repository root, run the Python entry point directly:

```bash
python3 tor_menu.py
```

The application expects Tor to be available locally. Its initial state is determined by whether port `9050` accepts a connection. The **Activate Tor** action starts the Homebrew Tor service when necessary, then enables the system SOCKS proxy. The **Deactivate Tor** action disables the proxy and stops the service.

The **Show Status and IP** action queries `https://api.ipify.org`; when Tor is active, the request is sent through the local SOCKS proxy.

## Build a macOS application

The checked-in `setup.py` defines a `py2app` application configuration, includes `icon_def.png` as application data, and uses `icon.icns` as the bundle icon. Build the application bundle with:

```bash
python setup.py py2app
```

## Project structure

```text
.
├── tor_menu.py   # Menu-bar application and Tor/proxy operations
├── setup.py      # py2app build configuration
├── icon.icns     # Application bundle icon
└── icon_def.png  # Menu-bar icon
```

## Testing

No automated test suite is included in the repository. The Python source files can be syntax-checked with:

```bash
python3 -c "import ast; from pathlib import Path; [ast.parse(Path(path).read_text(encoding='utf-8'), filename=path) for path in ('tor_menu.py', 'setup.py')]"
```

## Project status

This repository contains a compact, single-file utility. It has no documented release process, continuous integration workflow, or dependency lockfile. The application should therefore be treated as a local utility rather than a production service.

## License

This project is licensed under the MIT License. See the LICENSE file for details.
