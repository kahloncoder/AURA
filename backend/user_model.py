from flask_bcrypt import Bcrypt
from database import db
from datetime import datetime

bcrypt = Bcrypt()

def create_user(email, password):
    """Hashes a password and creates a new user in the database."""
    if db is None:
        raise Exception("Database not connected")
    
    # Check if user already exists
    if db.users.find_one({"email": email}):
        raise ValueError("User with this email already exists")

    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    
    user_doc = {
        "email": email,
        "password": hashed_password,
        "created_at": datetime.utcnow()
    }
    result = db.users.insert_one(user_doc)
    return result.inserted_id

def check_password(hashed_password, password):
    """Checks if a plain-text password matches a hashed password."""
    return bcrypt.check_password_hash(hashed_password, password)