from models.user import User, MemberProfile, TrainerProfile
from config.database import DatabaseManager

class AuthController:
    def __init__(self):
        self.db = DatabaseManager()
    
    def authenticate_user(self, username, password):
        """Authenticate user login"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        # Get user with password hash
        cursor.execute('''
            SELECT id, username, email, password_hash, user_type, first_name, last_name, 
                   phone, date_of_birth, gender, is_active
            FROM users 
            WHERE username = ? AND is_active = 1
        ''', (username,))
        
        user_row = cursor.fetchone()
        
        if user_row and self.db.verify_password(password, user_row['password_hash']):
            return {
                'id': user_row['id'],
                'username': user_row['username'],
                'email': user_row['email'],
                'user_type': user_row['user_type'],
                'first_name': user_row['first_name'],
                'last_name': user_row['last_name'],
                'phone': user_row['phone'],
                'date_of_birth': user_row['date_of_birth'],
                'gender': user_row['gender']
            }
        
        return None
    
    def register_user(self, user_data):
        """Register new user"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            # Check if username or email already exists
            cursor.execute('''
                SELECT id FROM users 
                WHERE username = ? OR email = ?
            ''', (user_data['username'], user_data['email']))
            
            if cursor.fetchone():
                return False  # User already exists
            
            # Hash password
            password_hash = self.db.hash_password(user_data['password'])
            
            # Insert new user
            cursor.execute('''
                INSERT INTO users (username, email, password_hash, user_type, first_name, last_name, phone)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_data['username'],
                user_data['email'],
                password_hash,
                user_data['user_type'],
                user_data['first_name'],
                user_data['last_name'],
                user_data.get('phone', '')
            ))
            
            user_id = cursor.lastrowid
            
            # Create profile based on user type
            if user_data['user_type'] == 'member':
                cursor.execute('''
                    INSERT INTO member_profiles (user_id)
                    VALUES (?)
                ''', (user_id,))
            elif user_data['user_type'] == 'trainer':
                cursor.execute('''
                    INSERT INTO trainer_profiles (user_id)
                    VALUES (?)
                ''', (user_id,))
            
            conn.commit()
            return True
            
        except Exception as e:
            conn.rollback()
            print(f"Registration error: {e}")
            return False
    
    def change_password(self, user_id, old_password, new_password):
        """Change user password"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        # Verify old password
        cursor.execute("SELECT password_hash FROM users WHERE id = ?", (user_id,))
        result = cursor.fetchone()
        
        if result and self.db.verify_password(old_password, result['password_hash']):
            # Update with new password
            new_password_hash = self.db.hash_password(new_password)
            cursor.execute('''
                UPDATE users 
                SET password_hash = ? 
                WHERE id = ?
            ''', (new_password_hash, user_id))
            
            conn.commit()
            return True
        
        return False
    
    def reset_password(self, email, new_password):
        """Reset password by email (admin function)"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        # Check if email exists
        cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
        result = cursor.fetchone()
        
        if result:
            new_password_hash = self.db.hash_password(new_password)
            cursor.execute('''
                UPDATE users 
                SET password_hash = ? 
                WHERE email = ?
            ''', (new_password_hash, email))
            
            conn.commit()
            return True
        
        return False