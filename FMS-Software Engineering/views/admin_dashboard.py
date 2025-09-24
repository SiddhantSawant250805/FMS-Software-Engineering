import customtkinter as ctk
from tkinter import messagebox
import tkinter as tk
from datetime import datetime, timedelta
from models.user import User, MemberProfile, TrainerProfile
from models.workout import Workout, Exercise
from models.session import Session, FitnessClass
from models.notification import Notification
from services.pdf_service import PDFService

class AdminDashboard:
    def __init__(self, parent, user_data, logout_callback):
        self.parent = parent
        self.user_data = user_data
        self.logout_callback = logout_callback
        self.user = User.get_by_id(user_data['id'])
        
        self.setup_ui()
        self.load_dashboard_data()
    
    def setup_ui(self):
        """Setup admin dashboard interface"""
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
        """Setup header with admin info and controls"""
        header_frame = ctk.CTkFrame(self.main_frame, height=80)
        header_frame.pack(fill="x", padx=10, pady=(10, 0))
        header_frame.pack_propagate(False)
        
        # Welcome message
        welcome_label = ctk.CTkLabel(
            header_frame,
            text=f"Admin Dashboard - {self.user.first_name}",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        welcome_label.pack(side="left", padx=20, pady=20)
        
        # Header buttons
        button_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        button_frame.pack(side="right", padx=20, pady=20)
        
        # System notifications
        system_notif_button = ctk.CTkButton(
            button_frame,
            text="📢 System Alerts",
            width=120,
            command=self.show_system_alerts
        )
        system_notif_button.pack(side="left", padx=(0, 10))
        
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
        sidebar_frame = ctk.CTkFrame(self.main_frame, width=220)
        sidebar_frame.pack(side="left", fill="y", padx=(10, 0), pady=10)
        sidebar_frame.pack_propagate(False)
        
        # Navigation buttons
        nav_buttons = [
            ("🏠 Dashboard", self.show_dashboard),
            ("👥 User Management", self.show_user_management),
            ("🏋️ Trainer Management", self.show_trainer_management),
            ("🏃 Member Management", self.show_member_management),
            ("🎯 Class Management", self.show_class_management),
            ("📊 Reports & Analytics", self.show_reports),
            ("💳 Payment Management", self.show_payments),
            ("📋 Exercise Library", self.show_exercise_management),
            ("📢 Notifications", self.show_notification_management),
            ("⚙️ System Settings", self.show_system_settings),
        ]
        
        for text, command in nav_buttons:
            button = ctk.CTkButton(
                sidebar_frame,
                text=text,
                width=200,
                height=40,
                anchor="w",
                command=command
            )
            button.pack(padx=10, pady=3)
    
    def clear_content(self):
        """Clear content frame"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
    
    def show_dashboard(self):
        """Show admin dashboard overview"""
        self.clear_content()
        
        # Title
        title_label = ctk.CTkLabel(
            self.content_frame,
            text="System Overview",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=(20, 30))
        
        # Stats cards row 1
        stats_frame_1 = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        stats_frame_1.pack(fill="x", padx=20, pady=(0, 20))
        
        # Get system stats
        total_members = len(User.get_all_by_type('member'))
        total_trainers = len(User.get_all_by_type('trainer'))
        total_sessions = len(Session.get_by_trainer_id(0))  # All sessions
        active_classes = len(FitnessClass.get_all_active())
        
        self.create_stat_card(stats_frame_1, "Total Members", str(total_members), "👥").pack(side="left", padx=10, fill="x", expand=True)
        self.create_stat_card(stats_frame_1, "Active Trainers", str(total_trainers), "🏋️").pack(side="left", padx=10, fill="x", expand=True)
        self.create_stat_card(stats_frame_1, "Total Sessions", str(len(Session.get_by_member_id(0))), "📅").pack(side="left", padx=10, fill="x", expand=True)
        self.create_stat_card(stats_frame_1, "Active Classes", str(active_classes), "🎯").pack(side="left", padx=10, fill="x", expand=True)
        
        # Recent activity section
        activity_frame = ctk.CTkFrame(self.content_frame)
        activity_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        activity_title = ctk.CTkLabel(
            activity_frame,
            text="Recent System Activity",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        activity_title.pack(pady=20)
        
        # Activity list (simplified for demo)
        activities = [
            "New member registration: John Doe",
            "Session completed: Personal Training",
            "New class created: Morning Yoga",
            "Trainer profile updated: Jane Smith",
            "Payment processed: $75.00"
        ]
        
        for activity in activities:
            activity_item = ctk.CTkFrame(activity_frame)
            activity_item.pack(fill="x", padx=20, pady=2)
            
            activity_label = ctk.CTkLabel(
                activity_item,
                text=f"• {activity}",
                font=ctk.CTkFont(size=12)
            )
            activity_label.pack(side="left", padx=15, pady=8)
            
            time_label = ctk.CTkLabel(
                activity_item,
                text="Just now",
                text_color="gray",
                font=ctk.CTkFont(size=10)
            )
            time_label.pack(side="right", padx=15, pady=8)
    
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
    
    def show_user_management(self):
        """Show user management interface"""
        self.clear_content()
        
        # Title and add user button
        header_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=20)
        
        title_label = ctk.CTkLabel(
            header_frame,
            text="User Management",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(side="left")
        
        add_user_button = ctk.CTkButton(
            header_frame,
            text="➕ Add New User",
            command=self.add_new_user
        )
        add_user_button.pack(side="right")
        
        # Filter tabs
        filter_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        filter_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        # User type filter
        self.user_filter = ctk.CTkSegmentedButton(
            filter_frame,
            values=["All Users", "Members", "Trainers", "Admins"],
            command=self.filter_users
        )
        self.user_filter.set("All Users")
        self.user_filter.pack(side="left")
        
        # Search
        search_frame = ctk.CTkFrame(filter_frame, fg_color="transparent")
        search_frame.pack(side="right")
        
        self.search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="Search users...",
            width=200
        )
        self.search_entry.pack(side="left", padx=(0, 10))
        
        search_button = ctk.CTkButton(
            search_frame,
            text="🔍",
            width=40,
            command=self.search_users
        )
        search_button.pack(side="left")
        
        # Users list
        self.users_frame = ctk.CTkScrollableFrame(self.content_frame)
        self.users_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        self.display_users("All Users")
    
    def show_trainer_management(self):
        """Show trainer-specific management"""
        self.clear_content()
        
        title_label = ctk.CTkLabel(
            self.content_frame,
            text="Trainer Management",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=20)
        
        # Trainer stats and management interface
        trainers_frame = ctk.CTkFrame(self.content_frame)
        trainers_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Placeholder for trainer management features
        placeholder_label = ctk.CTkLabel(
            trainers_frame,
            text="Trainer Management Features:\n\n• View trainer profiles and certifications\n• Assign trainers to classes\n• Monitor trainer performance\n• Manage trainer schedules\n• Review client assignments",
            font=ctk.CTkFont(size=14),
            text_color="gray",
            justify="left"
        )
        placeholder_label.pack(pady=50)
    
    def show_member_management(self):
        """Show member-specific management"""
        self.clear_content()
        
        title_label = ctk.CTkLabel(
            self.content_frame,
            text="Member Management",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=20)
        
        # Member management interface
        members_frame = ctk.CTkFrame(self.content_frame)
        members_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Placeholder for member management features
        placeholder_label = ctk.CTkLabel(
            members_frame,
            text="Member Management Features:\n\n• View member profiles and fitness goals\n• Monitor membership status\n• Track member progress\n• Manage member payments\n• Send targeted communications",
            font=ctk.CTkFont(size=14),
            text_color="gray",
            justify="left"
        )
        placeholder_label.pack(pady=50)
    
    def show_class_management(self):
        """Show fitness class management"""
        self.clear_content()
        
        # Title and add class button
        header_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=20)
        
        title_label = ctk.CTkLabel(
            header_frame,
            text="Class Management",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(side="left")
        
        add_class_button = ctk.CTkButton(
            header_frame,
            text="➕ Create New Class",
            command=self.create_new_class
        )
        add_class_button.pack(side="right")
        
        # Classes list
        classes_frame = ctk.CTkScrollableFrame(self.content_frame)
        classes_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Display existing classes
        classes = FitnessClass.get_all_active()
        
        if classes:
            for fitness_class in classes:
                class_card = ctk.CTkFrame(classes_frame)
                class_card.pack(fill="x", pady=10, padx=10)
                
                # Class info
                info_frame = ctk.CTkFrame(class_card, fg_color="transparent")
                info_frame.pack(fill="x", padx=20, pady=15)
                
                class_name = ctk.CTkLabel(
                    info_frame,
                    text=fitness_class.name,
                    font=ctk.CTkFont(size=16, weight="bold")
                )
                class_name.pack(side="left")
                
                # Class details
                if fitness_class.description:
                    desc_label = ctk.CTkLabel(
                        class_card,
                        text=fitness_class.description,
                        wraplength=600,
                        justify="left"
                    )
                    desc_label.pack(anchor="w", padx=20, pady=(0, 10))
                
                # Class stats
                stats_frame = ctk.CTkFrame(class_card, fg_color="transparent")
                stats_frame.pack(fill="x", padx=20, pady=(0, 15))
                
                capacity_label = ctk.CTkLabel(
                    stats_frame,
                    text=f"Capacity: {fitness_class.capacity or 'Unlimited'}",
                    text_color="gray"
                )
                capacity_label.pack(side="left")
                
                if fitness_class.price:
                    price_label = ctk.CTkLabel(
                        stats_frame,
                        text=f"Price: ${fitness_class.price:.2f}",
                        text_color="gray"
                    )
                    price_label.pack(side="left", padx=(20, 0))
                
                # Action buttons
                button_frame = ctk.CTkFrame(class_card, fg_color="transparent")
                button_frame.pack(fill="x", padx=20, pady=(0, 15))
                
                edit_button = ctk.CTkButton(
                    button_frame,
                    text="Edit",
                    width=80,
                    command=lambda c=fitness_class: self.edit_class(c)
                )
                edit_button.pack(side="right", padx=(5, 0))
                
                assign_trainer_button = ctk.CTkButton(
                    button_frame,
                    text="Assign Trainer",
                    width=120,
                    command=lambda c=fitness_class: self.assign_trainer_to_class(c)
                )
                assign_trainer_button.pack(side="right", padx=(5, 0))
        else:
            no_classes_label = ctk.CTkLabel(
                classes_frame,
                text="No fitness classes created yet.",
                font=ctk.CTkFont(size=16),
                text_color="gray"
            )
            no_classes_label.pack(pady=50)
    
    def show_reports(self):
        """Show reports and analytics"""
        self.clear_content()
        
        title_label = ctk.CTkLabel(
            self.content_frame,
            text="Reports & Analytics",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=20)
        
        # Reports grid
        reports_frame = ctk.CTkFrame(self.content_frame)
        reports_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Report buttons
        button_grid = ctk.CTkFrame(reports_frame, fg_color="transparent")
        button_grid.pack(expand=True, pady=50)
        
        # Row 1
        row1_frame = ctk.CTkFrame(button_grid, fg_color="transparent")
        row1_frame.pack(pady=10)
        
        user_report_button = ctk.CTkButton(
            row1_frame,
            text="📊 User Activity Report",
            width=200,
            height=50,
            command=self.generate_user_report
        )
        user_report_button.pack(side="left", padx=10)
        
        revenue_report_button = ctk.CTkButton(
            row1_frame,
            text="💰 Revenue Report",
            width=200,
            height=50,
            command=self.generate_revenue_report
        )
        revenue_report_button.pack(side="left", padx=10)
        
        # Row 2
        row2_frame = ctk.CTkFrame(button_grid, fg_color="transparent")
        row2_frame.pack(pady=10)
        
        session_report_button = ctk.CTkButton(
            row2_frame,
            text="📅 Session Analytics",
            width=200,
            height=50,
            command=self.generate_session_report
        )
        session_report_button.pack(side="left", padx=10)
        
        class_report_button = ctk.CTkButton(
            row2_frame,
            text="🎯 Class Performance",
            width=200,
            height=50,
            command=self.generate_class_report
        )
        class_report_button.pack(side="left", padx=10)
    
    def show_payments(self):
        """Show payment management"""
        self.clear_content()
        
        title_label = ctk.CTkLabel(
            self.content_frame,
            text="Payment Management",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=20)
        
        # Payment overview
        payments_frame = ctk.CTkFrame(self.content_frame)
        payments_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Payment stats
        stats_frame = ctk.CTkFrame(payments_frame, fg_color="transparent")
        stats_frame.pack(fill="x", padx=20, pady=20)
        
        # Calculate payment stats (simplified)
        all_sessions = Session.get_by_member_id(0)  # Get all sessions
        total_revenue = sum(s.price for s in all_sessions if s.price and s.status == 'completed')
        pending_payments = sum(s.price for s in all_sessions if s.price and s.status == 'scheduled')
        
        revenue_card = self.create_stat_card(stats_frame, "Total Revenue", f"${total_revenue:.2f}", "💰")
        revenue_card.pack(side="left", padx=10, fill="x", expand=True)
        
        pending_card = self.create_stat_card(stats_frame, "Pending", f"${pending_payments:.2f}", "⏳")
        pending_card.pack(side="left", padx=10, fill="x", expand=True)
        
        # Payment management features
        features_label = ctk.CTkLabel(
            payments_frame,
            text="Payment Management Features:\n\n• Process member payments\n• Manage trainer payouts\n• View payment history\n• Generate invoices\n• Handle refunds and adjustments",
            font=ctk.CTkFont(size=14),
            text_color="gray",
            justify="left"
        )
        features_label.pack(expand=True, pady=20)
    
    def show_exercise_management(self):
        """Show exercise library management"""
        self.clear_content()
        
        # Title and add exercise button
        header_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=20)
        
        title_label = ctk.CTkLabel(
            header_frame,
            text="Exercise Library Management",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(side="left")
        
        add_exercise_button = ctk.CTkButton(
            header_frame,
            text="➕ Add New Exercise",
            command=self.add_new_exercise
        )
        add_exercise_button.pack(side="right")
        
        # Exercises list
        exercises_frame = ctk.CTkScrollableFrame(self.content_frame)
        exercises_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
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
            
            # Edit button
            edit_button = ctk.CTkButton(
                header_frame,
                text="Edit",
                width=60,
                command=lambda e=exercise: self.edit_exercise(e)
            )
            edit_button.pack(side="right")
            
            # Exercise details
            details_frame = ctk.CTkFrame(exercise_card, fg_color="transparent")
            details_frame.pack(fill="x", padx=20, pady=(0, 15))
            
            if exercise.category:
                category_label = ctk.CTkLabel(
                    details_frame,
                    text=f"Category: {exercise.category}",
                    text_color="gray"
                )
                category_label.pack(anchor="w")
            
            if exercise.muscle_groups:
                muscle_label = ctk.CTkLabel(
                    details_frame,
                    text=f"Muscle Groups: {exercise.muscle_groups}",
                    text_color="gray"
                )
                muscle_label.pack(anchor="w")
            
            if exercise.difficulty_level:
                difficulty_label = ctk.CTkLabel(
                    details_frame,
                    text=f"Difficulty: {exercise.difficulty_level}",
                    text_color="gray"
                )
                difficulty_label.pack(anchor="w")
    
    def show_notification_management(self):
        """Show notification management"""
        self.clear_content()
        
        title_label = ctk.CTkLabel(
            self.content_frame,
            text="Notification Management",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=20)
        
        # Send broadcast notification
        broadcast_frame = ctk.CTkFrame(self.content_frame)
        broadcast_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        broadcast_title = ctk.CTkLabel(
            broadcast_frame,
            text="Send Broadcast Notification",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        broadcast_title.pack(pady=(15, 10))
        
        # Notification form
        form_frame = ctk.CTkFrame(broadcast_frame, fg_color="transparent")
        form_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        # Target audience
        audience_label = ctk.CTkLabel(form_frame, text="Send To:")
        audience_label.pack(anchor="w", pady=(0, 5))
        
        self.audience_menu = ctk.CTkOptionMenu(
            form_frame,
            values=["All Users", "Members Only", "Trainers Only"],
            width=200
        )
        self.audience_menu.pack(anchor="w", pady=(0, 10))
        
        # Title
        title_label = ctk.CTkLabel(form_frame, text="Title:")
        title_label.pack(anchor="w", pady=(0, 5))
        
        self.notification_title_entry = ctk.CTkEntry(
            form_frame,
            placeholder_text="Enter notification title",
            width=400
        )
        self.notification_title_entry.pack(anchor="w", pady=(0, 10))
        
        # Message
        message_label = ctk.CTkLabel(form_frame, text="Message:")
        message_label.pack(anchor="w", pady=(0, 5))
        
        self.notification_message_textbox = ctk.CTkTextbox(
            form_frame,
            height=100,
            width=400
        )
        self.notification_message_textbox.pack(anchor="w", pady=(0, 10))
        
        # Send button
        send_button = ctk.CTkButton(
            form_frame,
            text="📢 Send Notification",
            command=self.send_broadcast_notification
        )
        send_button.pack(pady=10)
    
    def show_system_settings(self):
        """Show system settings"""
        self.clear_content()
        
        title_label = ctk.CTkLabel(
            self.content_frame,
            text="System Settings",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=20)
        
        # Settings form
        settings_frame = ctk.CTkFrame(self.content_frame)
        settings_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # System configuration
        config_title = ctk.CTkLabel(
            settings_frame,
            text="System Configuration",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        config_title.pack(pady=(20, 15))
        
        # Settings options
        settings_options = [
            "Default session duration: 60 minutes",
            "Maximum booking advance: 30 days",
            "Automatic session reminders: Enabled",
            "Email notifications: Enabled",
            "Data backup frequency: Daily",
            "Session cancellation policy: 24 hours"
        ]
        
        for option in settings_options:
            option_frame = ctk.CTkFrame(settings_frame)
            option_frame.pack(fill="x", padx=20, pady=2)
            
            option_label = ctk.CTkLabel(
                option_frame,
                text=option,
                font=ctk.CTkFont(size=12)
            )
            option_label.pack(side="left", padx=15, pady=8)
            
            edit_button = ctk.CTkButton(
                option_frame,
                text="Edit",
                width=60,
                height=25
            )
            edit_button.pack(side="right", padx=15, pady=5)
    
    def show_system_alerts(self):
        """Show system alerts and notifications"""
        messagebox.showinfo("System Alerts", "No critical system alerts at this time.\n\nSystem Status: All services operational")
    
    # Event handlers and helper methods
    def toggle_theme(self):
        """Toggle between light and dark theme"""
        current_mode = ctk.get_appearance_mode()
        new_mode = "Dark" if current_mode == "Light" else "Light"
        ctk.set_appearance_mode(new_mode)
        self.theme_button.configure(text="☀️" if new_mode == "Dark" else "🌙")
    
    def filter_users(self, selected_filter):
        """Filter users by type"""
        self.display_users(selected_filter)
    
    def search_users(self):
        """Search users"""
        search_term = self.search_entry.get().strip()
        if search_term:
            messagebox.showinfo("Search", f"Searching for: {search_term}\n(Search functionality would be implemented here)")
        else:
            self.display_users(self.user_filter.get())
    
    def display_users(self, filter_type):
        """Display users based on filter"""
        # Clear current display
        for widget in self.users_frame.winfo_children():
            widget.destroy()
        
        # Get users based on filter
        if filter_type == "All Users":
            members = User.get_all_by_type('member')
            trainers = User.get_all_by_type('trainer')
            admins = User.get_all_by_type('admin')
            all_users = members + trainers + admins
        elif filter_type == "Members":
            all_users = User.get_all_by_type('member')
        elif filter_type == "Trainers":
            all_users = User.get_all_by_type('trainer')
        elif filter_type == "Admins":
            all_users = User.get_all_by_type('admin')
        else:
            all_users = []
        
        # Display users
        for user in all_users:
            user_card = ctk.CTkFrame(self.users_frame)
            user_card.pack(fill="x", pady=5, padx=10)
            
            # User info
            info_frame = ctk.CTkFrame(user_card, fg_color="transparent")
            info_frame.pack(fill="x", padx=20, pady=15)
            
            user_name = ctk.CTkLabel(
                info_frame,
                text=f"{user.full_name} ({user.user_type.title()})",
                font=ctk.CTkFont(size=14, weight="bold")
            )
            user_name.pack(side="left")
            
            # User details
            details_frame = ctk.CTkFrame(user_card, fg_color="transparent")
            details_frame.pack(fill="x", padx=20, pady=(0, 15))
            
            email_label = ctk.CTkLabel(
                details_frame,
                text=f"Email: {user.email}",
                text_color="gray"
            )
            email_label.pack(anchor="w")
            
            username_label = ctk.CTkLabel(
                details_frame,
                text=f"Username: {user.username}",
                text_color="gray"
            )
            username_label.pack(anchor="w")
            
            # Action buttons
            button_frame = ctk.CTkFrame(user_card, fg_color="transparent")
            button_frame.pack(fill="x", padx=20, pady=(0, 15))
            
            edit_button = ctk.CTkButton(
                button_frame,
                text="Edit",
                width=80,
                command=lambda u=user: self.edit_user(u)
            )
            edit_button.pack(side="right", padx=(5, 0))
            
            if user.user_type != 'admin':
                deactivate_button = ctk.CTkButton(
                    button_frame,
                    text="Deactivate" if user.is_active else "Activate",
                    width=100,
                    fg_color="red" if user.is_active else "green",
                    command=lambda u=user: self.toggle_user_status(u)
                )
                deactivate_button.pack(side="right", padx=(5, 0))
    
    def add_new_user(self):
        """Add new user"""
        from views.register_dialog import RegisterDialog
        dialog = RegisterDialog(self.parent)
        if dialog.result:
            messagebox.showinfo("Success", "New user added successfully!")
            self.display_users(self.user_filter.get())
    
    def edit_user(self, user):
        """Edit user"""
        messagebox.showinfo("Edit User", f"Edit user functionality for {user.full_name} would be implemented here")
    
    def toggle_user_status(self, user):
        """Toggle user active status"""
        action = "deactivate" if user.is_active else "activate"
        if messagebox.askyesno("Confirm", f"Are you sure you want to {action} {user.full_name}?"):
            user.is_active = not user.is_active
            user.save()
            messagebox.showinfo("Success", f"User {action}d successfully!")
            self.display_users(self.user_filter.get())
    
    def create_new_class(self):
        """Create new fitness class"""
        from views.class_creation_dialog import ClassCreationDialog
        dialog = ClassCreationDialog(self.parent)
        if dialog.result:
            messagebox.showinfo("Success", "New class created successfully!")
            self.show_class_management()
    
    def edit_class(self, fitness_class):
        """Edit fitness class"""
        messagebox.showinfo("Edit Class", f"Edit class functionality for {fitness_class.name} would be implemented here")
    
    def assign_trainer_to_class(self, fitness_class):
        """Assign trainer to class"""
        trainers = User.get_all_by_type('trainer')
        if not trainers:
            messagebox.showinfo("No Trainers", "No trainers available to assign")
            return
        
        messagebox.showinfo("Assign Trainer", f"Trainer assignment for {fitness_class.name} would be implemented here")
    
    def add_new_exercise(self):
        """Add new exercise to library"""
        from views.exercise_creation_dialog import ExerciseCreationDialog
        dialog = ExerciseCreationDialog(self.parent)
        if dialog.result:
            messagebox.showinfo("Success", "New exercise added successfully!")
            self.show_exercise_management()
    
    def edit_exercise(self, exercise):
        """Edit exercise"""
        messagebox.showinfo("Edit Exercise", f"Edit exercise functionality for {exercise.name} would be implemented here")
    
    def send_broadcast_notification(self):
        """Send broadcast notification"""
        title = self.notification_title_entry.get().strip()
        message = self.notification_message_textbox.get("1.0", "end-1c").strip()
        audience = self.audience_menu.get()
        
        if not title or not message:
            messagebox.showerror("Error", "Please enter both title and message")
            return
        
        # Get target users
        if audience == "All Users":
            members = User.get_all_by_type('member')
            trainers = User.get_all_by_type('trainer')
            target_users = members + trainers
        elif audience == "Members Only":
            target_users = User.get_all_by_type('member')
        elif audience == "Trainers Only":
            target_users = User.get_all_by_type('trainer')
        else:
            target_users = []
        
        # Send notifications
        for user in target_users:
            Notification.create_notification(user.id, title, message, "admin")
        
        messagebox.showinfo("Success", f"Broadcast notification sent to {len(target_users)} users!")
        
        # Clear form
        self.notification_title_entry.delete(0, 'end')
        self.notification_message_textbox.delete("1.0", 'end')
    
    def generate_user_report(self):
        """Generate user activity report"""
        messagebox.showinfo("User Report", "User activity report generated!\n\n(Detailed reporting functionality would be implemented here)")
    
    def generate_revenue_report(self):
        """Generate revenue report"""
        # Calculate basic revenue stats
        all_sessions = Session.get_by_member_id(0)  # All sessions
        total_revenue = sum(s.price for s in all_sessions if s.price and s.status == 'completed')
        total_sessions = len([s for s in all_sessions if s.status == 'completed'])
        
        messagebox.showinfo(
            "Revenue Report", 
            f"Revenue Report Generated!\n\nTotal Revenue: ${total_revenue:.2f}\nCompleted Sessions: {total_sessions}\nAverage per Session: ${total_revenue/total_sessions if total_sessions > 0 else 0:.2f}"
        )
    
    def generate_session_report(self):
        """Generate session analytics"""
        messagebox.showinfo("Session Analytics", "Session analytics report generated!\n\n(Detailed session analytics would be implemented here)")
    
    def generate_class_report(self):
        """Generate class performance report"""
        messagebox.showinfo("Class Performance", "Class performance report generated!\n\n(Class performance analytics would be implemented here)")
    
    def load_dashboard_data(self):
        """Load dashboard data"""
        pass
    
    def destroy(self):
        """Clean up the dashboard"""
        self.main_frame.destroy()