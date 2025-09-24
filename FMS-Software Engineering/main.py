import customtkinter as ctk
import sys
import os
from views.login_view import LoginView
from config.database import DatabaseManager
from config.settings import AppSettings

class FitnessApp:
    def __init__(self):
        # Set appearance mode and color theme
        ctk.set_appearance_mode("System")  # "System", "Dark", "Light"
        ctk.set_default_color_theme("blue")  # "blue", "green", "dark-blue"
        
        # Initialize database
        self.db_manager = DatabaseManager()
        self.db_manager.initialize_database()
        
        # Create main window
        self.root = ctk.CTk()
        self.root.title("FitPro Management System")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 600)
        
        # Center window on screen
        self.center_window()
        
        # Initialize login view
        self.login_view = LoginView(self.root, self.on_login_success)
        
    def center_window(self):
        # Get screen dimensions
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Calculate position coordinates
        x = (screen_width - 1200) // 2
        y = (screen_height - 800) // 2
        
        self.root.geometry(f"1200x800+{x}+{y}")
    
    def on_login_success(self, user_data):
        """Handle successful login and redirect to appropriate dashboard"""
        user_type = user_data.get('user_type')
        
        # Clear login view
        self.login_view.destroy()
        
        # Import and initialize appropriate dashboard
        if user_type == 'member':
            from views.member_dashboard import MemberDashboard
            self.dashboard = MemberDashboard(self.root, user_data, self.logout)
        elif user_type == 'trainer':
            from views.trainer_dashboard import TrainerDashboard
            self.dashboard = TrainerDashboard(self.root, user_data, self.logout)
        elif user_type == 'admin':
            from views.admin_dashboard import AdminDashboard
            self.dashboard = AdminDashboard(self.root, user_data, self.logout)
    
    def logout(self):
        """Handle user logout"""
        if hasattr(self, 'dashboard'):
            self.dashboard.destroy()
        
        # Recreate login view
        self.login_view = LoginView(self.root, self.on_login_success)
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = FitnessApp()
    app.run()