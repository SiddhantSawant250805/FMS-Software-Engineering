import customtkinter as ctk
from tkinter import messagebox
from models.session import FitnessClass
from models.user import User

class ClassCreationDialog:
    def __init__(self, parent):
        self.parent = parent
        self.result = None
        
        self.setup_dialog()
    
    def setup_dialog(self):
        """Setup class creation dialog"""
        self.dialog = ctk.CTkToplevel(self.parent)
        self.dialog.title("Create New Fitness Class")
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
            text="Create New Fitness Class",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.pack(pady=(0, 20))
        
        # Class name
        name_label = ctk.CTkLabel(main_frame, text="Class Name")
        name_label.pack(anchor="w", pady=(0, 5))
        
        self.name_entry = ctk.CTkEntry(
            main_frame,
            placeholder_text="Enter class name",
            width=400
        )
        self.name_entry.pack(pady=(0, 15))
        
        # Description
        desc_label = ctk.CTkLabel(main_frame, text="Description")
        desc_label.pack(anchor="w", pady=(0, 5))
        
        self.desc_textbox = ctk.CTkTextbox(
            main_frame,
            height=80,
            width=400
        )
        self.desc_textbox.pack(pady=(0, 15))
        
        # Trainer assignment
        trainer_label = ctk.CTkLabel(main_frame, text="Assign Trainer (optional)")
        trainer_label.pack(anchor="w", pady=(0, 5))
        
        trainers = User.get_all_by_type('trainer')
        trainer_names = ["No trainer assigned"] + [f"{trainer.full_name} (ID: {trainer.id})" for trainer in trainers]
        
        self.trainer_menu = ctk.CTkOptionMenu(
            main_frame,
            values=trainer_names,
            width=400
        )
        self.trainer_menu.pack(pady=(0, 15))
        
        # Capacity
        capacity_label = ctk.CTkLabel(main_frame, text="Class Capacity")
        capacity_label.pack(anchor="w", pady=(0, 5))
        
        self.capacity_entry = ctk.CTkEntry(
            main_frame,
            placeholder_text="Enter maximum number of participants",
            width=400
        )
        self.capacity_entry.pack(pady=(0, 15))
        
        # Price
        price_label = ctk.CTkLabel(main_frame, text="Class Price ($)")
        price_label.pack(anchor="w", pady=(0, 5))
        
        self.price_entry = ctk.CTkEntry(
            main_frame,
            placeholder_text="Enter class price (e.g., 25.00)",
            width=400
        )
        self.price_entry.pack(pady=(0, 15))
        
        # Duration
        duration_label = ctk.CTkLabel(main_frame, text="Duration (minutes)")
        duration_label.pack(anchor="w", pady=(0, 5))
        
        self.duration_menu = ctk.CTkOptionMenu(
            main_frame,
            values=["30", "45", "60", "75", "90"],
            width=400
        )
        self.duration_menu.set("60")
        self.duration_menu.pack(pady=(0, 15))
        
        # Schedule (simplified)
        schedule_label = ctk.CTkLabel(main_frame, text="Schedule")
        schedule_label.pack(anchor="w", pady=(0, 5))
        
        self.schedule_entry = ctk.CTkEntry(
            main_frame,
            placeholder_text="e.g., 'Mondays and Wednesdays at 6:00 PM'",
            width=400
        )
        self.schedule_entry.pack(pady=(0, 20))
        
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
        
        create_button = ctk.CTkButton(
            button_frame,
            text="Create Class",
            width=120,
            command=self.create_class
        )
        create_button.pack(side="right")
        
        # Set defaults
        self.price_entry.insert(0, "25.00")
        self.capacity_entry.insert(0, "20")
    
    def center_dialog(self):
        """Center dialog on screen"""
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() - self.dialog.winfo_width()) // 2
        y = (self.dialog.winfo_screenheight() - self.dialog.winfo_height()) // 2
        self.dialog.geometry(f"+{x}+{y}")
    
    def create_class(self):
        """Create the fitness class"""
        # Validate required fields
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showerror("Error", "Please enter a class name")
            return
        
        description = self.desc_textbox.get("1.0", "end-1c").strip()
        
        # Get trainer ID if assigned
        trainer_id = None
        trainer_selection = self.trainer_menu.get()
        if trainer_selection != "No trainer assigned":
            try:
                trainer_id = int(trainer_selection.split("ID: ")[1].split(")")[0])
            except (IndexError, ValueError):
                messagebox.showerror("Error", "Invalid trainer selection")
                return
        
        # Validate capacity
        try:
            capacity = int(self.capacity_entry.get().strip()) if self.capacity_entry.get().strip() else None
            if capacity is not None and capacity <= 0:
                raise ValueError("Capacity must be positive")
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid capacity")
            return
        
        # Validate price
        try:
            price = float(self.price_entry.get().strip()) if self.price_entry.get().strip() else None
            if price is not None and price < 0:
                raise ValueError("Price cannot be negative")
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid price")
            return
        
        duration = int(self.duration_menu.get())
        schedule = self.schedule_entry.get().strip()
        
        # Create fitness class
        fitness_class = FitnessClass(
            name=name,
            description=description,
            trainer_id=trainer_id,
            schedule=schedule,  # In a full implementation, this would be JSON formatted
            capacity=capacity,
            price=price,
            duration=duration
        )
        
        try:
            fitness_class.save()
            self.result = True
            self.dialog.destroy()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create class: {str(e)}")
    
    def cancel(self):
        """Cancel class creation"""
        self.result = False
        self.dialog.destroy()