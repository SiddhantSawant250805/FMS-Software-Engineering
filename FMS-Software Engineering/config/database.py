import sqlite3
import os
import bcrypt
from datetime import datetime

class DatabaseManager:
    def __init__(self, db_path="fitness_system.db"):
        self.db_path = db_path
        self.connection = None
    
    def get_connection(self):
        if self.connection is None:
            self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
            self.connection.row_factory = sqlite3.Row
        return self.connection
    
    def initialize_database(self):
        """Create all necessary tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                user_type TEXT NOT NULL CHECK(user_type IN ('member', 'trainer', 'admin')),
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                phone TEXT,
                date_of_birth DATE,
                gender TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT 1
            )
        ''')
        
        # Member profiles
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS member_profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER UNIQUE,
                height REAL,
                weight REAL,
                fitness_goals TEXT,
                medical_conditions TEXT,
                emergency_contact TEXT,
                emergency_phone TEXT,
                membership_type TEXT,
                membership_start DATE,
                membership_end DATE,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Trainer profiles
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trainer_profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER UNIQUE,
                specializations TEXT,
                certifications TEXT,
                experience_years INTEGER,
                hourly_rate REAL,
                bio TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Workouts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS workouts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                member_id INTEGER,
                trainer_id INTEGER,
                name TEXT NOT NULL,
                description TEXT,
                exercises TEXT, -- JSON formatted
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT 1,
                FOREIGN KEY (member_id) REFERENCES users (id),
                FOREIGN KEY (trainer_id) REFERENCES users (id)
            )
        ''')
        
        # Sessions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                member_id INTEGER,
                trainer_id INTEGER,
                session_date DATETIME,
                duration INTEGER, -- in minutes
                session_type TEXT,
                status TEXT DEFAULT 'scheduled',
                price REAL,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (member_id) REFERENCES users (id),
                FOREIGN KEY (trainer_id) REFERENCES users (id)
            )
        ''')
        
        # Classes table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS classes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                trainer_id INTEGER,
                schedule TEXT, -- JSON formatted for recurring classes
                capacity INTEGER,
                price REAL,
                duration INTEGER,
                is_active BOOLEAN DEFAULT 1,
                FOREIGN KEY (trainer_id) REFERENCES users (id)
            )
        ''')
        
        # Class enrollments
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS class_enrollments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                class_id INTEGER,
                member_id INTEGER,
                enrollment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'active',
                FOREIGN KEY (class_id) REFERENCES classes (id),
                FOREIGN KEY (member_id) REFERENCES users (id)
            )
        ''')
        
        # Notifications table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                title TEXT NOT NULL,
                message TEXT NOT NULL,
                type TEXT,
                is_read BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Progress tracking
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS progress_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                member_id INTEGER,
                record_date DATE,
                weight REAL,
                body_fat REAL,
                muscle_mass REAL,
                measurements TEXT, -- JSON formatted
                notes TEXT,
                photo_path TEXT,
                FOREIGN KEY (member_id) REFERENCES users (id)
            )
        ''')
        
        # Exercise library
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS exercises (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT,
                muscle_groups TEXT,
                equipment TEXT,
                instructions TEXT,
                difficulty_level TEXT,
                image_path TEXT
            )
        ''')
        
        conn.commit()
        self.create_default_data()
    
    def create_default_data(self):
        """Create default admin user and sample data"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Check if admin exists
        cursor.execute("SELECT id FROM users WHERE username = 'admin'")
        if not cursor.fetchone():
            # Create default admin
            password_hash = bcrypt.hashpw("admin123".encode('utf-8'), bcrypt.gensalt())
            cursor.execute('''
                INSERT INTO users (username, email, password_hash, user_type, first_name, last_name)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', ("admin", "admin@fitpro.com", password_hash, "admin", "Admin", "User"))
        
        # Add sample exercises
        sample_exercises = [
            ("Push-ups", "Chest", "Chest, Triceps, Shoulders", "Bodyweight", 
             "Start in a plank position, lower your body until your chest nearly touches the floor, then push back up.", "Beginner"),
            ("Squats", "Legs", "Quadriceps, Glutes, Hamstrings", "Bodyweight",
             "Stand with feet shoulder-width apart, lower your hips as if sitting back into a chair, then return to standing.", "Beginner"),
            ("Deadlift", "Back", "Hamstrings, Glutes, Lower Back", "Barbell",
             "Stand with feet hip-width apart, grip the bar, lift by extending your hips and knees to full extension.", "Intermediate"),
            ("Bench Press", "Chest", "Chest, Triceps, Shoulders", "Barbell",
             "Lie on bench, grip bar slightly wider than shoulders, lower to chest, then press back up.", "Intermediate"),
            ("Pull-ups", "Back", "Lats, Biceps, Rear Delts", "Pull-up Bar",
             "Hang from bar with arms extended, pull your body up until chin clears the bar.", "Advanced")
        ]
        
        for exercise in sample_exercises:
            cursor.execute("SELECT id FROM exercises WHERE name = ?", (exercise[0],))
            if not cursor.fetchone():
                cursor.execute('''
                    INSERT INTO exercises (name, category, muscle_groups, equipment, instructions, difficulty_level)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', exercise)
        
        conn.commit()
    
    def hash_password(self, password):
        """Hash a password for storing"""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    
    def verify_password(self, password, hashed):
        """Verify a stored password against provided password"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed)
    
    def close_connection(self):
        if self.connection:
            self.connection.close()
            self.connection = None