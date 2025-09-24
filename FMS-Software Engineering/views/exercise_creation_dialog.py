import customtkinter as ctk
from tkinter import messagebox
from models.workout import Exercise

class ExerciseCreationDialog:
    def __init__(self, parent):
        self.parent = parent
        self.result = None
        
        self.setup_dialog()
    
    def setup_dialog(self):
        """Setup exercise creation dialog"""
        self.dialog = ctk.CTkToplevel(self.parent)
        self.dialog.title("Add New Exercise")
        self.dialog.geometry("500x650")
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
            text="Add New Exercise",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.pack(pady=(0, 20))
        
        # Exercise name
        name_label = ctk.CTkLabel(main_frame, text="Exercise Name")
        name_label.pack(anchor="w", pady=(0, 5))
        
        self.name_entry = ctk.CTkEntry(
            main_frame,
            placeholder_text="Enter exercise name",
            width=400
        )
        self.name_entry.pack(pady=(0, 15))
        
        # Category
        category_label = ctk.CTkLabel(main_frame, text="Category")
        category_label.pack(anchor="w", pady=(0, 5))
        
        self.category_menu = ctk.CTkOptionMenu(
            main_frame,
            values=[
                "Chest", "Back", "Shoulders", "Arms", "Legs", 
                "Core", "Cardio", "Full Body", "Stretching", "Other"
            ],
            width=400
        )
        self.category_menu.pack(pady=(0, 15))
        
        # Muscle groups
        muscle_label = ctk.CTkLabel(main_frame, text="Primary Muscle Groups")
        muscle_label.pack(anchor="w", pady=(0, 5))
        
        self.muscle_entry = ctk.CTkEntry(
            main_frame,
            placeholder_text="e.g., Chest, Triceps, Shoulders",
            width=400
        )
        self.muscle_entry.pack(pady=(0, 15))
        
        # Equipment
        equipment_label = ctk.CTkLabel(main_frame, text="Equipment Required")
        equipment_label.pack(anchor="w", pady=(0, 5))
        
        self.equipment_menu = ctk.CTkOptionMenu(
            main_frame,
            values=[
                "Bodyweight", "Dumbbells", "Barbell", "Resistance Bands",
                "Pull-up Bar", "Kettlebell", "Medicine Ball", "Cable Machine",
                "Smith Machine", "Other"
            ],
            width=400
        )
        self.equipment_menu.pack(pady=(0, 15))
        
        # Difficulty level
        difficulty_label = ctk.CTkLabel(main_frame, text="Difficulty Level")
        difficulty_label.pack(anchor="w", pady=(0, 5))
        
        self.difficulty_menu = ctk.CTkOptionMenu(
            main_frame,
            values=["Beginner", "Intermediate", "Advanced"],
            width=400
        )
        self.difficulty_menu.pack(pady=(0, 15))
        
        # Instructions
        instructions_label = ctk.CTkLabel(main_frame, text="Exercise Instructions")
        instructions_label.pack(anchor="w", pady=(0, 5))
        
        self.instructions_textbox = ctk.CTkTextbox(
            main_frame,
            height=120,
            width=400
        )
        self.instructions_textbox.pack(pady=(0, 20))
        
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
        
        add_button = ctk.CTkButton(
            button_frame,
            text="Add Exercise",
            width=120,
            command=self.add_exercise
        )
        add_button.pack(side="right")
        
        # Set defaults
        self.category_menu.set("Other")
        self.equipment_menu.set("Bodyweight")
        self.difficulty_menu.set("Beginner")
    
    def center_dialog(self):
        """Center dialog on screen"""
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() - self.dialog.winfo_width()) // 2
        y = (self.dialog.winfo_screenheight() - self.dialog.winfo_height()) // 2
        self.dialog.geometry(f"+{x}+{y}")
    
    def add_exercise(self):
        """Add the exercise to the database"""
        # Validate required fields
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showerror("Error", "Please enter an exercise name")
            return
        
        category = self.category_menu.get()
        muscle_groups = self.muscle_entry.get().strip()
        equipment = self.equipment_menu.get()
        difficulty_level = self.difficulty_menu.get()
        instructions = self.instructions_textbox.get("1.0", "end-1c").strip()
        
        # Create exercise
        exercise = Exercise(
            name=name,
            category=category,
            muscle_groups=muscle_groups,
            equipment=equipment,
            instructions=instructions,
            difficulty_level=difficulty_level
        )
        
        try:
            exercise.save()
            self.result = True
            self.dialog.destroy()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add exercise: {str(e)}")
    
    def cancel(self):
        """Cancel exercise creation"""
        self.result = False
        self.dialog.destroy()