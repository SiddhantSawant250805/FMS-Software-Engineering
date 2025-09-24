import customtkinter as ctk
from tkinter import messagebox
from models.workout import Exercise

class ExerciseSelectionDialog:
    def __init__(self, parent):
        self.parent = parent
        self.result = None
        
        self.setup_dialog()
    
    def setup_dialog(self):
        """Setup exercise selection dialog"""
        self.dialog = ctk.CTkToplevel(self.parent)
        self.dialog.title("Add Exercise to Workout")
        self.dialog.geometry("600x500")
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.center_dialog()
        
        # Main container
        main_frame = ctk.CTkFrame(self.dialog)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title_label = ctk.CTkLabel(
            main_frame,
            text="Add Exercise to Workout",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.pack(pady=(10, 20))
        
        # Exercise selection
        exercise_label = ctk.CTkLabel(main_frame, text="Select Exercise")
        exercise_label.pack(anchor="w", padx=20, pady=(0, 5))
        
        # Get all exercises
        exercises = Exercise.get_all()
        exercise_names = [exercise.name for exercise in exercises]
        
        self.exercise_menu = ctk.CTkOptionMenu(
            main_frame,
            values=exercise_names if exercise_names else ["No exercises available"],
            width=500
        )
        self.exercise_menu.pack(padx=20, pady=(0, 15))
        
        # Exercise details frame
        details_frame = ctk.CTkFrame(main_frame)
        details_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        details_title = ctk.CTkLabel(
            details_frame,
            text="Exercise Parameters",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        details_title.pack(pady=(15, 10))
        
        # Sets
        sets_frame = ctk.CTkFrame(details_frame, fg_color="transparent")
        sets_frame.pack(fill="x", padx=20, pady=5)
        
        sets_label = ctk.CTkLabel(sets_frame, text="Sets:", width=80)
        sets_label.pack(side="left")
        
        self.sets_entry = ctk.CTkEntry(sets_frame, width=100, placeholder_text="3")
        self.sets_entry.pack(side="left", padx=(10, 0))
        
        # Reps
        reps_frame = ctk.CTkFrame(details_frame, fg_color="transparent")
        reps_frame.pack(fill="x", padx=20, pady=5)
        
        reps_label = ctk.CTkLabel(reps_frame, text="Reps:", width=80)
        reps_label.pack(side="left")
        
        self.reps_entry = ctk.CTkEntry(reps_frame, width=100, placeholder_text="10")
        self.reps_entry.pack(side="left", padx=(10, 0))
        
        # Weight
        weight_frame = ctk.CTkFrame(details_frame, fg_color="transparent")
        weight_frame.pack(fill="x", padx=20, pady=5)
        
        weight_label = ctk.CTkLabel(weight_frame, text="Weight:", width=80)
        weight_label.pack(side="left")
        
        self.weight_entry = ctk.CTkEntry(weight_frame, width=100, placeholder_text="lbs")
        self.weight_entry.pack(side="left", padx=(10, 0))
        
        # Rest time
        rest_frame = ctk.CTkFrame(details_frame, fg_color="transparent")
        rest_frame.pack(fill="x", padx=20, pady=5)
        
        rest_label = ctk.CTkLabel(rest_frame, text="Rest:", width=80)
        rest_label.pack(side="left")
        
        self.rest_entry = ctk.CTkEntry(rest_frame, width=100, placeholder_text="60s")
        self.rest_entry.pack(side="left", padx=(10, 0))
        
        # Notes
        notes_label = ctk.CTkLabel(details_frame, text="Notes:")
        notes_label.pack(anchor="w", padx=20, pady=(10, 5))
        
        self.notes_textbox = ctk.CTkTextbox(details_frame, height=60)
        self.notes_textbox.pack(fill="x", padx=20, pady=(0, 15))
        
        # Exercise info display
        self.info_frame = ctk.CTkFrame(main_frame)
        self.info_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        self.info_label = ctk.CTkLabel(
            self.info_frame,
            text="Select an exercise to view details",
            wraplength=500,
            justify="left"
        )
        self.info_label.pack(padx=20, pady=15)
        
        # Buttons
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(fill="x", padx=20, pady=(10, 20))
        
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
        
        # Bind exercise selection change
        self.exercise_menu.configure(command=self.on_exercise_change)
        
        # Set default values
        self.sets_entry.insert(0, "3")
        self.reps_entry.insert(0, "10")
        self.rest_entry.insert(0, "60s")
        
        # Load initial exercise info
        if exercise_names:
            self.on_exercise_change(exercise_names[0])
    
    def center_dialog(self):
        """Center dialog on screen"""
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() - self.dialog.winfo_width()) // 2
        y = (self.dialog.winfo_screenheight() - self.dialog.winfo_height()) // 2
        self.dialog.geometry(f"+{x}+{y}")
    
    def on_exercise_change(self, selected_exercise):
        """Handle exercise selection change"""
        if selected_exercise == "No exercises available":
            self.info_label.configure(text="No exercises available in database")
            return
        
        # Find selected exercise
        exercises = Exercise.get_all()
        selected_exercise_obj = None
        
        for exercise in exercises:
            if exercise.name == selected_exercise:
                selected_exercise_obj = exercise
                break
        
        if selected_exercise_obj:
            info_text = f"Exercise: {selected_exercise_obj.name}\n"
            info_text += f"Category: {selected_exercise_obj.category or 'Not specified'}\n"
            info_text += f"Muscle Groups: {selected_exercise_obj.muscle_groups or 'Not specified'}\n"
            info_text += f"Equipment: {selected_exercise_obj.equipment or 'Not specified'}\n"
            info_text += f"Difficulty: {selected_exercise_obj.difficulty_level or 'Not specified'}\n"
            
            if selected_exercise_obj.instructions:
                info_text += f"\nInstructions:\n{selected_exercise_obj.instructions}"
            
            self.info_label.configure(text=info_text)
        else:
            self.info_label.configure(text="Exercise details not found")
    
    def add_exercise(self):
        """Add exercise to workout"""
        if self.exercise_menu.get() == "No exercises available":
            messagebox.showerror("Error", "No exercise selected")
            return
        
        # Collect exercise data
        exercise_data = {
            'name': self.exercise_menu.get(),
            'sets': self.sets_entry.get().strip() or "3",
            'reps': self.reps_entry.get().strip() or "10",
            'weight': self.weight_entry.get().strip() or "",
            'rest': self.rest_entry.get().strip() or "60s",
            'notes': self.notes_textbox.get("1.0", "end-1c").strip()
        }
        
        # Validate sets and reps are numbers
        try:
            int(exercise_data['sets'])
            int(exercise_data['reps'])
        except ValueError:
            messagebox.showerror("Error", "Sets and reps must be valid numbers")
            return
        
        self.result = exercise_data
        self.dialog.destroy()
    
    def cancel(self):
        """Cancel exercise selection"""
        self.result = None
        self.dialog.destroy()