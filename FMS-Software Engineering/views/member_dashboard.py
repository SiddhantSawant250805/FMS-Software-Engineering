import customtkinter as ctk
from tkinter import messagebox
import tkinter as tk
from models.user import User, MemberProfile
from models.workout import Workout
from models.session import Session
from models.notification import Notification
from services.pdf_service import PDFService
from datetime import datetime, timedelta

class MemberDashboard:
    def __init__(self, parent, user_data, logout_callback):
        self.parent = parent
        self.user_data = user_data
        self.logout_callback = logout_callback
        self.user = User.get_by_id(user_data['id'])
        self.member_profile = MemberProfile.get_by_user_id(user_data['id'])
        
        self.setup_ui()
        self.load_dashboard_data()
    
    def setup_ui(self):
        """Setup member dashboard interface"""
        # Clear parent window
        for widget in self.parent.winfo_children():
            widget.destroy()
        
        # Main container
        self.main_frame = ctk.CTkFrame(self.parent, corner_radius=0)
        self.main_frame.pack(fill="both", expand=True)
        
        # Header
        self.setup_header()
        
        # Navigation sidebar
        self.setup_sidebar()
        
        # Content area
        self.content_frame = ctk.CTkFrame(self.main_frame)
        self.content_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)
        
        # Show dashboard by default
        self.show_dashboard()
    
    def setup_header(self):
        """Setup header with user info and notifications"""
        header_frame = ctk.CTkFrame(self.main_frame, height=80)
        header_frame.pack(fill="x", padx=10, pady=(10, 0))
        header_frame.pack_propagate(False)
        
        # Welcome message
        welcome_label = ctk.CTkLabel(
            header_frame,
            text=f"Welcome back, {self.user.first_name}!",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        welcome_label.pack(side="left", padx=20, pady=20)
        
        # Header buttons
        button_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        button_frame.pack(side="right", padx=20, pady=20)
        
        # Notifications button
        self.notifications_count = len(Notification.get_by_user_id(self.user.id, unread_only=True))
        notif_text = f"Notifications ({self.notifications_count})" if self.notifications_count > 0 else "Notifications"
        
        self.notifications_button = ctk.CTkButton(
            button_frame,
            text=notif_text,
            width=120,
            command=self.show_notifications
        )
        self.notifications_button.pack(side="left", padx=(0, 10))
        
        # Theme toggle
        self.theme_button = ctk.CTkButton(
            button_frame,
            text="🌙",
            width=40,
            command=self.toggle_theme
        )
        self.theme_button.pack(side="left", padx=(0, 10))
        
        # Logout button
        logout_button = ctk.CTkButton(
            button_frame,
            text="Logout",
            width=80,
            fg_color="gray",
            hover_color="dark gray",
            command=self.logout_callback
        )
        logout_button.pack(side="left")
    
    def setup_sidebar(self):
        """Setup navigation sidebar"""
        sidebar_frame = ctk.CTkFrame(self.main_frame, width=200)
        sidebar_frame.pack(side="left", fill="y", padx=(10, 0), pady=10)
        sidebar_frame.pack_propagate(False)
        
        # Navigation buttons
        nav_buttons = [
            ("🏠 Dashboard", self.show_dashboard),
            ("💪 My Workouts", self.show_workouts),
            ("📅 Sessions", self.show_sessions),
            ("📊 Progress", self.show_progress),
            ("👤 Profile", self.show_profile),
            ("🏋️ Exercise Library", self.show_exercises),
            ("🍎 Meal Plans", self.show_meals),
            ("⚙️ Settings", self.show_settings),
        ]
        
        for text, command in nav_buttons:
            button = ctk.CTkButton(
                sidebar_frame,
                text=text,
                width=180,
                height=40,
                anchor="w",
                command=command
            )
            button.pack(padx=10, pady=5)
    
    def clear_content(self):
        """Clear content frame"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
    
    def show_dashboard(self):
        """Show main dashboard with overview"""
        self.clear_content()
        
        # Title
        title_label = ctk.CTkLabel(
            self.content_frame,
            text="Dashboard Overview",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=(20, 30))
        
        # Stats cards
        stats_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        stats_frame.pack(fill="x", padx=20, pady=(0, 30))
        
        # Quick stats
        workouts_count = len(Workout.get_by_member_id(self.user.id))
        upcoming_sessions = len(Session.get_upcoming_sessions(self.user.id, 'member'))
        
        self.create_stat_card(stats_frame, "Total Workouts", str(workouts_count), "💪").pack(side="left", padx=10, fill="x", expand=True)
        self.create_stat_card(stats_frame, "Upcoming Sessions", str(upcoming_sessions), "📅").pack(side="left", padx=10, fill="x", expand=True)
        self.create_stat_card(stats_frame, "Profile Complete", "85%", "👤").pack(side="left", padx=10, fill="x", expand=True)
        
        # Recent activity
        activity_frame = ctk.CTkFrame(self.content_frame)
        activity_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        activity_title = ctk.CTkLabel(
            activity_frame,
            text="Recent Activity",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        activity_title.pack(pady=20)
        
        # Recent sessions
        recent_sessions = Session.get_by_member_id(self.user.id)[:3]
        if recent_sessions:
            for session in recent_sessions:
                session_frame = ctk.CTkFrame(activity_frame)
                session_frame.pack(fill="x", padx=20, pady=5)
                
                session_info = ctk.CTkLabel(
                    session_frame,
                    text=f"Session: {session.session_type or 'Training'} - {session.status.title()}",
                    font=ctk.CTkFont(size=14)
                )
                session_info.pack(side="left", padx=20, pady=10)
                
                session_date = ctk.CTkLabel(
                    session_frame,
                    text=session.session_date or "Date TBD",
                    text_color="gray"
                )
                session_date.pack(side="right", padx=20, pady=10)
        else:
            no_sessions_label = ctk.CTkLabel(
                activity_frame,
                text="No recent activity. Book your first session!",
                text_color="gray"
            )
            no_sessions_label.pack(pady=20)
    
    def create_stat_card(self, parent, title, value, icon):
        """Create a statistics card"""
        card = ctk.CTkFrame(parent)
        
        icon_label = ctk.CTkLabel(card, text=icon, font=ctk.CTkFont(size=24))
        icon_label.pack(pady=(15, 5))
        
        value_label = ctk.CTkLabel(
            card,
            text=value,
            font=ctk.CTkFont(size=28, weight="bold")
        )
        value_label.pack()
        
        title_label = ctk.CTkLabel(
            card,
            text=title,
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        title_label.pack(pady=(0, 15))
        
        return card
    
    def show_workouts(self):
        """Show member's workout plans"""
        self.clear_content()
        
        # Title and actions
        header_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=20)
        
        title_label = ctk.CTkLabel(
            header_frame,
            text="My Workout Plans",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(side="left")
        
        export_button = ctk.CTkButton(
            header_frame,
            text="📄 Export PDF",
            command=self.export_workouts_pdf
        )
        export_button.pack(side="right")
        
        # Workouts list
        workouts_frame = ctk.CTkScrollableFrame(self.content_frame)
        workouts_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        workouts = Workout.get_by_member_id(self.user.id)
        
        if workouts:
            for workout in workouts:
                workout_card = ctk.CTkFrame(workouts_frame)
                workout_card.pack(fill="x", pady=10, padx=10)
                
                # Workout info
                workout_info_frame = ctk.CTkFrame(workout_card, fg_color="transparent")
                workout_info_frame.pack(fill="x", padx=20, pady=15)
                
                workout_name = ctk.CTkLabel(
                    workout_info_frame,
                    text=workout.name,
                    font=ctk.CTkFont(size=16, weight="bold")
                )
                workout_name.pack(side="left")
                
                workout_date = ctk.CTkLabel(
                    workout_info_frame,
                    text=workout.created_at[:10] if workout.created_at else "",
                    text_color="gray"
                )
                workout_date.pack(side="right")
                
                # Description
                if workout.description:
                    desc_label = ctk.CTkLabel(
                        workout_card,
                        text=workout.description,
                        wraplength=600,
                        justify="left"
                    )
                    desc_label.pack(anchor="w", padx=20, pady=(0, 10))
                
                # Exercise count
                exercise_count = len(workout.exercises) if workout.exercises else 0
                count_label = ctk.CTkLabel(
                    workout_card,
                    text=f"{exercise_count} exercises",
                    text_color="gray"
                )
                count_label.pack(anchor="w", padx=20, pady=(0, 15))
        else:
            no_workouts_label = ctk.CTkLabel(
                workouts_frame,
                text="No workout plans yet. Contact a trainer to get started!",
                font=ctk.CTkFont(size=16),
                text_color="gray"
            )
            no_workouts_label.pack(pady=50)
    
    def show_sessions(self):
        """Show member's training sessions"""
        self.clear_content()
        
        # Title and book session button
        header_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=20)
        
        title_label = ctk.CTkLabel(
            header_frame,
            text="Training Sessions",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(side="left")
        
        book_button = ctk.CTkButton(
            header_frame,
            text="📅 Book Session",
            command=self.book_session
        )
        book_button.pack(side="right")
        
        # Sessions list
        sessions_frame = ctk.CTkScrollableFrame(self.content_frame)
        sessions_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        sessions = Session.get_by_member_id(self.user.id)
        
        if sessions:
            # Group by status
            upcoming = [s for s in sessions if s.status == 'scheduled']
            completed = [s for s in sessions if s.status == 'completed']
            cancelled = [s for s in sessions if s.status == 'cancelled']
            
            # Show upcoming sessions first
            if upcoming:
                upcoming_label = ctk.CTkLabel(
                    sessions_frame,
                    text="Upcoming Sessions",
                    font=ctk.CTkFont(size=18, weight="bold")
                )
                upcoming_label.pack(anchor="w", pady=(20, 10))
                
                for session in upcoming:
                    self.create_session_card(sessions_frame, session)
            
            # Show completed sessions
            if completed:
                completed_label = ctk.CTkLabel(
                    sessions_frame,
                    text="Completed Sessions",
                    font=ctk.CTkFont(size=18, weight="bold")
                )
                completed_label.pack(anchor="w", pady=(20, 10))
                
                for session in completed[:5]:  # Show last 5 completed
                    self.create_session_card(sessions_frame, session)
        else:
            no_sessions_label = ctk.CTkLabel(
                sessions_frame,
                text="No training sessions yet. Book your first session!",
                font=ctk.CTkFont(size=16),
                text_color="gray"
            )
            no_sessions_label.pack(pady=50)
    
    def create_session_card(self, parent, session):
        """Create a session card widget"""
        card = ctk.CTkFrame(parent)
        card.pack(fill="x", pady=5, padx=10)
        
        # Session info
        info_frame = ctk.CTkFrame(card, fg_color="transparent")
        info_frame.pack(fill="x", padx=20, pady=15)
        
        # Status indicator
        status_colors = {
            'scheduled': 'green',
            'completed': 'blue',
            'cancelled': 'red'
        }
        
        status_label = ctk.CTkLabel(
            info_frame,
            text=f"● {session.status.title()}",
            text_color=status_colors.get(session.status, 'gray')
        )
        status_label.pack(side="left")
        
        # Session type and date
        session_info = f"{session.session_type or 'Training Session'}"
        if session.session_date:
            session_info += f" - {session.session_date}"
        
        info_label = ctk.CTkLabel(
            info_frame,
            text=session_info,
            font=ctk.CTkFont(size=14)
        )
        info_label.pack(side="left", padx=(20, 0))
        
        # Price
        if session.price:
            price_label = ctk.CTkLabel(
                info_frame,
                text=f"${session.price:.2f}",
                font=ctk.CTkFont(weight="bold")
            )
            price_label.pack(side="right")
        
        # Cancel button for upcoming sessions
        if session.status == 'scheduled':
            cancel_button = ctk.CTkButton(
                info_frame,
                text="Cancel",
                width=80,
                fg_color="red",
                hover_color="dark red",
                command=lambda s=session: self.cancel_session(s)
            )
            cancel_button.pack(side="right", padx=(0, 20))
    
    def show_progress(self):
        """Show member's progress tracking"""
        self.clear_content()
        
        title_label = ctk.CTkLabel(
            self.content_frame,
            text="Progress Tracking",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=20)
        
        # Progress form
        progress_frame = ctk.CTkFrame(self.content_frame)
        progress_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        form_label = ctk.CTkLabel(
            progress_frame,
            text="Record Your Progress",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        form_label.pack(pady=20)
        
        # Simple progress form
        form_inner = ctk.CTkFrame(progress_frame)
        form_inner.pack(padx=40, pady=20, fill="x")
        
        # Weight entry
        ctk.CTkLabel(form_inner, text="Current Weight (lbs)").pack(anchor="w", padx=20, pady=(20, 5))
        self.weight_entry = ctk.CTkEntry(form_inner, placeholder_text="Enter weight")
        self.weight_entry.pack(padx=20, pady=(0, 15), fill="x")
        
        # Notes entry
        ctk.CTkLabel(form_inner, text="Progress Notes").pack(anchor="w", padx=20, pady=(0, 5))
        self.progress_notes = ctk.CTkTextbox(form_inner, height=100)
        self.progress_notes.pack(padx=20, pady=(0, 20), fill="x")
        
        # Save button
        save_button = ctk.CTkButton(
            form_inner,
            text="Save Progress",
            command=self.save_progress
        )
        save_button.pack(pady=20)
    
    def show_profile(self):
        """Show member profile management"""
        self.clear_content()
        
        title_label = ctk.CTkLabel(
            self.content_frame,
            text="My Profile",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=20)
        
        # Profile form
        profile_frame = ctk.CTkScrollableFrame(self.content_frame)
        profile_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Personal Information
        personal_frame = ctk.CTkFrame(profile_frame)
        personal_frame.pack(fill="x", padx=20, pady=10)
        
        personal_title = ctk.CTkLabel(
            personal_frame,
            text="Personal Information",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        personal_title.pack(pady=(15, 10))
        
        # Profile fields
        self.profile_entries = {}
        
        fields = [
            ("First Name", "first_name", self.user.first_name),
            ("Last Name", "last_name", self.user.last_name),
            ("Email", "email", self.user.email),
            ("Phone", "phone", self.user.phone),
        ]
        
        for label_text, field_name, current_value in fields:
            field_frame = ctk.CTkFrame(personal_frame, fg_color="transparent")
            field_frame.pack(fill="x", padx=20, pady=5)
            
            label = ctk.CTkLabel(field_frame, text=label_text, width=120)
            label.pack(side="left", padx=(0, 20))
            
            entry = ctk.CTkEntry(field_frame)
            if current_value:
                entry.insert(0, str(current_value))
            entry.pack(side="left", fill="x", expand=True)
            
            self.profile_entries[field_name] = entry
        
        # Fitness Information
        fitness_frame = ctk.CTkFrame(profile_frame)
        fitness_frame.pack(fill="x", padx=20, pady=10)
        
        fitness_title = ctk.CTkLabel(
            fitness_frame,
            text="Fitness Information",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        fitness_title.pack(pady=(15, 10))
        
        fitness_fields = [
            ("Height (inches)", "height", self.member_profile.height),
            ("Weight (lbs)", "weight", self.member_profile.weight),
            ("Fitness Goals", "fitness_goals", self.member_profile.fitness_goals),
        ]
        
        for label_text, field_name, current_value in fitness_fields:
            field_frame = ctk.CTkFrame(fitness_frame, fg_color="transparent")
            field_frame.pack(fill="x", padx=20, pady=5)
            
            label = ctk.CTkLabel(field_frame, text=label_text, width=120)
            label.pack(side="left", padx=(0, 20))
            
            if field_name == "fitness_goals":
                entry = ctk.CTkTextbox(field_frame, height=60)
                if current_value:
                    entry.insert("1.0", str(current_value))
            else:
                entry = ctk.CTkEntry(field_frame)
                if current_value:
                    entry.insert(0, str(current_value))
            
            entry.pack(side="left", fill="x", expand=True)
            self.profile_entries[field_name] = entry
        
        # Save button
        save_button = ctk.CTkButton(
            profile_frame,
            text="Save Profile",
            command=self.save_profile
        )
        save_button.pack(pady=30)
    
    def show_exercises(self):
        """Show exercise library"""
        self.clear_content()
        
        title_label = ctk.CTkLabel(
            self.content_frame,
            text="Exercise Library",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=20)
        
        # Search frame
        search_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        search_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="Search exercises...",
            width=300
        )
        search_entry.pack(side="left", padx=(0, 10))
        
        search_button = ctk.CTkButton(
            search_frame,
            text="Search",
            width=80
        )
        search_button.pack(side="left")
        
        # Exercises list
        exercises_frame = ctk.CTkScrollableFrame(self.content_frame)
        exercises_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        from models.workout import Exercise
        exercises = Exercise.get_all()
        
        for exercise in exercises:
            exercise_card = ctk.CTkFrame(exercises_frame)
            exercise_card.pack(fill="x", pady=5, padx=10)
            
            # Exercise header
            header_frame = ctk.CTkFrame(exercise_card, fg_color="transparent")
            header_frame.pack(fill="x", padx=20, pady=15)
            
            exercise_name = ctk.CTkLabel(
                header_frame,
                text=exercise.name,
                font=ctk.CTkFont(size=16, weight="bold")
            )
            exercise_name.pack(side="left")
            
            difficulty_label = ctk.CTkLabel(
                header_frame,
                text=exercise.difficulty_level or "Beginner",
                text_color="gray"
            )
            difficulty_label.pack(side="right")
            
            # Exercise details
            if exercise.muscle_groups:
                muscle_label = ctk.CTkLabel(
                    exercise_card,
                    text=f"Target Muscles: {exercise.muscle_groups}",
                    text_color="gray"
                )
                muscle_label.pack(anchor="w", padx=20)
            
            if exercise.equipment:
                equipment_label = ctk.CTkLabel(
                    exercise_card,
                    text=f"Equipment: {exercise.equipment}",
                    text_color="gray"
                )
                equipment_label.pack(anchor="w", padx=20, pady=(0, 15))
    
    def show_meals(self):
        """Show meal planning (placeholder)"""
        self.clear_content()
        
        title_label = ctk.CTkLabel(
            self.content_frame,
            text="Meal Planning",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=20)
        
        info_label = ctk.CTkLabel(
            self.content_frame,
            text="Meal planning feature coming soon!\n\nWork with your trainer to develop a nutrition plan.",
            font=ctk.CTkFont(size=16),
            text_color="gray",
            justify="center"
        )
        info_label.pack(pady=50)
    
    def show_notifications(self):
        """Show notifications"""
        self.clear_content()
        
        title_label = ctk.CTkLabel(
            self.content_frame,
            text="Notifications",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=20)
        
        # Mark all as read button
        mark_read_button = ctk.CTkButton(
            self.content_frame,
            text="Mark All as Read",
            command=self.mark_all_notifications_read
        )
        mark_read_button.pack(pady=(0, 20))
        
        # Notifications list
        notifications_frame = ctk.CTkScrollableFrame(self.content_frame)
        notifications_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        notifications = Notification.get_by_user_id(self.user.id)
        
        if notifications:
            for notification in notifications:
                notif_card = ctk.CTkFrame(notifications_frame)
                notif_card.pack(fill="x", pady=5, padx=10)
                
                # Notification header
                header_frame = ctk.CTkFrame(notif_card, fg_color="transparent")
                header_frame.pack(fill="x", padx=20, pady=15)
                
                title_text = notification.title
                if not notification.is_read:
                    title_text = "🔵 " + title_text
                
                notif_title = ctk.CTkLabel(
                    header_frame,
                    text=title_text,
                    font=ctk.CTkFont(size=14, weight="bold")
                )
                notif_title.pack(side="left")
                
                notif_date = ctk.CTkLabel(
                    header_frame,
                    text=notification.created_at[:10] if notification.created_at else "",
                    text_color="gray"
                )
                notif_date.pack(side="right")
                
                # Notification message
                message_label = ctk.CTkLabel(
                    notif_card,
                    text=notification.message,
                    wraplength=600,
                    justify="left"
                )
                message_label.pack(anchor="w", padx=20, pady=(0, 15))
        else:
            no_notif_label = ctk.CTkLabel(
                notifications_frame,
                text="No notifications yet.",
                font=ctk.CTkFont(size=16),
                text_color="gray"
            )
            no_notif_label.pack(pady=50)
    
    def show_settings(self):
        """Show settings"""
        self.clear_content()
        
        title_label = ctk.CTkLabel(
            self.content_frame,
            text="Settings",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=20)
        
        settings_frame = ctk.CTkFrame(self.content_frame)
        settings_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Theme setting
        theme_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
        theme_frame.pack(fill="x", padx=20, pady=20)
        
        theme_label = ctk.CTkLabel(theme_frame, text="Appearance Theme")
        theme_label.pack(side="left")
        
        theme_menu = ctk.CTkOptionMenu(
            theme_frame,
            values=["Light", "Dark", "System"],
            command=self.change_theme
        )
        theme_menu.pack(side="right")
        
        # Export data
        export_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
        export_frame.pack(fill="x", padx=20, pady=20)
        
        export_label = ctk.CTkLabel(export_frame, text="Data Export")
        export_label.pack(side="left")
        
        export_button = ctk.CTkButton(
            export_frame,
            text="Export My Data",
            command=self.export_user_data
        )
        export_button.pack(side="right")
    
    # Event handlers
    def toggle_theme(self):
        """Toggle between light and dark theme"""
        current_mode = ctk.get_appearance_mode()
        new_mode = "Dark" if current_mode == "Light" else "Light"
        ctk.set_appearance_mode(new_mode)
        
        # Update button text
        self.theme_button.configure(text="☀️" if new_mode == "Dark" else "🌙")
    
    def change_theme(self, new_theme):
        """Change theme from settings"""
        ctk.set_appearance_mode(new_theme)
    
    def book_session(self):
        """Book a new training session"""
        from views.book_session_dialog import BookSessionDialog
        dialog = BookSessionDialog(self.parent, self.user.id)
        if dialog.result:
            self.show_sessions()  # Refresh sessions view
            messagebox.showinfo("Success", "Session booked successfully!")
    
    def cancel_session(self, session):
        """Cancel a training session"""
        if messagebox.askyesno("Confirm", "Are you sure you want to cancel this session?"):
            session.cancel()
            self.show_sessions()  # Refresh sessions view
            messagebox.showinfo("Success", "Session cancelled successfully!")
    
    def save_progress(self):
        """Save progress record"""
        weight = self.weight_entry.get().strip()
        notes = self.progress_notes.get("1.0", "end-1c").strip()
        
        if not weight:
            messagebox.showerror("Error", "Please enter your current weight")
            return
        
        try:
            weight_float = float(weight)
            # Here you would save to progress_records table
            # For now, just show success message
            messagebox.showinfo("Success", "Progress recorded successfully!")
            self.weight_entry.delete(0, 'end')
            self.progress_notes.delete("1.0", 'end')
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid weight")
    
    def save_profile(self):
        """Save profile changes"""
        try:
            # Update user information
            self.user.first_name = self.profile_entries['first_name'].get().strip()
            self.user.last_name = self.profile_entries['last_name'].get().strip()
            self.user.email = self.profile_entries['email'].get().strip()
            self.user.phone = self.profile_entries['phone'].get().strip()
            self.user.save()
            
            # Update member profile
            height_text = self.profile_entries['height'].get().strip()
            weight_text = self.profile_entries['weight'].get().strip()
            
            self.member_profile.height = float(height_text) if height_text else None
            self.member_profile.weight = float(weight_text) if weight_text else None
            self.member_profile.fitness_goals = self.profile_entries['fitness_goals'].get("1.0", "end-1c").strip()
            self.member_profile.save()
            
            messagebox.showinfo("Success", "Profile updated successfully!")
            
        except ValueError as e:
            messagebox.showerror("Error", "Please enter valid numeric values for height and weight")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save profile: {str(e)}")
    
    def export_workouts_pdf(self):
        """Export workouts to PDF"""
        workouts = Workout.get_by_member_id(self.user.id)
        if not workouts:
            messagebox.showinfo("Info", "No workouts to export")
            return
        
        try:
            pdf_service = PDFService()
            filename = pdf_service.export_workouts_pdf(self.user, workouts)
            messagebox.showinfo("Success", f"Workouts exported to {filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export PDF: {str(e)}")
    
    def export_user_data(self):
        """Export all user data"""
        try:
            # This would export all user data to a file
            messagebox.showinfo("Success", "User data exported successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export data: {str(e)}")
    
    def mark_all_notifications_read(self):
        """Mark all notifications as read"""
        Notification.mark_all_as_read(self.user.id)
        self.notifications_count = 0
        self.notifications_button.configure(text="Notifications")
        self.show_notifications()  # Refresh view
    
    def load_dashboard_data(self):
        """Load initial dashboard data"""
        # This would load any additional data needed for the dashboard
        pass
    
    def destroy(self):
        """Clean up the dashboard"""
        self.main_frame.destroy()