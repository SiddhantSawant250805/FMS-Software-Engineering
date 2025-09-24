from datetime import datetime
from config.database import DatabaseManager

class Notification:
    def __init__(self, notification_id=None, user_id=None, title=None, 
                 message=None, notification_type=None, is_read=False, created_at=None):
        self.id = notification_id
        self.user_id = user_id
        self.title = title
        self.message = message
        self.type = notification_type
        self.is_read = is_read
        self.created_at = created_at
        self.db = DatabaseManager()
    
    def save(self):
        """Save notification to database"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        if self.id:
            # Update existing notification
            cursor.execute('''
                UPDATE notifications 
                SET user_id=?, title=?, message=?, type=?, is_read=?
                WHERE id=?
            ''', (self.user_id, self.title, self.message, self.type, self.is_read, self.id))
        else:
            # Insert new notification
            cursor.execute('''
                INSERT INTO notifications (user_id, title, message, type, is_read)
                VALUES (?, ?, ?, ?, ?)
            ''', (self.user_id, self.title, self.message, self.type, self.is_read))
            self.id = cursor.lastrowid
        
        conn.commit()
        return self.id
    
    @classmethod
    def get_by_user_id(cls, user_id, unread_only=False):
        """Get notifications for a user"""
        db = DatabaseManager()
        conn = db.get_connection()
        cursor = conn.cursor()
        
        if unread_only:
            cursor.execute('''
                SELECT * FROM notifications 
                WHERE user_id = ? AND is_read = 0 
                ORDER BY created_at DESC
            ''', (user_id,))
        else:
            cursor.execute('''
                SELECT * FROM notifications 
                WHERE user_id = ? 
                ORDER BY created_at DESC
            ''', (user_id,))
        
        rows = cursor.fetchall()
        
        notifications = []
        for row in rows:
            notifications.append(cls(
                notification_id=row['id'],
                user_id=row['user_id'],
                title=row['title'],
                message=row['message'],
                notification_type=row['type'],
                is_read=row['is_read'],
                created_at=row['created_at']
            ))
        
        return notifications
    
    @classmethod
    def create_notification(cls, user_id, title, message, notification_type="info"):
        """Create a new notification"""
        notification = cls(
            user_id=user_id,
            title=title,
            message=message,
            notification_type=notification_type
        )
        notification.save()
        return notification
    
    def mark_as_read(self):
        """Mark notification as read"""
        self.is_read = True
        self.save()
    
    @classmethod
    def mark_all_as_read(cls, user_id):
        """Mark all notifications as read for a user"""
        db = DatabaseManager()
        conn = db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE notifications 
            SET is_read = 1 
            WHERE user_id = ? AND is_read = 0
        ''', (user_id,))
        
        conn.commit()