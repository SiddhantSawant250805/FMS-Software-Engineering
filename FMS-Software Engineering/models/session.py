from datetime import datetime
from config.database import DatabaseManager

class Session:
    def __init__(self, session_id=None, member_id=None, trainer_id=None, 
                 session_date=None, duration=None, session_type=None, 
                 status='scheduled', price=None, notes=None, created_at=None):
        self.id = session_id
        self.member_id = member_id
        self.trainer_id = trainer_id
        self.session_date = session_date
        self.duration = duration  # in minutes
        self.session_type = session_type
        self.status = status  # scheduled, completed, cancelled
        self.price = price
        self.notes = notes
        self.created_at = created_at
        self.db = DatabaseManager()
    
    def save(self):
        """Save session to database"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        if self.id:
            # Update existing session
            cursor.execute('''
                UPDATE sessions 
                SET member_id=?, trainer_id=?, session_date=?, duration=?, 
                    session_type=?, status=?, price=?, notes=?
                WHERE id=?
            ''', (self.member_id, self.trainer_id, self.session_date, self.duration,
                  self.session_type, self.status, self.price, self.notes, self.id))
        else:
            # Insert new session
            cursor.execute('''
                INSERT INTO sessions (member_id, trainer_id, session_date, duration, 
                                    session_type, status, price, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (self.member_id, self.trainer_id, self.session_date, self.duration,
                  self.session_type, self.status, self.price, self.notes))
            self.id = cursor.lastrowid
        
        conn.commit()
        return self.id
    
    @classmethod
    def get_by_id(cls, session_id):
        """Get session by ID"""
        db = DatabaseManager()
        conn = db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM sessions WHERE id = ?", (session_id,))
        row = cursor.fetchone()
        
        if row:
            return cls(
                session_id=row['id'],
                member_id=row['member_id'],
                trainer_id=row['trainer_id'],
                session_date=row['session_date'],
                duration=row['duration'],
                session_type=row['session_type'],
                status=row['status'],
                price=row['price'],
                notes=row['notes'],
                created_at=row['created_at']
            )
        return None
    
    @classmethod
    def get_by_member_id(cls, member_id):
        """Get all sessions for a member"""
        db = DatabaseManager()
        conn = db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM sessions 
            WHERE member_id = ? 
            ORDER BY session_date DESC
        ''', (member_id,))
        rows = cursor.fetchall()
        
        sessions = []
        for row in rows:
            sessions.append(cls(
                session_id=row['id'],
                member_id=row['member_id'],
                trainer_id=row['trainer_id'],
                session_date=row['session_date'],
                duration=row['duration'],
                session_type=row['session_type'],
                status=row['status'],
                price=row['price'],
                notes=row['notes'],
                created_at=row['created_at']
            ))
        
        return sessions
    
    @classmethod
    def get_by_trainer_id(cls, trainer_id):
        """Get all sessions for a trainer"""
        db = DatabaseManager()
        conn = db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM sessions 
            WHERE trainer_id = ? 
            ORDER BY session_date DESC
        ''', (trainer_id,))
        rows = cursor.fetchall()
        
        sessions = []
        for row in rows:
            sessions.append(cls(
                session_id=row['id'],
                member_id=row['member_id'],
                trainer_id=row['trainer_id'],
                session_date=row['session_date'],
                duration=row['duration'],
                session_type=row['session_type'],
                status=row['status'],
                price=row['price'],
                notes=row['notes'],
                created_at=row['created_at']
            ))
        
        return sessions
    
    @classmethod
    def get_upcoming_sessions(cls, user_id, user_type):
        """Get upcoming sessions for a user"""
        db = DatabaseManager()
        conn = db.get_connection()
        cursor = conn.cursor()
        
        if user_type == 'member':
            cursor.execute('''
                SELECT * FROM sessions 
                WHERE member_id = ? AND session_date > datetime('now') AND status = 'scheduled'
                ORDER BY session_date ASC
            ''', (user_id,))
        elif user_type == 'trainer':
            cursor.execute('''
                SELECT * FROM sessions 
                WHERE trainer_id = ? AND session_date > datetime('now') AND status = 'scheduled'
                ORDER BY session_date ASC
            ''', (user_id,))
        else:
            return []
        
        rows = cursor.fetchall()
        
        sessions = []
        for row in rows:
            sessions.append(cls(
                session_id=row['id'],
                member_id=row['member_id'],
                trainer_id=row['trainer_id'],
                session_date=row['session_date'],
                duration=row['duration'],
                session_type=row['session_type'],
                status=row['status'],
                price=row['price'],
                notes=row['notes'],
                created_at=row['created_at']
            ))
        
        return sessions
    
    def cancel(self):
        """Cancel session"""
        self.status = 'cancelled'
        self.save()
    
    def complete(self):
        """Mark session as completed"""
        self.status = 'completed'
        self.save()

class FitnessClass:
    def __init__(self, class_id=None, name=None, description=None, trainer_id=None,
                 schedule=None, capacity=None, price=None, duration=None, is_active=True):
        self.id = class_id
        self.name = name
        self.description = description
        self.trainer_id = trainer_id
        self.schedule = schedule  # JSON formatted for recurring classes
        self.capacity = capacity
        self.price = price
        self.duration = duration  # in minutes
        self.is_active = is_active
        self.db = DatabaseManager()
    
    def save(self):
        """Save class to database"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        if self.id:
            # Update existing class
            cursor.execute('''
                UPDATE classes 
                SET name=?, description=?, trainer_id=?, schedule=?, 
                    capacity=?, price=?, duration=?, is_active=?
                WHERE id=?
            ''', (self.name, self.description, self.trainer_id, self.schedule,
                  self.capacity, self.price, self.duration, self.is_active, self.id))
        else:
            # Insert new class
            cursor.execute('''
                INSERT INTO classes (name, description, trainer_id, schedule, 
                                   capacity, price, duration, is_active)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (self.name, self.description, self.trainer_id, self.schedule,
                  self.capacity, self.price, self.duration, self.is_active))
            self.id = cursor.lastrowid
        
        conn.commit()
        return self.id
    
    @classmethod
    def get_all_active(cls):
        """Get all active classes"""
        db = DatabaseManager()
        conn = db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM classes WHERE is_active = 1 ORDER BY name")
        rows = cursor.fetchall()
        
        classes = []
        for row in rows:
            classes.append(cls(
                class_id=row['id'],
                name=row['name'],
                description=row['description'],
                trainer_id=row['trainer_id'],
                schedule=row['schedule'],
                capacity=row['capacity'],
                price=row['price'],
                duration=row['duration'],
                is_active=row['is_active']
            ))
        
        return classes