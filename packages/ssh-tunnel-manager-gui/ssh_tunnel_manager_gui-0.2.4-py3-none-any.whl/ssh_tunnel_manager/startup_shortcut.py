import os
import sys
import platform
import subprocess
from pathlib import Path
from typing import Optional
from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtCore import Qt
from .config import get_config_path, load_config, save_config


def get_shortcut_preference() -> Optional[bool]:
    """Get the saved preference for creating shortcuts."""
    config = load_config()
    return config.get("shortcut_created")


def save_shortcut_preference(created: bool) -> None:
    """Save the preference for creating shortcuts."""
    config = load_config()
    config["shortcut_created"] = created
    save_config(config)


def create_windows_shortcut() -> bool:
    """Create a Windows Start Menu shortcut."""
    try:
        import win32com.client
        
        # Get the Start Menu path
        start_menu = Path(os.environ['APPDATA']) / "Microsoft" / "Windows" / "Start Menu" / "Programs"
        shortcut_path = start_menu / "SSH Tunnel Manager.lnk"
        
        # Get the executable path
        if getattr(sys, 'frozen', False):
            # Running as compiled executable
            target_path = sys.executable
        else:
            # Running as Python script
            target_path = sys.executable
            arguments = f'"{sys.argv[0]}"'
        
        # Create shortcut
        shell = win32com.client.Dispatch("WScript.Shell")
        shortcut = shell.CreateShortCut(str(shortcut_path))
        shortcut.TargetPath = target_path
        if not getattr(sys, 'frozen', False):
            shortcut.Arguments = arguments
        shortcut.WorkingDirectory = str(Path(target_path).parent)
        shortcut.IconLocation = target_path
        shortcut.Description = "SSH Tunnel Manager - Manage your SSH tunnels with ease"
        shortcut.save()
        
        return True
    except Exception as e:
        print(f"Error creating Windows shortcut: {e}")
        return False


def create_linux_desktop_entry() -> bool:
    """Create a Linux desktop entry for the application launcher."""
    try:
        # Get the desktop entry path
        desktop_dir = Path.home() / ".local" / "share" / "applications"
        desktop_dir.mkdir(parents=True, exist_ok=True)
        desktop_file = desktop_dir / "ssh-tunnel-manager.desktop"
        
        # Get the executable command
        if getattr(sys, 'frozen', False):
            # Running as compiled executable
            exec_command = sys.executable
        else:
            # Running as Python script - use the console script entry point
            exec_command = "ssh-tunnel-manager"
        
        # Get icon path
        icon_path = Path(__file__).parent / "icon.ico"
        if not icon_path.exists():
            icon_path = "ssh-tunnel-manager"  # Fallback to icon name
        
        # Create desktop entry content
        desktop_content = f"""[Desktop Entry]
Version=1.0
Type=Application
Name=SSH Tunnel Manager
Comment=Manage your SSH tunnels with ease
Exec={exec_command}
Icon={icon_path}
Terminal=false
Categories=Network;Utility;
StartupNotify=true
"""
        
        # Write desktop file
        desktop_file.write_text(desktop_content)
        
        # Make it executable
        desktop_file.chmod(0o755)
        
        # Update desktop database
        try:
            subprocess.run(["update-desktop-database", str(desktop_dir)], 
                         capture_output=True, check=False)
        except:
            pass  # Not critical if this fails
        
        return True
    except Exception as e:
        print(f"Error creating Linux desktop entry: {e}")
        return False


def create_shortcut() -> bool:
    """Create a shortcut based on the current platform."""
    system = platform.system()
    
    if system == "Windows":
        return create_windows_shortcut()
    elif system == "Linux":
        return create_linux_desktop_entry()
    else:
        print(f"Unsupported platform: {system}")
        return False


def check_and_ask_shortcut(parent=None) -> None:
    """Check if we should ask about creating a shortcut and handle the response."""
    # Check if we've already asked
    preference = get_shortcut_preference()
    if preference is not None:
        # Already asked, don't ask again
        return
    
    # Prepare the message based on platform
    system = platform.system()
    if system == "Windows":
        location = "Windows Start Menu"
    elif system == "Linux":
        location = "application launcher"
    else:
        # Unsupported platform, don't ask
        save_shortcut_preference(False)
        return
    
    # Create and show the message box
    msg_box = QMessageBox(parent)
    msg_box.setWindowTitle("Create Shortcut")
    msg_box.setText(f"Would you like to add SSH Tunnel Manager to your {location}?")
    msg_box.setInformativeText("This will make it easier to launch the application in the future.")
    msg_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
    msg_box.setDefaultButton(QMessageBox.StandardButton.Yes)
    msg_box.setIcon(QMessageBox.Icon.Question)
    
    # Show the dialog and get the response
    response = msg_box.exec()
    
    if response == QMessageBox.StandardButton.Yes:
        # Try to create the shortcut
        success = create_shortcut()
        save_shortcut_preference(success)
        
        if success:
            QMessageBox.information(
                parent,
                "Success",
                f"SSH Tunnel Manager has been added to your {location}!",
                QMessageBox.StandardButton.Ok
            )
        else:
            QMessageBox.warning(
                parent,
                "Error",
                "Failed to create the shortcut. You can try again later by running the application with administrator privileges.",
                QMessageBox.StandardButton.Ok
            )
    else:
        # User said no, save the preference
        save_shortcut_preference(False) 