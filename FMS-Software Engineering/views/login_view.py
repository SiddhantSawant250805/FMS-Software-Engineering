import customtkinter as ctk
from tkinter import messagebox
from controllers.auth_controller import AuthController

class LoginView:
    def __init__(self, parent, on_success_callback):
        self.parent = parent
        self.on_success_callback = on_success_callback
        self.auth_controller = AuthController()
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the login interface"""
        # Clear parent window
        for widget in self.parent.winfo_children():
            widget.destroy()
        
        # Main container
        self.main_frame = ctk.CTkFrame(self.parent, corner_radius=0)
        self.main_frame.pack(fill="both", expand=True)
        
        # Center login container
        self.login_container = ctk.CTkFrame(self.main_frame, width=400, height=500, corner_radius=20)
        self.login_container.place(relx=0.5, rely=0.5, anchor="center")
        self.login_container.pack_propagate(False)
        
        # Title
        self.title_label = ctk.CTkLabel(
            self.login_container,
            text="FitPro Management System",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.title_label.pack(pady=(40, 10))
        
        self.subtitle_label = ctk.CTkLabel(
            self.login_container,
            text="Your Complete Fitness Solution",
            font=ctk.CTkFont(size=14),
            text_color="gray"
        )
        self.subtitle_label.pack(pady=(0, 30))
        
        # Username field
        self.username_label = ctk.CTkLabel(self.login_container, text="Username")
        self.username_label.pack(anchor="w", padx=40, pady=(0, 5))
        
        self.username_entry = ctk.CTkEntry(
            self.login_container,
            placeholder_text="Enter your username",
            width=320,
            height=40
        )
        self.username_entry.pack(padx=40, pady=(0, 20))
        
        # Password field
        self.password_label = ctk.CTkLabel(self.login_container, text="Password")
        self.password_label.pack(anchor="w", padx=40, pady=(0, 5))
        
        self.password_entry = ctk.CTkEntry(
            self.login_container,
            placeholder_text="Enter your password",
            show="*",
            width=320,
            height=40
        )
        self.password_entry.pack(padx=40, pady=(0, 20))
        
        # Login button
        self.login_button = ctk.CTkButton(
            self.login_container,
            text="LOGIN",
            width=320,
            height=40,
            font=ctk.CTkFont(size=16, weight="bold"),
            command=self.handle_login
        )
        self.login_button.pack(padx=40, pady=(10, 20))
        
        # Register link
        self.register_frame = ctk.CTkFrame(self.login_container, fg_color="transparent")
        self.register_frame.pack(pady=(20, 0))
        
        self.register_label = ctk.CTkLabel(
            self.register_frame,
            text="Don't have an account?",
            text_color="gray"
        )
        self.register_label.pack(side="left")
        
        self.register_button = ctk.CTkButton(
            self.register_frame,
            text="Sign Up",
            width=80,
            height=30,
            fg_color="transparent",
            text_color=("gray10", "#DCE4EE"),
            hover_color=("gray70", "gray30"),
            command=self.show_register
        )
        self.register_button.pack(side="left", padx=(10, 0))
        
        # Quick login info
        self.info_frame = ctk.CTkFrame(self.login_container, fg_color="transparent")
        self.info_frame.pack(pady=(30, 0))
        
        self.info_label = ctk.CTkLabel(
            self.info_frame,
            text="Demo Login: admin / admin123",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        self.info_label.pack()
        
        # Bind Enter key to login
        self.parent.bind('<Return>', lambda event: self.handle_login())
        
        # Focus on username entry
        self.username_entry.focus()
    
    def handle_login(self):
        """Handle login attempt"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        
        if not username or not password:
            messagebox.showerror("Error", "Please enter both username and password")
            return
        
        # Attempt authentication
        user_data = self.auth_controller.authenticate_user(username, password)
        
        if user_data:
            messagebox.showinfo("Success", f"Welcome, {user_data['first_name']}!")
            self.on_success_callback(user_data)
        else:
            messagebox.showerror("Error", "Invalid username or password")
            self.password_entry.delete(0, 'end')
    
    def show_register(self):
        """Show registration dialog"""
        from views.register_dialog import RegisterDialog
        dialog = RegisterDialog(self.parent)
        if dialog.result:
            messagebox.showinfo("Success", "Registration successful! Please login with your new credentials.")
    
    def destroy(self):
        """Clean up the view"""
        self.main_frame.destroy()