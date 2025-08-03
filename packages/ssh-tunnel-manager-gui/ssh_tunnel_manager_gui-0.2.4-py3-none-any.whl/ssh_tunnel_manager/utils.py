# Utility functions (command generation, validation, etc.) will go here
import shlex
import os
import subprocess
from pathlib import Path
from typing import Optional, Tuple, Dict, Any


def is_valid_port(port: int) -> bool:
    """Checks if a port number is valid (1-65535)."""
    # Ensure it's an integer first
    if not isinstance(port, int):
        return False
    return 1 <= port <= 65535

def parse_port_mapping(mapping_str: str) -> Optional[Tuple[int, int]]:
    """Parses a 'local:remote' port mapping string."""
    parts = mapping_str.split(':')
    if len(parts) == 2:
        try:
            # Strip whitespace before converting to int
            local_part = parts[0].strip()
            remote_part = parts[1].strip()
            if not local_part or not remote_part: # Check for empty strings after strip
                return None
            local_port = int(local_part)
            remote_port = int(remote_part)
            if is_valid_port(local_port) and is_valid_port(remote_port):
                return local_port, remote_port
        except ValueError:
            pass # Invalid integer
    return None

def is_valid_profile_name(name: str) -> bool:
    """Checks if a profile name is valid (non-empty, no leading/trailing whitespace)."""
    return bool(name) and name.strip() == name

def is_privileged_port(port: int) -> bool:
    """Checks if a port is a privileged port (< 1024) that requires root/sudo access."""
    return 1 <= port < 1024

def has_sudo_privileges() -> bool:
    """Checks if the current user has sudo privileges."""
    try:
        # Check if running as root
        if os.getuid() == 0:
            return True
        
        # Check if user can run sudo without password prompt
        # Use sudo -n (non-interactive) to test
        result = subprocess.run(
            ['sudo', '-n', 'true'], 
            capture_output=True, 
            timeout=5
        )
        return result.returncode == 0
    except (OSError, subprocess.TimeoutExpired, AttributeError):
        # AttributeError for Windows (no os.getuid), OSError if sudo not found
        return False

def get_privileged_port_warning(port: int) -> Optional[str]:
    """Returns a warning message if the port requires privileges the user doesn't have."""
    if not is_privileged_port(port):
        return None
    
    if has_sudo_privileges():
        return None
    
    return (f"Port {port} is a privileged port (< 1024) that typically requires "
            f"root/sudo access to bind to. You may need to run the application "
            f"with sudo or use a port >= 1024.")

def generate_ssh_command(profile: Dict[str, Any]) -> Optional[str]:
    """Generates the SSH command string based on the profile data."""
    server = profile.get("server")
    port = profile.get("port", 22)
    key_path_str = profile.get("key_path", "")
    auth_method = profile.get("auth_method", "key")  # Default to key for backward compatibility
    password = profile.get("password", "")
    port_mappings = profile.get("port_mappings", [])

    if not server:
        print("Error: Server address is required.")
        return None

    if not is_valid_port(port):
        print(f"Error: Invalid SSH port {port}.")
        return None

    # For password authentication, check if sshpass is available and password is provided
    if auth_method == "password":
        if not password:
            print("Error: Password is required for password authentication.")
            return None
        # Note: sshpass must be installed on the system for password authentication to work
        cmd = ["sshpass", "-p", password, "ssh"]
    else:
        # Key-based authentication (default)
        cmd = ["ssh"]

    cmd.extend(["-p", str(port)])

    # Only add key path for key-based authentication
    if auth_method == "key" and key_path_str:
        # Expand tilde
        expanded_key_path = Path(key_path_str).expanduser()
        # No need to quote here; shlex.join will handle it.
        cmd.extend(["-i", str(expanded_key_path)])

    # For password authentication, disable strict host key checking to avoid interactive prompts
    if auth_method == "password":
        cmd.extend(["-o", "StrictHostKeyChecking=no"])
        cmd.extend(["-o", "UserKnownHostsFile=/dev/null"])

    valid_mappings = []
    for mapping_str in port_mappings:
        parsed = parse_port_mapping(mapping_str)
        if parsed:
            local_port, remote_port = parsed
            # Remote host is always localhost according to requirements
            cmd.extend(["-L", f"{local_port}:localhost:{remote_port}"])
            valid_mappings.append(mapping_str)
        else:
            print(f"Warning: Skipping invalid port mapping '{mapping_str}'")

    if not valid_mappings:
        print("Warning: No valid port mappings provided.")
        # Decide if command should still be generated without mappings
        # For now, let's allow it, but it might not be useful.

    # Add required flags
    cmd.extend(["-N", "-T"])

    # Add recommended options for stability
    cmd.extend(["-o", "ExitOnForwardFailure=yes"])
    cmd.extend(["-o", "ConnectTimeout=10"])
    # You might want to add ServerAliveInterval/CountMax for keepalive
    # cmd.extend(["-o", "ServerAliveInterval=60"])
    # cmd.extend(["-o", "ServerAliveCountMax=3"])

    cmd.append(server)

    return shlex.join(cmd)


# Example usage (can be removed later)
if __name__ == '__main__':
    test_profile_1 = {
        "server": "user@example.com",
        "port": 2222,
        "key_path": "~/.ssh/id_rsa test",
        "port_mappings": ["8080:80", "9000:9001", "invalid", "3000:abc"]
    }
    test_profile_2 = {
        "server": "another@server",
        # Missing port, should default
        "key_path": "/path/without/spaces",
        "port_mappings": ["5432:5432"]
    }
    test_profile_3 = {
        "server": "", # Invalid profile
        "port": 22,
        "key_path": "",
        "port_mappings": []
    }

    cmd1 = generate_ssh_command(test_profile_1)
    print(f"Profile 1 Command:\n{cmd1}\n")

    cmd2 = generate_ssh_command(test_profile_2)
    print(f"Profile 2 Command:\n{cmd2}\n")

    cmd3 = generate_ssh_command(test_profile_3)
    print(f"Profile 3 Command:\n{cmd3}\n")

    print(f"Is port 80 valid? {is_valid_port(80)}")
    print(f"Is port 0 valid? {is_valid_port(0)}")
    print(f"Is port 70000 valid? {is_valid_port(70000)}")

    print(f"Parse '8080:80': {parse_port_mapping('8080:80')}")
    print(f"Parse 'abc:80': {parse_port_mapping('abc:80')}")
    print(f"Parse '8080:': {parse_port_mapping('8080:')}")

    print(f"Is 'My Profile' valid name? {is_valid_profile_name('My Profile')}")
    print(f"Is ' My Profile ' valid name? {is_valid_profile_name(' My Profile ')}")
    print(f"Is '' valid name? {is_valid_profile_name('')}") 