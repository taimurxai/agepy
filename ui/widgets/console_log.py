import customtkinter as ctk
from datetime import datetime
from ui.theme import Theme
import tkinter as tk

class ProConsole(ctk.CTkFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, fg_color=Theme.BG_CARD, corner_radius=Theme.RADIUS_CARD, border_width=1, border_color=Theme.BORDER_SUBTLE, **kwargs)
        self.all_logs = []
        self.autoscroll = True
        self.setup_ui()
        self._configure_tags()
        
    def setup_ui(self):
        # Top toolbar
        toolbar = ctk.CTkFrame(self, fg_color="transparent")
        toolbar.pack(fill="x", padx=12, pady=(10, 6))
        
        title_label = ctk.CTkLabel(
            toolbar, 
            text="LIVE AUDIT CONSOLE", 
            font=Theme.font_sub(), 
            text_color=Theme.TEXT_SECONDARY
        )
        title_label.pack(side="left")
        
        # Right-side controls
        btn_frame = ctk.CTkFrame(toolbar, fg_color="transparent")
        btn_frame.pack(side="right")
        
        # Filter Menu
        self.filter_var = ctk.StringVar(value="ALL")
        self.filter_menu = ctk.CTkOptionMenu(
            btn_frame,
            values=["ALL", "INFO", "SUCCESS", "WARN", "ERROR"],
            variable=self.filter_var,
            width=90,
            height=26,
            font=Theme.font_small(),
            fg_color=Theme.BG_INPUT,
            button_color=Theme.SECONDARY,
            button_hover_color=Theme.SECONDARY_HOVER,
            command=self._apply_filter
        )
        self.filter_menu.pack(side="left", padx=4)
        
        # Auto-scroll Toggle
        self.autoscroll_switch = ctk.CTkSwitch(
            btn_frame,
            text="Auto-scroll",
            font=Theme.font_small(),
            text_color=Theme.TEXT_MUTED,
            command=self._toggle_autoscroll,
            progress_color=Theme.PRIMARY,
            width=36,
            height=18
        )
        self.autoscroll_switch.select()
        self.autoscroll_switch.pack(side="left", padx=8)
        
        # Copy Button
        copy_btn = ctk.CTkButton(
            btn_frame,
            text="Copy",
            width=50,
            height=26,
            font=Theme.font_small(),
            fg_color=Theme.BG_INPUT,
            hover_color=Theme.SECONDARY,
            command=self.copy_logs
        )
        copy_btn.pack(side="left", padx=2)
        
        # Export Button
        export_btn = ctk.CTkButton(
            btn_frame,
            text="Export",
            width=55,
            height=26,
            font=Theme.font_small(),
            fg_color=Theme.BG_INPUT,
            hover_color=Theme.SECONDARY,
            command=self.export_logs
        )
        export_btn.pack(side="left", padx=2)
        
        # Clear Button
        clear_btn = ctk.CTkButton(
            btn_frame,
            text="Clear",
            width=50,
            height=26,
            font=Theme.font_small(),
            fg_color=Theme.BG_INPUT,
            hover_color=Theme.DANGER_HOVER,
            command=self.clear_logs
        )
        clear_btn.pack(side="left", padx=2)
        
        # Textbox Console
        self.textbox = ctk.CTkTextbox(
            self,
            fg_color=Theme.BG_INPUT,
            text_color=Theme.TEXT_PRIMARY,
            border_width=1,
            border_color=Theme.BORDER_SUBTLE,
            corner_radius=Theme.RADIUS_INPUT,
            font=Theme.font_mono(11),
            wrap="char"
        )
        self.textbox.pack(fill="both", expand=True, padx=12, pady=(0, 10))
        self.textbox.configure(state="disabled")
        
    def _configure_tags(self):
        # Configure internal tkinter Text tags for colors
        raw_text = self.textbox._textbox
        raw_text.tag_config("timestamp", foreground=Theme.TEXT_MUTED)
        raw_text.tag_config("info", foreground=Theme.INFO)
        raw_text.tag_config("success", foreground=Theme.SUCCESS)
        raw_text.tag_config("warn", foreground=Theme.WARNING)
        raw_text.tag_config("error", foreground=Theme.DANGER)
        raw_text.tag_config("debug", foreground=Theme.TEXT_ACCENT)
        raw_text.tag_config("msg", foreground=Theme.TEXT_PRIMARY)

    def log(self, message: str, level: str = None):
        if not level:
            up_msg = message.upper()
            if "ERROR" in up_msg or "FAILED" in up_msg:
                level = "ERROR"
            elif "SUCCESS" in up_msg or "FINISHED" in up_msg or "ACCEPTED" in up_msg:
                level = "SUCCESS"
            elif "WARN" in up_msg:
                level = "WARN"
            else:
                level = "INFO"
                
        now = datetime.now().strftime("%H:%M:%S")
        entry = {"timestamp": now, "level": level, "message": message}
        self.all_logs.append(entry)
        
        # Filter check
        current_filter = self.filter_var.get()
        if current_filter != "ALL" and current_filter != level:
            return
            
        self._insert_log_entry(entry)

    def _insert_log_entry(self, entry):
        self.textbox.configure(state="normal")
        raw_text = self.textbox._textbox
        
        # Insert timestamp
        raw_text.insert(tk.END, f"[{entry['timestamp']}] ", "timestamp")
        
        # Insert level
        lvl_tag = entry['level'].lower()
        raw_text.insert(tk.END, f"[{entry['level']:<7}] ", lvl_tag)
        
        # Insert message
        raw_text.insert(tk.END, f"{entry['message']}\n", "msg")
        
        if self.autoscroll:
            self.textbox.see("end")
            
        self.textbox.configure(state="disabled")

    def _toggle_autoscroll(self):
        self.autoscroll = bool(self.autoscroll_switch.get())

    def _apply_filter(self, selected):
        self.textbox.configure(state="normal")
        self.textbox.delete("1.0", "end")
        self.textbox.configure(state="disabled")
        
        for entry in self.all_logs:
            if selected == "ALL" or entry["level"] == selected:
                self._insert_log_entry(entry)

    def clear_logs(self):
        self.all_logs.clear()
        self.textbox.configure(state="normal")
        self.textbox.delete("1.0", "end")
        self.textbox.configure(state="disabled")

    def copy_logs(self):
        text = self.textbox.get("1.0", "end").strip()
        if text:
            self.clipboard_clear()
            self.clipboard_append(text)
            self.log("Console logs copied to clipboard.", "INFO")

    def export_logs(self):
        from customtkinter import filedialog
        path = filedialog.asksaveasfilename(
            defaultextension=".log",
            filetypes=[("Log Files", "*.log"), ("Text Files", "*.txt"), ("All Files", "*.*")],
            title="Export Console Logs"
        )
        if path:
            try:
                with open(path, "w", encoding="utf-8") as f:
                    for entry in self.all_logs:
                        f.write(f"[{entry['timestamp']}] [{entry['level']:<7}] {entry['message']}\n")
                self.log(f"Logs successfully exported to {path}", "SUCCESS")
            except Exception as e:
                self.log(f"Failed to export logs: {e}", "ERROR")
