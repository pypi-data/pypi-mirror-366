import os
import shutil
import subprocess
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from threading import Thread
import json
import sys
import webbrowser
import tempfile
import http.server
import socketserver
import socket
import time
import zipfile
import glob
from xml.etree import ElementTree as ET
import re

class HTMLtoAPKConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("HTML To APK/AAB")
        self.root.geometry("500x640")  # Increased height for new features
        self.root.resizable(True, True)
        self.icon_path = os.path.join(os.path.dirname(__file__), "icon.ico")
        if os.path.exists(self.icon_path):
            self.root.iconbitmap(self.icon_path)
        
        # Variables
        self.html_dir = tk.StringVar()
        self.app_name = tk.StringVar(value="MyApp")
        self.package_name = tk.StringVar(value="com.example.myapp")
        self.output_dir = tk.StringVar(value=os.path.join(os.getcwd(), "dist"))
        self.icon_path = tk.StringVar()
        self.splash_path = tk.StringVar()
        self.platform_var = tk.StringVar(value="android")
        self.version_var = tk.StringVar(value="1.0.0")
        self.orientation_var = tk.StringVar(value="portrait")
        self.installation_status = tk.StringVar(value="Checking requirements...")
        self.aab_path = tk.StringVar()
        
        # Cordova options
        self.cordova_options = {
            "fullscreen": tk.BooleanVar(value=False),
            "disallow_overscroll": tk.BooleanVar(value=False),
            "preferences": {
                "AllowInlineMediaPlayback": tk.BooleanVar(value=False),
                "BackupWebStorage": tk.StringVar(value="none"),
                "DisallowOverscroll": tk.BooleanVar(value=False),
                "EnableViewportScale": tk.BooleanVar(value=False),
                "KeyboardDisplayRequiresUserAction": tk.BooleanVar(value=True),
                "SuppressesIncrementalRendering": tk.BooleanVar(value=False),
                "GapBetweenPages": tk.StringVar(value="0"),
                "PageLength": tk.StringVar(value="0"),
                "TopActivityIndicator": tk.StringVar(value="gray"),
                "HideKeyboardFormAccessoryBar": tk.BooleanVar(value=False),
                "SuppressesLongPressGesture": tk.BooleanVar(value=False),
                "Suppresses3DTouchGesture": tk.BooleanVar(value=False),
                "MediaPlaybackRequiresUserAction": tk.BooleanVar(value=False),
                "ShouldPersistSession": tk.BooleanVar(value=False),
            }
        }
        
        # Preview server
        self.preview_port = self.find_free_port()
        self.httpd = None
        
        # ADB status
        self.adb_status = tk.StringVar(value="ADB: Not connected")
        self.device_connected = False
        
        # UI Setup
        self.create_ui()
        
        # Initial checks
        self.root.after(100, self.check_requirements)
        self.root.after(500, self.check_adb)
    
    def find_free_port(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('', 0))
            return s.getsockname()[1]
    
    def create_ui(self):
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Notebook for tabs
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Settings Tab
        settings_tab = ttk.Frame(notebook, padding="10")
        notebook.add(settings_tab, text="Settings")
        
        # HTML Folder
        ttk.Label(settings_tab, text="HTML Folder:").grid(row=0, column=0, sticky=tk.W, pady=2)
        ttk.Entry(settings_tab, textvariable=self.html_dir, width=50).grid(row=0, column=1, padx=2)
        ttk.Button(settings_tab, text="Browse", command=self.browse_html, width=8).grid(row=0, column=2)
        
        # App Name
        ttk.Label(settings_tab, text="App Name:").grid(row=1, column=0, sticky=tk.W, pady=2)
        ttk.Entry(settings_tab, textvariable=self.app_name, width=50).grid(row=1, column=1, padx=2)
        
        # Package Name
        ttk.Label(settings_tab, text="Package Name:").grid(row=2, column=0, sticky=tk.W, pady=2)
        ttk.Entry(settings_tab, textvariable=self.package_name, width=50).grid(row=2, column=1, padx=2)
        
        # Version
        ttk.Label(settings_tab, text="Version:").grid(row=3, column=0, sticky=tk.W, pady=2)
        ttk.Entry(settings_tab, textvariable=self.version_var, width=50).grid(row=3, column=1, padx=2)
        
        # Output Directory
        ttk.Label(settings_tab, text="Output Folder:").grid(row=4, column=0, sticky=tk.W, pady=2)
        ttk.Entry(settings_tab, textvariable=self.output_dir, width=50).grid(row=4, column=1, padx=2)
        ttk.Button(settings_tab, text="Browse", command=self.browse_output, width=8).grid(row=4, column=2)
        
        # Icon File
        ttk.Label(settings_tab, text="App Icon:").grid(row=5, column=0, sticky=tk.W, pady=2)
        ttk.Entry(settings_tab, textvariable=self.icon_path, width=50).grid(row=5, column=1, padx=2)
        ttk.Button(settings_tab, text="Browse", command=self.browse_icon, width=8).grid(row=5, column=2)
        
        # Splash Screen
        ttk.Label(settings_tab, text="Splash Screen:").grid(row=6, column=0, sticky=tk.W, pady=2)
        ttk.Entry(settings_tab, textvariable=self.splash_path, width=50).grid(row=6, column=1, padx=2)
        ttk.Button(settings_tab, text="Browse", command=self.browse_splash, width=8).grid(row=6, column=2)
        
        # Platform Selection
        ttk.Label(settings_tab, text="Platform:").grid(row=7, column=0, sticky=tk.W, pady=2)
        platform_frame = ttk.Frame(settings_tab)
        platform_frame.grid(row=7, column=1, columnspan=2, sticky=tk.W)
        ttk.Radiobutton(platform_frame, text="Android", variable=self.platform_var, value="android").pack(side=tk.LEFT)
        ttk.Radiobutton(platform_frame, text="iOS", variable=self.platform_var, value="ios").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(platform_frame, text="Windows", variable=self.platform_var, value="windows").pack(side=tk.LEFT)
        ttk.Radiobutton(platform_frame, text="Browser", variable=self.platform_var, value="browser").pack(side=tk.LEFT, padx=5)
        
        # Orientation
        ttk.Label(settings_tab, text="Orientation:").grid(row=8, column=0, sticky=tk.W, pady=2)
        orientation_frame = ttk.Frame(settings_tab)
        orientation_frame.grid(row=8, column=1, columnspan=2, sticky=tk.W)
        ttk.Radiobutton(orientation_frame, text="Portrait", variable=self.orientation_var, value="portrait").pack(side=tk.LEFT)
        ttk.Radiobutton(orientation_frame, text="Landscape", variable=self.orientation_var, value="landscape").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(orientation_frame, text="Both", variable=self.orientation_var, value="both").pack(side=tk.LEFT)
        
        # Options Tab
        options_tab = ttk.Frame(notebook, padding="10")
        notebook.add(options_tab, text="Cordova Options")
        
        # Main options
        ttk.Checkbutton(options_tab, text="Fullscreen", variable=self.cordova_options["fullscreen"]).grid(row=0, column=0, sticky=tk.W)
        ttk.Checkbutton(options_tab, text="Disallow Overscroll", variable=self.cordova_options["disallow_overscroll"]).grid(row=0, column=1, sticky=tk.W)
        
        # Preferences
        ttk.Label(options_tab, text="Preferences", font=("", 10, "bold")).grid(row=1, column=0, sticky=tk.W, pady=5, columnspan=2)
        
        row_num = 2
        for pref, var in self.cordova_options["preferences"].items():
            if isinstance(var, tk.BooleanVar):
                ttk.Checkbutton(options_tab, text=pref, variable=var).grid(row=row_num, column=0, sticky=tk.W)
                row_num += 1
            else:
                ttk.Label(options_tab, text=pref).grid(row=row_num, column=0, sticky=tk.W)
                ttk.Entry(options_tab, textvariable=var, width=15).grid(row=row_num, column=1, sticky=tk.W)
                row_num += 1
        
        # AAB to APK Tab
        aab_tab = ttk.Frame(notebook, padding="10")
        notebook.add(aab_tab, text="AAB to APK")
        
        # AAB File
        ttk.Label(aab_tab, text="AAB File:").grid(row=0, column=0, sticky=tk.W, pady=2)
        ttk.Entry(aab_tab, textvariable=self.aab_path, width=50).grid(row=0, column=1, padx=2)
        ttk.Button(aab_tab, text="Browse", command=self.browse_aab, width=8).grid(row=0, column=2)
        
        # Keystore Info
        ttk.Label(aab_tab, text="Keystore File:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.keystore_path = tk.StringVar()
        ttk.Entry(aab_tab, textvariable=self.keystore_path, width=50).grid(row=1, column=1, padx=2)
        ttk.Button(aab_tab, text="Browse", command=self.browse_keystore, width=8).grid(row=1, column=2)
        
        ttk.Label(aab_tab, text="Keystore Password:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.keystore_pass = tk.StringVar()
        ttk.Entry(aab_tab, textvariable=self.keystore_pass, show="*", width=50).grid(row=2, column=1, padx=2)
        
        ttk.Label(aab_tab, text="Key Alias:").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.key_alias = tk.StringVar()
        ttk.Entry(aab_tab, textvariable=self.key_alias, width=50).grid(row=3, column=1, padx=2)
        
        ttk.Label(aab_tab, text="Key Password:").grid(row=4, column=0, sticky=tk.W, pady=2)
        self.key_pass = tk.StringVar()
        ttk.Entry(aab_tab, textvariable=self.key_pass, show="*", width=50).grid(row=4, column=1, padx=2)
        
        # Convert AAB button
        ttk.Button(
            aab_tab, 
            text="Convert AAB to APK", 
            command=self.start_aab_conversion,
            width=20
        ).grid(row=5, column=1, pady=10)
        
        # Console Output
        console_frame = ttk.LabelFrame(main_frame, text="Output Log", padding="5")
        console_frame.pack(fill=tk.BOTH, expand=False, pady=5)
        
        # Create a container frame for the console with fixed height
        console_container = ttk.Frame(console_frame, height=150)
        console_container.pack(fill=tk.BOTH, expand=True)
        console_container.pack_propagate(False)  # Prevent the frame from resizing to contents
        
        self.console = scrolledtext.ScrolledText(
            console_container, 
            wrap=tk.WORD,
            font=("Consolas", 8),
            state='disabled'
        )
        self.console.pack(fill=tk.BOTH, expand=True)
        
        # Status and Buttons
        bottom_frame = ttk.Frame(main_frame)
        bottom_frame.pack(fill=tk.X, pady=5)
        
        # ADB status label
        self.adb_label = ttk.Label(bottom_frame, textvariable=self.adb_status)
        self.adb_label.pack(side=tk.LEFT, padx=5)
        
        # Refresh ADB button
        ttk.Button(
            bottom_frame, 
            text="ADB", 
            command=self.check_adb,
            width=5
        ).pack(side=tk.LEFT, padx=2)
        
        # Install button
        self.install_btn = ttk.Button(
            bottom_frame, 
            text="Install APK", 
            command=self.install_apk,
            state=tk.DISABLED,
            width=5
        )
        self.install_btn.pack(side=tk.RIGHT, padx=2)
        
        # Install Requirements button
        self.install_req_btn = ttk.Button(
            bottom_frame, 
            text="Requirements", 
            command=self.install_requirements,
            width=15
        )
        self.install_req_btn.pack(side=tk.RIGHT, padx=2)
        
        # Convert button
        self.convert_btn = ttk.Button(
            bottom_frame, 
            text="Build APK/AAB", 
            command=self.start_conversion,
            state=tk.DISABLED,
            width=25
        )
        self.convert_btn.pack(side=tk.RIGHT, padx=2)
    
    def browse_aab(self):
        file_path = filedialog.askopenfilename(
            title="Select AAB File",
            filetypes=[("Android App Bundle", "*.aab"), ("All Files", "*.*")]
        )
        if file_path:
            self.aab_path.set(file_path)
    
    def browse_keystore(self):
        file_path = filedialog.askopenfilename(
            title="Select Keystore File",
            filetypes=[("Keystore Files", "*.keystore;*.jks"), ("All Files", "*.*")]
        )
        if file_path:
            self.keystore_path.set(file_path)
    
    def browse_html(self):
        dir_path = filedialog.askdirectory(title="Select HTML Folder")
        if dir_path:
            self.html_dir.set(dir_path)
            default_name = os.path.basename(dir_path)
            if default_name:
                self.app_name.set(default_name)
                self.package_name.set(f"com.example.{default_name.lower().replace(' ', '')}")
    
    def browse_output(self):
        dir_path = filedialog.askdirectory(title="Select Output Directory")
        if dir_path:
            self.output_dir.set(dir_path)
    
    def browse_icon(self):
        file_path = filedialog.askopenfilename(
            title="Select Icon File",
            filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.ico"), ("All Files", "*.*")]
        )
        if file_path:
            self.icon_path.set(file_path)
    
    def browse_splash(self):
        file_path = filedialog.askopenfilename(
            title="Select Splash Screen",
            filetypes=[("Image Files", "*.png;*.jpg;*.jpeg"), ("All Files", "*.*")]
        )
        if file_path:
            self.splash_path.set(file_path)
    
    def log(self, message):
        self.console.configure(state='normal')
        self.console.insert(tk.END, message + "\n")
        self.console.see(tk.END)
        self.console.configure(state='disabled')
        self.root.update()
    
    def clear_log(self):
        self.console.configure(state='normal')
        self.console.delete(1.0, tk.END)
        self.console.configure(state='disabled')
    
    def check_adb(self):
        """Check if ADB is available and device is connected"""
        try:
            self.log("Checking ADB connection...")
            
            # Check if ADB is available
            adb_version = subprocess.check_output(
                ["adb", "--version"],
                stderr=subprocess.STDOUT,
                shell=True,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
            ).decode().strip().split('\n')[0]
            
            self.log(f"✔ {adb_version}")
            
            # Check for connected devices
            devices_output = subprocess.check_output(
                ["adb", "devices"],
                stderr=subprocess.STDOUT,
                shell=True,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
            ).decode().strip()
            
            # Parse devices
            devices = [line.split('\t')[0] for line in devices_output.split('\n')[1:] if line.strip()]
            
            if devices and "device" in devices_output:
                self.device_connected = True
                self.adb_status.set(f"ADB: Connected ({len(devices)} device(s))")
                self.install_btn.config(state=tk.NORMAL)
                self.log(f"✔ Connected devices: {', '.join(devices)}")
            else:
                self.device_connected = False
                self.adb_status.set("ADB: No devices connected")
                self.install_btn.config(state=tk.DISABLED)
                self.log("✖ No devices connected")
            
            return True
        except subprocess.CalledProcessError as e:
            self.device_connected = False
            self.adb_status.set("ADB: Not available")
            self.install_btn.config(state=tk.DISABLED)
            self.log("✖ ADB not found or not in PATH")
            return False
        except Exception as e:
            self.device_connected = False
            self.adb_status.set("ADB: Error checking")
            self.install_btn.config(state=tk.DISABLED)
            self.log(f"✖ Error checking ADB: {str(e)}")
            return False
    
    def check_requirements(self):
        self.clear_log()
        self.log("Checking system requirements...")
        
        try:
            # Check Node.js
            node_version = subprocess.check_output(
                ["node", "--version"],
                stderr=subprocess.STDOUT,
                shell=True,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
            ).decode().strip()
            self.log(f"✔ Node.js {node_version} detected")
            
            # Check npm
            npm_version = subprocess.check_output(
                ["npm", "--version"],
                stderr=subprocess.STDOUT,
                shell=True,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
            ).decode().strip()
            self.log(f"✔ npm {npm_version} detected")
            
            # Check Cordova
            try:
                cordova_version = subprocess.check_output(
                    ["cordova", "--version"],
                    stderr=subprocess.STDOUT,
                    shell=True,
                    creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
                ).decode().strip()
                self.log(f"✔ Cordova {cordova_version} detected")
                self.installation_status.set("Requirements satisfied")
                self.convert_btn.config(state=tk.NORMAL)
                return True
            except subprocess.CalledProcessError:
                self.log("✖ Cordova not found (but Node.js is installed)")
                self.installation_status.set("Cordova not found - install required")
                return False
            
        except subprocess.CalledProcessError:
            self.log("✖ Node.js and npm are not installed or not in PATH")
            self.log("Please install Node.js from https://nodejs.org/")
            self.installation_status.set("Node.js not found - install required")
            return False
    
    def install_requirements(self):
        self.clear_log()
        self.log("Installing required packages...")
        
        try:
            # Install only essential packages
            process = subprocess.Popen(
                ["npm", "install", "-g", "cordova"],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                shell=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
            )
            
            for line in process.stdout:
                self.log(line.strip())
            
            process.wait()
            
            if process.returncode == 0:
                self.log("✔ Cordova installed successfully")
                self.installation_status.set("Requirements satisfied")
                self.convert_btn.config(state=tk.NORMAL)
                messagebox.showinfo("Success", "Cordova installed successfully")
            else:
                raise Exception("Failed to install Cordova")
        
        except Exception as e:
            self.log(f"Error: {str(e)}")
            self.installation_status.set("Installation failed")
            messagebox.showerror("Error", f"Failed to install requirements: {str(e)}")
    
    def start_conversion(self):
        if not self.html_dir.get():
            messagebox.showerror("Error", "Please select an HTML folder to convert")
            return
            
        self.convert_btn.config(state=tk.DISABLED)
        self.install_req_btn.config(state=tk.DISABLED)
        Thread(target=self.convert_to_apk, daemon=True).start()
    
    def start_aab_conversion(self):
        if not self.aab_path.get():
            messagebox.showerror("Error", "Please select an AAB file to convert")
            return
            
        if not self.keystore_path.get():
            messagebox.showerror("Error", "Please select a keystore file")
            return
            
        Thread(target=self.convert_aab_to_apk, daemon=True).start()
    
    def install_apk(self):
        if not self.device_connected:
            messagebox.showerror("Error", "No Android device connected")
            return
            
        apk_path = filedialog.askopenfilename(
            title="Select APK to Install",
            filetypes=[("Android Package", "*.apk"), ("All Files", "*.*")]
        )
        
        if not apk_path:
            return
            
        Thread(target=self.do_install_apk, args=(apk_path,), daemon=True).start()
    
    def do_install_apk(self, apk_path):
        try:
            self.clear_log()
            self.log(f"Installing APK: {apk_path}")
            
            process = subprocess.Popen(
                ["adb", "install", "-r", apk_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                shell=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
            )
            
            for line in process.stdout:
                self.log(line.strip())
            
            process.wait()
            
            if process.returncode == 0:
                self.log("✔ APK installed successfully")
                messagebox.showinfo("Success", "APK installed successfully on the device")
            else:
                raise Exception("Failed to install APK")
        
        except Exception as e:
            self.log(f"✖ Error: {str(e)}")
            messagebox.showerror("Error", f"Failed to install APK: {str(e)}")
    
    def generate_config_xml(self):
        preferences = []
        for pref, var in self.cordova_options["preferences"].items():
            if isinstance(var, tk.BooleanVar):
                value = "true" if var.get() else "false"
            else:
                value = var.get()
            preferences.append(f'<preference name="{pref}" value="{value}" />')
        
        orientation_config = f'<preference name="Orientation" value="{self.orientation_var.get()}" />'
        
        config_xml = f"""<?xml version='1.0' encoding='utf-8'?>
<widget id="{self.package_name.get()}" 
        version="{self.version_var.get()}" 
        xmlns="http://www.w3.org/ns/widgets" 
        xmlns:cdv="http://cordova.apache.org/ns/1.0">
    <name>{self.app_name.get()}</name>
    <description>
        A HTML5 application built with Cordova
    </description>
    <author email="support@example.com" href="http://example.com">
        Your Name
    </author>
    <content src="index.html" />
    <access origin="*" />
    {orientation_config}
    {"".join(preferences)}
</widget>
"""
        return config_xml
    
    def copy_www_contents(self, www_dir):
        html_dir = self.html_dir.get()
        
        # Clear existing www directory
        if os.path.exists(www_dir):
            shutil.rmtree(www_dir)
        os.makedirs(www_dir)
        
        # Copy all files from HTML folder
        for item in os.listdir(html_dir):
            s = os.path.join(html_dir, item)
            d = os.path.join(www_dir, item)
            if os.path.isdir(s):
                shutil.copytree(s, d)
            else:
                shutil.copy2(s, d)
    
    def copy_icon_and_splash(self, project_dir):
        # Copy icon
        if self.icon_path.get():
            icon_ext = os.path.splitext(self.icon_path.get())[1].lower()
            res_dir = os.path.join(project_dir, "resources")
            
            if not os.path.exists(res_dir):
                os.makedirs(res_dir)
            
            icon_dir = os.path.join(res_dir, "icon")
            if not os.path.exists(icon_dir):
                os.makedirs(icon_dir)
            
            shutil.copy2(self.icon_path.get(), os.path.join(icon_dir, f"icon{icon_ext}"))
        
        # Copy splash screen
        if self.splash_path.get():
            splash_ext = os.path.splitext(self.splash_path.get())[1].lower()
            res_dir = os.path.join(project_dir, "resources")
            
            if not os.path.exists(res_dir):
                os.makedirs(res_dir)
            
            splash_dir = os.path.join(res_dir, "splash")
            if not os.path.exists(splash_dir):
                os.makedirs(splash_dir)
            
            shutil.copy2(self.splash_path.get(), os.path.join(splash_dir, f"splash{splash_ext}"))
    
    def sign_apk(self, apk_path, project_dir):
        """Automatically sign the APK using debug keystore"""
        try:
            # Path to debug keystore (usually in ~/.android/debug.keystore)
            debug_keystore = os.path.join(os.path.expanduser("~"), ".android", "debug.keystore")
            
            if not os.path.exists(debug_keystore):
                self.log("Debug keystore not found, creating one...")
                # Create debug keystore if it doesn't exist
                keytool_cmd = [
                    "keytool",
                    "-genkey",
                    "-v",
                    "-keystore", debug_keystore,
                    "-alias", "androiddebugkey",
                    "-keyalg", "RSA",
                    "-keysize", "2048",
                    "-validity", "10000",
                    "-storepass", "android",
                    "-keypass", "android",
                    "-dname", "CN=Android Debug,O=Android,C=US"
                ]
                
                keytool_process = subprocess.Popen(
                    keytool_cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    shell=True,
                    text=True,
                    creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
                )
                
                for line in keytool_process.stdout:
                    self.log(line.strip())
                
                keytool_process.wait()
                
                if keytool_process.returncode != 0:
                    raise Exception("Failed to create debug keystore")
            
            # Sign the APK
            self.log("Signing APK with debug keystore...")
            
            # Find the zipalign tool (part of Android SDK)
            sdk_dir = os.getenv("ANDROID_HOME", os.getenv("ANDROID_SDK_ROOT", ""))
            if not sdk_dir:
                # Try to find SDK in common locations
                common_locations = [
                    os.path.join(os.getenv("LOCALAPPDATA", ""), "Android", "Sdk"),
                    os.path.join(os.getenv("ProgramFiles", ""), "Android", "android-sdk"),
                    os.path.join(os.path.expanduser("~"), "Library", "Android", "sdk"),
                    os.path.join(os.path.expanduser("~"), "Android", "Sdk"),
                ]
                
                for loc in common_locations:
                    if os.path.exists(loc):
                        sdk_dir = loc
                        break
            
            if not sdk_dir:
                raise Exception("Android SDK not found. Please set ANDROID_HOME environment variable.")
            
            build_tools_dir = os.path.join(sdk_dir, "build-tools")
            if not os.path.exists(build_tools_dir):
                raise Exception("Android build-tools not found")
            
            # Get the highest version of build-tools available
            build_tools_versions = os.listdir(build_tools_dir)
            if not build_tools_versions:
                raise Exception("No build-tools versions found")
            
            latest_version = sorted(build_tools_versions)[-1]
            build_tools_path = os.path.join(build_tools_dir, latest_version)
            
            zipalign_path = os.path.join(build_tools_path, "zipalign")
            if sys.platform == "win32":
                zipalign_path += ".exe"
            
            if not os.path.exists(zipalign_path):
                raise Exception(f"zipalign tool not found at {zipalign_path}")
            
            # Align the APK
            aligned_apk = os.path.join(project_dir, "app-aligned.apk")
            zipalign_cmd = [
                zipalign_path,
                "-v", "4",
                apk_path,
                aligned_apk
            ]
            
            zipalign_process = subprocess.Popen(
                zipalign_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                shell=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
            )
            
            for line in zipalign_process.stdout:
                self.log(line.strip())
            
            zipalign_process.wait()
            
            if zipalign_process.returncode != 0:
                raise Exception("Failed to align APK")
            
            # Sign the aligned APK
            signed_apk = os.path.join(project_dir, "app-signed.apk")
            apksigner_path = os.path.join(build_tools_path, "apksigner")
            if sys.platform == "win32":
                apksigner_path += ".bat"
            
            apksigner_cmd = [
                apksigner_path,
                "sign",
                "--ks", debug_keystore,
                "--ks-pass", "pass:android",
                "--key-pass", "pass:android",
                "--ks-key-alias", "androiddebugkey",
                "--out", signed_apk,
                aligned_apk
            ]
            
            apksigner_process = subprocess.Popen(
                apksigner_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                shell=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
            )
            
            for line in apksigner_process.stdout:
                self.log(line.strip())
            
            apksigner_process.wait()
            
            if apksigner_process.returncode != 0:
                raise Exception("Failed to sign APK")
            
            # Clean up intermediate files
            os.remove(aligned_apk)
            
            # Move signed APK to output directory
            final_apk = os.path.join(self.output_dir.get(), f"{self.app_name.get()}-signed.apk")
            if os.path.exists(final_apk):
                os.remove(final_apk)
            
            shutil.move(signed_apk, final_apk)
            
            return final_apk
            
        except Exception as e:
            self.log(f"Error signing APK: {str(e)}")
            return None
    
    def convert_aab_to_apk(self):
        """Convert AAB to APK using bundletool"""
        try:
            self.clear_log()
            self.log("Starting AAB to APK conversion...")
            
            aab_path = self.aab_path.get()
            keystore_path = self.keystore_path.get()
            keystore_pass = self.keystore_pass.get()
            key_alias = self.key_alias.get()
            key_pass = self.key_pass.get()
            
            if not aab_path or not os.path.exists(aab_path):
                raise Exception("AAB file not found")
            
            if not keystore_path or not os.path.exists(keystore_path):
                raise Exception("Keystore file not found")
            
            # Create temp directory
            temp_dir = tempfile.mkdtemp()
            self.log(f"Using temp directory: {temp_dir}")
            
            # Download bundletool if not exists
            bundletool_path = os.path.join(temp_dir, "bundletool.jar")
            if not os.path.exists(bundletool_path):
                self.log("Downloading bundletool...")
                webbrowser.open("https://github.com/google/bundletool/releases/latest")
                raise Exception("Please download bundletool.jar from GitHub and place it in the temp directory")
            
            # Generate APKS file
            apks_path = os.path.join(temp_dir, "output.apks")
            self.log("Generating APKS file...")
            
            keystore_args = [
                f"--ks={keystore_path}",
                f"--ks-pass=pass:{keystore_pass}",
                f"--ks-key-alias={key_alias}",
                f"--key-pass=pass:{key_pass}"
            ] if keystore_pass else []
            
            bundletool_cmd = [
                "java", "-jar", bundletool_path,
                "build-apks",
                f"--bundle={aab_path}",
                f"--output={apks_path}",
                "--mode=universal"
            ] + keystore_args
            
            process = subprocess.Popen(
                bundletool_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                shell=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
            )
            
            for line in process.stdout:
                self.log(line.strip())
            
            process.wait()
            
            if process.returncode != 0:
                raise Exception("Failed to generate APKS file")
            
            # Extract APK from APKS
            self.log("Extracting APK from APKS...")
            with zipfile.ZipFile(apks_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
            
            # Find the universal APK
            universal_apk = os.path.join(temp_dir, "universal.apk")
            if not os.path.exists(universal_apk):
                # Sometimes the name is different
                apk_files = [f for f in os.listdir(temp_dir) if f.endswith(".apk")]
                if not apk_files:
                    raise Exception("No APK found in the APKS file")
                universal_apk = os.path.join(temp_dir, apk_files[0])
            
            # Move APK to output directory
            output_apk = os.path.join(
                self.output_dir.get(),
                f"{os.path.splitext(os.path.basename(aab_path))[0]}.apk"
            )
            
            if os.path.exists(output_apk):
                os.remove(output_apk)
            
            shutil.move(universal_apk, output_apk)
            
            self.log(f"\n✔ Conversion successful! APK saved to: {output_apk}")
            messagebox.showinfo(
                "Success",
                f"AAB successfully converted to APK!\nOutput APK: {output_apk}"
            )
            
            # Clean up
            shutil.rmtree(temp_dir, ignore_errors=True)
            
            return output_apk
            
        except Exception as e:
            self.log(f"\n✖ Error: {str(e)}")
            messagebox.showerror("Error", f"AAB to APK conversion failed: {str(e)}")
            return None
    
    def convert_to_apk(self):
        try:
            self.clear_log()
            self.log("Starting conversion process...")
            
            html_dir = self.html_dir.get()
            app_name = self.app_name.get()
            package_name = self.package_name.get()
            output_dir = self.output_dir.get()
            platform = self.platform_var.get()
            
            if not os.path.exists(html_dir):
                raise Exception(f"HTML folder not found: {html_dir}")
            
            # Check for index.html
            if not os.path.exists(os.path.join(html_dir, "index.html")):
                raise Exception("No index.html found in the selected folder")
            
            os.makedirs(output_dir, exist_ok=True)
            
            # Create Cordova project
            project_dir = os.path.join(output_dir, f"{app_name}-cordova")
            if os.path.exists(project_dir):
                shutil.rmtree(project_dir)
            
            self.log("Creating Cordova project...")
            process = subprocess.Popen(
                ["cordova", "create", project_dir, package_name, app_name],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                shell=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
            )
            
            for line in process.stdout:
                self.log(line.strip())
            
            process.wait()
            
            if process.returncode != 0:
                raise Exception("Failed to create Cordova project")
            
            # Add platform
            self.log(f"Adding {platform} platform...")
            platform_process = subprocess.Popen(
                ["cordova", "platform", "add", platform],
                cwd=project_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                shell=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
            )
            
            for line in platform_process.stdout:
                self.log(line.strip())
            
            platform_process.wait()
            
            if platform_process.returncode != 0:
                raise Exception(f"Failed to add {platform} platform")
            
            # Update config.xml
            self.log("Updating config.xml...")
            with open(os.path.join(project_dir, "config.xml"), "w") as f:
                f.write(self.generate_config_xml())
            
            # Copy www contents
            www_dir = os.path.join(project_dir, "www")
            self.log("Copying HTML files...")
            self.copy_www_contents(www_dir)
            
            # Copy icon and splash screen if provided
            if self.icon_path.get() or self.splash_path.get():
                self.log("Copying resources...")
                self.copy_icon_and_splash(project_dir)
            
            # Build the project
            self.log(f"Building {platform} project...")
            build_process = subprocess.Popen(
                ["cordova", "build", platform, "--release"],
                cwd=project_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                shell=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
            )
            
            for line in build_process.stdout:
                self.log(line.strip())
            
            build_process.wait()
            
            if build_process.returncode == 0:
                self.log("\n✔ Build successful!")
                
                # Find the built APK
                apk_search_path = os.path.join(
                    project_dir,
                    "platforms",
                    "android",
                    "app",
                    "build",
                    "outputs",
                    "apk",
                    "release",
                    "app-release-unsigned.apk"
                )
                
                if not os.path.exists(apk_search_path):
                    # Try alternative path for older Cordova versions
                    apk_search_path = os.path.join(
                        project_dir,
                        "platforms",
                        "android",
                        "build",
                        "outputs",
                        "apk",
                        "release",
                        "android-release-unsigned.apk"
                    )
                
                if os.path.exists(apk_search_path):
                    # Automatically sign the APK
                    signed_apk = self.sign_apk(apk_search_path, project_dir)
                    
                    if signed_apk:
                        self.log(f"\n✔ APK signed successfully: {signed_apk}")
                        messagebox.showinfo(
                            "Success", 
                            f"Application successfully built and signed!\nOutput APK: {signed_apk}"
                        )
                    else:
                        self.log("\n✖ APK signing failed")
                        messagebox.showinfo(
                            "Success with Warning", 
                            f"Application built but signing failed.\nUnsigned APK: {apk_search_path}"
                        )
                else:
                    self.log("\n✖ Could not locate built APK file")
                    messagebox.showinfo(
                        "Success with Warning", 
                        f"Application built but APK file not found in expected location.\nCheck: {project_dir}/platforms/android/"
                    )
                
            else:
                raise Exception("Build failed")
            
        except Exception as e:
            self.log(f"\n✖ Error: {str(e)}")
            messagebox.showerror("Error", f"Conversion failed: {str(e)}")
        finally:
            self.convert_btn.config(state=tk.NORMAL)
            self.install_req_btn.config(state=tk.NORMAL)

def run_gui():
    root = tk.Tk()
    
    # Set Windows style if available
    if sys.platform == "win32":
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)

    app = HTMLtoAPKConverter(root)
    root.mainloop()

if __name__ == "__main__":
    run_gui()