"""
GUI Module - Premium CustomTkinter Interface
===============================
The core graphical interface of the project. Features a modern, premium,
and user-friendly design to streamline interactions and demonstrations.

Author: Student FYP (Jazzy)
Purpose: Premium & modern interface designed for presentation/viva
"""

import os
import sys
# Add current directory to path to prevent local module import errors
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

import customtkinter as ctk # type: ignore
import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
from encryption import AESEncryption # type: ignore
from echo_hiding import EchoHiding # type: ignore
import threading
import run_steganalysis # type: ignore
from PIL import Image # type: ignore
import ctypes
from typing import Any, cast

# Configuration (Windows-only settings)
if sys.platform == "win32":
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("FYP.SteganographyTool.v1.0")
    ctypes.windll.shcore.SetProcessDpiAwareness(1)  # Enable sharp rendering on 4K/high-DPI screens
ctk.set_appearance_mode("Dark")  # Utilize Dark Mode for a premium appearance
ctk.set_default_color_theme("dark-blue")  # Dark blue color theme


class SteganographyGUI:
    """
    Handles all CustomTkinter interface components.
    Design upgraded to a modern dark mode aesthetic.
    """
    
    def __init__(self, root):
        """
        Setup main window.
        """
        self.root = root
        self.root.title("Secure Audio Steganography System - FYP")
        self.root.geometry("1000x750")
        
        # Variable placeholders
        self.audio_file_path = tk.StringVar()
        self.stego_file_path = tk.StringVar()
        self.password = tk.StringVar()
        self.extract_password = tk.StringVar()
        self.analysis_file_path = tk.StringVar()
        
        # UI Component Placeholders (Using cast(Any, None) to satisfy linter for dynamic initialization)
        self.sidebar_frame = cast(Any, None)
        self.logo_label = cast(Any, None)
        self.subtitle_label = cast(Any, None)
        self.status_label_title = cast(Any, None)
        self.status_label = cast(Any, None)
        self.tabview = cast(Any, None)
        self.tab_embed = cast(Any, None)
        self.tab_extract = cast(Any, None)
        self.tab_analysis = cast(Any, None)
        self.grp_audio = cast(Any, None)
        self.entry_audio = cast(Any, None)
        self.grp_msg = cast(Any, None)
        self.message_text = cast(Any, None)
        self.grp_action = cast(Any, None)
        self.entry_pass = cast(Any, None)
        self.btn_embed = cast(Any, None)
        self.embed_log = cast(Any, None)
        self.grp_stego = cast(Any, None)
        self.entry_stego = cast(Any, None)
        self.grp_decrypt = cast(Any, None)
        self.entry_extract_pass = cast(Any, None)
        self.btn_extract = cast(Any, None)
        self.grp_result = cast(Any, None)
        self.extracted_text = cast(Any, None)
        self.extract_log = cast(Any, None)
        self.info_frame = cast(Any, None)
        self.grp_ana_file = cast(Any, None)
        self.entry_analysis = cast(Any, None)
        self.grp_controls = cast(Any, None)
        self.btn_run_analysis = cast(Any, None)
        self.btn_view_graphs = cast(Any, None)
        self.grp_term = cast(Any, None)
        self.analysis_log = cast(Any, None)
        
        self._create_widgets()
        
    def resource_path(self, relative_path):
        """ Get absolute path to resource (icon/image). Works for dev or PyInstaller """
        # PyInstaller creates a temp folder _MEIPASS when running an exe
        base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
        return os.path.join(base_path, relative_path)

    def _create_widgets(self):
        """Construct all GUI widgets"""
        
        # Configuration
        try:
            self.root.iconbitmap(self.resource_path("logo.ico")) # Set Window Icon
        except Exception:
            pass # Icon might not be available in dev mode sometimes if not in root
        
        # Grid layout configuration
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=1)

        # 1. Sidebar Frame
        self.sidebar_frame = ctk.CTkFrame(self.root, width=220, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(5, weight=1)

        # Title in Sidebar (Replaced with Logo Image)
        try:
            logo_path = self.resource_path("logo.png")
            logo_img = ctk.CTkImage(
                light_image=Image.open(logo_path),
                dark_image=Image.open(logo_path),
                size=(150, 150) # Adjust size as needed
            )
            self.logo_label = ctk.CTkLabel(
                self.sidebar_frame, 
                text="", 
                image=logo_img
            )
            self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        except Exception as e:
            print(f"Error loading logo: {e}")
            # Fallback to text if image fails
            self.logo_label = ctk.CTkLabel(
                self.sidebar_frame, 
                text="Steganography Tool", 
                font=ctk.CTkFont(size=22, weight="bold")
            )
            self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        
        self.subtitle_label = ctk.CTkLabel(
            self.sidebar_frame,
            text="Echo Hiding + AES-256\nDevelop By Jazimin",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        self.subtitle_label.grid(row=1, column=0, padx=20, pady=(0, 20))

        # Action Buttons (Additional navigation can be placed here)
        # We can put status or persistent info here
        self.status_label_title = ctk.CTkLabel(self.sidebar_frame, text="Current Status:", anchor="w")
        self.status_label_title.grid(row=5, column=0, padx=20, pady=(10, 0))
        
        self.status_label = ctk.CTkLabel(
            self.sidebar_frame, 
            text="Ready", 
            text_color="#2ecc71",
            wraplength=180
        )
        self.status_label.grid(row=6, column=0, padx=20, pady=(0, 20))


        # 2. Main Tab View (Right Section)
        self.tabview = ctk.CTkTabview(self.root, corner_radius=10)
        self.tabview.grid(row=0, column=1, padx=20, pady=10, sticky="nsew")
        
        # Construct individual tabs
        self.tab_embed = self.tabview.add("Embed Message")
        self.tab_extract = self.tabview.add("Extract Message")
        self.tab_analysis = self.tabview.add("Steganalysis")
        
        # Configure Grid for Tabs
        self.tab_embed.grid_columnconfigure(0, weight=1)
        self.tab_extract.grid_columnconfigure(0, weight=1)
        self.tab_analysis.grid_columnconfigure(0, weight=1)

        # Populate each tab with content
        self._setup_embed_tab()
        self._setup_extract_tab()
        self._setup_analysis_tab()
    
    def _setup_embed_tab(self):
        """Setup content for the Embed Message tab"""
        
        # --- Section 1: Audio Selection ---
        self.grp_audio = ctk.CTkFrame(self.tab_embed)
        self.grp_audio.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        
        ctk.CTkLabel(self.grp_audio, text="Source Audio (FLAC)", font=("Roboto", 14, "bold")).pack(anchor="w", padx=10, pady=5)
        
        audio_frame_inner = ctk.CTkFrame(self.grp_audio, fg_color="transparent")
        audio_frame_inner.pack(fill="x", padx=10, pady=(0, 10))
        
        self.entry_audio = ctk.CTkEntry(audio_frame_inner, textvariable=self.audio_file_path, placeholder_text="Path to source audio...")
        self.entry_audio.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        ctk.CTkButton(audio_frame_inner, text="Browse", width=100, command=self._browse_audio_file).pack(side="right")

        # --- Section 2: Secret Message ---
        self.grp_msg = ctk.CTkFrame(self.tab_embed)
        self.grp_msg.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        self.tab_embed.grid_rowconfigure(1, weight=1) # Validated expansion
        
        ctk.CTkLabel(self.grp_msg, text="Secret Message", font=("Roboto", 14, "bold")).pack(anchor="w", padx=10, pady=5)
        
        self.message_text = ctk.CTkTextbox(self.grp_msg, height=150)
        self.message_text.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # --- Section 3: Password & Action Buttons ---
        self.grp_action = ctk.CTkFrame(self.tab_embed)
        self.grp_action.grid(row=2, column=0, padx=10, pady=10, sticky="ew")
        
        ctk.CTkLabel(self.grp_action, text="Encryption Password:", font=("Roboto", 12)).pack(side="left", padx=10)
        self.entry_pass = ctk.CTkEntry(self.grp_action, textvariable=self.password, show="*", width=200)
        self.entry_pass.pack(side="left", padx=10)
        
        self.btn_embed = ctk.CTkButton(
            self.grp_action, 
            text="EMBED DATA", 
            command=self._embed_message,
            fg_color="#e67e22", hover_color="#d35400", # Orange accent
            font=("Roboto", 13, "bold"),
            height=35
        )
        self.btn_embed.pack(side="right", padx=10, pady=10)
        
        # --- Section 4: Log ---
        self.embed_log = ctk.CTkTextbox(self.tab_embed, height=80, fg_color="#2b2b2b", text_color="#ecf0f1")
        self.embed_log.grid(row=3, column=0, padx=10, pady=(0, 10), sticky="ew")
        self.embed_log.insert("1.0", "System Ready for Embedding...\n")
        self.embed_log.configure(state="disabled")

    def _setup_extract_tab(self):
        """Setup the extract message tab content"""
        
        # --- Section 1: Stego File Selection ---
        self.grp_stego = ctk.CTkFrame(self.tab_extract)
        self.grp_stego.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        
        ctk.CTkLabel(self.grp_stego, text="Stego Audio File (FLAC)", font=("Roboto", 14, "bold")).pack(anchor="w", padx=10, pady=5)
        
        stego_frame_inner = ctk.CTkFrame(self.grp_stego, fg_color="transparent")
        stego_frame_inner.pack(fill="x", padx=10, pady=(0, 10))
        
        self.entry_stego = ctk.CTkEntry(stego_frame_inner, textvariable=self.stego_file_path, placeholder_text="Path to stego audio...")
        self.entry_stego.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        ctk.CTkButton(stego_frame_inner, text="Browse", width=100, command=self._browse_stego_file).pack(side="right")
        
        # --- Section 2: Decryption ---
        self.grp_decrypt = ctk.CTkFrame(self.tab_extract)
        self.grp_decrypt.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        
        ctk.CTkLabel(self.grp_decrypt, text="Decryption Password:", font=("Roboto", 12)).pack(side="left", padx=10, pady=15)
        self.entry_extract_pass = ctk.CTkEntry(self.grp_decrypt, textvariable=self.extract_password, show="*", width=200)
        self.entry_extract_pass.pack(side="left", padx=10)
        
        self.btn_extract = ctk.CTkButton(
            self.grp_decrypt, 
            text="EXTRACT DATA", 
            command=self._extract_message,
            fg_color="#9b59b6", hover_color="#8e44ad", # Purple accent
            font=("Roboto", 13, "bold"),
            height=35
        )
        self.btn_extract.pack(side="right", padx=10)
        
        # --- Section 3: Result ---
        self.grp_result = ctk.CTkFrame(self.tab_extract)
        self.grp_result.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")
        self.tab_extract.grid_rowconfigure(2, weight=1)
        
        ctk.CTkLabel(self.grp_result, text="Decoded Message", font=("Roboto", 14, "bold")).pack(anchor="w", padx=10, pady=5)
        
        self.extracted_text = ctk.CTkTextbox(self.grp_result, height=150, font=("Consolas", 14))
        self.extracted_text.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self.extracted_text.configure(state="disabled")

        # --- Section 4: Log ---
        self.extract_log = ctk.CTkTextbox(self.tab_extract, height=80, fg_color="#2b2b2b", text_color="#ecf0f1")
        self.extract_log.grid(row=3, column=0, padx=10, pady=(0, 10), sticky="ew")
        self.extract_log.insert("1.0", "System Ready for Extraction...\n")
        self.extract_log.configure(state="disabled")

    def _setup_analysis_tab(self):
        """Setup the analysis tab"""
        
        # --- Info Header ---
        self.info_frame = ctk.CTkFrame(self.tab_analysis, fg_color="transparent")
        self.info_frame.grid(row=0, column=0, padx=10, pady=5, sticky="ew")
        
        ctk.CTkLabel(
            self.info_frame, 
            text="Deep Learning Steganalysis (CNN)", 
            font=("Roboto", 18, "bold")
        ).pack(anchor="w")
        
        ctk.CTkLabel(
            self.info_frame, 
            text="AI-powered analysis (CNN) to detect hidden data.\nUtilizing Spectrogram + SHAP (XAI) to visualize AI attention mechanisms.",
            font=("Roboto", 12), text_color="gray"
        ).pack(anchor="w")

        # --- Section 1: File Selection ---
        self.grp_ana_file = ctk.CTkFrame(self.tab_analysis)
        self.grp_ana_file.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        
        ctk.CTkLabel(self.grp_ana_file, text="Target Audio for Analysis", font=("Roboto", 14, "bold")).pack(anchor="w", padx=10, pady=5)
        
        ana_inner = ctk.CTkFrame(self.grp_ana_file, fg_color="transparent")
        ana_inner.pack(fill="x", padx=10, pady=(0, 10))
        
        self.entry_analysis = ctk.CTkEntry(ana_inner, textvariable=self.analysis_file_path, placeholder_text="Path to suspicious audio...")
        self.entry_analysis.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        ctk.CTkButton(ana_inner, text="Browse", width=100, command=self._browse_analysis_file).pack(side="right")
        
        # --- Section 2: Control Buttons ---
        self.grp_controls = ctk.CTkFrame(self.tab_analysis, fg_color="transparent")
        self.grp_controls.grid(row=2, column=0, padx=10, pady=5, sticky="ew")
        
        self.btn_run_analysis = ctk.CTkButton(
            self.grp_controls,
            text="RUN SECURITY SCAN",
            command=self._run_analysis,
            fg_color="#e74c3c", hover_color="#c0392b", # Red for security/alert
            font=("Roboto", 13, "bold"),
            height=40
        )
        self.btn_run_analysis.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        self.btn_view_graphs = ctk.CTkButton(
            self.grp_controls,
            text="VIEW GRAPHS",
            command=self._view_graphs,
            state="disabled",
            fg_color="#34495e", # Disabled look initially
            height=40
        )
        self.btn_view_graphs.pack(side="right", fill="x", expand=True)

        # --- Section 3: Output Log (Terminal style) ---
        self.grp_term = ctk.CTkFrame(self.tab_analysis)
        self.grp_term.grid(row=3, column=0, padx=10, pady=10, sticky="nsew")
        self.tab_analysis.grid_rowconfigure(3, weight=1)
        
        ctk.CTkLabel(self.grp_term, text="System Logs", font=("Consolas", 12)).pack(anchor="w", padx=10, pady=(5,0))
        
        self.analysis_log = ctk.CTkTextbox(self.grp_term, font=("Consolas", 11), fg_color="#1e1e1e", text_color="#00ff00")
        self.analysis_log.pack(fill="both", expand=True, padx=5, pady=5)
        self.analysis_log.configure(state="disabled")

    # --- ACTION HANDLERS (Button Logic) ---

    def _browse_audio_file(self):
        filename = filedialog.askopenfilename(filetypes=[("FLAC files", "*.flac"), ("All files", "*.*")])
        if filename:
            self.audio_file_path.set(filename)
            self._update_status(f"Selected Source: {os.path.basename(filename)}")
    
    def _browse_stego_file(self):
        filename = filedialog.askopenfilename(filetypes=[("FLAC files", "*.flac"), ("All files", "*.*")])
        if filename:
            self.stego_file_path.set(filename)
            self._update_status(f"Selected Stego: {os.path.basename(filename)}")
            
    def _browse_analysis_file(self):
        filename = filedialog.askopenfilename(filetypes=[("FLAC files", "*.flac"), ("All files", "*.*")])
        if filename:
            self.analysis_file_path.set(filename)

    def _update_status(self, message):
        self.status_label.configure(text=message)
        self.root.update()
    
    def _log_result(self, text_widget, message):
        text_widget.configure(state="normal")
        text_widget.insert("end", message + "\n")
        text_widget.see("end")
        text_widget.configure(state="disabled")
    
    # --- WORKERS (Background threads to prevent GUI freezing) ---
    
    def _embed_message(self):
        if not self.audio_file_path.get():
            messagebox.showerror("Error", "Please select an audio file")
            return
        
        message = self.message_text.get("1.0", "end-1c").strip()
        if not message:
            messagebox.showerror("Error", "Please enter a secret message")
            return
        
        if not self.password.get():
            messagebox.showerror("Error", "Please enter a password")
            return
        
        # Disable button
        self.btn_embed.configure(state="disabled", text="PROCESSING...")
        
        thread = threading.Thread(target=self._embed_worker, args=(message,))
        thread.start()
    
    def _embed_worker(self, message):
        try:
            self._update_status("Encrypting...")
            aes = AESEncryption(self.password.get())
            encrypted_message = aes.encrypt(message)
            
            self._update_status("Embedding...")
            echo = EchoHiding()
            
            input_file = self.audio_file_path.get()
            base_name = os.path.splitext(input_file)[0]
            output_file = f"{base_name}_stego.flac"
            
            result = echo.embed(input_file, encrypted_message, output_file)
            
            if result['status'] == 'success':
                self.root.after(0, lambda: self._log_result(self.embed_log, f"\n[SUCCESS] {result['message']}"))
                self.root.after(0, lambda: self._log_result(self.embed_log, f"Output: {output_file}"))
                self.root.after(0, lambda: self._update_status("Embedding Complete"))
                msg = f"Saved to:\n{os.path.basename(output_file)}\n\nIMPORTANT: Use this new file for extraction!"
                self.root.after(0, lambda: messagebox.showinfo("Success", msg))
            else:
                self.root.after(0, lambda: self._log_result(self.embed_log, f"[ERROR] {result['message']}"))
                self.root.after(0, lambda: messagebox.showerror("Error", result['message']))
                
        except Exception as e:
            self.root.after(0, lambda: self._log_result(self.embed_log, f"[CRITICAL] {str(e)}"))
            self.root.after(0, lambda: messagebox.showerror("Error", str(e)))
        finally:
             self.root.after(0, lambda: self.btn_embed.configure(state="normal", text="EMBED DATA"))

    def _extract_message(self):
        if not self.stego_file_path.get():
            messagebox.showerror("Error", "Please select a stego audio file")
            return
        if not self.extract_password.get():
            messagebox.showerror("Error", "Please enter password")
            return
            
        self.btn_extract.configure(state="disabled", text="PROCESSING...")
        thread = threading.Thread(target=self._extract_worker)
        thread.start()
    
    def _extract_worker(self):
        try:
            self._update_status("Extracting...")
            echo = EchoHiding()
            
            # 1. Extract
            result = echo.extract(self.stego_file_path.get())
            
            if result['status'] == 'success':
                encrypted_msg = result['secret_text']
                quality = result.get('quality', 1.0)
                bits = result.get('bits_extracted', 0)
                delim_found = result.get('delimiter_found', True)
                detected_red = result.get('detected_redundancy', 5)
                
                self._update_status(f"Decrypting (Quality: {quality:.2f})...")
                self.root.after(0, lambda: self._log_result(self.extract_log, f"[INFO] Bits Extracted: {bits}, Quality: {quality:.2f}, Redundancy: {detected_red}x"))
                
                if not delim_found:
                    self.root.after(0, lambda: self._log_result(self.extract_log, "[WARNING] End-of-message marker not found. Data might be corrupted or truncated."))
                
                # Quality warning
                if quality < 0.2: # Raised threshold for warning
                    self.root.after(0, lambda: self._log_result(self.extract_log, "[WARNING] Very low signal quality. Decryption likely to fail."))
                
                # 2. Decrypt
                aes = AESEncryption(self.extract_password.get())
                try:
                    decrypted = aes.decrypt(encrypted_msg)
                    
                    self.root.after(0, lambda: self.extracted_text.configure(state="normal"))
                    self.root.after(0, lambda: self.extracted_text.delete("1.0", "end"))
                    self.root.after(0, lambda: self.extracted_text.insert("1.0", decrypted))
                    self.root.after(0, lambda: self.extracted_text.configure(state="disabled"))
                    
                    # Console debug
                    print(f"DEBUG: Decrypted Result: '{decrypted}' (Len: {len(decrypted)})")
                    
                    self.root.after(0, lambda: self._log_result(self.extract_log, f"[SUCCESS] Message Decrypted!"))
                    self.root.after(0, lambda: self._update_status("Extraction Complete"))
                    
                except Exception as e:
                    # Clearer error message with quality and delimiter context
                    error_msg = "Decryption Failed"
                    tip = "Please check your password or re-embed the message."
                    
                    if not delim_found:
                        error_msg = "EOM Marker Not Found"
                        tip = "The system couldn't find the end-of-message marker. Try a cleaner audio file or re-embed the message."
                    elif quality < 0.2:
                        error_msg = "Signal Too Noisy"
                        tip = "Audio quality is too low for reliable decryption."
                    
                    self.root.after(0, lambda: self._log_result(self.extract_log, f"[FAIL] {error_msg}"))
                    self.root.after(0, lambda: messagebox.showerror(error_msg, tip))
            else:
                 self.root.after(0, lambda: self._log_result(self.extract_log, f"[ERROR] {result['message']}"))
                 
        except Exception as e:
            self.root.after(0, lambda: self._log_result(self.extract_log, f"[CRITICAL] {str(e)}"))
        finally:
            self.root.after(0, lambda: self.btn_extract.configure(state="normal", text="EXTRACT DATA"))

    def _run_analysis(self):
        if not self.analysis_file_path.get():
            messagebox.showerror("Error", "Select audio file first!")
            return

        if messagebox.askyesno("Confirm", "Run Deep Learning Analysis? (Takes ~1 min)"):
            self.btn_run_analysis.configure(state="disabled")
            self.btn_view_graphs.configure(state="disabled")
            self.analysis_log.configure(state="normal")
            self.analysis_log.delete("1.0", "end")
            self.analysis_log.configure(state="disabled")
            
            thread = threading.Thread(target=self._analysis_worker)
            thread.start()


    def _analysis_worker(self):
        try:
            self._update_status("Initializing CNN...")
            target_file = self.analysis_file_path.get()
            
            # Wrapper to send logs to GUI in a thread-safe way
            def log_callback(message):
                self.root.after(0, self._append_log, message)

            # Run the heavy analysis directly in this thread
            run_steganalysis.run_analysis(target_file, log_callback=log_callback)
            
            self.root.after(0, lambda: self._update_status("Analysis Done"))
            self.root.after(0, lambda: messagebox.showinfo("Analysis", "Scan Complete!"))
            self.root.after(0, lambda: self.btn_view_graphs.configure(state="normal", command=self._view_graphs))
                 
        except Exception as err:
            self._append_log(f"\n[ERROR] Analysis failed: {str(err)}\n")
            self.root.after(0, lambda e=err: messagebox.showerror("Error", f"Analysis Failed: {str(e)}"))
        finally:
            self.root.after(0, lambda: self.btn_run_analysis.configure(state="normal"))

    def _append_log(self, text):
        self.analysis_log.configure(state="normal")
        self.analysis_log.insert("end", text)
        self.analysis_log.see("end")
        self.analysis_log.configure(state="disabled")
        
    def _view_graphs(self):
        try:
            import platform
            graphs = ["steganalysis_history.png", "steganalysis_confusion_matrix.png", "steganalysis_explain.png", "steganalysis_diff.png", "steganalysis_report.txt"]
            found = False
            for graph in graphs:
                if os.path.exists(graph):
                    if sys.platform == "win32":
                        os.startfile(graph)
                    elif sys.platform == "darwin":
                        subprocess.call(('open', graph))
                    else:  # Linux and others
                        subprocess.call(('xdg-open', graph))
                    found = True
            if not found:
                 messagebox.showwarning("Warning", "No graphs found.")
        except Exception as e:
            messagebox.showerror("Error", str(e))


def main():
    app = ctk.CTk() # Use CustomTkinter main window
    gui = SteganographyGUI(app)
    app.mainloop()


if __name__ == "__main__":
    main()
