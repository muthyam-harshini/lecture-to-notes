"""
Database connection and management for lecture voice notes application.
"""
import sqlite3
import os
from typing import Optional, Dict, Any, List

class LectureDatabase:
    def __init__(self, db_path: str = None):
        if db_path is None:
            # Get the path to the data directory relative to this file
            current_dir = os.path.dirname(os.path.abspath(__file__))
            parent_dir = os.path.dirname(current_dir)
            db_path = os.path.join(parent_dir, "data", "lecture_notes.db")
        
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the database with required tables."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create lectures table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS lectures (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            transcript TEXT,
            summary TEXT,
            quiz TEXT,
            flashcards TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        conn.commit()
        conn.close()
    
    def insert_lecture(self, filename: str, transcript: str = None, 
                      summary: str = None, quiz: str = None, 
                      flashcards: str = None) -> int:
        """Insert a new lecture record."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
        INSERT INTO lectures (filename, transcript, summary, quiz, flashcards)
        VALUES (?, ?, ?, ?, ?)
        """, (filename, transcript, summary, quiz, flashcards))
        
        lecture_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return lecture_id
    
    def update_lecture(self, lecture_id: int, **kwargs):
        """Update a lecture record with new data."""
        if not kwargs:
            return
        
        # Build dynamic update query
        set_clause = ", ".join([f"{key} = ?" for key in kwargs.keys()])
        query = f"UPDATE lectures SET {set_clause}, updated_at = CURRENT_TIMESTAMP WHERE id = ?"
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(query, list(kwargs.values()) + [lecture_id])
        conn.commit()
        conn.close()
    
    def get_lecture(self, lecture_id: int) -> Optional[Dict[str, Any]]:
        """Get a single lecture by ID."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable dict-like access
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM lectures WHERE id = ?", (lecture_id,))
        row = cursor.fetchone()
        
        conn.close()
        
        if row:
            return dict(row)
        return None
    
    def get_all_lectures(self) -> List[Dict[str, Any]]:
        """Get all lectures from the database."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM lectures ORDER BY created_at DESC")
        rows = cursor.fetchall()
        
        conn.close()
        
        return [dict(row) for row in rows]
    
    def delete_lecture(self, lecture_id: int) -> bool:
        """Delete a lecture by ID."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM lectures WHERE id = ?", (lecture_id,))
        deleted_count = cursor.rowcount
        
        conn.commit()
        conn.close()
        
        return deleted_count > 0
    
    def search_lectures(self, query: str) -> List[Dict[str, Any]]:
        """Search lectures by filename, transcript, or summary."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        search_query = f"%{query}%"
        cursor.execute("""
        SELECT * FROM lectures 
        WHERE filename LIKE ? OR transcript LIKE ? OR summary LIKE ?
        ORDER BY created_at DESC
        """, (search_query, search_query, search_query))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]


# Initialize the database when module is imported
def get_database():
    """Get a database instance."""
    return LectureDatabase()


if __name__ == "__main__":
    # Test the database functionality
    db = LectureDatabase()
    print("Database initialized successfully!")
    
    # Test insert
    lecture_id = db.insert_lecture(
        filename="test_lecture.mp3",
        transcript="This is a test transcript"
    )
    print(f"Inserted lecture with ID: {lecture_id}")
    
    # Test get
    lecture = db.get_lecture(lecture_id)
    print(f"Retrieved lecture: {lecture}")
    
    # Test update
    db.update_lecture(lecture_id, summary="This is a test summary")
    print("Updated lecture with summary")
    
    # Test get all
    all_lectures = db.get_all_lectures()
    print(f"Total lectures: {len(all_lectures)}")