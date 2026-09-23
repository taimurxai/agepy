import customtkinter as ctk

class Theme:
    # --- Color Palette (Enterprise Dark Mode 60-30-10) ---
    # 60% Background & Surface (Slight purple/blue tint for premium feel)
    BG_BASE = "#090A0F"         # App Background
    BG_SURFACE = "#12141D"      # Sidebars / Header Background
    BG_CARD = "#1A1D27"         # Cards, Dialogs
    BG_CARD_HOVER = "#232736"   # Hover state for cards
    BG_INPUT = "#12141D"        # Input fields
    
    # 30% Borders & Secondary
    BORDER_SUBTLE = "#272B38"   # Subtle divider
    BORDER_LIGHT = "#353A4D"    # Default borders
    BORDER_FOCUS = "#3B82F6"    # Primary Blue focus
    
    # 10% Primary & Accent
    PRIMARY = "#3B82F6"         # Electric Blue
    PRIMARY_HOVER = "#2563EB"   # Deep Blue Hover
    PRIMARY_ACTIVE = "#1D4ED8"
    
    # Secondary & Neutrals
    SECONDARY = "#475569"
    SECONDARY_HOVER = "#334155"
    
    # Functional / Status (Semantic Colors)
    SUCCESS = "#10B981"
    SUCCESS_HOVER = "#059669"
    SUCCESS_BG = "#064E3B"
    
    WARNING = "#F59E0B"
    WARNING_HOVER = "#D97706"
    WARNING_BG = "#78350F"
    
    DANGER = "#EF4444"
    DANGER_HOVER = "#DC2626"
    DANGER_BG = "#7F1D1D"
    
    INFO = "#3B82F6"
    INFO_BG = "#0C4A6E"
    
    # Typography Colors
    TEXT_PRIMARY = "#FFFFFF"     # Crisp White for main text
    TEXT_SECONDARY = "#A1A1AA"   # Zinc for sub-text
    TEXT_MUTED = "#71717A"       # Muted Zinc
    TEXT_ACCENT = "#60A5FA"      # Blue Accent
    
    # --- Metrics ---
    RADIUS_CARD = 12       # Increased for more premium smooth look
    RADIUS_INPUT = 8       # Increased for smooth inputs
    RADIUS_BUTTON = 8      # Smooth buttons
    
    # --- Fonts (Enterprise Typography System) ---
    FONT_FAMILY = "Inter"
    FONT_MONO = "Consolas"
    
    @classmethod
    def font_title(cls):
        # H1 Level (20px)
        return ctk.CTkFont(family=cls.FONT_FAMILY, size=20, weight="bold")
        
    @classmethod
    def font_header(cls):
        # H2 Level (16px)
        return ctk.CTkFont(family=cls.FONT_FAMILY, size=16, weight="bold")
        
    @classmethod
    def font_sub(cls):
        # Sub-title (12px)
        return ctk.CTkFont(family=cls.FONT_FAMILY, size=12, weight="normal")
        
    @classmethod
    def font_body(cls):
        # Standard Body Base (13px)
        return ctk.CTkFont(family=cls.FONT_FAMILY, size=13, weight="normal")
        
    @classmethod
    def font_body_bold(cls):
        return ctk.CTkFont(family=cls.FONT_FAMILY, size=13, weight="bold")
        
    @classmethod
    def font_small(cls):
        # Captions / Badges (11px)
        return ctk.CTkFont(family=cls.FONT_FAMILY, size=11, weight="normal")
        
    @classmethod
    def font_mono(cls, size=12):
        return ctk.CTkFont(family=cls.FONT_MONO, size=size)
