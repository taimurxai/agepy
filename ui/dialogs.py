import threading
import customtkinter as ctk
from ui.theme import Theme

class AuthLoginDialog(ctk.CTkToplevel):
    def __init__(self, parent, auth_service):
        super().__init__(parent)
        self.auth_service = auth_service
        self.title("AgeSmart - Enterprise Login")
        self.geometry("440x520")
        self.resizable(False, False)
        self.configure(fg_color=Theme.BG_BASE)
        self.is_authenticated = False
        
        # Center on screen
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (440 // 2)
        y = (self.winfo_screenheight() // 2) - (520 // 2)
        self.geometry(f"+{x}+{y}")
        
        self.setup_ui()
        self.grab_set()

    def setup_ui(self):
        # Center Card Container
        self.card = ctk.CTkFrame(
            self, 
            fg_color=Theme.BG_CARD, 
            corner_radius=Theme.RADIUS_CARD + 2,
            border_width=1,
            border_color=Theme.BORDER_SUBTLE
        )
        self.card.pack(expand=True, fill="both", padx=25, pady=25)
        
        # --- Brand Header ---
        header_frame = ctk.CTkFrame(self.card, fg_color="transparent")
        header_frame.pack(fill="x", padx=25, pady=(20, 15))
        
        icon_label = ctk.CTkLabel(
            header_frame,
            text="🛡️",
            font=ctk.CTkFont(size=32)
        )
        icon_label.pack(pady=(0, 4))
        
        brand_label = ctk.CTkLabel(
            header_frame,
            text="AgeSmart Enterprise",
            font=Theme.font_title(),
            text_color=Theme.TEXT_PRIMARY
        )
        brand_label.pack()
        
        sub_label = ctk.CTkLabel(
            header_frame,
            text="Secure Identity & Verification Suite",
            font=Theme.font_small(),
            text_color=Theme.TEXT_MUTED
        )
        sub_label.pack()
        
        # --- Error / Info Banner ---
        self.banner = ctk.CTkLabel(
            self.card,
            text="",
            font=Theme.font_small(),
            text_color=Theme.DANGER,
            fg_color="transparent",
            corner_radius=4,
            height=20
        )
        self.banner.pack(fill="x", padx=25, pady=(0, 10))

        # --- Form Fields ---
        form_frame = ctk.CTkFrame(self.card, fg_color="transparent")
        form_frame.pack(fill="x", padx=25)
        
        # Username / Email
        ctk.CTkLabel(
            form_frame,
            text="Email or Username",
            font=Theme.font_body_bold(),
            text_color=Theme.TEXT_SECONDARY
        ).pack(anchor="w", pady=(0, 4))
        
        self.username_entry = ctk.CTkEntry(
            form_frame,
            placeholder_text="user@domain.com",
            fg_color=Theme.BG_INPUT,
            border_color=Theme.BORDER_SUBTLE,
            text_color=Theme.TEXT_PRIMARY,
            height=38,
            corner_radius=Theme.RADIUS_INPUT,
            font=Theme.font_body()
        )
        self.username_entry.pack(fill="x", pady=(0, 12))
        self.username_entry.bind("<Enter>", lambda e: self.username_entry.configure(border_color=Theme.PRIMARY))
        self.username_entry.bind("<Leave>", lambda e: self.username_entry.configure(border_color=Theme.BORDER_SUBTLE))
        
        # Password
        ctk.CTkLabel(
            form_frame,
            text="Password",
            font=Theme.font_body_bold(),
            text_color=Theme.TEXT_SECONDARY
        ).pack(anchor="w", pady=(0, 4))
        
        pass_container = ctk.CTkFrame(form_frame, fg_color="transparent")
        pass_container.pack(fill="x", pady=(0, 10))
        
        self.password_entry = ctk.CTkEntry(
            pass_container,
            placeholder_text="••••••••••••",
            show="*",
            fg_color=Theme.BG_INPUT,
            border_color=Theme.BORDER_SUBTLE,
            text_color=Theme.TEXT_PRIMARY,
            height=38,
            corner_radius=Theme.RADIUS_INPUT,
            font=Theme.font_body()
        )
        self.password_entry.pack(side="left", fill="x", expand=True)
        self.password_entry.bind("<Enter>", lambda e: self.password_entry.configure(border_color=Theme.PRIMARY))
        self.password_entry.bind("<Leave>", lambda e: self.password_entry.configure(border_color=Theme.BORDER_SUBTLE))
        
        # Toggle Password Visibility
        self.is_pwd_visible = False
        self.btn_toggle_pwd = ctk.CTkButton(
            pass_container,
            text="👁",
            width=36,
            height=38,
            fg_color=Theme.BG_INPUT,
            hover_color=Theme.SECONDARY,
            border_color=Theme.BORDER_SUBTLE,
            border_width=1,
            corner_radius=Theme.RADIUS_INPUT,
            command=self.toggle_password_visibility
        )
        self.btn_toggle_pwd.pack(side="left", padx=(5, 0))
        
        # Remember Me Checkbox
        self.remember_var = ctk.BooleanVar(value=True)
        self.remember_cb = ctk.CTkCheckBox(
            form_frame,
            text="Remember credentials",
            variable=self.remember_var,
            font=Theme.font_small(),
            text_color=Theme.TEXT_SECONDARY,
            checkbox_width=18,
            checkbox_height=18,
            corner_radius=4,
            fg_color=Theme.PRIMARY,
            hover_color=Theme.PRIMARY_HOVER
        )
        self.remember_cb.pack(anchor="w", pady=(4, 15))
        
        # --- Login Action Button ---
        self.login_btn = ctk.CTkButton(
            self.card,
            text="Sign In to Enterprise",
            command=self.start_login_thread,
            height=40,
            corner_radius=Theme.RADIUS_BUTTON,
            fg_color=Theme.PRIMARY,
            hover_color=Theme.PRIMARY_HOVER,
            font=Theme.font_body_bold()
        )
        self.login_btn.pack(fill="x", padx=25, pady=(0, 15))
        
        # Enter key triggers login
        self.bind("<Return>", lambda e: self.start_login_thread())

    def toggle_password_visibility(self):
        self.is_pwd_visible = not self.is_pwd_visible
        if self.is_pwd_visible:
            self.password_entry.configure(show="")
            self.btn_toggle_pwd.configure(text="🔒")
        else:
            self.password_entry.configure(show="*")
            self.btn_toggle_pwd.configure(text="👁")

    def show_error(self, message: str):
        self.banner.configure(text=message, text_color=Theme.DANGER, fg_color=Theme.DANGER_BG)

    def show_info(self, message: str):
        self.banner.configure(text=message, text_color=Theme.INFO, fg_color=Theme.INFO_BG)

    def start_login_thread(self):
        email = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        
        if not email or not password:
            self.show_error("Please enter both username/email and password.")
            return
            
        self.show_info("Authenticating with enterprise server...")
        self.login_btn.configure(state="disabled", text="Authenticating...")
        
        # Thread-safe result container
        self._login_result = None
        
        threading.Thread(
            target=self._async_login,
            args=(email, password),
            daemon=True
        ).start()
        
        # Poll for result from main thread (avoids 'main thread is not in main loop')
        self._poll_login_result()

    def _async_login(self, email, password):
        try:
            success, msg = self.auth_service.login(email, password)
            if success and hasattr(self.auth_service, 'verify_device'):
                # Enforce device binding check after login
                dev_success, dev_msg = self.auth_service.verify_device()
                if not dev_success:
                    self._login_result = (False, f"Device Authorization Failed: {dev_msg}")
                    return
            self._login_result = (success, msg)
        except Exception as e:
            self._login_result = (False, str(e))

    def _poll_login_result(self):
        """Check if background login thread has posted a result yet."""
        if self._login_result is None:
            # Not ready yet — check again in 100ms
            try:
                self.after(100, self._poll_login_result)
            except Exception:
                pass
            return
        
        success, msg = self._login_result
        if success:
            self.is_authenticated = True
            self.destroy()
        else:
            self.show_error(f"Sign in failed: {msg}")
            self.login_btn.configure(state="normal", text="Sign In to Enterprise")
