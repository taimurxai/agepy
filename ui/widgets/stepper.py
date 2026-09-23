import customtkinter as ctk
from ui.theme import Theme

class WorkflowStepper(ctk.CTkFrame):
    STEPS = [
        ("Session & CSRF", "Init & handshake"),
        ("ID Processing", "Sanitize & twin"),
        ("Selfie Sync", "Biometric clean"),
        ("Video Upload", "Transcode & verify"),
        ("Final Polling", "Decision check")
    ]
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, fg_color=Theme.BG_CARD, corner_radius=Theme.RADIUS_CARD, border_width=1, border_color=Theme.BORDER_SUBTLE, **kwargs)
        self.step_widgets = []
        self.current_step = -1
        self.setup_ui()
        
    def setup_ui(self):
        # Header Row
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=15, pady=(12, 8))
        
        title_label = ctk.CTkLabel(
            header_frame, 
            text="PIPELINE EXECUTION STATUS", 
            font=Theme.font_sub(), 
            text_color=Theme.TEXT_SECONDARY
        )
        title_label.pack(side="left")
        
        self.status_badge = ctk.CTkLabel(
            header_frame,
            text="READY",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=10, weight="bold"),
            text_color=Theme.TEXT_SECONDARY,
            fg_color=Theme.BG_INPUT,
            corner_radius=4,
            padx=8,
            pady=2
        )
        self.status_badge.pack(side="right")
        
        # Steps Row
        self.steps_container = ctk.CTkFrame(self, fg_color="transparent")
        self.steps_container.pack(fill="x", padx=15, pady=(0, 10))
        self.steps_container.grid_columnconfigure(tuple(range(len(self.STEPS))), weight=1)
        
        for idx, (title, subtitle) in enumerate(self.STEPS):
            step_box = ctk.CTkFrame(self.steps_container, fg_color="transparent")
            step_box.grid(row=0, column=idx, sticky="ew", padx=3)
            
            # Step circle / indicator
            circle = ctk.CTkLabel(
                step_box,
                text=str(idx + 1),
                width=26,
                height=26,
                corner_radius=13,
                fg_color=Theme.BG_INPUT,
                text_color=Theme.TEXT_MUTED,
                font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=11, weight="bold")
            )
            circle.pack(pady=(0, 4))
            
            title_lbl = ctk.CTkLabel(
                step_box,
                text=title,
                font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=11, weight="bold"),
                text_color=Theme.TEXT_MUTED
            )
            title_lbl.pack()
            
            sub_lbl = ctk.CTkLabel(
                step_box,
                text=subtitle,
                font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=9),
                text_color=Theme.TEXT_MUTED
            )
            sub_lbl.pack()
            
            self.step_widgets.append({
                "box": step_box,
                "circle": circle,
                "title": title_lbl,
                "sub": sub_lbl,
                "state": "pending"
            })
            
        # Progress Bar
        self.progress_bar = ctk.CTkProgressBar(
            self,
            height=6,
            corner_radius=3,
            fg_color=Theme.BG_INPUT,
            progress_color=Theme.PRIMARY
        )
        self.progress_bar.pack(fill="x", padx=15, pady=(0, 12))
        self.progress_bar.set(0.0)
        
    def reset(self):
        self.current_step = -1
        self.progress_bar.set(0.0)
        self.status_badge.configure(text="READY", fg_color=Theme.BG_INPUT, text_color=Theme.TEXT_SECONDARY)
        for idx, w in enumerate(self.step_widgets):
            w["circle"].configure(text=str(idx + 1), fg_color=Theme.BG_INPUT, text_color=Theme.TEXT_MUTED)
            w["title"].configure(text_color=Theme.TEXT_MUTED)
            w["sub"].configure(text_color=Theme.TEXT_MUTED)
            w["state"] = "pending"
            
    def set_step_active(self, step_idx: int, message: str = ""):
        self.current_step = step_idx
        # Calculate progress
        target_pct = max(0.05, (step_idx) / len(self.STEPS))
        self.animate_progress(target_pct)
        self.status_badge.configure(text="IN PROGRESS", fg_color=Theme.WARNING_BG, text_color=Theme.WARNING)
        
        for i in range(step_idx):
            w = self.step_widgets[i]
            w["circle"].configure(text="✓", fg_color=Theme.SUCCESS, text_color=Theme.TEXT_PRIMARY)
            w["title"].configure(text_color=Theme.TEXT_PRIMARY)
            w["sub"].configure(text_color=Theme.SUCCESS)
            w["state"] = "completed"
            
        w_cur = self.step_widgets[step_idx]
        w_cur["circle"].configure(text="●", fg_color=Theme.PRIMARY, text_color=Theme.TEXT_PRIMARY)
        w_cur["title"].configure(text_color=Theme.TEXT_ACCENT)
        if message:
            w_cur["sub"].configure(text=message[:18], text_color=Theme.TEXT_SECONDARY)
        w_cur["state"] = "active"

    def set_step_completed(self, step_idx: int, message: str = ""):
        w = self.step_widgets[step_idx]
        w["circle"].configure(text="✓", fg_color=Theme.SUCCESS, text_color=Theme.TEXT_PRIMARY)
        w["title"].configure(text_color=Theme.TEXT_PRIMARY)
        if message:
            w["sub"].configure(text=message[:18], text_color=Theme.SUCCESS)
        w["state"] = "completed"
        
        if step_idx == len(self.STEPS) - 1:
            self.animate_progress(1.0)
            self.status_badge.configure(text="SUCCESS", fg_color=Theme.SUCCESS_BG, text_color=Theme.SUCCESS)

    def animate_progress(self, target_value):
        current_val = self.progress_bar.get()
        step = 0.02
        if current_val < target_value:
            new_val = min(current_val + step, target_value)
            self.progress_bar.set(new_val)
            if new_val < target_value:
                self.after(20, self.animate_progress, target_value)
        elif current_val > target_value:
            self.progress_bar.set(target_value)

    def set_step_error(self, step_idx: int, error_msg: str = ""):
        if 0 <= step_idx < len(self.step_widgets):
            w = self.step_widgets[step_idx]
            w["circle"].configure(text="✕", fg_color=Theme.DANGER, text_color=Theme.TEXT_PRIMARY)
            w["title"].configure(text_color=Theme.DANGER)
            if error_msg:
                w["sub"].configure(text=error_msg[:18], text_color=Theme.DANGER)
            w["state"] = "error"
        self.status_badge.configure(text="FAILED", fg_color=Theme.DANGER_BG, text_color=Theme.DANGER)
