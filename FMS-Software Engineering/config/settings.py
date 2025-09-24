import os

class AppSettings:
    # Database settings
    DATABASE_PATH = "fitness_system.db"
    
    # UI Settings
    WINDOW_WIDTH = 1200
    WINDOW_HEIGHT = 800
    MIN_WIDTH = 1000
    MIN_HEIGHT = 600
    
    # Theme settings
    DEFAULT_THEME = "blue"
    DEFAULT_APPEARANCE = "System"  # "System", "Dark", "Light"
    
    # File paths
    ASSETS_DIR = "assets"
    ICONS_DIR = os.path.join(ASSETS_DIR, "icons")
    IMAGES_DIR = os.path.join(ASSETS_DIR, "images")
    EXPORTS_DIR = "exports"
    
    # Session settings
    SESSION_DURATION_MINUTES = 60
    
    # Email settings (for notifications - would need SMTP setup)
    EMAIL_ENABLED = False
    SMTP_SERVER = ""
    SMTP_PORT = 587
    EMAIL_USERNAME = ""
    EMAIL_PASSWORD = ""
    
    # PDF Export settings
    PDF_FONT = "Helvetica"
    PDF_TITLE_SIZE = 16
    PDF_HEADER_SIZE = 14
    PDF_BODY_SIZE = 12
    
    @classmethod
    def create_directories(cls):
        """Create necessary directories if they don't exist"""
        directories = [cls.ASSETS_DIR, cls.ICONS_DIR, cls.IMAGES_DIR, cls.EXPORTS_DIR]
        for directory in directories:
            os.makedirs(directory, exist_ok=True)