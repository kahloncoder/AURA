"""
AURA Database Module
MongoDB integration for session storage (for future use)
All code is commented out - uncomment when ready to use MongoDB
"""

# from pymongo import MongoClient
# from config import MONGO_URI, MONGO_DB_NAME

# # Global MongoDB client and database
# mongo_client = None
# db = None


# def initialize_mongodb():
#     """Initialize MongoDB connection"""
#     global mongo_client, db
    
#     try:
#         mongo_client = MongoClient(MONGO_URI)
#         db = mongo_client[MONGO_DB_NAME]
        
#         # Test connection
#         db.command('ping')
        
#         # Create indexes for better performance
#         db.sessions.create_index("start_time")
#         db.sessions.create_index("status")
        
#         print("✅ MongoDB connected successfully")
#         return True
        
#     except Exception as e:
#         print(f"⚠️ MongoDB connection failed: {e}")
#         print("   Falling back to file-based logging")
#         return False


# def save_session_to_db(session_data):
#     """
#     Save complete session to MongoDB
    
#     Args:
#         session_data: Dict containing session info
#     """
#     if db is not None:
#         try:
#             result = db.sessions.insert_one(session_data)
#             print(f"💾 Session saved to MongoDB: {result.inserted_id}")
#             return result.inserted_id
#         except Exception as e:
#             print(f"❌ MongoDB save error: {e}")
#             return None
#     return None


# def get_session_by_id(session_id):
#     """Get session from MongoDB by ID"""
#     if db is not None:
#         try:
#             return db.sessions.find_one({"_id": session_id})
#         except Exception as e:
#             print(f"❌ MongoDB query error: {e}")
#             return None
#     return None


# def get_recent_sessions(limit=10):
#     """Get recent sessions"""
#     if db is not None:
#         try:
#             return list(db.sessions.find().sort("start_time", -1).limit(limit))
#         except Exception as e:
#             print(f"❌ MongoDB query error: {e}")
#             return []
#     return []


# def update_session_status(session_id, status):
#     """Update session status"""
#     if db is not None:
#         try:
#             db.sessions.update_one(
#                 {"_id": session_id},
#                 {"$set": {"status": status}}
#             )
#             return True
#         except Exception as e:
#             print(f"❌ MongoDB update error: {e}")
#             return False
#     return False