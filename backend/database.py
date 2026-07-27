"""
MongoDB Database Manager
Handles connection, user operations, and state persistence.

Storage:
  - users: Google OAuth credentials (google_id, email, name, picture)
  - user_states: Emotional states (ST/MT/LT) + adaptive parameters

Note: No message history is stored. Only user credentials and their
      emotional states are persisted across sessions.
"""

from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
from typing import Optional
from bson import ObjectId


# ==========================================================
# MONGODB CONNECTION MANAGER
# ==========================================================

class MongoDB:
    """Singleton MongoDB connection manager"""
    client: AsyncIOMotorClient = None
    db = None

    @classmethod
    async def connect(cls, uri: str, db_name: str = "state_management"):
        """Connect to MongoDB and create indexes"""
        if not uri:
            raise ValueError(
                "MONGODB_URI is not set. Please add it to your .env file.\n"
                "See .env.example for setup instructions."
            )

        import certifi
        # Add a 5-second timeout and explicit CA bundle for SSL
        cls.client = AsyncIOMotorClient(
            uri,
            serverSelectionTimeoutMS=5000,
            tlsCAFile=certifi.where()
        )
        cls.db = cls.client[db_name]

        # Create indexes for performance and uniqueness
        await cls.db.users.create_index("google_id", unique=True)
        await cls.db.users.create_index("email", unique=True)
        await cls.db.user_states.create_index("user_id", unique=True)

        # Verify connection
        await cls.client.admin.command("ping")
        print("✅ Connected to MongoDB")

    @classmethod
    async def disconnect(cls):
        """Close MongoDB connection"""
        if cls.client:
            cls.client.close()
            print("🔌 Disconnected from MongoDB")

    @classmethod
    def get_db(cls):
        """Get database instance"""
        if cls.db is None:
            raise RuntimeError(
                "Database not connected. Call MongoDB.connect() first."
            )
        return cls.db


# ==========================================================
# USER OPERATIONS (Authentication)
# ==========================================================

async def create_user(
    google_id: str, email: str, name: str, picture: str = ""
) -> dict:
    """
    Create a new user from Google OAuth data.

    Args:
        google_id: Google's unique user ID (sub claim)
        email: User's email from Google
        name: Display name from Google
        picture: Profile picture URL from Google

    Returns:
        Created user document with _id
    """
    db = MongoDB.get_db()

    user_doc = {
        "google_id": google_id,
        "email": email,
        "name": name,
        "picture": picture,
        "created_at": datetime.utcnow(),
        "last_login": datetime.utcnow(),
    }

    result = await db.users.insert_one(user_doc)
    user_doc["_id"] = result.inserted_id
    return user_doc


async def get_user_by_google_id(google_id: str) -> Optional[dict]:
    """Find user by Google ID"""
    db = MongoDB.get_db()
    return await db.users.find_one({"google_id": google_id})


async def get_user_by_id(user_id: str) -> Optional[dict]:
    """Find user by MongoDB ObjectId string"""
    db = MongoDB.get_db()
    try:
        return await db.users.find_one({"_id": ObjectId(user_id)})
    except Exception:
        return None


async def update_last_login(user_id: str):
    """Update user's last login timestamp"""
    db = MongoDB.get_db()
    await db.users.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"last_login": datetime.utcnow()}},
    )


# ==========================================================
# STATE OPERATIONS (Emotional State Persistence)
# ==========================================================

async def save_user_state(user_id: str, state_data: dict):
    """
    Save or update user's emotional state in database.
    Uses upsert to create on first save.

    Args:
        user_id: User's MongoDB ObjectId as string
        state_data: Dict from UserProfile.to_db_dict()
    """
    db = MongoDB.get_db()

    state_data["user_id"] = user_id
    state_data["last_updated"] = datetime.utcnow()

    await db.user_states.update_one(
        {"user_id": user_id},
        {"$set": state_data},
        upsert=True,
    )


async def load_user_state(user_id: str) -> Optional[dict]:
    """
    Load user's emotional state from database.

    Args:
        user_id: User's MongoDB ObjectId as string

    Returns:
        State document or None if not found
    """
    db = MongoDB.get_db()
    return await db.user_states.find_one({"user_id": user_id})


async def delete_user_state(user_id: str):
    """
    Delete user's emotional state (for reset).

    Args:
        user_id: User's MongoDB ObjectId as string
    """
    db = MongoDB.get_db()
    await db.user_states.delete_one({"user_id": user_id})
