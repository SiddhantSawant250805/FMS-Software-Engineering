import customtkinter as ctk
from tkinter import messagebox
from controllers.auth_controller import AuthController

class RegisterDialog:
    def __init__(self, parent):
        self.parent = parent
        self.auth_controller = AuthController()
        self.result = None
        
        self.setup_dialog()
    
    def setup_dialog(self):
        """Setup registration dialog"""
        self.dialog = ctk.CTkToplevel(self.parent)
        self.dialog.title("Register New Account")
        self.dialog.geometry("450x600")
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() - self.dialog.winfo_width()) // 2
        y = (self.dialog.winfo_screenheight() - self.dialog.winfo_height()) // 2
        self.dialog.geometry(f"+{x}+{y}")
        
        # Main container
        main_frame = ctk.CTkScrollableFrame(self.dialog)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title_label = ctk.CTkLabel(
            main_frame,
            text="Create New Account",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.pack(pady=(0, 20))
        
        # User type selection
        user_type_label = ctk.CTkLabel(main_frame, text="Account Type")
        user_type_label.pack(anchor="w", pady=(0, 5))
        
        self.user_type_var = ctk.StringVar(value="member")
        user_type_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        user_type_frame.pack(fill="x", pady=(0, 20))
        
        member_radio = ctk.CTkRadioButton(
            user_type_frame, text="Member", variable=self.user_type_var, value="member"
        )
        member_radio.pack(side="left", padx=(0, 20))
        
        trainer_radio = ctk.CTkRadioButton(
            user_type_frame, text="Trainer", variable=self.user_type_var, value="trainer"
        )
        trainer_radio.pack(side="left")
        
        # Personal information fields
        fields = [
            ("First Name", "first_name"),
            ("Last Name", "last_name"),
            ("Username", "username"),
            ("Email", "email"),
            ("Phone", "phone"),
            ("Password", "password"),
            ("Confirm Password", "confirm_password")
        ]
        
        self.entries = {}
        
        for label_text, field_name in fields:
            label = ctk.CTkLabel(main_frame, text=label_text)
            label.pack(anchor="w", pady=(10, 5))
            
            if field_name in ["password", "confirm_password"]:
                entry = ctk.CTkEntry(main_frame, placeholder_text=f"Enter {label_text.lower()}", 
                                   show="*", width=350)
            else:
                entry = ctk.CTkEntry(main_frame, placeholder_text=f"Enter {label_text.lower()}", 
                                   width=350)
            
            entry.pack(pady=(0, 10))
            self.entries[field_name] = entry
        
        # Buttons
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(fill="x", pady=(20, 0))
        
        cancel_button = ctk.CTkButton(
            button_frame,
            text="Cancel",
            width=100,
            command=self.cancel
        )
        cancel_button.pack(side="right", padx=(10, 0))
        
        register_button = ctk.CTkButton(
            button_frame,
            text="Register",
            width=100,
            command=self.handle_register
        )
        register_button.pack(side="right")
    
    def handle_register(self):
        """Handle registration"""
        # Collect form data
        data = {}
        for field, entry in self.entries.items():
            data[field] = entry.get().strip()
        
        data['user_type'] = self.user_type_var.get()
        
        # Validate required fields
        required_fields = ["first_name", "last_name", "username", "email", "password", "confirm_password"]
        for field in required_fields:
            if not data.get(field):
                messagebox.showerror("Error", f"Please fill in the {field.replace('_', ' ').title()} field")
                return
        
        # Validate password match
        if data['password'] != data['confirm_password']:
            messagebox.showerror("Error", "Passwords do not match")
            return
        
        # Validate password strength
        if len(data['password']) < 6:
            messagebox.showerror("Error", "Password must be at least 6 characters long")
            return
        
        # Validate email format (basic)
        if '@' not in data['email'] or '.' not in data['email']:
            messagebox.showerror("Error", "Please enter a valid email address")
            return
        
        # Attempt registration
        try:
            success = self.auth_controller.register_user(data)
            if success:
                self.result = True
                self.dialog.destroy()
            else:
                messagebox.showerror("Error", "Registration failed. Username or email may already exist.")
        except Exception as e:
            messagebox.showerror("Error", f"Registration failed: {str(e)}")
    
    def cancel(self):
        """Cancel registration"""
        self.result = False
        self.dialog.destroy()