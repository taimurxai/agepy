import os
import sys
import threading
import customtkinter as ctk
from core.workflow import WorkflowEvent
from ui.theme import Theme
from ui.widgets.media_card import MediaCard
from ui.widgets.stepper import WorkflowStepper
from ui.widgets.console_log import ProConsole

try:
    from tkinterdnd2 import TkinterDnD, DND_FILES
except ImportError:
    TkinterDnD = None
    DND_FILES = None

class TkinterDnD_CTk(ctk.CTk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if TkinterDnD:
            try:
                self.TkdndVersion = TkinterDnD._require(self)
            except Exception:
                pass

if TkinterDnD:
    class MainWindowBase(TkinterDnD_CTk, TkinterDnD.DnDWrapper): pass
else:
    class MainWindowBase(ctk.CTk): pass

class MainWindow(MainWindowBase):
    def __init__(self, workflow, history_service, user_info=None, smartweb_service=None):
        super().__init__()
        self.workflow = workflow
        self.history_service = history_service
        self.user_info = user_info or {}
        self.smartweb_service = smartweb_service
        
        self.selected_files = {"ID": None, "Selfie": None, "Video": None}
        self.input_entries = {}
        
        # Window Configuration
        self.title("AgeSmart Enterprise - Account Verification Suite")
        self.geometry("1200x750")
        self.minsize(360, 640)
        
        ctk.set_appearance_mode("dark")
        self.configure(fg_color=Theme.BG_BASE)
        
        # Start fully transparent for fade-in
        self.attributes("-alpha", 0.0)
        
        self.setup_ui()
        if self.workflow:
            self.workflow.on_event(self.on_workflow_event)
            
        self.fade_in()
            
    def fade_in(self, alpha=0.0):
        alpha += 0.05
        if alpha < 1.0:
            self.attributes("-alpha", alpha)
            self.after(20, self.fade_in, alpha)
        else:
            self.attributes("-alpha", 1.0)
            
    def setup_ui(self):
        # 1. Global Header Bar
        self.setup_header()
        
        # 2. Main Tabview Navigation
        self.tabview = ctk.CTkTabview(
            self,
            fg_color=Theme.BG_BASE,
            segmented_button_fg_color=Theme.BG_CARD,
            segmented_button_selected_color=Theme.PRIMARY,
            segmented_button_selected_hover_color=Theme.PRIMARY_HOVER,
            segmented_button_unselected_color=Theme.BG_SURFACE,
            segmented_button_unselected_hover_color=Theme.SECONDARY,
            text_color=Theme.TEXT_PRIMARY,
            corner_radius=Theme.RADIUS_CARD
        )
        self.tabview.pack(fill="both", expand=True, padx=6, pady=(0, 6))
        
        # Add Tabs
        self.tab_studio = self.tabview.add("🚀 Verification Studio")
        self.tab_history = self.tabview.add("📊 History & Audit Log")
        self.tab_network = self.tabview.add("🌐 Network & Proxy")
        
        # Setup individual tab content
        self.setup_studio_tab(self.tab_studio)
        self.setup_history_tab(self.tab_history)
        self.setup_network_tab(self.tab_network)
        
    def setup_header(self):
        header = ctk.CTkFrame(self, fg_color=Theme.BG_SURFACE, height=48, corner_radius=0, border_width=1, border_color=Theme.BORDER_SUBTLE)
        header.pack(fill="x", padx=0, pady=(0, 4))
        header.pack_propagate(False)
        
        # Left: Brand Logo & Title
        left_box = ctk.CTkFrame(header, fg_color="transparent")
        left_box.pack(side="left", padx=10)
        
        ctk.CTkLabel(left_box, text="🛡️", font=ctk.CTkFont(size=22)).pack(side="left", padx=(0, 8))
        ctk.CTkLabel(left_box, text="AgeSmart Enterprise", font=Theme.font_header(), text_color=Theme.TEXT_PRIMARY).pack(side="left")
        
        ver_badge = ctk.CTkLabel(
            left_box,
            text="v2.0.0 PRO",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=9, weight="bold"),
            text_color=Theme.PRIMARY,
            fg_color=Theme.BG_CARD,
            corner_radius=4,
            padx=6,
            pady=2
        )
        ver_badge.pack(side="left", padx=(10, 0))
        
        # Center: Live System & Proxy Indicators
        center_box = ctk.CTkFrame(header, fg_color="transparent")
        center_box.pack(side="left", expand=True)
        
        self.lbl_server_status = ctk.CTkLabel(
            center_box,
            text="● Online (Supabase Connected)",
            font=Theme.font_small(),
            text_color=Theme.SUCCESS
        )
        self.lbl_server_status.pack(side="left", padx=15)
        
        self.lbl_header_proxy = ctk.CTkLabel(
            center_box,
            text="🌐 Direct Connection",
            font=Theme.font_small(),
            text_color=Theme.TEXT_SECONDARY
        )
        self.lbl_header_proxy.pack(side="left", padx=15)
        
        # Right: User info & Action controls
        right_box = ctk.CTkFrame(header, fg_color="transparent")
        right_box.pack(side="right", padx=15)
        
        username = self.user_info.get("email", "Enterprise User")
        self.lbl_header_user = ctk.CTkLabel(
            right_box,
            text=f"👤 {username}",
            font=Theme.font_small(),
            text_color=Theme.TEXT_PRIMARY
        )
        self.lbl_header_user.pack(side="left", padx=(0, 10))
        
        ctk.CTkButton(
            right_box,
            text="⚙️",
            width=32,
            height=30,
            fg_color=Theme.BG_CARD,
            hover_color=Theme.SECONDARY,
            font=ctk.CTkFont(size=14),
            command=self.open_settings
        ).pack(side="left", padx=(0, 6))
        
        ctk.CTkButton(
            right_box,
            text="Sign Out",
            width=70,
            height=30,
            fg_color=Theme.DANGER_BG,
            hover_color=Theme.DANGER_HOVER,
            text_color=Theme.DANGER,
            font=Theme.font_small(),
            command=self.do_logout
        ).pack(side="left")

    def setup_studio_tab(self, tab):
        tab.grid_columnconfigure(0, weight=3) # Left (Credentials)
        tab.grid_columnconfigure(1, weight=6) # Middle (Media & Logs)
        tab.grid_columnconfigure(2, weight=2) # Right (Telemetry & Profile)
        tab.grid_rowconfigure(0, weight=1)
        
        # ==========================================
        # 1. LEFT COLUMN: Session Credentials & Form
        # ==========================================
        left_col = ctk.CTkFrame(
            tab, 
            fg_color=Theme.BG_CARD, 
            corner_radius=Theme.RADIUS_CARD,
            border_width=1,
            border_color=Theme.BORDER_SUBTLE
        )
        left_col.grid(row=0, column=0, sticky="nsew", padx=3, pady=3)
        
        ctk.CTkLabel(
            left_col, 
            text="SESSION & CREDENTIALS", 
            font=Theme.font_sub(), 
            text_color=Theme.TEXT_SECONDARY
        ).pack(anchor="w", padx=8, pady=(8, 4))
        
        # Form Fields
        self.create_smart_input(left_col, "Verification URL", "Target verification URL", "URL")
        self.create_smart_input(left_col, "User agent", "Mozilla/5.0...", "UserAgent")
        self.create_smart_input(left_col, "JSESSIONID", "Valid session ID token", "JSESSIONID")
        self.create_smart_input(left_col, "XSRF-TOKEN", "CSRF verification token", "XSRF-TOKEN")
        self.create_smart_input(left_col, "DOB", "YYYY-MM-DD", "DOB")
        self.create_smart_input(left_col, "Timecodes", "Video timecodes", "Timecodes")
        if "Timecodes" in self.input_entries:
            self.input_entries["Timecodes"].insert(0, "10")
        
        # Separator
        ctk.CTkFrame(left_col, fg_color=Theme.BORDER_SUBTLE, height=1).pack(fill="x", padx=8, pady=8)
        
        # Execution Controls
        self.btn_start = ctk.CTkButton(
            left_col,
            text="⚡ Start Auto Verification",
            height=36,
            font=Theme.font_body_bold(),
            fg_color=Theme.PRIMARY,
            hover_color=Theme.PRIMARY_HOVER,
            corner_radius=Theme.RADIUS_BUTTON,
            command=self.start_workflow
        )
        self.btn_start.pack(fill="x", padx=8, pady=(0, 4))
        

        
        # ==========================================
        # 2. MIDDLE COLUMN: Stepper, Media & Console
        # ==========================================
        mid_col = ctk.CTkFrame(tab, fg_color="transparent")
        mid_col.grid(row=0, column=1, sticky="nsew", padx=3, pady=3)
        mid_col.grid_rowconfigure(0, weight=0) # Stepper
        mid_col.grid_rowconfigure(1, weight=3) # Media Cards
        mid_col.grid_rowconfigure(2, weight=4) # Console Log
        mid_col.grid_columnconfigure(0, weight=1)
        
        # 1. Visual Stepper
        self.stepper = WorkflowStepper(mid_col)
        self.stepper.grid(row=0, column=0, sticky="ew", pady=(0, 4))
        
        # 2. Media Upload Cards Row
        self.media_container = ctk.CTkFrame(mid_col, fg_color="transparent")
        self.media_container.grid(row=1, column=0, sticky="nsew", pady=(0, 4))
        self.media_container.grid_columnconfigure((0, 1, 2), weight=1)
        self.media_container.grid_rowconfigure(0, weight=1)
        
        self.card_id = MediaCard(
            self.media_container, 
            card_type="ID", 
            title="ID Document", 
            subtitle="JPG, PNG • Front ID",
            on_file_selected=self.on_media_selected,
            on_file_cleared=self.on_media_cleared
        )
        self.card_id.grid(row=0, column=0, sticky="nsew", padx=(0, 2))
        
        self.card_selfie = MediaCard(
            self.media_container, 
            card_type="Selfie", 
            title="Biometric Selfie", 
            subtitle="JPG, PNG • Clear face",
            on_file_selected=self.on_media_selected,
            on_file_cleared=self.on_media_cleared
        )
        self.card_selfie.grid(row=0, column=1, sticky="nsew", padx=2)
        
        self.card_video = MediaCard(
            self.media_container, 
            card_type="Video", 
            title="Liveness Video", 
            subtitle="MP4, MOV • Max 15s",
            on_file_selected=self.on_media_selected,
            on_file_cleared=self.on_media_cleared
        )
        self.card_video.grid(row=0, column=2, sticky="nsew", padx=(2, 0))
        
        # 3. Pro Console Terminal
        self.console = ProConsole(mid_col)
        self.console.grid(row=2, column=0, sticky="nsew", pady=(0, 0))
        self.console.log("AgeSmart Enterprise Suite initialized successfully.", "SUCCESS")
        
        # ==========================================
        # 3. RIGHT COLUMN: Telemetry & Account
        # ==========================================
        right_col = ctk.CTkFrame(tab, fg_color="transparent")
        right_col.grid(row=0, column=2, sticky="nsew", padx=3, pady=3)
        
        # Account Card
        acc_card = ctk.CTkFrame(right_col, fg_color=Theme.BG_CARD, corner_radius=Theme.RADIUS_CARD, border_width=1, border_color=Theme.BORDER_SUBTLE)
        acc_card.pack(fill="x", pady=(0, 6), ipady=2)
        
        ctk.CTkLabel(acc_card, text="ACCOUNT & LICENSE", font=Theme.font_sub(), text_color=Theme.TEXT_SECONDARY).pack(anchor="w", padx=8, pady=(6, 4))
        
        username = self.user_info.get("email", "Enterprise User")
        self.lbl_acc_user = ctk.CTkLabel(acc_card, text=f"User: {username}", font=Theme.font_body(), text_color=Theme.TEXT_PRIMARY)
        self.lbl_acc_user.pack(anchor="w", padx=8, pady=0)
        
        tier_row = ctk.CTkFrame(acc_card, fg_color="transparent")
        tier_row.pack(fill="x", padx=8, pady=0)
        ctk.CTkLabel(tier_row, text="Plan:", font=Theme.font_body(), text_color=Theme.TEXT_MUTED).pack(side="left")
        ctk.CTkLabel(tier_row, text="Enterprise Unlimited", font=Theme.font_body_bold(), text_color=Theme.TEXT_ACCENT).pack(side="left", padx=5)
        
        status_row = ctk.CTkFrame(acc_card, fg_color="transparent")
        status_row.pack(fill="x", padx=8, pady=0)
        ctk.CTkLabel(status_row, text="Status:", font=Theme.font_body(), text_color=Theme.TEXT_MUTED).pack(side="left")
        ctk.CTkLabel(status_row, text="Active ✓", font=Theme.font_body_bold(), text_color=Theme.SUCCESS).pack(side="left", padx=5)
        
        ctk.CTkButton(
            acc_card,
            text="Manage Subscription",
            font=Theme.font_small(),
            height=24,
            fg_color=Theme.BG_INPUT,
            hover_color=Theme.SECONDARY,
            command=lambda: self.console.log("Subscription management opened.", "INFO")
        ).pack(fill="x", padx=8, pady=(6, 8))
        
        # Security & Integrity Card
        sec_card = ctk.CTkFrame(right_col, fg_color=Theme.BG_CARD, corner_radius=Theme.RADIUS_CARD, border_width=1, border_color=Theme.BORDER_SUBTLE)
        sec_card.pack(fill="x", pady=(0, 6), ipady=2)
        
        ctk.CTkLabel(sec_card, text="SYSTEM INTEGRITY", font=Theme.font_sub(), text_color=Theme.TEXT_SECONDARY).pack(anchor="w", padx=8, pady=(6, 4))
        
        self.create_status_pill(sec_card, "Hardware Binding", "Verified ✓", Theme.SUCCESS)
        self.create_status_pill(sec_card, "Killswitch Gate", "Passed ✓", Theme.SUCCESS)
        self.create_status_pill(sec_card, "Metadata Sanitizer", "Armed ✓", Theme.SUCCESS)
        self.create_status_pill(sec_card, "Twin Generator", "Armed ✓", Theme.SUCCESS)
        
        # Support / Help Card
        sup_card = ctk.CTkFrame(right_col, fg_color=Theme.BG_CARD, corner_radius=Theme.RADIUS_CARD, border_width=1, border_color=Theme.BORDER_SUBTLE)
        sup_card.pack(fill="x", ipady=2)
        
        ctk.CTkLabel(sup_card, text="HELP & SUPPORT", font=Theme.font_sub(), text_color=Theme.TEXT_SECONDARY).pack(anchor="w", padx=8, pady=(6, 2))
        ctk.CTkLabel(sup_card, text="Enterprise 24/7 Priority Support", font=Theme.font_small(), text_color=Theme.TEXT_MUTED).pack(anchor="w", padx=8, pady=0)
        
        ctk.CTkButton(
            sup_card,
            text="💬 Contact Desk",
            font=Theme.font_small(),
            height=24,
            fg_color=Theme.PRIMARY,
            hover_color=Theme.PRIMARY_HOVER,
            command=lambda: self.console.log("Support contact requested. Telegram: @agesmart_support", "INFO")
        ).pack(fill="x", padx=8, pady=(6, 8))

    def create_smart_input(self, parent, label_text, placeholder, key):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", padx=8, pady=2)
        
        # Label
        ctk.CTkLabel(
            frame, 
            text=label_text, 
            font=Theme.font_small(), 
            text_color=Theme.TEXT_SECONDARY
        ).pack(anchor="w", pady=0)
        
        # Row with Entry + Paste + Clear
        row = ctk.CTkFrame(frame, fg_color="transparent")
        row.pack(fill="x")
        
        entry = ctk.CTkEntry(
            row,
            placeholder_text=placeholder,
            fg_color=Theme.BG_INPUT,
            border_color=Theme.BORDER_SUBTLE,
            text_color=Theme.TEXT_PRIMARY,
            height=28,
            font=Theme.font_body(),
            corner_radius=Theme.RADIUS_INPUT
        )
        entry.pack(side="left", fill="x", expand=True)
        
        # Hover effect
        entry.bind("<Enter>", lambda e, ent=entry: ent.configure(border_color=Theme.PRIMARY))
        entry.bind("<Leave>", lambda e, ent=entry: ent.configure(border_color=Theme.BORDER_SUBTLE))
        
        self.input_entries[key] = entry
        
        # Paste Button
        def paste_val():
            try:
                clip = self.clipboard_get().strip()
                if clip:
                    entry.delete(0, "end")
                    entry.insert(0, clip)
                    self.console.log(f"Pasted content into {label_text}.", "INFO")
            except Exception:
                pass
                
        btn_paste = ctk.CTkButton(
            row,
            text="📋",
            width=24,
            height=28,
            fg_color=Theme.BG_INPUT,
            hover_color=Theme.SECONDARY,
            border_width=1,
            border_color=Theme.BORDER_SUBTLE,
            corner_radius=Theme.RADIUS_INPUT,
            command=paste_val
        )
        btn_paste.pack(side="left", padx=(2, 0))
        
        # Clear Button
        btn_clear = ctk.CTkButton(
            row,
            text="✕",
            width=24,
            height=28,
            fg_color=Theme.BG_INPUT,
            hover_color=Theme.DANGER_HOVER,
            border_width=1,
            border_color=Theme.BORDER_SUBTLE,
            corner_radius=Theme.RADIUS_INPUT,
            command=lambda: entry.delete(0, "end")
        )
        btn_clear.pack(side="left", padx=(2, 0))

    def create_status_pill(self, parent, title, status_text, color):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", padx=8, pady=1)
        ctk.CTkLabel(row, text=title, font=Theme.font_small(), text_color=Theme.TEXT_MUTED).pack(side="left")
        ctk.CTkLabel(row, text=status_text, font=Theme.font_small(), text_color=color).pack(side="right")

    def on_media_selected(self, card_type, file_path):
        self.selected_files[card_type] = file_path
        self.console.log(f"Loaded {card_type}: {os.path.basename(file_path)}", "INFO")
        self.check_ready_state()

    def on_media_cleared(self, card_type):
        self.selected_files[card_type] = None
        self.console.log(f"Cleared {card_type} file.", "INFO")
        self.check_ready_state()
        
    def check_ready_state(self):
        doc = self.selected_files.get("ID")
        selfie = self.selected_files.get("Selfie")
        vid = self.selected_files.get("Video")
        
        if all([doc, selfie, vid]):
            # Start pulsing if not already pulsing
            if not getattr(self, '_is_pulsing', False):
                self._is_pulsing = True
                self._pulse_direction = 1
                self.pulse_start_button()
        else:
            self._is_pulsing = False
            self.btn_start.configure(fg_color=Theme.PRIMARY)

    def pulse_start_button(self):
        if getattr(self, '_is_pulsing', False) and self.btn_start.cget("state") != "disabled":
            # Simple toggle between PRIMARY and PRIMARY_HOVER for pulsing
            current_color = self.btn_start.cget("fg_color")
            if current_color == Theme.PRIMARY:
                self.btn_start.configure(fg_color=Theme.PRIMARY_ACTIVE)
            else:
                self.btn_start.configure(fg_color=Theme.PRIMARY)
            self.after(600, self.pulse_start_button)
        else:
            self.btn_start.configure(fg_color=Theme.PRIMARY)

    def reset_form(self):
        for entry in self.input_entries.values():
            entry.delete(0, "end")
        self.card_id.clear_file()
        self.card_selfie.clear_file()
        self.card_video.clear_file()
        self.media_container.grid() # Show media cards again
        self.media_container.master.grid_rowconfigure(1, weight=3) # Restore space for media cards
        self.stepper.reset()
        self.console.log("Form and media selections reset.", "INFO")

    def start_workflow(self):
        doc = self.selected_files.get("ID")
        selfie = self.selected_files.get("Selfie")
        vid = self.selected_files.get("Video")
        
        if not all([doc, selfie, vid]):
            self.console.log("Validation Error: Please select ID, Selfie, and Video files first.", "ERROR")
            return
            
        token = self.input_entries.get("XSRF-TOKEN").get().strip() if "XSRF-TOKEN" in self.input_entries else ""
        dob = self.input_entries.get("DOB").get().strip() if "DOB" in self.input_entries else ""
        timecodes_val = self.input_entries.get("Timecodes").get().strip() if "Timecodes" in self.input_entries else ""
        
        if not token:
            self.console.log("Validation Error: Verification token (XSRF-TOKEN) is missing.", "ERROR")
            return

        self.btn_start.configure(state="disabled")
        self._is_pulsing = False
        self.btn_start.configure(fg_color=Theme.SECONDARY)
        self.media_container.grid_remove() # Hide media cards
        self.media_container.master.grid_rowconfigure(1, weight=0) # Remove space for media cards
        
        self.stepper.reset()
        self.stepper.set_step_active(0, "Init & CSRF")
        self.console.log("Initializing Smart Verification Pipeline...", "INFO")
        
        self.workflow.start_workflow(doc, selfie, vid, token, dob, timecodes_val)

    def on_workflow_event(self, event_name, data):
        self.after(0, self._handle_event_ui, event_name, data)

    def _handle_event_ui(self, event_name, data):
        if event_name == WorkflowEvent.STARTED:
            self.stepper.set_step_active(0, "CSRF Init")
            self.console.log("Workflow accepted. Initializing session and CSRF handshake...", "INFO")
            
        elif event_name == WorkflowEvent.UPLOAD_STARTED:
            msg = str(data)
            if "Document (Original)" in msg:
                self.stepper.set_step_active(1, "Original ID")
            elif "Document (Altered)" in msg:
                self.stepper.set_step_active(1, "Altered ID")
            elif "Selfie (Original)" in msg:
                self.stepper.set_step_active(2, "Original Selfie")
            elif "Selfie (Altered)" in msg:
                self.stepper.set_step_active(2, "Altered Selfie")
            elif "Video" in msg:
                self.stepper.set_step_active(3, "Transcode Video")
            elif "submit" in msg.lower():
                self.stepper.set_step_active(4, "Biometric Polling")
                
            self.console.log(msg, "INFO")
            
        elif event_name == WorkflowEvent.FINISHED:
            self.btn_start.configure(state="normal")
            self.media_container.grid() # Restore media cards
            self.media_container.master.grid_rowconfigure(1, weight=3) # Restore space for media cards
            
            is_err = False
            if isinstance(data, dict):
                status_str = data.get("status", "Finished")
                if "Error" in status_str or "error" in data:
                    is_err = True
            else:
                status_str = str(data)
                
            if is_err:
                self.stepper.set_step_error(self.stepper.current_step, "Failed")
                self.console.log(f"Workflow Terminated with Error: {data}", "ERROR")
            else:
                self.stepper.set_step_completed(4, "Verified")
                self.console.log(f"Workflow Completed Successfully: {data}", "SUCCESS")
                
            # SmartWeb Sync Feedback
            if isinstance(data, dict) and "website_synced" in data:
                if data.get("website_synced"):
                    self.console.log(f"Synced to SmartWeb Dashboard: {data.get('website_msg')}", "SUCCESS")
                else:
                    self.console.log(f"SmartWeb Sync Notice: {data.get('website_msg')}", "WARN")

            # Log to History
            if self.history_service:
                self.history_service.add_entry(status_str, str(data))
                self.load_history_ui()

    # ==========================================
    # HISTORY & AUDIT LOG TAB
    # ==========================================
    def setup_history_tab(self, tab):
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(1, weight=1)
        
        # Toolbar
        toolbar = ctk.CTkFrame(tab, fg_color=Theme.BG_CARD, corner_radius=Theme.RADIUS_CARD, border_width=1, border_color=Theme.BORDER_SUBTLE)
        toolbar.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 8))
        
        ctk.CTkLabel(toolbar, text="AUDIT & VERIFICATION HISTORY", font=Theme.font_sub(), text_color=Theme.TEXT_SECONDARY).pack(side="left", padx=15, pady=10)
        
        # Search Entry
        self.hist_search_var = ctk.StringVar()
        self.hist_search_entry = ctk.CTkEntry(
            toolbar,
            placeholder_text="Search runs...",
            textvariable=self.hist_search_var,
            width=200,
            height=30,
            fg_color=Theme.BG_INPUT,
            border_color=Theme.BORDER_SUBTLE
        )
        self.hist_search_entry.pack(side="left", padx=10)
        self.hist_search_entry.bind("<KeyRelease>", lambda e: self.filter_history_ui())
        
        # Export CSV Button
        ctk.CTkButton(
            toolbar,
            text="Export to CSV",
            font=Theme.font_small(),
            width=90,
            height=30,
            fg_color=Theme.BG_INPUT,
            hover_color=Theme.SECONDARY,
            command=self.export_history_csv
        ).pack(side="right", padx=(5, 15))

        # Sync Online History Button
        ctk.CTkButton(
            toolbar,
            text="🌐 Sync Online",
            font=Theme.font_small(),
            width=95,
            height=30,
            fg_color=Theme.BG_INPUT,
            hover_color=Theme.SECONDARY,
            command=self.sync_online_history
        ).pack(side="right", padx=5)
        
        # Refresh Button
        ctk.CTkButton(
            toolbar,
            text="Refresh",
            font=Theme.font_small(),
            width=70,
            height=30,
            fg_color=Theme.PRIMARY,
            hover_color=Theme.PRIMARY_HOVER,
            command=self.load_history_ui
        ).pack(side="right", padx=5)
        
        # Scrollable Container for History Items
        self.history_scroll = ctk.CTkScrollableFrame(
            tab,
            fg_color=Theme.BG_CARD,
            corner_radius=Theme.RADIUS_CARD,
            border_width=1,
            border_color=Theme.BORDER_SUBTLE
        )
        self.history_scroll.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        
        self.load_history_ui()

    def load_history_ui(self):
        # Clear existing items
        for widget in self.history_scroll.winfo_children():
            widget.destroy()
            
        if not self.history_service:
            return
            
        history = self.history_service.get_history()
        if not history:
            ctk.CTkLabel(
                self.history_scroll,
                text="No verification runs recorded yet.",
                font=Theme.font_body(),
                text_color=Theme.TEXT_MUTED
            ).pack(pady=40)
            return
            
        for item in history:
            self._render_history_card(item)

    def _render_history_card(self, item):
        card = ctk.CTkFrame(
            self.history_scroll,
            fg_color=Theme.BG_INPUT,
            corner_radius=Theme.RADIUS_INPUT,
            border_width=1,
            border_color=Theme.BORDER_SUBTLE
        )
        card.pack(fill="x", padx=10, pady=5, ipady=4)
        
        # Top line: Status + Timestamp
        top_row = ctk.CTkFrame(card, fg_color="transparent")
        top_row.pack(fill="x", padx=10, pady=(6, 2))
        
        status = item.get("status", "Unknown")
        is_success = "success" in status.lower() or "verified" in status.lower() or "passed" in status.lower()
        badge_color = Theme.SUCCESS if is_success else Theme.DANGER
        badge_bg = Theme.SUCCESS_BG if is_success else Theme.DANGER_BG
        badge_text = "PASSED ✓" if is_success else f"STATUS: {status.upper()}"
        
        ctk.CTkLabel(
            top_row,
            text=badge_text,
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=10, weight="bold"),
            text_color=badge_color,
            fg_color=badge_bg,
            corner_radius=4,
            padx=6,
            pady=2
        ).pack(side="left")
        
        ts = item.get("timestamp", "")
        formatted_ts = ts.replace("T", " ").split(".")[0] if ts else "N/A"
        ctk.CTkLabel(
            top_row,
            text=f"Executed at: {formatted_ts}",
            font=Theme.font_small(),
            text_color=Theme.TEXT_MUTED
        ).pack(side="left", padx=10)
        
        run_id = item.get("run_id", "")[:12]
        ctk.CTkLabel(
            top_row,
            text=f"ID: {run_id}",
            font=Theme.font_mono(10),
            text_color=Theme.TEXT_MUTED
        ).pack(side="right")
        
        # Bottom line: Details
        details = item.get("details", "")
        ctk.CTkLabel(
            card,
            text=str(details),
            font=Theme.font_small(),
            text_color=Theme.TEXT_SECONDARY,
            anchor="w",
            wraplength=850
        ).pack(fill="x", padx=10, pady=(2, 6))

    def filter_history_ui(self):
        query = self.hist_search_var.get().lower().strip()
        for widget in self.history_scroll.winfo_children():
            widget.destroy()
            
        if not self.history_service:
            return
            
        history = self.history_service.get_history()
        filtered = [
            item for item in history 
            if query in str(item.get("status", "")).lower() or query in str(item.get("details", "")).lower() or query in str(item.get("run_id", "")).lower()
        ]
        
        if not filtered:
            ctk.CTkLabel(
                self.history_scroll,
                text="No matching history records found.",
                font=Theme.font_body(),
                text_color=Theme.TEXT_MUTED
            ).pack(pady=40)
            return
            
        for item in filtered:
            self._render_history_card(item)

    def export_history_csv(self):
        from customtkinter import filedialog
        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")],
            title="Export History"
        )
        if path:
            try:
                import csv
                history = self.history_service.get_history()
                with open(path, "w", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    writer.writerow(["Run ID", "Timestamp", "Status", "Details"])
                    for item in history:
                        writer.writerow([item.get("run_id"), item.get("timestamp"), item.get("status"), item.get("details")])
                self.console.log(f"History exported to {path}", "SUCCESS")
            except Exception as e:
                self.console.log(f"Export failed: {e}", "ERROR")

    # ==========================================
    # NETWORK & PROXY TAB
    # ==========================================
    def setup_network_tab(self, tab):
        tab.grid_columnconfigure(0, weight=1)
        
        net_card = ctk.CTkFrame(tab, fg_color=Theme.BG_CARD, corner_radius=Theme.RADIUS_CARD, border_width=1, border_color=Theme.BORDER_SUBTLE)
        net_card.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(net_card, text="NETWORK & PROXY MANAGEMENT", font=Theme.font_sub(), text_color=Theme.TEXT_SECONDARY).pack(anchor="w", padx=20, pady=(20, 10))
        
        # Proxy Entry
        ctk.CTkLabel(net_card, text="Active Proxy Endpoint", font=Theme.font_body_bold(), text_color=Theme.TEXT_PRIMARY).pack(anchor="w", padx=20, pady=(10, 4))
        
        p_row = ctk.CTkFrame(net_card, fg_color="transparent")
        p_row.pack(fill="x", padx=20, pady=(0, 10))
        
        self.net_proxy_entry = ctk.CTkEntry(
            p_row,
            placeholder_text="http://username:password@host:port",
            fg_color=Theme.BG_INPUT,
            border_color=Theme.BORDER_SUBTLE,
            text_color=Theme.TEXT_PRIMARY,
            height=36
        )
        self.net_proxy_entry.pack(side="left", fill="x", expand=True)
        
        self.btn_apply_proxy = ctk.CTkButton(
            p_row,
            text="Apply Proxy",
            width=100,
            height=36,
            fg_color=Theme.PRIMARY,
            hover_color=Theme.PRIMARY_HOVER,
            command=self.apply_network_proxy
        )
        self.btn_apply_proxy.pack(side="left", padx=(8, 0))
        
        self.btn_test_proxy = ctk.CTkButton(
            p_row,
            text="Test Proxy",
            width=100,
            height=36,
            fg_color=Theme.SECONDARY,
            hover_color=Theme.SECONDARY_HOVER,
            command=self.test_network_proxy
        )
        self.btn_test_proxy.pack(side="left", padx=(8, 0))
        
        self.lbl_net_status = ctk.CTkLabel(
            net_card,
            text="Current Status: Direct Connection (No proxy set)",
            font=Theme.font_body(),
            text_color=Theme.TEXT_MUTED
        )
        self.lbl_net_status.pack(anchor="w", padx=20, pady=(0, 20))

    def apply_network_proxy(self):
        proxy = self.net_proxy_entry.get().strip()
        if proxy:
            if self.workflow and self.workflow.api_client:
                self.workflow.api_client.session.proxies.update({"http": proxy, "https": proxy})
            self.lbl_header_proxy.configure(text=f"🌐 Proxy Active ({proxy[:18]}...)", text_color=Theme.PRIMARY)
            self.lbl_net_status.configure(text=f"Proxy configured: {proxy}", text_color=Theme.SUCCESS)
            self.console.log(f"Proxy updated to: {proxy}", "SUCCESS")
        else:
            if self.workflow and self.workflow.api_client:
                self.workflow.api_client.session.proxies.clear()
            self.lbl_header_proxy.configure(text="🌐 Direct Connection", text_color=Theme.TEXT_SECONDARY)
            self.lbl_net_status.configure(text="Direct Connection (No proxy)", text_color=Theme.TEXT_MUTED)
            self.console.log("Proxy cleared. Using direct connection.", "INFO")

    def test_network_proxy(self):
        proxy = self.net_proxy_entry.get().strip()
        self.lbl_net_status.configure(text="Testing proxy...", text_color=Theme.WARNING)
        
        def run_test():
            from core.api_client import AgeSmartApiClient
            res = AgeSmartApiClient.check_proxy(proxy_url=proxy if proxy else None)
            if res.get("success"):
                ip = res["data"].get("ip", "Unknown")
                country = res["data"].get("country", "Unknown")
                self.after(0, lambda: self.lbl_net_status.configure(text=f"Proxy OK: IP {ip} ({country})", text_color=Theme.SUCCESS))
                self.after(0, lambda: self.console.log(f"Proxy tested successfully. IP: {ip}, Country: {country}", "SUCCESS"))
            else:
                err = res.get("error", "Unknown error")
                self.after(0, lambda: self.lbl_net_status.configure(text=f"Proxy Test Failed: {err}", text_color=Theme.DANGER))
                self.after(0, lambda: self.console.log(f"Proxy test failed: {err}", "ERROR"))
                
        threading.Thread(target=run_test, daemon=True).start()

    def sync_online_history(self):
        if not self.smartweb_service:
            self.console.log("SmartWeb service not available.", "WARN")
            return
            
        self.console.log("Fetching audit history from SmartWeb...", "INFO")
        def run_sync():
            ok, records = self.smartweb_service.fetch_online_history()
            if ok and records:
                for r in records:
                    code = r.get("code") or (r.get("trackingCode", {}).get("code") if isinstance(r.get("trackingCode"), dict) else "N/A")
                    status = "RECORDED"
                    if isinstance(r.get("trackingCode"), dict):
                        status = r.get("trackingCode", {}).get("overrideStatus") or "RECORDED"
                    self.history_service.add_entry(status, f"Website Code: {code}")
                self.after(0, self.load_history_ui)
                self.after(0, lambda: self.console.log(f"Synced {len(records)} records from SmartWeb.", "SUCCESS"))
            else:
                self.after(0, lambda: self.console.log("No new online records found from website.", "INFO"))
        threading.Thread(target=run_sync, daemon=True).start()

    def open_settings(self):
        from ui.settings_dialog import SettingsDialog
        current_proxy = self.net_proxy_entry.get() if hasattr(self, 'net_proxy_entry') else ""
        current_ua = self.input_entries.get("UserAgent").get() if "UserAgent" in self.input_entries else ""
        current_web = self.smartweb_service.base_url if self.smartweb_service else "https://smart-web-blue.vercel.app"
        dialog = SettingsDialog(self, current_proxy=current_proxy, current_ua=current_ua, current_web_url=current_web)
        self.wait_window(dialog)
        if dialog.result:
            p = dialog.result.get("proxy")
            ua = dialog.result.get("user_agent")
            web_url = dialog.result.get("website_url")
            if p:
                self.net_proxy_entry.delete(0, "end")
                self.net_proxy_entry.insert(0, p)
                self.apply_network_proxy()
            if ua and "UserAgent" in self.input_entries:
                self.input_entries["UserAgent"].delete(0, "end")
                self.input_entries["UserAgent"].insert(0, ua)
            if web_url and self.smartweb_service:
                self.smartweb_service.set_base_url(web_url)
                self.console.log(f"SmartWeb endpoint updated to: {web_url}", "INFO")
            self.console.log("Settings applied.", "INFO")

    def do_logout(self):
        self.console.log("Signing out...", "INFO")
        sys.exit(0)

    def set_authenticated_user(self, email: str):
        self.user_info["email"] = email
        if hasattr(self, "lbl_acc_user"):
            self.lbl_acc_user.configure(text=f"User: {email}")
        if hasattr(self, "lbl_header_user"):
            self.lbl_header_user.configure(text=f"👤 {email}")
