import threading
import customtkinter as ctk
from ui.theme import Theme

class SettingsDialog(ctk.CTkToplevel):
    def __init__(self, master, current_proxy="", current_ua="", current_web_url="https://smart-web-blue.vercel.app"):
        super().__init__(master)
        self.title("Application Settings & Preferences")
        self.geometry("520x540")
        self.resizable(False, False)
        self.configure(fg_color=Theme.BG_BASE)
        
        self.proxy_var = ctk.StringVar(value=current_proxy)
        self.ua_var = ctk.StringVar(value=current_ua)
        self.web_url_var = ctk.StringVar(value=current_web_url)
        self.sanitize_meta_var = ctk.BooleanVar(value=True)
        self.altered_twin_var = ctk.BooleanVar(value=True)
        
        self.result = None
        
        # Center dialog
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (520 // 2)
        y = (self.winfo_screenheight() // 2) - (480 // 2)
        self.geometry(f"+{x}+{y}")
        
        self.setup_ui()
        self.grab_set()

    def setup_ui(self):
        # Container
        container = ctk.CTkFrame(
            self,
            fg_color=Theme.BG_CARD,
            corner_radius=Theme.RADIUS_CARD,
            border_width=1,
            border_color=Theme.BORDER_SUBTLE
        )
        container.pack(expand=True, fill="both", padx=20, pady=20)
        
        # Header
        header = ctk.CTkFrame(container, fg_color="transparent")
        header.pack(fill="x", padx=15, pady=(15, 5))
        
        ctk.CTkLabel(
            header,
            text="⚙️  Preferences & Configurations",
            font=Theme.font_header(),
            text_color=Theme.TEXT_PRIMARY
        ).pack(side="left")
        
        # Tabview
        self.tabview = ctk.CTkTabview(
            container,
            fg_color=Theme.BG_INPUT,
            segmented_button_fg_color=Theme.BG_CARD,
            segmented_button_selected_color=Theme.PRIMARY,
            segmented_button_selected_hover_color=Theme.PRIMARY_HOVER,
            segmented_button_unselected_color=Theme.BG_INPUT,
            segmented_button_unselected_hover_color=Theme.SECONDARY,
            text_color=Theme.TEXT_PRIMARY
        )
        self.tabview.pack(fill="both", expand=True, padx=15, pady=10)
        
        tab_net = self.tabview.add("Network & Proxy")
        tab_sec = self.tabview.add("Privacy & Workflow")
        tab_ui = self.tabview.add("Appearance")
        
        # --- TAB 1: Network & Proxy ---
        ctk.CTkLabel(
            tab_net,
            text="Proxy Configuration (HTTP / SOCKS5)",
            font=Theme.font_body_bold(),
            text_color=Theme.TEXT_SECONDARY
        ).pack(anchor="w", padx=10, pady=(10, 4))
        
        proxy_row = ctk.CTkFrame(tab_net, fg_color="transparent")
        proxy_row.pack(fill="x", padx=10, pady=(0, 10))
        
        self.proxy_entry = ctk.CTkEntry(
            proxy_row,
            textvariable=self.proxy_var,
            placeholder_text="http://user:pass@host:port or host:port",
            fg_color=Theme.BG_CARD,
            border_color=Theme.BORDER_SUBTLE,
            text_color=Theme.TEXT_PRIMARY,
            height=34
        )
        self.proxy_entry.pack(side="left", fill="x", expand=True)
        
        self.btn_test_proxy = ctk.CTkButton(
            proxy_row,
            text="Test Latency",
            width=90,
            height=34,
            fg_color=Theme.SECONDARY,
            hover_color=Theme.SECONDARY_HOVER,
            command=self.test_proxy_connection
        )
        self.btn_test_proxy.pack(side="left", padx=(8, 0))
        
        self.lbl_proxy_status = ctk.CTkLabel(
            tab_net,
            text="Direct connection (No proxy active)",
            font=Theme.font_small(),
            text_color=Theme.TEXT_MUTED
        )
        self.lbl_proxy_status.pack(anchor="w", padx=10, pady=(0, 10))
        
        ctk.CTkLabel(
            tab_net,
            text="Default User Agent",
            font=Theme.font_body_bold(),
            text_color=Theme.TEXT_SECONDARY
        ).pack(anchor="w", padx=10, pady=(5, 4))
        
        self.ua_entry = ctk.CTkEntry(
            tab_net,
            textvariable=self.ua_var,
            placeholder_text="Mozilla/5.0 (Windows NT 10.0; Win64; x64)...",
            fg_color=Theme.BG_CARD,
            border_color=Theme.BORDER_SUBTLE,
            text_color=Theme.TEXT_PRIMARY,
            height=34
        )
        self.ua_entry.pack(fill="x", padx=10, pady=(0, 10))

        # SmartWeb API Base URL
        ctk.CTkLabel(
            tab_net,
            text="SmartWeb Website API Endpoint",
            font=Theme.font_body_bold(),
            text_color=Theme.TEXT_SECONDARY
        ).pack(anchor="w", padx=10, pady=(5, 4))

        web_row = ctk.CTkFrame(tab_net, fg_color="transparent")
        web_row.pack(fill="x", padx=10, pady=(0, 6))

        self.web_entry = ctk.CTkEntry(
            web_row,
            textvariable=self.web_url_var,
            placeholder_text="https://smart-web-blue.vercel.app or http://localhost:3000",
            fg_color=Theme.BG_CARD,
            border_color=Theme.BORDER_SUBTLE,
            text_color=Theme.TEXT_PRIMARY,
            height=34
        )
        self.web_entry.pack(side="left", fill="x", expand=True)

        preset_frame = ctk.CTkFrame(tab_net, fg_color="transparent")
        preset_frame.pack(fill="x", padx=10, pady=(0, 10))

        ctk.CTkButton(
            preset_frame,
            text="Live Vercel",
            width=80,
            height=24,
            font=Theme.font_small(),
            fg_color=Theme.BG_INPUT,
            hover_color=Theme.SECONDARY,
            command=lambda: self.web_url_var.set("https://smart-web-blue.vercel.app")
        ).pack(side="left", padx=(0, 5))

        ctk.CTkButton(
            preset_frame,
            text="Localhost:3000",
            width=95,
            height=24,
            font=Theme.font_small(),
            fg_color=Theme.BG_INPUT,
            hover_color=Theme.SECONDARY,
            command=lambda: self.web_url_var.set("http://localhost:3000")
        ).pack(side="left")
        
        # --- TAB 2: Privacy & Workflow ---
        ctk.CTkCheckBox(
            tab_sec,
            text="Strip and sanitize EXIF/Camera metadata automatically",
            variable=self.sanitize_meta_var,
            font=Theme.font_body(),
            text_color=Theme.TEXT_PRIMARY,
            fg_color=Theme.PRIMARY
        ).pack(anchor="w", padx=15, pady=(15, 8))
        
        ctk.CTkCheckBox(
            tab_sec,
            text="Generate altered twin image for anti-fingerprint injection",
            variable=self.altered_twin_var,
            font=Theme.font_body(),
            text_color=Theme.TEXT_PRIMARY,
            fg_color=Theme.PRIMARY
        ).pack(anchor="w", padx=15, pady=8)
        
        # --- TAB 3: Appearance ---
        ctk.CTkLabel(
            tab_ui,
            text="Theme Mode",
            font=Theme.font_body_bold(),
            text_color=Theme.TEXT_SECONDARY
        ).pack(anchor="w", padx=15, pady=(15, 5))
        
        self.theme_menu = ctk.CTkOptionMenu(
            tab_ui,
            values=["Dark", "Light", "System"],
            fg_color=Theme.BG_CARD,
            button_color=Theme.SECONDARY,
            button_hover_color=Theme.SECONDARY_HOVER
        )
        self.theme_menu.pack(anchor="w", padx=15, pady=(0, 15))
        
        # --- Footer Actions ---
        footer = ctk.CTkFrame(container, fg_color="transparent")
        footer.pack(fill="x", padx=15, pady=(0, 15))
        
        ctk.CTkButton(
            footer,
            text="Save Settings",
            fg_color=Theme.PRIMARY,
            hover_color=Theme.PRIMARY_HOVER,
            width=110,
            height=32,
            font=Theme.font_body_bold(),
            command=self.save
        ).pack(side="right", padx=(8, 0))
        
        ctk.CTkButton(
            footer,
            text="Cancel",
            fg_color=Theme.BG_INPUT,
            hover_color=Theme.SECONDARY,
            width=80,
            height=32,
            font=Theme.font_body(),
            command=self.destroy
        ).pack(side="right")

    def test_proxy_connection(self):
        proxy = self.proxy_var.get().strip()
        if not proxy:
            self.lbl_proxy_status.configure(text="Please enter a proxy first.", text_color=Theme.WARNING)
            return
            
        self.lbl_proxy_status.configure(text="Testing connection...", text_color=Theme.INFO)
        self.btn_test_proxy.configure(state="disabled")
        
        def run_test():
            import time
            import requests
            try:
                proxies = {"http": proxy, "https": proxy}
                t0 = time.time()
                res = requests.get("https://httpbin.org/ip", proxies=proxies, timeout=6)
                latency_ms = int((time.time() - t0) * 1000)
                ip = res.json().get("origin", "Unknown")
                self.after(0, lambda: self._on_test_done(True, f"Connected! IP: {ip} ({latency_ms}ms)"))
            except Exception as e:
                self.after(0, lambda: self._on_test_done(False, f"Connection Failed: {str(e)[:40]}..."))
                
        threading.Thread(target=run_test, daemon=True).start()
        
    def _on_test_done(self, success, msg):
        self.btn_test_proxy.configure(state="normal")
        color = Theme.SUCCESS if success else Theme.DANGER
        self.lbl_proxy_status.configure(text=msg, text_color=color)

    def save(self):
        self.result = {
            "proxy": self.proxy_var.get().strip(),
            "user_agent": self.ua_var.get().strip(),
            "website_url": self.web_url_var.get().strip(),
            "sanitize_metadata": self.sanitize_meta_var.get(),
            "altered_twin": self.altered_twin_var.get(),
            "theme": self.theme_menu.get()
        }
        self.destroy()
