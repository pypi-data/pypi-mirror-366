# GUI implementation using PyQt6 will go here
import sys
import os
from typing import Optional, Dict, Any
import importlib.resources # Added for icon loading

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QFileDialog, QComboBox,
    QTableWidget, QTableWidgetItem, QAbstractItemView, QHeaderView,
    QMessageBox, QSpinBox, QFormLayout, QGroupBox, QInputDialog, QSizePolicy,
    QRadioButton, QButtonGroup
)
from PyQt6.QtCore import Qt, QProcess, QProcessEnvironment, QTimer
from PyQt6.QtGui import QIcon, QCloseEvent

from . import config
from . import utils
from . import startup_shortcut

# Find the directory of the script to locate the icon
# This might need adjustment based on how the app is packaged
# SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# ICON_PATH = os.path.join(SCRIPT_DIR, 'icon.png') # Assuming icon.png is in the same dir
ICON_PATH = None
try:
    with importlib.resources.path("ssh_tunnel_manager", "icon.ico") as icon_path_obj:
        ICON_PATH = str(icon_path_obj)
except FileNotFoundError:
    print("Warning: icon.ico not found in package.")
    # You could try to load a default icon or skip setting it
    # For now, ICON_PATH will remain None if not found

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.config_data: Dict[str, Any] = config.load_config()
        self.current_profile_name: str = self.config_data.get("last_profile", "Default")
        self.active_process: Optional[QProcess] = None
        self.is_tunnel_running = False # Add state variable

        self.setWindowTitle("SSH Tunnel Manager")
        self.setGeometry(100, 100, 700, 550) # Adjusted initial size

        # Set window icon (optional, requires icon.png)
        if ICON_PATH and os.path.exists(ICON_PATH):
            self.setWindowIcon(QIcon(ICON_PATH))
        else:
            print("GUI: Icon not loaded or path does not exist.")

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)

        # --- Create UI Elements ---
        self._create_profile_section()
        self._create_connection_section()
        self._create_port_mapping_section()
        self._create_control_section()
        self._create_status_section()

        # --- Load Initial Profile ---
        self.load_profile(self.current_profile_name)

        # --- Connect Signals --- # Placeholder connections
        self.profile_combo.currentTextChanged.connect(self._profile_changed)
        self.save_as_button.clicked.connect(self._save_profile_as)
        self.delete_profile_button.clicked.connect(self._delete_profile)
        self.browse_button.clicked.connect(self._browse_key_file)
        self.add_mapping_button.clicked.connect(self._add_port_mapping)
        self.remove_mapping_button.clicked.connect(self._remove_port_mapping)
        self.port_mappings_table.itemChanged.connect(self._port_mapping_edited)

        # Connect changes in main fields to auto-save
        self.server_input.textChanged.connect(self._schedule_save_current_profile)
        self.port_input.valueChanged.connect(self._schedule_save_current_profile)
        self.key_path_input.textChanged.connect(self._schedule_save_current_profile)
        self.password_input.textChanged.connect(self._schedule_save_current_profile)
        
        # Connect authentication method change to update UI
        self.auth_key_radio.toggled.connect(self._auth_method_changed)
        self.auth_password_radio.toggled.connect(self._auth_method_changed)

        # Connect tunnel control signals
        self.start_button.clicked.connect(self._start_tunnel)
        self.stop_button.clicked.connect(self._stop_tunnel)
        self.copy_cmd_button.clicked.connect(self._copy_command)

        # --- Apply Initial State ---
        self._update_ui_state()
        self._auth_method_changed()  # Set initial field visibility
        QTimer.singleShot(0, self._adjust_window_height)
        
        # Check if we should ask about creating a shortcut
        QTimer.singleShot(100, lambda: startup_shortcut.check_and_ask_shortcut(self))

    def _create_profile_section(self):
        profile_group = QGroupBox("Profile Management")
        profile_layout = QHBoxLayout()

        self.profile_combo = QComboBox()
        self.profile_combo.setToolTip("Select an existing profile to load or modify.")
        self._populate_profile_combo()

        self.save_as_button = QPushButton("Save As...")
        self.save_as_button.setToolTip("Save the current settings as a new profile.")

        self.delete_profile_button = QPushButton("Delete")
        self.delete_profile_button.setToolTip("Delete the currently selected profile.")

        profile_layout.addWidget(QLabel("Profile:"))
        profile_layout.addWidget(self.profile_combo, 1)
        profile_layout.addWidget(self.save_as_button)
        profile_layout.addWidget(self.delete_profile_button)
        profile_group.setLayout(profile_layout)
        self.main_layout.addWidget(profile_group)

    def _create_connection_section(self):
        connection_group = QGroupBox("Connection Details")
        connection_layout = QFormLayout()
        connection_layout.setRowWrapPolicy(QFormLayout.RowWrapPolicy.WrapLongRows)

        server_layout = QHBoxLayout()
        server_label = QLabel("Server:")
        server_label.setFixedWidth(100)  # Same width as other labels for consistency
        self.server_input = QLineEdit()
        self.server_input.setPlaceholderText("user@hostname")
        self.server_input.setToolTip("SSH server address (e.g., user@example.com)")
        server_layout.addWidget(server_label)
        server_layout.addWidget(self.server_input, 1)
        
        server_widget = QWidget()
        server_widget.setLayout(server_layout)
        connection_layout.addRow(server_widget)

        ssh_port_layout = QHBoxLayout()
        port_label = QLabel("SSH Port:")
        port_label.setFixedWidth(100)  # Same width as other labels for consistency
        self.port_input = QSpinBox()
        self.port_input.setRange(1, 65535)
        self.port_input.setValue(22)
        self.port_input.setToolTip("SSH server port (1-65535)")
        ssh_port_layout.addWidget(port_label)
        ssh_port_layout.addWidget(self.port_input)
        ssh_port_layout.addStretch()
        
        port_widget = QWidget()
        port_widget.setLayout(ssh_port_layout)
        connection_layout.addRow(port_widget)

        # Authentication method selection
        auth_layout = QHBoxLayout()
        auth_label = QLabel("Authentication:")
        auth_label.setFixedWidth(100)  # Same width as other labels for consistency
        self.auth_button_group = QButtonGroup()
        self.auth_key_radio = QRadioButton("SSH Key")
        self.auth_password_radio = QRadioButton("Password")
        self.auth_key_radio.setChecked(True)  # Default to SSH key
        self.auth_key_radio.setToolTip("Use SSH key file for authentication")
        self.auth_password_radio.setToolTip("Use password for authentication")
        
        self.auth_button_group.addButton(self.auth_key_radio)
        self.auth_button_group.addButton(self.auth_password_radio)
        
        auth_layout.addWidget(auth_label)
        auth_layout.addWidget(self.auth_key_radio)
        auth_layout.addWidget(self.auth_password_radio)
        auth_layout.addStretch()
        
        auth_widget = QWidget()
        auth_widget.setLayout(auth_layout)
        connection_layout.addRow(auth_widget)

        # SSH Key File row - create a horizontal layout with label and controls
        ssh_key_row_layout = QHBoxLayout()
        self.ssh_key_label = QLabel("SSH Key File:")
        self.ssh_key_label.setFixedWidth(100)  # Fixed width for consistent alignment
        
        self.key_path_input = QLineEdit()
        self.key_path_input.setPlaceholderText("/path/to/your/private_key")
        self.key_path_input.setToolTip("Path to your SSH private key file (e.g., ~/.ssh/id_rsa)")
        self.browse_button = QPushButton("Browse...")
        self.browse_button.setToolTip("Browse for your SSH private key file.")
        
        ssh_key_row_layout.addWidget(self.ssh_key_label)
        ssh_key_row_layout.addWidget(self.key_path_input, 1)
        ssh_key_row_layout.addWidget(self.browse_button)
        
        self.ssh_key_widget = QWidget()
        self.ssh_key_widget.setLayout(ssh_key_row_layout)
        
        # Add the SSH key row to the main layout
        connection_layout.addRow(self.ssh_key_widget)

        # Password row - create a horizontal layout with label and controls
        password_row_layout = QHBoxLayout()
        self.password_label = QLabel("Password:")
        self.password_label.setFixedWidth(100)  # Same width as SSH key label
        
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText("Enter SSH password")
        self.password_input.setToolTip("SSH password for authentication")
        
        # Add an invisible spacer to maintain consistent spacing with the SSH key row
        password_spacer = QWidget()
        password_spacer.setFixedWidth(self.browse_button.sizeHint().width())
        
        password_row_layout.addWidget(self.password_label)
        password_row_layout.addWidget(self.password_input, 1)
        password_row_layout.addWidget(password_spacer)
        
        self.password_widget = QWidget()
        self.password_widget.setLayout(password_row_layout)
        
        # Add the password row to the main layout
        connection_layout.addRow(self.password_widget)

        connection_group.setLayout(connection_layout)
        self.main_layout.addWidget(connection_group)

    def _create_port_mapping_section(self):
        mapping_group = QGroupBox("Port Forwarding (Local -> Remote via SSH Server)")
        mapping_layout = QVBoxLayout()

        self.port_mappings_table = QTableWidget()
        self.port_mappings_table.setColumnCount(2)
        self.port_mappings_table.setHorizontalHeaderLabels(["Local Port", "Remote Port (on localhost of server)"])
        self.port_mappings_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.port_mappings_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.port_mappings_table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.port_mappings_table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.port_mappings_table.setToolTip("Define local ports to forward to remote ports on the server's localhost.")
        mapping_layout.addWidget(self.port_mappings_table)

        mapping_buttons_layout = QHBoxLayout()
        self.add_mapping_button = QPushButton("Add Mapping")
        self.add_mapping_button.setToolTip("Add a new port forwarding rule.")
        self.remove_mapping_button = QPushButton("Remove Selected")
        self.remove_mapping_button.setToolTip("Remove the selected port forwarding rule.")
        mapping_buttons_layout.addStretch()
        mapping_buttons_layout.addWidget(self.add_mapping_button)
        mapping_buttons_layout.addWidget(self.remove_mapping_button)
        mapping_layout.addLayout(mapping_buttons_layout)

        mapping_group.setLayout(mapping_layout)
        self.main_layout.addWidget(mapping_group)

    def _create_control_section(self):
        control_group = QGroupBox("Tunnel Control")
        control_layout = QHBoxLayout()

        self.start_button = QPushButton("Start Tunnel")
        # Set background and text color for better contrast
        self.start_button.setStyleSheet("background-color: lightgreen; color: black;")
        self.start_button.setToolTip("Start the SSH tunnel with the current configuration.")

        self.stop_button = QPushButton("Stop Tunnel")
        # Set background and text color for better contrast
        self.stop_button.setStyleSheet("background-color: lightcoral; color: black;")
        self.stop_button.setToolTip("Stop the currently running SSH tunnel.")

        self.copy_cmd_button = QPushButton("Copy SSH Command")
        self.copy_cmd_button.setToolTip("Copy the generated SSH command to the clipboard.")

        control_layout.addWidget(self.start_button)
        control_layout.addWidget(self.stop_button)
        control_layout.addStretch()
        control_layout.addWidget(self.copy_cmd_button)
        control_group.setLayout(control_layout)
        self.main_layout.addWidget(control_group)

    def _create_status_section(self):
        status_group = QGroupBox("Status")
        status_layout = QHBoxLayout()
        self.status_label = QLabel("Status: Idle")
        self.status_label.setToolTip("Current status of the SSH tunnel.")
        status_layout.addWidget(self.status_label)
        status_group.setLayout(status_layout)
        self.main_layout.addWidget(status_group)

    def _populate_profile_combo(self):
        self.profile_combo.clear()
        profiles = sorted(self.config_data.get("profiles", {}).keys())
        self.profile_combo.addItems(profiles)
        if self.current_profile_name in profiles:
            self.profile_combo.setCurrentText(self.current_profile_name)
        elif profiles: # If last profile was deleted, select the first available
            self.current_profile_name = profiles[0]
            self.profile_combo.setCurrentIndex(0)

    def load_profile(self, profile_name: str):
        profile_data = self.config_data.get("profiles", {}).get(profile_name)
        if not profile_data:
            print(f"Error: Profile '{profile_name}' not found. Loading defaults.")
            # Maybe load default or handle error differently?
            profile_data = config.DEFAULT_PROFILE
            profile_name = "Default" # Or handle appropriately
            # You might want to ensure a Default profile always exists
            if "Default" not in self.config_data.get("profiles", {}):
                self.config_data.setdefault("profiles", {})["Default"] = config.DEFAULT_PROFILE.copy()
                # Save immediately if Default profile had to be recreated
                config.save_config(self.config_data)
                self._populate_profile_combo()

        self.current_profile_name = profile_name
        self.config_data["last_profile"] = profile_name # Update last used profile
        # Save the config whenever a profile is successfully loaded/selected
        # This ensures 'last_profile' is persisted
        # Consider if this should only happen on explicit save/app close
        config.save_config(self.config_data)

        if self.profile_combo.currentText() != profile_name:
             self.profile_combo.setCurrentText(profile_name)

        print(f"Loading profile: {profile_name}")

        # --- Update UI elements --- (Disable signals temporarily if needed)
        # self.profile_combo.blockSignals(True)
        self.server_input.setText(profile_data.get("server", ""))
        self.port_input.setValue(profile_data.get("port", 22))
        self.key_path_input.setText(profile_data.get("key_path", ""))
        
        # Handle authentication method - default to "key" for backward compatibility
        auth_method = profile_data.get("auth_method", "key")
        if auth_method == "password":
            self.auth_password_radio.setChecked(True)
            self.password_input.setText(profile_data.get("password", ""))
        else:
            self.auth_key_radio.setChecked(True)
            # Don't clear password field - preserve any user input from current session
        
        # Update field enabled states based on auth method
        self._auth_method_changed()

        self.port_mappings_table.setRowCount(0) # Clear table
        mappings = profile_data.get("port_mappings", [])
        self.port_mappings_table.setRowCount(len(mappings))
        for row, mapping_str in enumerate(mappings):
            parts = utils.parse_port_mapping(mapping_str)
            if parts:
                local_port, remote_port = parts
                self.port_mappings_table.setItem(row, 0, QTableWidgetItem(str(local_port)))
                self.port_mappings_table.setItem(row, 1, QTableWidgetItem(str(remote_port)))
            else:
                # Handle potential invalid data saved in config?
                 print(f"Warning: Invalid mapping '{mapping_str}' found in profile '{profile_name}'")
                 # Optionally add placeholder or skip row
                 # For now, just create empty cells
                 self.port_mappings_table.setItem(row, 0, QTableWidgetItem("INVALID"))
                 self.port_mappings_table.setItem(row, 1, QTableWidgetItem("INVALID"))
        # self.profile_combo.blockSignals(False)

        self._update_ui_state() # Update button states etc.
        self._adjust_window_height()

    def _update_ui_state(self):
        """Enable/disable UI elements based on tunnel state."""
        is_running = self.is_tunnel_running

        # Define styles for button states
        # Use darker, more saturated colors for enabled state
        start_enabled_style = "background-color: #2E8B57; color: white;"  # SeaGreen
        stop_enabled_style = "background-color: #B22222; color: white;"   # FireBrick

        # For disabled state, remove background and set text to gray
        disabled_style = "color: gray;" # No background-color specified

        # Set button enabled state and style
        self.start_button.setEnabled(not is_running)
        self.start_button.setStyleSheet(start_enabled_style if not is_running else disabled_style)

        self.stop_button.setEnabled(is_running)
        self.stop_button.setStyleSheet(stop_enabled_style if is_running else disabled_style)

        # Disable editing when running
        self.profile_combo.setEnabled(not is_running)
        self.save_as_button.setEnabled(not is_running)
        # Disable delete if only one profile exists or tunnel is running
        can_delete = len(self.config_data.get("profiles", {})) > 1
        self.delete_profile_button.setEnabled(not is_running and can_delete)
        self.server_input.setEnabled(not is_running)
        self.port_input.setEnabled(not is_running)
        
        # Authentication controls
        self.auth_key_radio.setEnabled(not is_running)
        self.auth_password_radio.setEnabled(not is_running)
        # Key/password fields are only enabled based on tunnel state (visibility is handled by _auth_method_changed)
        self.key_path_input.setEnabled(not is_running)
        self.browse_button.setEnabled(not is_running)
        self.password_input.setEnabled(not is_running)
        
        self.port_mappings_table.setEnabled(not is_running)
        self.add_mapping_button.setEnabled(not is_running)
        self.remove_mapping_button.setEnabled(not is_running)

        # Update status label
        if is_running and self.active_process:
            pid = self.active_process.processId()
            self.status_label.setText(f"Status: Running (PID: {pid})")
            self.status_label.setStyleSheet("color: green")
        elif is_running:
             self.status_label.setText(f"Status: Starting...")
             self.status_label.setStyleSheet("color: orange")
        else:
            # Determine the default text color based on the application palette
            # This tries to respect the theme better than hardcoding 'white'
            text_color = self.palette().text().color().name()
            self.status_label.setText("Status: Idle")
            self.status_label.setStyleSheet(f"color: {text_color}") # Use theme text color

    def _auth_method_changed(self):
        """Handles changes in authentication method selection."""
        is_key_auth = self.auth_key_radio.isChecked()
        
        # Show/hide the entire row widgets based on authentication method
        # Each widget contains both the label and input controls in a horizontal layout
        self.ssh_key_widget.setVisible(is_key_auth)
        self.password_widget.setVisible(not is_key_auth)
        
        # Don't clear the fields - preserve user input so they can switch back
        # This way users don't lose their SSH key path or password when experimenting
        
        # Trigger auto-save
        self._schedule_save_current_profile()

    def _profile_changed(self, profile_name):
        """Handles selection changes in the profile dropdown."""
        if profile_name and profile_name != self.current_profile_name:
            print(f"Profile selection changed to: {profile_name}")
            # Check for unsaved changes before loading?
            # For now, directly load the selected profile
            self.load_profile(profile_name)

    def _get_current_profile_from_ui(self) -> Dict[str, Any]:
        """Reads the current values from the UI fields into a profile dict."""
        mappings = []
        for row in range(self.port_mappings_table.rowCount()):
            local_item = self.port_mappings_table.item(row, 0)
            remote_item = self.port_mappings_table.item(row, 1)
            if local_item and remote_item and local_item.text() and remote_item.text():
                # Basic validation - check if they look like ports
                try:
                    local_port = int(local_item.text())
                    remote_port = int(remote_item.text())
                    if utils.is_valid_port(local_port) and utils.is_valid_port(remote_port):
                        mappings.append(f"{local_port}:{remote_port}")
                    else:
                        print(f"Skipping invalid port data in table row {row+1}")
                except ValueError:
                     print(f"Skipping non-numeric port data in table row {row+1}")

        current_data = {
            "server": self.server_input.text().strip(),
            "port": self.port_input.value(),
            "key_path": self.key_path_input.text().strip(),
            "auth_method": "key" if self.auth_key_radio.isChecked() else "password",
            "password": self.password_input.text(),
            "port_mappings": mappings
        }
        return current_data

    def _save_profile_as(self):
        """Saves the current UI settings as a new named profile."""
        new_name, ok = QInputDialog.getText(self, "Save Profile As", "Enter new profile name:")

        if ok and new_name:
            new_name = new_name.strip()
            if not utils.is_valid_profile_name(new_name):
                QMessageBox.warning(self, "Invalid Name", "Profile name cannot be empty or contain leading/trailing spaces.")
                return

            if new_name in self.config_data.get("profiles", {}):
                reply = QMessageBox.question(self, "Overwrite Profile?",
                                             f"Profile '{new_name}' already exists. Overwrite it?",
                                             QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                             QMessageBox.StandardButton.No)
                if reply == QMessageBox.StandardButton.No:
                    return

            profile_data = self._get_current_profile_from_ui()
            self.config_data.setdefault("profiles", {})[new_name] = profile_data
            self.config_data["last_profile"] = new_name
            config.save_config(self.config_data)
            print(f"Saved profile: {new_name}")

            # Update combo box and set current
            current_text = self.profile_combo.currentText()
            self.profile_combo.blockSignals(True) # Avoid triggering _profile_changed during update
            self._populate_profile_combo() # Reload combo box items
            self.profile_combo.setCurrentText(new_name) # Set the new profile as selected
            self.profile_combo.blockSignals(False)

            self.current_profile_name = new_name # Update internal state
            self._update_ui_state() # Update button states (like delete button enable state)
        elif ok and not new_name:
             QMessageBox.warning(self, "Invalid Name", "Profile name cannot be empty.")

    def _delete_profile(self):
        """Deletes the currently selected profile."""
        profile_to_delete = self.current_profile_name
        profiles = self.config_data.get("profiles", {})

        if profile_to_delete not in profiles:
            QMessageBox.warning(self, "Error", f"Profile '{profile_to_delete}' not found?")
            return

        if len(profiles) <= 1:
            QMessageBox.warning(self, "Cannot Delete", "Cannot delete the last profile.")
            return

        reply = QMessageBox.question(self, "Confirm Delete",
                                     f"Are you sure you want to delete the profile '{profile_to_delete}'?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                     QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            del profiles[profile_to_delete]
            print(f"Deleted profile: {profile_to_delete}")

            # Select the next available profile
            remaining_profiles = sorted(profiles.keys())
            new_selection = remaining_profiles[0] if remaining_profiles else None

            self.config_data["last_profile"] = new_selection
            config.save_config(self.config_data)

            # Update UI
            self._populate_profile_combo()
            if new_selection:
                self.load_profile(new_selection)
            else:
                # This case shouldn't happen due to the len(profiles) <= 1 check, but handle defensively
                print("Error: No profiles left after delete?")
                # Maybe create a new default?

            self._update_ui_state()

    def _browse_key_file(self):
        """Opens a file dialog to select an SSH key file."""
        # Start in user's home directory or ~/.ssh if possible
        start_dir = os.path.expanduser("~/.ssh")
        if not os.path.isdir(start_dir):
            start_dir = os.path.expanduser("~")

        file_name, _ = QFileDialog.getOpenFileName(
            self, "Select SSH Key File", start_dir, "All Files (*);;Private Key Files (*.key *.pem id_*)"
        )
        if file_name:
            self.key_path_input.setText(file_name)
            # Auto-save triggered by textChanged signal

    def _add_port_mapping(self):
        """Adds a new empty row to the port mapping table."""
        current_row_count = self.port_mappings_table.rowCount()
        self.port_mappings_table.insertRow(current_row_count)

        # Immediately add empty items with the default background to avoid white cells
        default_bg_color = self.port_mappings_table.palette().base().color()

        item1 = QTableWidgetItem("")
        item1.setBackground(default_bg_color)
        self.port_mappings_table.setItem(current_row_count, 0, item1)

        item2 = QTableWidgetItem("")
        item2.setBackground(default_bg_color)
        self.port_mappings_table.setItem(current_row_count, 1, item2)

        # Auto-save will be triggered by _port_mapping_edited when user adds data
        self._adjust_window_height()

    def _remove_port_mapping(self):
        """Removes the selected row(s) from the port mapping table."""
        selected_rows = sorted([item.row() for item in self.port_mappings_table.selectedIndexes()], reverse=True)
        if not selected_rows:
            QMessageBox.information(self, "Remove Mapping", "Please select a row to remove.")
            return

        # Remove duplicate row indices if multiple columns were selected in the same row
        unique_rows = list(dict.fromkeys(selected_rows))

        self.port_mappings_table.blockSignals(True) # Prevent itemChanged during removal
        for row in unique_rows:
            self.port_mappings_table.removeRow(row)
        self.port_mappings_table.blockSignals(False)

        self._save_current_profile() # Save after removal
        self._adjust_window_height()

    def _port_mapping_edited(self, item: QTableWidgetItem):
        """Validates input in the port mapping table and triggers auto-save."""
        if self.is_tunnel_running or self.port_mappings_table.signalsBlocked():
            return

        text = item.text().strip()
        row = item.row()
        col = item.column()

        print(f"Port mapping edited: Row {row}, Col {col}, Text: {text}")

        # Basic validation: Check if it's an integer
        is_valid = False
        port_num = None
        if text:
            try:
                port_num = int(text)
                if utils.is_valid_port(port_num):
                    is_valid = True
                else:
                    print(f"Port number {port_num} is out of range (1-65535).")
            except ValueError:
                print(f"Invalid integer value: {text}")
        # Allow empty cells for now, they will be ignored during save/command generation
        else:
             is_valid = True # Allow empty

        if not is_valid:
            # Indicate error visually (e.g., change background color)
            item.setBackground(Qt.GlobalColor.red)
            # Optionally revert or clear the cell
            # item.setText("") # Or revert to previous value if stored
        else:
            # Clear error indication
            # Reset to the table's base color to respect theme
            base_color = self.port_mappings_table.palette().base().color()
            item.setBackground(base_color)
            
            # Check for privileged port warning (only for local ports - column 0)
            if port_num is not None and col == 0:  # Local port column
                warning = utils.get_privileged_port_warning(port_num)
                if warning:
                    QMessageBox.warning(self, "Privileged Port Warning", warning)
            
            # Trigger save only if the content is valid or empty
            self._save_current_profile()
            self._adjust_window_height()

    def _save_current_profile(self):
        """Saves the current UI state to the selected profile in config_data."""
        if self.is_tunnel_running: # Don't save if tunnel is active
            return

        if not self.current_profile_name:
            print("Warning: No current profile selected, cannot save.")
            return

        print(f"Auto-saving changes to profile: {self.current_profile_name}")
        profile_data = self._get_current_profile_from_ui()
        self.config_data.setdefault("profiles", {})[self.current_profile_name] = profile_data
        # Also ensure last_profile is set correctly (might be redundant here)
        self.config_data["last_profile"] = self.current_profile_name
        config.save_config(self.config_data)

    def _schedule_save_current_profile(self):
        """Placeholder for potentially debouncing saves if needed."""
        # For now, save immediately. Could add a QTimer here later.
        self._save_current_profile()

    def _start_tunnel(self):
        """Starts the SSH tunnel process."""
        if self.active_process:
            QMessageBox.warning(self, "Already Running", "Tunnel process seems to be active already.")
            return

        profile_data = self._get_current_profile_from_ui()
        # Re-validate essential fields before starting
        if not profile_data.get("server"):
            QMessageBox.critical(self, "Error", "Server address is required to start the tunnel.")
            return
        if not utils.is_valid_port(profile_data.get("port", -1)): # Use -1 for invalid default
            QMessageBox.critical(self, "Error", f"Invalid SSH port: {profile_data.get('port')}")
            return
        
        # Check for privileged ports in port mappings
        privileged_ports = []
        for mapping_str in profile_data.get("port_mappings", []):
            parsed = utils.parse_port_mapping(mapping_str)
            if parsed:
                local_port, remote_port = parsed
                warning = utils.get_privileged_port_warning(local_port)
                if warning:
                    privileged_ports.append(local_port)
        
        # Warn about privileged ports before starting
        if privileged_ports:
            ports_str = ", ".join(map(str, privileged_ports))
            reply = QMessageBox.question(
                self, 
                "Privileged Ports Detected",
                f"The following local ports require elevated privileges: {ports_str}\n\n"
                f"Ports below 1024 typically require root/sudo access to bind to. "
                f"The tunnel may fail to start unless you run this application with sudo.\n\n"
                f"Do you want to continue anyway?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.No:
                return
        
        # Consider validating key path existence if provided?
        ssh_command_str = utils.generate_ssh_command(profile_data)
        if not ssh_command_str:
            QMessageBox.critical(self, "Error", "Failed to generate SSH command. Check console for details.")
            return

        print(f"Starting tunnel with command:\n{ssh_command_str}")
        self.active_process = QProcess(self)
        self.active_process.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels) # Combine stdout/stderr

        # Connect signals for process management
        self.active_process.started.connect(self._handle_process_started)
        self.active_process.finished.connect(self._handle_process_finished) # Catches normal exit and crashes
        self.active_process.errorOccurred.connect(self._handle_process_error)
        self.active_process.readyReadStandardOutput.connect(self._handle_stdout)
        # self.active_process.readyReadStandardError.connect(self._handle_stderr) # Merged now

        # Environment setup (important for finding ssh, keys, etc.)
        env = QProcessEnvironment.systemEnvironment()
        # Add SSH_ASKPASS=never or similar if you want to prevent password prompts
        # env.insert("SSH_ASKPASS", "/path/to/dummy_script") # Requires a script
        # env.insert("DISPLAY", ":0") # May be needed depending on ssh setup
        self.active_process.setProcessEnvironment(env)

        # Parse the command string back into program and arguments for QProcess
        # NOTE: This relies on shlex correctly handling the quoting from generate_ssh_command
        try:
            cmd_parts = utils.shlex.split(ssh_command_str)
            program = cmd_parts[0] # Should be 'ssh'
            arguments = cmd_parts[1:]
            self.active_process.start(program, arguments)
            # Update state immediately to 'Starting...'
            self.is_tunnel_running = True
            self._update_ui_state()
            self.status_label.setText("Status: Starting...")
            self.status_label.setStyleSheet("color: orange")
        except Exception as e:
            QMessageBox.critical(self, "Start Error", f"Failed to parse or start the SSH command: {e}")
            self.active_process = None # Clean up failed process object
            self.is_tunnel_running = False
            self._update_ui_state()

    def _stop_tunnel(self):
        """Stops the running SSH tunnel process."""
        if self.active_process and self.active_process.state() != QProcess.ProcessState.NotRunning:
            print("Stopping tunnel process...")
            # Try terminating gracefully first
            self.active_process.terminate()
            # Add a timeout and potentially kill if terminate doesn't work?
            # if not self.active_process.waitForFinished(3000): # Wait 3 seconds
            #     print("Process did not terminate gracefully, killing...")
            #     self.active_process.kill()
        else:
            print("Stop command ignored: No active process found.")
            # Ensure UI state is consistent if stop is clicked erroneously
            if self.is_tunnel_running:
                self.is_tunnel_running = False
                self.active_process = None
                self._update_ui_state()

    def _copy_command(self):
        """Generates the SSH command and copies it to the clipboard."""
        profile_data = self._get_current_profile_from_ui()
        ssh_command_str = utils.generate_ssh_command(profile_data)

        if ssh_command_str:
            clipboard = QApplication.clipboard()
            clipboard.setText(ssh_command_str)
            print("SSH command copied to clipboard.")
            # Optionally show a brief confirmation message
            self.statusBar().showMessage("SSH command copied!", 2000) # Requires self.setStatusBar(QStatusBar())
        else:
            QMessageBox.warning(self, "Cannot Copy Command", "Could not generate SSH command (check inputs or console output).")

    def _handle_process_started(self):
        pid = self.active_process.processId()
        print(f"Tunnel process started successfully (PID: {pid}).")
        self.is_tunnel_running = True # Ensure state is true
        self._update_ui_state() # Update UI (status label, buttons)

    def _handle_process_finished(self, exit_code, exit_status: QProcess.ExitStatus):
        status_text = "normally" if exit_status == QProcess.ExitStatus.NormalExit else "with errors/crash"
        print(f"Tunnel process finished {status_text}. Exit code: {exit_code}")
        # Store error message if it occurred before finished signal
        error_message = ""
        if hasattr(self, '_last_process_error_str') and self._last_process_error_str:
            error_message = self._last_process_error_str
            self._last_process_error_str = None # Clear it

        self.active_process = None
        self.is_tunnel_running = False
        self._update_ui_state()

        if exit_status != QProcess.ExitStatus.NormalExit or exit_code != 0:
            self.status_label.setText(f"Status: Stopped (Error code: {exit_code})")
            self.status_label.setStyleSheet("color: red")
            details = f"The SSH tunnel process exited unexpectedly.\nExit Code: {exit_code}\nStatus: {exit_status.name}"
            if error_message:
                details += f"\nError Details: {error_message}"
            QMessageBox.warning(self, "Tunnel Stopped Unexpectedly", details)
        else:
            self.status_label.setText("Status: Stopped")
            text_color = self.palette().text().color().name() # Get theme text color
            self.status_label.setStyleSheet(f"color: {text_color}")

    def _handle_process_error(self, error: QProcess.ProcessError):
        error_str = self.active_process.errorString() if self.active_process else "Unknown QProcess error"
        print(f"Tunnel process error: {error.name} - {error_str}")
        # Store the error string to potentially show it in the finished handler
        self._last_process_error_str = error_str
        # UI state update will happen in _handle_process_finished

    def _handle_stdout(self):
        if not self.active_process:
            return
        data = self.active_process.readAllStandardOutput()
        try:
            text = bytes(data).decode('utf-8', errors='ignore')
            print(f"SSH_OUT: {text.strip()}", end='') # Print directly
        except Exception as e:
            print(f"Error decoding process output: {e}")

    def closeEvent(self, event: QCloseEvent):
        """Handle the window closing event."""
        print("Close event triggered")
        # Attempt to stop tunnel if running
        if self.active_process and self.active_process.state() != QProcess.ProcessState.NotRunning:
            reply = QMessageBox.question(
                self,
                "Tunnel Running",
                "The SSH tunnel is currently running. Stop it before exiting?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel,
                QMessageBox.StandardButton.Yes
            )
            if reply == QMessageBox.StandardButton.Yes:
                self._stop_tunnel()
                # Optionally wait briefly for it to stop?
                if self.active_process:
                    self.active_process.waitForFinished(1000) # Wait max 1 sec
                event.accept() # Proceed with closing
            elif reply == QMessageBox.StandardButton.No:
                event.accept() # Proceed with closing, leave tunnel running
            else: # Cancel
                event.ignore() # Prevent closing
            return
        else:
            event.accept() # No tunnel running, close normally

        # Save current state? (e.g., last profile is already saved on load/change)
        super().closeEvent(event)

    def _adjust_window_height(self):
        """Adjust window height to fit table content, up to a max screen percentage."""
        if not self.port_mappings_table.isVisible(): # Don't adjust if called too early
            return # Correct indentation

        try:
            # Calculate ideal height for table content
            header_h = self.port_mappings_table.horizontalHeader().height()
            rows_h = sum(self.port_mappings_table.rowHeight(r) for r in range(self.port_mappings_table.rowCount()))
            buffer = 20 # Small buffer for margins/borders
            ideal_table_height = header_h + rows_h + buffer

            # Set a minimum height for the table (header + 1 row or just header)
            min_row_height = self.port_mappings_table.verticalHeader().defaultSectionSize()
            min_table_height = header_h + min_row_height + buffer
            self.port_mappings_table.setMinimumHeight(min_table_height)

            # Get the layout's preferred height hint
            # Need to use the central widget's layout, not the main window's
            if self.central_widget and self.central_widget.layout():
                preferred_height = self.central_widget.layout().sizeHint().height()
            else:
                 preferred_height = self.height() # Fallback

            # Get the current width to preserve it
            current_width = self.width()

            # Apply the preferred height
            new_height = preferred_height

            # Clamp the height if it exceeds 75% of the screen
            screen_geom = self.screen().availableGeometry()
            max_window_height = int(screen_geom.height() * 0.75)

            if new_height > max_window_height:
                print(f"Window height ({new_height}) exceeds max ({max_window_height}), clamping.")
                new_height = max_window_height
                # If clamped, we likely need the scrollbar
                self.port_mappings_table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
            else:
                # If not clamped, we ideally don't need the scrollbar
                self.port_mappings_table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

            # Apply the final (potentially clamped) height, preserving width
            if self.height() != new_height: # Avoid unnecessary resize calls
                self.resize(current_width, new_height)

        except Exception as e:
            # Avoid crashing the UI if height calculation fails for some reason
            print(f"Error calculating window height: {e}")

# Example Icon (replace with your actual icon.png or remove if not needed)
# You can create a simple 16x16 or 32x32 png file named icon.png
# in the same directory as gui.py

# Example main execution (for testing gui.py directly)
# Normally, this would be run from main.py
if __name__ == '__main__':
    app = QApplication(sys.argv)
    # Apply a style (optional, Fusion is often a good cross-platform choice)
    # app.setStyle('Fusion')
    window = MainWindow()
    window.show()
    sys.exit(app.exec()) 