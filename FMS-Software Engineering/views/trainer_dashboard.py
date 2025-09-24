import customtkinter as ctk
from tkinter import messagebox
import tkinter as tk
from datetime import datetime, timedelta
from models.user import User, MemberProfile, TrainerProfile
from models.workout import Workout, Exercise
from models.session import Session
from models.notification import Notification
from services.pdf_service import PDFService
import json

class TrainerDashboard:
    def __init__(self, parent, user_data, logout_callback):
        self.parent = parent
        self.user_data = user_data
        self.logout_callback = logout_callback
        self.user = User.get_by_id(user_data['id'])
        self.trainer_profile = TrainerProfile.get_by_user_id(user_data['id'])
        
        self.setup_ui()
        self.load_dashboard_data()
    
    def setup_ui(self):
        """Setup trainer dashboard interface"""
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
        """Setup header with trainer info and notifications"""
        header_frame = ctk.CTkFrame(self.main_frame, height=80)
        header_frame.pack(fill="x", padx=10, pady=(10, 0))
        header_frame.pack_propagate(False)
        
        # Welcome message
        welcome_label = ctk.CTkLabel(
            header_frame,
            text=f"Trainer Dashboard - {self.user.first_name}",
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
            ("👥 My Clients", self.show_clients),
            ("📅 Sessions", self.show_sessions),
            ("💪 Create Workout", self.show_create_workout),
            ("📊 Client Progress", self.show_client_progress),
            ("📋 Reports", self.show_reports),
            ("👤 Profile", self.show_profile),
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
        """Show trainer dashboard overview"""
        self.clear_content()
        
        # Title
        title_label = ctk.CTkLabel(
            self.content_frame,
            text="Trainer Dashboard",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=(20, 30))
        
        # Stats cards
        stats_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        stats_frame.pack(fill="x", padx=20, pady=(0, 30))
        
        # Get trainer stats
        my_clients = self.get_trainer_clients()
        my_sessions = Session.get_by_trainer_id(self.user.id)
        upcoming_sessions = Session.get_upcoming_sessions(self.user.id, 'trainer')
        total_revenue = sum(s.price for s in my_sessions if s.price and s.status == 'completed')
        
        self.create_stat_card(stats_frame, "Total Clients", str(len(my_clients)), "👥").pack(side="left", padx=10, fill="x", expand=True)
        self.create_stat_card(stats_frame, "Upcoming Sessions", str(len(upcoming_sessions)), "📅").pack(side="left", padx=10, fill="x", expand=True)
        self.create_stat_card(stats_frame, "Total Sessions", str(len(my_sessions)), "💪").pack(side="left", padx=10, fill="x", expand=True)
        self.create_stat_card(stats_frame, "Total Revenue", f"${total_revenue:.2f}", "💰").pack(side="left", padx=10, fill="x", expand=True)
        
        # Today's schedule
        schedule_frame = ctk.CTkFrame(self.content_frame)
        schedule_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        schedule_title = ctk.CTkLabel(
            schedule_frame,
            text="Today's Schedule",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        schedule_title.pack(pady=20)
        
        # Today's sessions
        today = datetime.now().date()
        today_sessions = [s for s in upcoming_sessions if s.session_date and s.session_date.startswith(today.strftime('%Y-%m-%d'))]
        
        if today_sessions:
            for session in today_sessions:
                session_frame = ctk.CTkFrame(schedule_frame)
                session_frame.pack(fill="x", padx=20, pady=5)
                
                member = User.get_by_id(session.member_id)
                
                session_info = ctk.CTkLabel(
                    session_frame,
                    text=f"{session.session_date[11:16]} - {member.full_name if member else 'Unknown'} ({session.session_type or 'Training'})",
                    font=ctk.CTkFont(size=14)
                )
                session_info.pack(side="left", padx=20, pady=15)
                
                complete_button = ctk.CTkButton(
                    session_frame,
                    text="Mark Complete",
                    width=120,
                    command=lambda s=session: self.complete_session(s)
                )
                complete_button.pack(side="right", padx=20, pady=10)
        else:
            no_sessions_label = ctk.CTkLabel(
                schedule_frame,
                text="No sessions scheduled for today",
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
    
    def show_clients(self):
        """Show trainer's clients"""
        self.clear_content()
        
        # Title and add client button
        header_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=20)
        
        title_label = ctk.CTkLabel(
            header_frame,
            text="My Clients",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(side="left")
        
        # Clients list
        clients_frame = ctk.CTkScrollableFrame(self.content_frame)
        clients_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        clients = self.get_trainer_clients()
        
        if clients:
            for client in clients:
                client_card = ctk.CTkFrame(clients_frame)
                client_card.pack(fill="x", pady=10, padx=10)
                
                # Client info
                info_frame = ctk.CTkFrame(client_card, fg_color="transparent")
                info_frame.pack(fill="x", padx=20, pady=15)
                
                client_name = ctk.CTkLabel(
                    info_frame,
                    text=client.full_name,
                    font=ctk.CTkFont(size=16, weight="bold")
                )
                client_name.pack(side="left")
                
                # Client details
                details_frame = ctk.CTkFrame(client_card, fg_color="transparent")
                details_frame.pack(fill="x", padx=20, pady=(0, 15))
                
                email_label = ctk.CTkLabel(
                    details_frame,
                    text=f"Email: {client.email or 'Not provided'}",
                    text_color="gray"
                )
                email_label.pack(anchor="w")
                
                phone_label = ctk.CTkLabel(
                    details_frame,
                    text=f"Phone: {client.phone or 'Not provided'}",
                    text_color="gray"
                )
                phone_label.pack(anchor="w")
                
                # Action buttons
                button_frame = ctk.CTkFrame(client_card, fg_color="transparent")
                button_frame.pack(fill="x", padx=20, pady=(0, 15))
                
                view_progress_button = ctk.CTkButton(
                    button_frame,
                    text="View Progress",
                    width=120,
                    command=lambda c=client: self.view_client_progress(c)
                )
                view_progress_button.pack(side="left", padx=(0, 10))
                
                create_workout_button = ctk.CTkButton(
                    button_frame,
                    text="Create Workout",
                    width=120,
                    command=lambda c=client: self.create_client_workout(c)
                )
                create_workout_button.pack(side="left")
        else:
            no_clients_label = ctk.CTkLabel(
                clients_frame,
                text="No clients assigned yet.",
                font=ctk.CTkFont(size=16),
                text_color="gray"
            )
            no_clients_label.pack(pady=50)
    
    def show_sessions(self):
        """Show trainer's sessions"""
        self.clear_content()
        
        # Title and session management
        header_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=20)
        
        title_label = ctk.CTkLabel(
            header_frame,
            text="Training Sessions",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(side="left")
        
        # Sessions list
        sessions_frame = ctk.CTkScrollableFrame(self.content_frame)
        sessions_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        sessions = Session.get_by_trainer_id(self.user.id)
        
        if sessions:
            # Group by status
            upcoming = [s for s in sessions if s.status == 'scheduled']
            completed = [s for s in sessions if s.status == 'completed']
            
            # Show upcoming sessions first
            if upcoming:
                upcoming_label = ctk.CTkLabel(
                    sessions_frame,
                    text="Upcoming Sessions",
                    font=ctk.CTkFont(size=18, weight="bold")
                )
                upcoming_label.pack(anchor="w", pady=(20, 10))
                
                for session in upcoming:
                    self.create_session_card(sessions_frame, session, is_trainer=True)
            
            # Show completed sessions
            if completed:
                completed_label = ctk.CTkLabel(
                    sessions_frame,
                    text="Recent Completed Sessions",
                    font=ctk.CTkFont(size=18, weight="bold")
                )
                completed_label.pack(anchor="w", pady=(20, 10))
                
                for session in completed[:10]:  # Show last 10 completed
                    self.create_session_card(sessions_frame, session, is_trainer=True)
        else:
            no_sessions_label = ctk.CTkLabel(
                sessions_frame,
                text="No training sessions yet.",
                font=ctk.CTkFont(size=16),
                text_color="gray"
            )
            no_sessions_label.pack(pady=50)
    
    def create_session_card(self, parent, session, is_trainer=False):
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
        
        # Get member info
        member = User.get_by_id(session.member_id)
        client_name = member.full_name if member else "Unknown Client"
        
        # Session info
        session_info = f"{client_name} - {session.session_type or 'Training Session'}"
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
        
        # Action buttons for trainer
        if is_trainer and session.status == 'scheduled':
            button_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
            button_frame.pack(side="right", padx=(0, 20))
            
            complete_button = ctk.CTkButton(
                button_frame,
                text="Complete",
                width=80,
                fg_color="green",
                hover_color="dark green",
                command=lambda s=session: self.complete_session(s)
            )
            complete_button.pack(side="left", padx=(0, 5))
            
            cancel_button = ctk.CTkButton(
                button_frame,
                text="Cancel",
                width=80,
                fg_color="red",
                hover_color="dark red",
                command=lambda s=session: self.cancel_session(s)
            )
            cancel_button.pack(side="left")
    
    def show_create_workout(self):
        """Show workout creation interface"""
        self.clear_content()
        
        title_label = ctk.CTkLabel(
            self.content_frame,
            text="Create Workout Plan",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=(20, 30))
        
        # Create workout form
        form_frame = ctk.CTkFrame(self.content_frame)
        form_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Client selection
        client_label = ctk.CTkLabel(form_frame, text="Select Client")
        client_label.pack(anchor="w", padx=20, pady=(20, 5))
        
        clients = self.get_trainer_clients()
        client_names = [f"{client.full_name} (ID: {client.id})" for client in clients]
        
        self.client_menu = ctk.CTkOptionMenu(
            form_frame,
            values=client_names if client_names else ["No clients available"],
            width=400
        )
        self.client_menu.pack(padx=20, pady=(0, 15))
        
        # Workout name
        name_label = ctk.CTkLabel(form_frame, text="Workout Name")
        name_label.pack(anchor="w", padx=20, pady=(0, 5))
        
        self.workout_name_entry = ctk.CTkEntry(
            form_frame,
            placeholder_text="Enter workout name",
            width=400
        )
        self.workout_name_entry.pack(padx=20, pady=(0, 15))
        
        # Description
        desc_label = ctk.CTkLabel(form_frame, text="Description")
        desc_label.pack(anchor="w", padx=20, pady=(0, 5))
        
        self.workout_desc_textbox = ctk.CTkTextbox(
            form_frame,
            height=80,
            width=400
        )
        self.workout_desc_textbox.pack(padx=20, pady=(0, 15))
        
        # Exercise selection
        exercise_label = ctk.CTkLabel(form_frame, text="Add Exercises")
        exercise_label.pack(anchor="w", padx=20, pady=(0, 5))
        
        # Exercise list frame
        self.exercise_list_frame = ctk.CTkScrollableFrame(form_frame, height=200)
        self.exercise_list_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        self.selected_exercises = []
        
        # Add exercise button
        add_exercise_button = ctk.CTkButton(
            form_frame,
            text="+ Add Exercise",
            command=self.add_exercise_to_workout
        )
        add_exercise_button.pack(pady=10)
        
        # Save workout button
        save_workout_button = ctk.CTkButton(
            form_frame,
            text="Save Workout Plan",
            width=200,
            command=self.save_workout_plan
        )
        save_workout_button.pack(pady=20)
    
    def show_client_progress(self):
        """Show client progress tracking"""
        self.clear_content()
        
        title_label = ctk.CTkLabel(
            self.content_frame,
            text="Client Progress Tracking",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=20)
        
        # Client selection
        client_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        client_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        client_label = ctk.CTkLabel(client_frame, text="Select Client:")
        client_label.pack(side="left", padx=(0, 10))
        
        clients = self.get_trainer_clients()
        client_names = [f"{client.full_name} (ID: {client.id})" for client in clients]
        
        self.progress_client_menu = ctk.CTkOptionMenu(
            client_frame,
            values=client_names if client_names else ["No clients available"],
            width=300,
            command=self.load_client_progress
        )
        self.progress_client_menu.pack(side="left")
        
        # Progress display area
        self.progress_display_frame = ctk.CTkFrame(self.content_frame)
        self.progress_display_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Initial message
        initial_label = ctk.CTkLabel(
            self.progress_display_frame,
            text="Select a client to view their progress",
            font=ctk.CTkFont(size=16),
            text_color="gray"
        )
        initial_label.pack(expand=True, pady=50)
    
    def show_reports(self):
        """Show trainer reports"""
        self.clear_content()
        
        title_label = ctk.CTkLabel(
            self.content_frame,
            text="Training Reports",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=20)
        
        # Reports frame
        reports_frame = ctk.CTkFrame(self.content_frame)
        reports_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Report generation buttons
        button_frame = ctk.CTkFrame(reports_frame, fg_color="transparent")
        button_frame.pack(pady=30)
        
        client_report_button = ctk.CTkButton(
            button_frame,
            text="📄 Generate Client Report",
            width=200,
            height=50,
            command=self.generate_client_report
        )
        client_report_button.pack(pady=10)
        
        session_report_button = ctk.CTkButton(
            button_frame,
            text="📊 Generate Session Report",
            width=200,
            height=50,
            command=self.generate_session_report
        )
        session_report_button.pack(pady=10)
        
        revenue_report_button = ctk.CTkButton(
            button_frame,
            text="💰 Generate Revenue Report",
            width=200,
            height=50,
            command=self.generate_revenue_report
        )
        revenue_report_button.pack(pady=10)
    
    def show_profile(self):
        """Show trainer profile management"""
        self.clear_content()
        
        title_label = ctk.CTkLabel(
            self.content_frame,
            text="Trainer Profile",
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
        
        # Professional Information
        professional_frame = ctk.CTkFrame(profile_frame)
        professional_frame.pack(fill="x", padx=20, pady=10)
        
        professional_title = ctk.CTkLabel(
            professional_frame,
            text="Professional Information",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        professional_title.pack(pady=(15, 10))
        
        prof_fields = [
            ("Specializations", "specializations", self.trainer_profile.specializations),
            ("Certifications", "certifications", self.trainer_profile.certifications),
            ("Experience (years)", "experience_years", self.trainer_profile.experience_years),
            ("Hourly Rate ($)", "hourly_rate", self.trainer_profile.hourly_rate),
        ]
        
        for label_text, field_name, current_value in prof_fields:
            field_frame = ctk.CTkFrame(professional_frame, fg_color="transparent")
            field_frame.pack(fill="x", padx=20, pady=5)
            
            label = ctk.CTkLabel(field_frame, text=label_text, width=120)
            label.pack(side="left", padx=(0, 20))
            
            entry = ctk.CTkEntry(field_frame)
            if current_value:
                entry.insert(0, str(current_value))
            entry.pack(side="left", fill="x", expand=True)
            
            self.profile_entries[field_name] = entry
        
        # Bio
        bio_frame = ctk.CTkFrame(professional_frame, fg_color="transparent")
        bio_frame.pack(fill="x", padx=20, pady=5)
        
        bio_label = ctk.CTkLabel(bio_frame, text="Bio", width=120)
        bio_label.pack(side="left", padx=(0, 20), anchor="n")
        
        self.bio_textbox = ctk.CTkTextbox(bio_frame, height=80)
        if self.trainer_profile.bio:
            self.bio_textbox.insert("1.0", self.trainer_profile.bio)
        self.bio_textbox.pack(side="left", fill="x", expand=True)
        
        # Save button
        save_button = ctk.CTkButton(
            profile_frame,
            text="Save Profile",
            command=self.save_trainer_profile
        )
        save_button.pack(pady=30)
    
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
    
    # Event handlers and helper methods
    def toggle_theme(self):
        """Toggle between light and dark theme"""
        current_mode = ctk.get_appearance_mode()
        new_mode = "Dark" if current_mode == "Light" else "Light"
        ctk.set_appearance_mode(new_mode)
        self.theme_button.configure(text="☀️" if new_mode == "Dark" else "🌙")
    
    def change_theme(self, new_theme):
        """Change theme from settings"""
        ctk.set_appearance_mode(new_theme)
    
    def get_trainer_clients(self):
        """Get clients assigned to this trainer (simplified - in real app would have proper assignment logic)"""
        # For demo purposes, return recent session members
        sessions = Session.get_by_trainer_id(self.user.id)
        member_ids = list(set([s.member_id for s in sessions if s.member_id]))
        
        clients = []
        for member_id in member_ids:
            member = User.get_by_id(member_id)
            if member:
                clients.append(member)
        
        return clients
    
    def complete_session(self, session):
        """Mark session as completed"""
        if messagebox.askyesno("Confirm", "Mark this session as completed?"):
            session.complete()
            
            # Create notification for member
            member = User.get_by_id(session.member_id)
            if member:
                Notification.create_notification(
                    member.id,
                    "Session Completed",
                    f"Your {session.session_type or 'training'} session with {self.user.full_name} has been completed.",
                    "success"
                )
            
            messagebox.showinfo("Success", "Session marked as completed!")
            self.show_sessions()  # Refresh view
    
    def cancel_session(self, session):
        """Cancel session"""
        if messagebox.askyesno("Confirm", "Are you sure you want to cancel this session?"):
            session.cancel()
            messagebox.showinfo("Success", "Session cancelled!")
            self.show_sessions()  # Refresh view
    
    def add_exercise_to_workout(self):
        """Add exercise to workout plan"""
        from views.exercise_selection_dialog import ExerciseSelectionDialog
        dialog = ExerciseSelectionDialog(self.parent)
        
        if dialog.result:
            exercise_data = dialog.result
            self.selected_exercises.append(exercise_data)
            self.refresh_exercise_list()
    
    def refresh_exercise_list(self):
        """Refresh the exercise list display"""
        # Clear current display
        for widget in self.exercise_list_frame.winfo_children():
            widget.destroy()
        
        # Display selected exercises
        for i, exercise in enumerate(self.selected_exercises):
            exercise_frame = ctk.CTkFrame(self.exercise_list_frame)
            exercise_frame.pack(fill="x", pady=2)
            
            exercise_label = ctk.CTkLabel(
                exercise_frame,
                text=f"{exercise['name']} - Sets: {exercise['sets']}, Reps: {exercise['reps']}",
                font=ctk.CTkFont(size=12)
            )
            exercise_label.pack(side="left", padx=10, pady=5)
            
            remove_button = ctk.CTkButton(
                exercise_frame,
                text="Remove",
                width=60,
                height=25,
                command=lambda idx=i: self.remove_exercise(idx)
            )
            remove_button.pack(side="right", padx=10, pady=5)
    
    def remove_exercise(self, index):
        """Remove exercise from workout plan"""
        if 0 <= index < len(self.selected_exercises):
            self.selected_exercises.pop(index)
            self.refresh_exercise_list()
    
    def save_workout_plan(self):
        """Save the workout plan"""
        # Get client ID
        client_selection = self.client_menu.get()
        if client_selection == "No clients available":
            messagebox.showerror("Error", "No client selected")
            return
        
        try:
            client_id = int(client_selection.split("ID: ")[1].split(")")[0])
        except (IndexError, ValueError):
            messagebox.showerror("Error", "Please select a valid client")
            return
        
        workout_name = self.workout_name_entry.get().strip()
        if not workout_name:
            messagebox.showerror("Error", "Please enter a workout name")
            return
        
        workout_description = self.workout_desc_textbox.get("1.0", "end-1c").strip()
        
        # Create workout
        workout = Workout(
            member_id=client_id,
            trainer_id=self.user.id,
            name=workout_name,
            description=workout_description,
            exercises=self.selected_exercises
        )
        
        try:
            workout.save()
            
            # Create notification for client
            client = User.get_by_id(client_id)
            if client:
                Notification.create_notification(
                    client_id,
                    "New Workout Plan",
                    f"Your trainer {self.user.full_name} has created a new workout plan: {workout_name}",
                    "info"
                )
            
            messagebox.showinfo("Success", "Workout plan created successfully!")
            
            # Clear form
            self.workout_name_entry.delete(0, 'end')
            self.workout_desc_textbox.delete("1.0", 'end')
            self.selected_exercises = []
            self.refresh_exercise_list()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save workout: {str(e)}")
    
    def view_client_progress(self, client):
        """View specific client's progress"""
        self.show_client_progress()
        # Select the client in the dropdown
        client_text = f"{client.full_name} (ID: {client.id})"
        self.progress_client_menu.set(client_text)
        self.load_client_progress(client_text)
    
    def create_client_workout(self, client):
        """Create workout for specific client"""
        self.show_create_workout()
        # Select the client in the dropdown
        client_text = f"{client.full_name} (ID: {client.id})"
        self.client_menu.set(client_text)
    
    def load_client_progress(self, client_selection):
        """Load and display client progress"""
        # Clear current display
        for widget in self.progress_display_frame.winfo_children():
            widget.destroy()
        
        if client_selection == "No clients available":
            no_data_label = ctk.CTkLabel(
                self.progress_display_frame,
                text="No clients available",
                font=ctk.CTkFont(size=16),
                text_color="gray"
            )
            no_data_label.pack(expand=True, pady=50)
            return
        
        try:
            client_id = int(client_selection.split("ID: ")[1].split(")")[0])
            client = User.get_by_id(client_id)
            
            if not client:
                return
            
            # Display client info
            client_info_frame = ctk.CTkFrame(self.progress_display_frame)
            client_info_frame.pack(fill="x", padx=20, pady=20)
            
            client_title = ctk.CTkLabel(
                client_info_frame,
                text=f"Progress for {client.full_name}",
                font=ctk.CTkFont(size=18, weight="bold")
            )
            client_title.pack(pady=15)
            
            # Progress placeholder (would integrate with progress_records table in full implementation)
            progress_info = ctk.CTkLabel(
                self.progress_display_frame,
                text="Progress tracking data would be displayed here\nwith charts and measurements over time.",
                font=ctk.CTkFont(size=14),
                text_color="gray"
            )
            progress_info.pack(expand=True, pady=20)
            
        except (IndexError, ValueError):
            error_label = ctk.CTkLabel(
                self.progress_display_frame,
                text="Error loading client data",
                font=ctk.CTkFont(size=16),
                text_color="red"
            )
            error_label.pack(expand=True, pady=50)
    
    def generate_client_report(self):
        """Generate client report PDF"""
        try:
            clients = self.get_trainer_clients()
            sessions = Session.get_by_trainer_id(self.user.id)
            
            pdf_service = PDFService()
            filename = pdf_service.export_trainer_report_pdf(self.user, clients, sessions)
            messagebox.showinfo("Success", f"Client report generated: {filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate report: {str(e)}")
    
    def generate_session_report(self):
        """Generate session report"""
        messagebox.showinfo("Info", "Session report generation feature coming soon!")
    
    def generate_revenue_report(self):
        """Generate revenue report"""
        sessions = Session.get_by_trainer_id(self.user.id)
        total_revenue = sum(s.price for s in sessions if s.price and s.status == 'completed')
        completed_sessions = len([s for s in sessions if s.status == 'completed'])
        
        messagebox.showinfo(
            "Revenue Report",
            f"Total Completed Sessions: {completed_sessions}\nTotal Revenue: ${total_revenue:.2f}\nAverage per Session: ${total_revenue/completed_sessions if completed_sessions > 0 else 0:.2f}"
        )
    
    def save_trainer_profile(self):
        """Save trainer profile changes"""
        try:
            # Update user information
            self.user.first_name = self.profile_entries['first_name'].get().strip()
            self.user.last_name = self.profile_entries['last_name'].get().strip()
            self.user.email = self.profile_entries['email'].get().strip()
            self.user.phone = self.profile_entries['phone'].get().strip()
            self.user.save()
            
            # Update trainer profile
            self.trainer_profile.specializations = self.profile_entries['specializations'].get().strip()
            self.trainer_profile.certifications = self.profile_entries['certifications'].get().strip()
            
            exp_text = self.profile_entries['experience_years'].get().strip()
            rate_text = self.profile_entries['hourly_rate'].get().strip()
            
            self.trainer_profile.experience_years = int(exp_text) if exp_text else None
            self.trainer_profile.hourly_rate = float(rate_text) if rate_text else None
            self.trainer_profile.bio = self.bio_textbox.get("1.0", "end-1c").strip()
            
            self.trainer_profile.save()
            
            messagebox.showinfo("Success", "Profile updated successfully!")
            
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numeric values for experience and hourly rate")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save profile: {str(e)}")
    
    def mark_all_notifications_read(self):
        """Mark all notifications as read"""
        Notification.mark_all_as_read(self.user.id)
        self.notifications_count = 0
        self.notifications_button.configure(text="Notifications")
        self.show_notifications()  # Refresh view
    
    def load_dashboard_data(self):
        """Load dashboard data"""
        pass
    
    def destroy(self):
        """Clean up the dashboard"""
        self.main_frame.destroy()