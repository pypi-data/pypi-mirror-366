# SSH Tunnel Manager GUI

[![Build status](https://github.com/NtWriteCode/ssh-tunnel-manager/actions/workflows/main-build.yml/badge.svg)](https://github.com/NtWriteCode/ssh-tunnel-manager/actions/workflows/main-build.yml)
[![PyPi upload status](https://github.com/NtWriteCode/ssh-tunnel-manager/actions/workflows/publish-to-pypi.yml/badge.svg)](https://github.com/NtWriteCode/ssh-tunnel-manager/actions/workflows/publish-to-pypi.yml)

![SSH Tunnel Manager Icon](./ssh_tunnel_manager/icon.ico)

![SSH Tunnel Manager Screenshot](./resources/gui.png)

A modern, user-friendly desktop application for managing SSH tunnels with ease.

## Overview

The SSH Tunnel Manager simplifies creating, managing, and executing SSH tunnels through an intuitive Graphical User Interface (GUI). Built with Python and PyQt6, it allows for easy configuration of connection profiles, port forwarding, and tunnel control.

## Getting Started

There are a couple of easy ways to get started with SSH Tunnel Manager:

### 1. Download Executable (Recommended)

The easiest way to use the application is to download a pre-built executable for your operating system.

1.  Go to the [Releases page](https://github.com/NtWriteCode/ssh-tunnel-manager/releases).
2.  Download the latest executable for your system (Windows, macOS, or Linux).
3.  Run the downloaded application. No installation is typically required.

### 2. Install with pip (Cross-Platform)

If you have Python and pip installed, you can install the SSH Tunnel Manager GUI directly from PyPI:

```bash
pip install ssh-tunnel-manager-gui
```
Then, you should be able to run it from your terminal (the exact command might depend on your system's PATH configuration, often it's `ssh-tunnel-manager-gui`).

## Key Features

*   **Intuitive Profile Management:** Save, load, and manage multiple SSH connection profiles.
*   **Easy Port Forwarding:** Configure multiple local-to-remote port mappings per profile.
*   **Simple Tunnel Control:** Start/stop tunnels with a click. Copy the underlying SSH command.
*   **Real-time Status:** Clear visual feedback on tunnel status (Idle, Starting, Running, Stopped, Errors).
*   **Automatic Persistence:** Profiles are saved to `~/.config/ssh_tunnel_manager/config.json`.
*   **Privileged Port Warnings:** Automatic detection and warnings for ports < 1024 that require sudo/root access.

## Configuration

Once the application is running:

*   **Server:** Enter the SSH server address (`user@hostname`).
*   **SSH Port:** Specify the SSH server port (defaults to 22).
*   **Authentication:** Choose between SSH Key (default) or Password authentication.
    *   **SSH Key File:** (Optional) Path to your SSH private key (tilde `~` expansion supported).
    *   **Password:** Enter your SSH password (requires `sshpass` to be installed).
*   **Port Forwarding:** Add/remove `Local Port` to `Remote Port` mappings.
*   **Profiles:** Save, load, or delete configurations. Changes are auto-saved.

Application data is stored in `~/.config/ssh_tunnel_manager/config.json`.

## For Developers

If you want to contribute or run the latest development version:

### Running from Source

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/NtWriteCode/ssh-tunnel-manager.git
    cd ssh-tunnel-manager
    ```
2.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```
3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    # For development, also install dev dependencies:
    # pip install -r requirements.dev.txt
    ```
4.  **Run the application:**
    ```bash
    python -m ssh_tunnel_manager.main  # Or your project's main entry point
    ```
    *(Note: I've assumed `python -m ssh_tunnel_manager.main` as a common way to run GUI apps from a package structure. If your entry point is just `python main.py` at the root, please adjust or let me know.)*

### Requirements (for running from source)

*   Python 3.x
*   PyQt6 (`PyQt6>=6.0.0`)
*   `typing-extensions>=4.0.0`
*   An SSH client installed and available in your system's PATH (e.g., OpenSSH).
*   `sshpass` (optional, required for password authentication):
    *   Ubuntu/Debian: `sudo apt install sshpass`
    *   macOS: `brew install sshpass`
    *   CentOS/RHEL: `sudo yum install sshpass`

### Building from Source

The project uses PyInstaller. The GitHub Actions workflow (`.github/workflows/main-build.yml`) handles release builds.

To build manually:
1.  Ensure you are in the project root with your virtual environment activated.
2.  Install build dependencies: `pip install pyinstaller`
3.  Run PyInstaller (example):
    ```bash
    pyinstaller --onefile --name ssh-tunnel-manager-gui --windowed --icon="ssh_tunnel_manager/icon.ico" --add-data "ssh_tunnel_manager/icon.ico:ssh_tunnel_manager" run_app.py
    ```
    (The `run_app.py` script is a dedicated entry point for PyInstaller. `--icon` sets the executable icon. `--add-data` ensures the icon is also bundled for runtime access. `--windowed` is good for GUI apps. The name `ssh-tunnel-manager-gui` aligns with the PyPI name.)
    Executables are found in the `dist` directory.

## Contributing

Contributions are welcome! Please fork the repository, create a feature branch, commit your changes, and open a pull request.

1.  Fork the Project
2.  Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3.  Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4.  Push to the Branch (`git push origin feature/AmazingFeature`)
5.  Open a Pull Request

## License

Distributed under the MIT License. See `LICENSE` for more information.
