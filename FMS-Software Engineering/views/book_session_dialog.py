import customtkinter as ctk
from tkinter import messagebox
from tkcalendar import DateEntry
from datetime import datetime, timedelta
from models.user import User
from models.session import Session
from models.notification import Notification

class BookSessionDialog:
    def __init__(self, parent, member_id):
        self.parent = parent
        self.member_id = member_id
        self.result = None
        
        self.setup_dialog()
    
    def setup_dialog(self):
        """Setup session booking dialog"""
        self.dialog = ctk.CTkToplevel(self.parent)
        self.dialog.title("Book Training Session")
        self.dialog.geometry("500x600")
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.center_dialog()
        
        # Main container
        main_frame = ctk.CTkScrollableFrame(self.dialog)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title_label = ctk.CTkLabel(
            main_frame,
            text="Book Training Session",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.pack(pady=(0, 20))
        
        # Trainer selection
        trainer_label = ctk.CTkLabel(main_frame, text="Select Trainer")
        trainer_label.pack(anchor="w", pady=(0, 5))
        
        trainers = User.get_all_by_type('trainer')
        trainer_names = [f"{trainer.full_name} (ID: {trainer.id})" for trainer in trainers]
        
        self.trainer_menu = ctk.CTkOptionMenu(
            main_frame,
            values=trainer_names if trainer_names else ["No trainers available"],
            width=400
        )
        self.trainer_menu.pack(pady=(0, 20))
        
        # Session type
        type_label = ctk.CTkLabel(main_frame, text="Session Type")
        type_label.pack(anchor="w", pady=(0, 5))
        
        self.type_menu = ctk.CTkOptionMenu(
            main_frame,
            values=[
                "Personal Training",
                "Strength Training",
                "Cardio Session",
                "Flexibility & Mobility",
                "Nutrition Consultation",
                "Fitness Assessment"
            ],
            width=400
        )
        self.type_menu.pack(pady=(0, 20))
        
        # Date selection
        date_label = ctk.CTkLabel(main_frame, text="Session Date")
        date_label.pack(anchor="w", pady=(0, 5))
        
        # Create a frame to hold the date entry
        date_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        date_frame.pack(fill="x", pady=(0, 20))
        
        # Date entry widget
        self.date_entry = DateEntry(
            date_frame,
            width=12,
            background='darkblue',
            foreground='white',
            borderwidth=2,
            year=datetime.now().year,
            month=datetime.now().month,
            day=datetime.now().day,
            mindate=datetime.now().date(),
            maxdate=(datetime.now() + timedelta(days=90)).date()
        )
        self.date_entry.pack(side="left")
        
        # Time selection
        time_label = ctk.CTkLabel(main_frame, text="Session Time")
        time_label.pack(anchor="w", pady=(0, 5))
        
        time_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        time_frame.pack(fill="x", pady=(0, 20))
        
        # Hour selection
        self.hour_menu = ctk.CTkOptionMenu(
            time_frame,
            values=[f"{i:02d}" for i in range(6, 22)],  # 6 AM to 9 PM
            width=80
        )
        self.hour_menu.pack(side="left", padx=(0, 10))
        
        colon_label = ctk.CTkLabel(time_frame, text=":")
        colon_label.pack(side="left")
        
        # Minute selection
        self.minute_menu = ctk.CTkOptionMenu(
            time_frame,
            values=["00", "15", "30", "45"],
            width=80
        )
        self.minute_menu.pack(side="left", padx=(10, 0))
        
        # Duration
        duration_label = ctk.CTkLabel(main_frame, text="Duration (minutes)")
        duration_label.pack(anchor="w", pady=(0, 5))
        
        self.duration_menu = ctk.CTkOptionMenu(
            main_frame,
            values=["30", "45", "60", "75", "90", "120"],
            width=400
        )
        self.duration_menu.set("60")
        self.duration_menu.pack(pady=(0, 20))
        
        # Price
        price_label = ctk.CTkLabel(main_frame, text="Session Price ($)")
        price_label.pack(anchor="w", pady=(0, 5))
        
        self.price_entry = ctk.CTkEntry(
            main_frame,
            placeholder_text="Enter session price (e.g., 75.00)",
            width=400
        )
        self.price_entry.pack(pady=(0, 20))
        
        # Notes
        notes_label = ctk.CTkLabel(main_frame, text="Additional Notes (optional)")
        notes_label.pack(anchor="w", pady=(0, 5))
        
        self.notes_textbox = ctk.CTkTextbox(
            main_frame,
            height=80,
            width=400
        )
        self.notes_textbox.pack(pady=(0, 20))
        
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
        
        book_button = ctk.CTkButton(
            button_frame,
            text="Book Session",
            width=120,
            command=self.book_session
        )
        book_button.pack(side="right")
        
        # Set default values
        self.hour_menu.set("09")
        self.minute_menu.set("00")
        self.price_entry.insert(0, "75.00")
    
    def center_dialog(self):
        """Center dialog on screen"""
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() - self.dialog.winfo_width()) // 2
        y = (self.dialog.winfo_screenheight() - self.dialog.winfo_height()) // 2
        self.dialog.geometry(f"+{x}+{y}")
    
    def book_session(self):
        """Handle session booking"""
        # Validate trainer selection
        if self.trainer_menu.get() == "No trainers available":
            messagebox.showerror("Error", "No trainers available to book with.")
            return
        
        # Extract trainer ID from selection
        trainer_selection = self.trainer_menu.get()
        try:
            trainer_id = int(trainer_selection.split("ID: ")[1].split(")")[0])
        except (IndexError, ValueError):
            messagebox.showerror("Error", "Please select a valid trainer.")
            return
        
        # Validate price
        try:
            price = float(self.price_entry.get().strip())
            if price <= 0:
                raise ValueError("Price must be positive")
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid price.")
            return
        
        # Build session datetime
        selected_date = self.date_entry.get()
        hour = int(self.hour_menu.get())
        minute = int(self.minute_menu.get())
        
        session_datetime = datetime.combine(selected_date, datetime.min.time().replace(hour=hour, minute=minute))
        
        # Check if session is in the past
        if session_datetime <= datetime.now():
            messagebox.showerror("Error", "Session date and time must be in the future.")
            return
        
        # Create session
        session = Session(
            member_id=self.member_id,
            trainer_id=trainer_id,
            session_date=session_datetime.strftime('%Y-%m-%d %H:%M:%S'),
            duration=int(self.duration_menu.get()),
            session_type=self.type_menu.get(),
            status='scheduled',
            price=price,
            notes=self.notes_textbox.get("1.0", "end-1c").strip()
        )
        
        try:
            session.save()
            
            # Create notifications
            member = User.get_by_id(self.member_id)
            trainer = User.get_by_id(trainer_id)
            
            # Notify member
            Notification.create_notification(
                self.member_id,
                "Session Booked",
                f"Your {self.type_menu.get()} session with {trainer.full_name} has been scheduled for {session_datetime.strftime('%B %d, %Y at %I:%M %p')}.",
                "success"
            )
            
            # Notify trainer
            Notification.create_notification(
                trainer_id,
                "New Session Request",
                f"{member.full_name} has booked a {self.type_menu.get()} session with you for {session_datetime.strftime('%B %d, %Y at %I:%M %p')}.",
                "info"
            )
            
            self.result = True
            self.dialog.destroy()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to book session: {str(e)}")
    
    def cancel(self):
        """Cancel session booking"""
        self.result = False
        self.dialog.destroy()