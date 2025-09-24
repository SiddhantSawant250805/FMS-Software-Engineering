import json
from datetime import datetime
from config.database import DatabaseManager

class Workout:
    def __init__(self, workout_id=None, member_id=None, trainer_id=None, 
                 name=None, description=None, exercises=None, created_at=None, is_active=True):
        self.id = workout_id
        self.member_id = member_id
        self.trainer_id = trainer_id
        self.name = name
        self.description = description
        self.exercises = exercises or []
        self.created_at = created_at
        self.is_active = is_active
        self.db = DatabaseManager()
    
    def save(self):
        """Save workout to database"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        exercises_json = json.dumps(self.exercises)
        
        if self.id:
            # Update existing workout
            cursor.execute('''
                UPDATE workouts 
                SET member_id=?, trainer_id=?, name=?, description=?, exercises=?, is_active=?
                WHERE id=?
            ''', (self.member_id, self.trainer_id, self.name, self.description, 
                  exercises_json, self.is_active, self.id))
        else:
            # Insert new workout
            cursor.execute('''
                INSERT INTO workouts (member_id, trainer_id, name, description, exercises, is_active)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (self.member_id, self.trainer_id, self.name, self.description, 
                  exercises_json, self.is_active))
            self.id = cursor.lastrowid
        
        conn.commit()
        return self.id
    
    @classmethod
    def get_by_id(cls, workout_id):
        """Get workout by ID"""
        db = DatabaseManager()
        conn = db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM workouts WHERE id = ?", (workout_id,))
        row = cursor.fetchone()
        
        if row:
            exercises = json.loads(row['exercises']) if row['exercises'] else []
            return cls(
                workout_id=row['id'],
                member_id=row['member_id'],
                trainer_id=row['trainer_id'],
                name=row['name'],
                description=row['description'],
                exercises=exercises,
                created_at=row['created_at'],
                is_active=row['is_active']
            )
        return None
    
    @classmethod
    def get_by_member_id(cls, member_id):
        """Get all workouts for a member"""
        db = DatabaseManager()
        conn = db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM workouts 
            WHERE member_id = ? AND is_active = 1 
            ORDER BY created_at DESC
        ''', (member_id,))
        rows = cursor.fetchall()
        
        workouts = []
        for row in rows:
            exercises = json.loads(row['exercises']) if row['exercises'] else []
            workouts.append(cls(
                workout_id=row['id'],
                member_id=row['member_id'],
                trainer_id=row['trainer_id'],
                name=row['name'],
                description=row['description'],
                exercises=exercises,
                created_at=row['created_at'],
                is_active=row['is_active']
            ))
        
        return workouts
    
    @classmethod
    def get_by_trainer_id(cls, trainer_id):
        """Get all workouts created by a trainer"""
        db = DatabaseManager()
        conn = db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM workouts 
            WHERE trainer_id = ? AND is_active = 1 
            ORDER BY created_at DESC
        ''', (trainer_id,))
        rows = cursor.fetchall()
        
        workouts = []
        for row in rows:
            exercises = json.loads(row['exercises']) if row['exercises'] else []
            workouts.append(cls(
                workout_id=row['id'],
                member_id=row['member_id'],
                trainer_id=row['trainer_id'],
                name=row['name'],
                description=row['description'],
                exercises=exercises,
                created_at=row['created_at'],
                is_active=row['is_active']
            ))
        
        return workouts
    
    def add_exercise(self, exercise):
        """Add an exercise to the workout"""
        self.exercises.append(exercise)
    
    def remove_exercise(self, exercise_index):
        """Remove an exercise by index"""
        if 0 <= exercise_index < len(self.exercises):
            self.exercises.pop(exercise_index)
    
    def delete(self):
        """Soft delete workout"""
        self.is_active = False
        self.save()

class Exercise:
    def __init__(self, exercise_id=None, name=None, category=None, muscle_groups=None,
                 equipment=None, instructions=None, difficulty_level=None, image_path=None):
        self.id = exercise_id
        self.name = name
        self.category = category
        self.muscle_groups = muscle_groups
        self.equipment = equipment
        self.instructions = instructions
        self.difficulty_level = difficulty_level
        self.image_path = image_path
        self.db = DatabaseManager()
    
    def save(self):
        """Save exercise to database"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        if self.id:
            # Update existing exercise
            cursor.execute('''
                UPDATE exercises 
                SET name=?, category=?, muscle_groups=?, equipment=?, 
                    instructions=?, difficulty_level=?, image_path=?
                WHERE id=?
            ''', (self.name, self.category, self.muscle_groups, self.equipment,
                  self.instructions, self.difficulty_level, self.image_path, self.id))
        else:
            # Insert new exercise
            cursor.execute('''
                INSERT INTO exercises (name, category, muscle_groups, equipment, 
                                     instructions, difficulty_level, image_path)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (self.name, self.category, self.muscle_groups, self.equipment,
                  self.instructions, self.difficulty_level, self.image_path))
            self.id = cursor.lastrowid
        
        conn.commit()
        return self.id
    
    @classmethod
    def get_all(cls):
        """Get all exercises"""
        db = DatabaseManager()
        conn = db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM exercises ORDER BY name")
        rows = cursor.fetchall()
        
        exercises = []
        for row in rows:
            exercises.append(cls(
                exercise_id=row['id'],
                name=row['name'],
                category=row['category'],
                muscle_groups=row['muscle_groups'],
                equipment=row['equipment'],
                instructions=row['instructions'],
                difficulty_level=row['difficulty_level'],
                image_path=row['image_path']
            ))
        
        return exercises
    
    @classmethod
    def search_by_category(cls, category):
        """Search exercises by category"""
        db = DatabaseManager()
        conn = db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM exercises WHERE category LIKE ? ORDER BY name", (f"%{category}%",))
        rows = cursor.fetchall()
        
        exercises = []
        for row in rows:
            exercises.append(cls(
                exercise_id=row['id'],
                name=row['name'],
                category=row['category'],
                muscle_groups=row['muscle_groups'],
                equipment=row['equipment'],
                instructions=row['instructions'],
                difficulty_level=row['difficulty_level'],
                image_path=row['image_path']
            ))
        
        return exercises