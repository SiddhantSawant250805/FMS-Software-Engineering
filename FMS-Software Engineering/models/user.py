from datetime import datetime
from config.database import DatabaseManager

class User:
    def __init__(self, user_id=None, username=None, email=None, user_type=None, 
                 first_name=None, last_name=None, phone=None, date_of_birth=None, 
                 gender=None, created_at=None, is_active=True):
        self.id = user_id
        self.username = username
        self.email = email
        self.user_type = user_type
        self.first_name = first_name
        self.last_name = last_name
        self.phone = phone
        self.date_of_birth = date_of_birth
        self.gender = gender
        self.created_at = created_at
        self.is_active = is_active
        self.db = DatabaseManager()
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def save(self):
        """Save user to database"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        if self.id:
            # Update existing user
            cursor.execute('''
                UPDATE users 
                SET username=?, email=?, first_name=?, last_name=?, 
                    phone=?, date_of_birth=?, gender=?, is_active=?
                WHERE id=?
            ''', (self.username, self.email, self.first_name, self.last_name,
                  self.phone, self.date_of_birth, self.gender, self.is_active, self.id))
        else:
            # Insert new user (password_hash should be handled separately)
            cursor.execute('''
                INSERT INTO users (username, email, user_type, first_name, last_name,
                                 phone, date_of_birth, gender, is_active)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (self.username, self.email, self.user_type, self.first_name, self.last_name,
                  self.phone, self.date_of_birth, self.gender, self.is_active))
            self.id = cursor.lastrowid
        
        conn.commit()
        return self.id
    
    @classmethod
    def get_by_id(cls, user_id):
        """Get user by ID"""
        db = DatabaseManager()
        conn = db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        
        if row:
            return cls(
                user_id=row['id'],
                username=row['username'],
                email=row['email'],
                user_type=row['user_type'],
                first_name=row['first_name'],
                last_name=row['last_name'],
                phone=row['phone'],
                date_of_birth=row['date_of_birth'],
                gender=row['gender'],
                created_at=row['created_at'],
                is_active=row['is_active']
            )
        return None
    
    @classmethod
    def get_by_username(cls, username):
        """Get user by username"""
        db = DatabaseManager()
        conn = db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        row = cursor.fetchone()
        
        if row:
            return cls(
                user_id=row['id'],
                username=row['username'],
                email=row['email'],
                user_type=row['user_type'],
                first_name=row['first_name'],
                last_name=row['last_name'],
                phone=row['phone'],
                date_of_birth=row['date_of_birth'],
                gender=row['gender'],
                created_at=row['created_at'],
                is_active=row['is_active']
            )
        return None
    
    @classmethod
    def get_all_by_type(cls, user_type):
        """Get all users of a specific type"""
        db = DatabaseManager()
        conn = db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM users WHERE user_type = ? AND is_active = 1", (user_type,))
        rows = cursor.fetchall()
        
        users = []
        for row in rows:
            users.append(cls(
                user_id=row['id'],
                username=row['username'],
                email=row['email'],
                user_type=row['user_type'],
                first_name=row['first_name'],
                last_name=row['last_name'],
                phone=row['phone'],
                date_of_birth=row['date_of_birth'],
                gender=row['gender'],
                created_at=row['created_at'],
                is_active=row['is_active']
            ))
        
        return users
    
    def delete(self):
        """Soft delete user (set is_active to False)"""
        self.is_active = False
        self.save()

class MemberProfile:
    def __init__(self, user_id, height=None, weight=None, fitness_goals=None,
                 medical_conditions=None, emergency_contact=None, emergency_phone=None,
                 membership_type=None, membership_start=None, membership_end=None):
        self.user_id = user_id
        self.height = height
        self.weight = weight
        self.fitness_goals = fitness_goals
        self.medical_conditions = medical_conditions
        self.emergency_contact = emergency_contact
        self.emergency_phone = emergency_phone
        self.membership_type = membership_type
        self.membership_start = membership_start
        self.membership_end = membership_end
        self.db = DatabaseManager()
    
    def save(self):
        """Save member profile"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO member_profiles 
            (user_id, height, weight, fitness_goals, medical_conditions,
             emergency_contact, emergency_phone, membership_type, membership_start, membership_end)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (self.user_id, self.height, self.weight, self.fitness_goals,
              self.medical_conditions, self.emergency_contact, self.emergency_phone,
              self.membership_type, self.membership_start, self.membership_end))
        
        conn.commit()
    
    @classmethod
    def get_by_user_id(cls, user_id):
        """Get member profile by user ID"""
        db = DatabaseManager()
        conn = db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM member_profiles WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        
        if row:
            return cls(
                user_id=row['user_id'],
                height=row['height'],
                weight=row['weight'],
                fitness_goals=row['fitness_goals'],
                medical_conditions=row['medical_conditions'],
                emergency_contact=row['emergency_contact'],
                emergency_phone=row['emergency_phone'],
                membership_type=row['membership_type'],
                membership_start=row['membership_start'],
                membership_end=row['membership_end']
            )
        return cls(user_id=user_id)  # Return empty profile if not found

class TrainerProfile:
    def __init__(self, user_id, specializations=None, certifications=None,
                 experience_years=None, hourly_rate=None, bio=None):
        self.user_id = user_id
        self.specializations = specializations
        self.certifications = certifications
        self.experience_years = experience_years
        self.hourly_rate = hourly_rate
        self.bio = bio
        self.db = DatabaseManager()
    
    def save(self):
        """Save trainer profile"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO trainer_profiles 
            (user_id, specializations, certifications, experience_years, hourly_rate, bio)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (self.user_id, self.specializations, self.certifications,
              self.experience_years, self.hourly_rate, self.bio))
        
        conn.commit()
    
    @classmethod
    def get_by_user_id(cls, user_id):
        """Get trainer profile by user ID"""
        db = DatabaseManager()
        conn = db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM trainer_profiles WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        
        if row:
            return cls(
                user_id=row['user_id'],
                specializations=row['specializations'],
                certifications=row['certifications'],
                experience_years=row['experience_years'],
                hourly_rate=row['hourly_rate'],
                bio=row['bio']
            )
        return cls(user_id=user_id)  # Return empty profile if not found