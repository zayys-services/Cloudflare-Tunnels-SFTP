import customtkinter as ctk
import subprocess
import threading
import time
import os
from PIL import Image
from datetime import datetime
import json
import sys
from dataclasses import dataclass
from typing import Dict, Optional

@dataclass
class AppConfig:
    # App information
    APP_NAME: str = "Zayys Services"
    APP_VERSION: str = "v1.0.0"
    WINDOW_TITLE: str = "Zayys Services - Cloudflared Installer"
    WINDOW_SIZE: tuple = (1000, 700)
    WINDOW_MIN_SIZE: tuple = (900, 600)
    
    # Enterprise badge configuration
    SHOW_ENTERPRISE_BADGE: bool = True
    ENTERPRISE_BADGE_TEXT: str = "ENTERPRISE"
    
    # Theme and colors
    COLORS: Dict[str, str] = None
    
    # Server configuration
    SERVER_CONFIG: Dict[str, str] = None
    
    # Connection details configuration
    CONNECTION_DETAILS: Dict[str, str] = None
    
    # Cloudflared installation configuration
    CLOUDFLARED_PACKAGE: str = "Cloudflare.cloudflared"
    PACKAGE_MANAGER: str = "winget"
    
    # UI Configuration
    FONTS: Dict[str, tuple] = None
    
    # Log panel configuration
    LOG_PANEL_HEIGHT: int = 150
    SHOW_TIMESTAMPS_IN_LOGS: bool = True
    
    # Status update intervals (milliseconds)
    TIME_UPDATE_INTERVAL: int = 1000
    UPTIME_UPDATE_INTERVAL: int = 1000
    
    # Installation steps configuration
    INSTALLATION_STEPS: list = None

    def __post_init__(self):
        # Initialize colors if not set
        if self.COLORS is None:
            self.COLORS = {
                'bg_primary': "#0f172a",
                'bg_secondary': "#1e293b",
                'accent': "#3b82f6",
                'success': "#22c55e",
                'warning': "#f59e0b",
                'error': "#ef4444",
                'text': "#f8fafc"
            }
        
        # Initialize server config if not set
        if self.SERVER_CONFIG is None:
            self.SERVER_CONFIG = {
                'hostname': "ftp.zayy.pro",
                'local_url': "tcp://localhost:2022",
                'log_level': "trace"
            }
        
        # Initialize connection details if not set
        if self.CONNECTION_DETAILS is None:
            self.CONNECTION_DETAILS = {
                'Host': "sftp://localhost:2022",
                'Username': "Your username from the panel",
                'Password': "Your password from the panel",
                'Port': "2022"
            }
        
        # Initialize fonts if not set
        if self.FONTS is None:
            self.FONTS = {
                'header': ("Segoe UI", 24, "bold"),
                'subheader': ("Segoe UI", 16, "bold"),
                'normal': ("Segoe UI", 12),
                'small': ("Segoe UI", 10),
                'badge': ("Segoe UI", 10, "bold")
            }
        
        # Initialize installation steps if not set
        if self.INSTALLATION_STEPS is None:
            self.INSTALLATION_STEPS = [
                "Checking system requirements...",
                "Verifying network connectivity...",
                "Checking Cloudflared installation...",
                "Validating configuration..."
            ]

class ModernTooltip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip = None
        self.widget.bind('<Enter>', self.show_tooltip)
        self.widget.bind('<Leave>', self.hide_tooltip)

    def show_tooltip(self, event=None):
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 20

        self.tooltip = ctk.CTkToplevel(self.widget)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{x}+{y}")

        label = ctk.CTkLabel(
            self.tooltip,
            text=self.text,
            fg_color="#1c1c1c",
            corner_radius=6,
            padx=10,
            pady=5
        )
        label.pack()

    def hide_tooltip(self, event=None):
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None

class EnterpriseCloudflaredApp(ctk.CTk):
    def __init__(self, config: Optional[AppConfig] = None):
        super().__init__()
        
        # Initialize configuration
        self.config = config or AppConfig()
        
        # Configure window
        self.title(self.config.WINDOW_TITLE)
        self.geometry(f"{self.config.WINDOW_SIZE[0]}x{self.config.WINDOW_SIZE[1]}")
        self.minsize(*self.config.WINDOW_MIN_SIZE)
        
        # Set theme and colors
        self.colors = self.config.COLORS
        
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Create header
        self.create_header()
        
        # Create main content
        self.create_main_content()
        
        # Create status bar
        self.create_status_bar()
        
        # Initialize system
        self.initialize_system()

    def create_header(self):
        header = ctk.CTkFrame(self, fg_color=self.colors['bg_secondary'], height=80)
        header.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
        header.grid_columnconfigure(0, weight=1)
        header.grid_propagate(False)

        # Logo and title container
        title_frame = ctk.CTkFrame(header, fg_color="transparent")
        title_frame.grid(row=0, column=0, sticky="w", padx=20)

        if self.config.SHOW_ENTERPRISE_BADGE:
            # Enterprise badge
            enterprise_badge = ctk.CTkLabel(
                title_frame,
                text=self.config.ENTERPRISE_BADGE_TEXT,
                font=self.config.FONTS['badge'],
                fg_color=self.colors['accent'],
                text_color=self.colors['text'],
                corner_radius=4,
                padx=8,
                pady=2
            )
            enterprise_badge.pack(side="left", padx=(0, 10))

        # Title
        title = ctk.CTkLabel(
            title_frame,
            text=self.config.APP_NAME,
            font=self.config.FONTS['header'],
            text_color=self.colors['text']
        )
        title.pack(side="left")

        # Version number
        version = ctk.CTkLabel(
            title_frame,
            text=self.config.APP_VERSION,
            font=self.config.FONTS['normal'],
            text_color="#64748b"
        )
        version.pack(side="left", padx=10)

    def create_main_content(self):
        # Main content container
        self.main_frame = ctk.CTkFrame(self, fg_color=self.colors['bg_primary'])
        self.main_frame.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)

        # Progress frame
        self.progress_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.progress_frame.grid(row=0, column=0, sticky="nsew", padx=40, pady=40)
        self.progress_frame.grid_columnconfigure(0, weight=1)
        self.progress_frame.grid_rowconfigure(1, weight=1)

        # Animated progress circle
        self.progress_circle = ctk.CTkProgressBar(
            self.progress_frame,
            width=200,
            height=10,
            corner_radius=5,
            mode="determinate"
        )
        self.progress_circle.grid(row=0, column=0, pady=(100, 20))
        self.progress_circle.set(0)

        self.progress_label = ctk.CTkLabel(
            self.progress_frame,
            text="Initializing System...",
            font=self.config.FONTS['normal']
        )
        self.progress_label.grid(row=1, column=0)

        # Server controls frame (initially hidden)
        self.server_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        
        # Control panel
        control_panel = ctk.CTkFrame(
            self.server_frame,
            fg_color=self.colors['bg_secondary'],
            corner_radius=15
        )
        control_panel.pack(fill="x", padx=40, pady=20)

        # Server status indicator
        self.status_indicator = ctk.CTkLabel(
            control_panel,
            text="●",
            font=self.config.FONTS['header'],
            text_color=self.colors['warning']
        )
        self.status_indicator.pack(side="left", padx=20)

        # Start button
        self.start_button = ctk.CTkButton(
            control_panel,
            text="Start Server",
            font=self.config.FONTS['normal'],
            height=40,
            command=self.start_server,
            fg_color=self.colors['accent'],
            hover_color="#2563eb"
        )
        self.start_button.pack(side="left", padx=10)

        # Stats container
        stats_frame = ctk.CTkFrame(
            control_panel,
            fg_color="transparent"
        )
        stats_frame.pack(side="right", padx=20)

        self.uptime_label = ctk.CTkLabel(
            stats_frame,
            text="Uptime: 00:00:00",
            font=self.config.FONTS['normal']
        )
        self.uptime_label.pack(side="right", padx=10)

        # Connection panel
        connection_panel = ctk.CTkFrame(
            self.server_frame,
            fg_color=self.colors['bg_secondary'],
            corner_radius=15
        )
        connection_panel.pack(fill="x", padx=40, pady=20)

        # Panel header
        panel_header = ctk.CTkFrame(
            connection_panel,
            fg_color="transparent"
        )
        panel_header.pack(fill="x", padx=20, pady=10)

        ctk.CTkLabel(
            panel_header,
            text="Connection Details",
            font=self.config.FONTS['subheader']
        ).pack(side="left")

        # Connection details grid
        details_frame = ctk.CTkFrame(connection_panel, fg_color="transparent")
        details_frame.pack(fill="x", padx=20, pady=10)

        for label, value in self.config.CONNECTION_DETAILS.items():
            # Container for each detail row
            row_frame = ctk.CTkFrame(
                details_frame,
                fg_color=self.colors['bg_primary'],
                corner_radius=8
            )
            row_frame.pack(fill="x", pady=5)

            # Label
            ctk.CTkLabel(
                row_frame,
                text=label,
                font=self.config.FONTS['normal']
            ).pack(side="left", padx=15, pady=10)

            # Value
            value_label = ctk.CTkLabel(
                row_frame,
                text=value,
                font=self.config.FONTS['normal']
            )
            value_label.pack(side="left", padx=5)

            # Copy button
            copy_btn = ctk.CTkButton(
                row_frame,
                text="Copy",
                width=60,
                height=28,
                command=lambda v=value: self.copy_to_clipboard(v),
                fg_color=self.colors['bg_secondary'],
                hover_color=self.colors['accent']
            )
            copy_btn.pack(side="right", padx=10)

        # Logs panel
        self.logs_panel = ctk.CTkTextbox(
            self.server_frame,
            fg_color=self.colors['bg_secondary'],
            corner_radius=15,
            height=self.config.LOG_PANEL_HEIGHT
        )
        self.logs_panel.pack(fill="x", padx=40, pady=20)

    def create_status_bar(self):
        status_bar = ctk.CTkFrame(self, height=30, fg_color=self.colors['bg_secondary'])
        status_bar.grid(row=2, column=0, sticky="ew")
        status_bar.grid_columnconfigure(1, weight=1)

        # System status
        self.system_status = ctk.CTkLabel(
            status_bar,
            text="System Status: Ready",
            font=self.config.FONTS['small'],
            text_color="#64748b"
        )
        self.system_status.grid(row=0, column=0, padx=10)

        # Current time
        self.time_label = ctk.CTkLabel(
            status_bar,
            text="",
            font=self.config.FONTS['small'],
            text_color="#64748b"
        )
        self.time_label.grid(row=0, column=2, padx=10)
        self.update_time()

    def update_time(self):
        current_time = datetime.now().strftime("%H:%M:%S")
        self.time_label.configure(text=f"Local Time: {current_time}")
        self.after(self.config.TIME_UPDATE_INTERVAL, self.update_time)

    def initialize_system(self):
        self.check_thread = threading.Thread(target=self.check_cloudflared)
        self.check_thread.start()

    def copy_to_clipboard(self, text):
        self.clipboard_clear()
        self.clipboard_append(text)
        self.system_status.configure(text="System Status: Copied to clipboard")
        self.after(2000, lambda: self.system_status.configure(text="System Status: Ready"))

    def add_log(self, message, level="info"):
        if self.config.SHOW_TIMESTAMPS_IN_LOGS:
            timestamp = datetime.now().strftime("%H:%M:%S")
            message = f"[{timestamp}] {message}"
        else:
            message = f"{message}"
            
        color_map = {
            "info": "#94a3b8",
            "success": self.colors['success'],
            "warning": self.colors['warning'],
            "error": self.colors['error']
        }
        self.logs_panel.insert("end", f"{message}\n")
        self.logs_panel.see("end")

    def check_cloudflared(self):
        for i, step in enumerate(self.config.INSTALLATION_STEPS):
            self.progress_label.configure(text=step)
            for j in range(25):
                time.sleep(0.05)
                progress = (i * 25 + j) / 100
                self.progress_circle.set(progress)

        try:
            subprocess.run(["cloudflared", "--version"], 
                         check=True, 
                         capture_output=True)
            installed = True
        except (subprocess.CalledProcessError, FileNotFoundError):
            installed = False
            
        if not installed:
            self.progress_label.configure(text="Installing Cloudflared...")
            try:
                subprocess.run(
                    [self.config.PACKAGE_MANAGER, "install", "--id", self.config.CLOUDFLARED_PACKAGE],
                    check=True
                )
            except subprocess.CalledProcessError as e:
                self.progress_label.configure(
                    text="Installation Failed",
                    text_color=self.colors['error']
                )
                return

        self.progress_circle.set(1)
        self.progress_label.configure(text="System Ready")
        time.sleep(1)
        
        self.progress_frame.grid_forget()
        self.server_frame.grid(row=0, column=0, sticky="nsew")
        
        self.add_log("System initialized successfully", "success")
        self.add_log("Cloudflared service ready", "info")

    def start_server(self):
        self.start_button.configure(state="disabled")
        self.status_indicator.configure(text="●", text_color=self.colors['warning'])
        self.add_log("Starting server...", "warning")

        def run_server():
            try:
                process = subprocess.Popen(
                    [
                        "cloudflared",
                        "access",
                        "ssh",
                        "--hostname",
                        self.config.SERVER_CONFIG['hostname'],
                        "--url",
                        self.config.SERVER_CONFIG['local_url'],
                        "--loglevel",
                        self.config.SERVER_CONFIG['log_level']
                    ],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                
                self.status_indicator.configure(text="●", text_color=self.colors['success'])
                self.add_log("Server started successfully", "success")
                self.system_status.configure(text="System Status: Server Running")
                
                start_time = time.time()
                
                def update_uptime():
                    if process.poll() is None:  # If process is still running
                        uptime = int(time.time() - start_time)
                        hours = uptime // 3600
                        minutes = (uptime % 3600) // 60
                        seconds = uptime % 60
                        self.uptime_label.configure(
                            text=f"Uptime: {hours:02d}:{minutes:02d}:{seconds:02d}"
                        )
                        self.after(self.config.UPTIME_UPDATE_INTERVAL, update_uptime)
                
                update_uptime()
                
                # Monitor process output
                while True:
                    output = process.stdout.readline()
                    if not output and process.poll() is not None:
                        break
                    if output:
                        self.add_log(output.strip().decode(), "info")
                
                # Process stopped
                self.status_indicator.configure(text="●", text_color=self.colors['error'])
                self.add_log("Server stopped unexpectedly", "error")
                self.system_status.configure(text="System Status: Server Stopped")
                self.start_button.configure(state="normal")
                self.uptime_label.configure(text="Uptime: 00:00:00")
                
            except Exception as e:
                self.status_indicator.configure(text="●", text_color=self.colors['error'])
                self.add_log(f"Error: {str(e)}", "error")
                self.system_status.configure(text="System Status: Error")
                self.start_button.configure(state="normal")
                self.uptime_label.configure(text="Uptime: 00:00:00")

        server_thread = threading.Thread(target=run_server)
        server_thread.daemon = True
        server_thread.start()

if __name__ == "__main__":
    try:
        app = EnterpriseCloudflaredApp()
        app.mainloop()
    except Exception as e:
        print(f"Critical Error: {str(e)}")
        sys.exit(1)