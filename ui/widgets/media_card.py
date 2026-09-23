import os
import customtkinter as ctk
from ui.theme import Theme

try:
    from PIL import Image
    try:
        import pillow_heif
        pillow_heif.register_heif_opener()
    except ImportError:
        pass
except ImportError:
    Image = None

try:
    from tkinterdnd2 import DND_FILES
except ImportError:
    DND_FILES = None

class MediaCard(ctk.CTkFrame):
    def __init__(self, parent, card_type: str, title: str, subtitle: str, on_file_selected=None, on_file_cleared=None, **kwargs):
        super().__init__(parent, fg_color=Theme.BG_CARD, corner_radius=Theme.RADIUS_CARD, border_width=1, border_color=Theme.BORDER_SUBTLE, **kwargs)
        self.card_type = card_type # "ID", "Selfie", "Video"
        self.title_text = title
        self.subtitle_text = subtitle
        self.on_file_selected = on_file_selected
        self.on_file_cleared = on_file_cleared
        
        self.file_path = None
        self.preview_image = None
        
        self.setup_ui()
        self._setup_dnd()
        
    def setup_ui(self):
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # --- Top Header ---
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=8, pady=(6, 4))
        
        # Icon & Title
        icons = {"ID": "🪪", "Selfie": "👤", "Video": "🎥"}
        icon = icons.get(self.card_type, "📁")
        
        lbl_title = ctk.CTkLabel(
            header, 
            text=f"{icon}  {self.title_text}", 
            font=Theme.font_sub(), 
            text_color=Theme.TEXT_PRIMARY
        )
        lbl_title.pack(side="left")
        
        self.badge = ctk.CTkLabel(
            header,
            text="REQUIRED",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=10, weight="bold"),
            text_color=Theme.TEXT_MUTED,
            fg_color=Theme.BG_INPUT,
            corner_radius=4,
            padx=6,
            pady=1
        )
        self.badge.pack(side="right")
        
        # --- Center Dropzone / Preview ---
        self.drop_frame = ctk.CTkFrame(
            self, 
            fg_color=Theme.BG_INPUT, 
            corner_radius=Theme.RADIUS_INPUT,
            border_width=1,
            border_color=Theme.BORDER_SUBTLE
        )
        self.drop_frame.grid(row=1, column=0, sticky="nsew", padx=8, pady=2)
        self.drop_frame.grid_propagate(False)
        self.drop_frame.pack_propagate(False)
        
        # Hover events
        self.drop_frame.bind("<Enter>", self.on_drop_enter)
        self.drop_frame.bind("<Leave>", self.on_drop_leave)
        
        # Placeholder container
        self.placeholder_frame = ctk.CTkFrame(self.drop_frame, fg_color="transparent")
        self.placeholder_frame.pack(expand=True, fill="both", padx=4, pady=4)
        
        self.upload_icon_label = ctk.CTkLabel(
            self.placeholder_frame,
            text="⤓",
            font=ctk.CTkFont(size=24),
            text_color=Theme.PRIMARY
        )
        self.upload_icon_label.pack(pady=(4, 0))
        
        self.btn_browse = ctk.CTkButton(
            self.placeholder_frame,
            text=f"Select {self.card_type}",
            font=Theme.font_small(),
            height=24,
            fg_color=Theme.PRIMARY,
            hover_color=Theme.PRIMARY_HOVER,
            command=self.browse_file
        )
        self.btn_browse.pack(pady=4)
        
        self.sub_text_label = ctk.CTkLabel(
            self.placeholder_frame,
            text=self.subtitle_text,
            font=Theme.font_small(),
            text_color=Theme.TEXT_MUTED
        )
        self.sub_text_label.pack(pady=(0, 2))
        
        # Preview container (hidden initially)
        self.preview_frame = ctk.CTkFrame(self.drop_frame, fg_color="transparent")
        self.preview_label = ctk.CTkLabel(self.preview_frame, text="")
        self.preview_label.pack(expand=True, fill="both", padx=4, pady=4)
        
        # --- Bottom Meta / Actions ---
        self.footer = ctk.CTkFrame(self, fg_color="transparent")
        self.footer.grid(row=2, column=0, sticky="ew", padx=8, pady=(4, 6))
        
        self.file_info_label = ctk.CTkLabel(
            self.footer,
            text="No file selected",
            font=Theme.font_small(),
            text_color=Theme.TEXT_MUTED,
            anchor="w"
        )
        self.file_info_label.pack(side="left", fill="x", expand=True)
        
        # Action Buttons
        self.btn_clear = ctk.CTkButton(
            self.footer,
            text="✕",
            width=26,
            height=26,
            font=Theme.font_small(),
            fg_color=Theme.BG_INPUT,
            hover_color=Theme.DANGER_HOVER,
            command=self.clear_file
        )
        # Hidden until file selected
        
        # Bind children for hover effect
        for child in [self.placeholder_frame, self.upload_icon_label, self.sub_text_label]:
            child.bind("<Enter>", self.on_drop_enter)
            child.bind("<Leave>", self.on_drop_leave)
            
    def on_drop_enter(self, event=None):
        if not self.file_path:
            self.drop_frame.configure(border_color=Theme.PRIMARY)
            
    def on_drop_leave(self, event=None):
        if not self.file_path:
            self.drop_frame.configure(border_color=Theme.BORDER_SUBTLE)
        
    def _setup_dnd(self):
        if DND_FILES:
            try:
                self.drop_frame.drop_target_register(DND_FILES)
                def on_drop(event):
                    path = event.data.strip("{}").strip('"')
                    if os.path.isfile(path):
                        self.set_file(path)
                self.drop_frame.dnd_bind('<<Drop>>', on_drop)
            except Exception:
                pass

    def browse_file(self):
        from customtkinter import filedialog
        types = [("Image Files", "*.jpg *.jpeg *.png *.webp *.bmp"), ("All Files", "*.*")]
        if self.card_type == "Video":
            types = [("Video Files", "*.mp4 *.mov *.avi *.mkv"), ("All Files", "*.*")]
            
        path = filedialog.askopenfilename(
            title=f"Select {self.title_text}",
            filetypes=types
        )
        if path:
            self.set_file(path)

    def set_file(self, file_path: str):
        if not os.path.exists(file_path):
            return
            
        self.file_path = file_path
        filename = os.path.basename(file_path)
        size_bytes = os.path.getsize(file_path)
        size_mb = size_bytes / (1024 * 1024)
        
        # Update badge
        self.badge.configure(text="LOADED", fg_color=Theme.SUCCESS_BG, text_color=Theme.SUCCESS)
        
        # Truncate filename if long
        short_name = filename if len(filename) <= 18 else filename[:15] + "..."
        self.file_info_label.configure(
            text=f"{short_name} ({size_mb:.1f} MB)",
            text_color=Theme.TEXT_PRIMARY
        )
        self.btn_clear.pack(side="right", padx=(4, 0))
        
        # Display preview if Image
        if self.card_type in ["ID", "Selfie"] and Image:
            self._show_fallback_preview(filename + " (Loading...)")
            import threading
            def load_img():
                try:
                    img = Image.open(file_path)
                    # Compute thumbnail keeping aspect ratio
                    max_w, max_h = 100, 60
                    img.thumbnail((max_w, max_h), Image.Resampling.LANCZOS)
                    self.preview_image = ctk.CTkImage(light_image=img, dark_image=img, size=img.size)
                    self.after(0, self._apply_img_preview)
                except Exception:
                    self.after(0, lambda: self._show_fallback_preview(filename))
            threading.Thread(target=load_img, daemon=True).start()
        elif self.card_type == "Video":
            self._show_video_preview(filename, size_mb)
        else:
            self._show_fallback_preview(filename)
            
        if self.on_file_selected:
            self.on_file_selected(self.card_type, file_path)

    def _apply_img_preview(self):
        self.preview_label.configure(image=self.preview_image, text="")
        self.placeholder_frame.pack_forget()
        self.preview_frame.pack(expand=True, fill="both", padx=6, pady=6)

    def _show_video_preview(self, filename, size_mb):
        self.placeholder_frame.pack_forget()
        self.preview_label.configure(
            text=f"🎥\n{filename}\n{size_mb:.1f} MB Video Ready",
            font=Theme.font_small(),
            text_color=Theme.TEXT_ACCENT
        )
        self.preview_frame.pack(expand=True, fill="both", padx=6, pady=6)

    def _show_fallback_preview(self, filename):
        self.placeholder_frame.pack_forget()
        self.preview_label.configure(
            text=f"📄\n{filename}\nReady",
            font=Theme.font_small(),
            text_color=Theme.TEXT_ACCENT
        )
        self.preview_frame.pack(expand=True, fill="both", padx=6, pady=6)

    def clear_file(self):
        self.file_path = None
        self.preview_image = None
        self.preview_label.configure(image=None, text="")
        self.preview_frame.pack_forget()
        self.placeholder_frame.pack(expand=True, fill="both", padx=10, pady=10)
        
        self.badge.configure(text="REQUIRED", fg_color=Theme.BG_INPUT, text_color=Theme.TEXT_MUTED)
        self.file_info_label.configure(text="No file selected", text_color=Theme.TEXT_MUTED)
        self.btn_clear.pack_forget()
        
        if self.on_file_cleared:
            self.on_file_cleared(self.card_type)
