"""
A clean, structured, and production-style mini Twitter backend.
All in-memory storage. No external DB required.
"""

import time
import hashlib
import jwt
from uuid import uuid4
from typing import Dict, Set, List, Optional, Any


# ----------------------------------------------------------------------
# CONFIG
# ----------------------------------------------------------------------

JWT_SECRET = "supersecret"   # Use environment variables in production
JWT_ALGO = "HS256"
MAX_TWEET_LENGTH = 280


# ----------------------------------------------------------------------
# IN-MEMORY DATABASE
# ----------------------------------------------------------------------

users: Dict[str, Dict[str, Any]] = {}
tweets: Dict[str, Dict[str, Any]] = {}

followers: Dict[str, Set[str]] = {}
following: Dict[str, Set[str]] = {}
notifications: Dict[str, List[Dict[str, Any]]] = {}


# ----------------------------------------------------------------------
# HELPERS
# ----------------------------------------------------------------------

def hash_pw(password: str) -> str:
    """Return SHA-256 hash of a password."""
    return hashlib.sha256(password.encode()).hexdigest()


def generate_token(user_id: str) -> str:
    """Generate a JWT for a user."""
    payload = {"uid": user_id, "ts": time.time()}
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGO)


def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """Verify token and return payload or None."""
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGO])
    except Exception:
        return None


def find_user_by_username(username: str) -> Optional[Dict[str, Any]]:
    """Return a user dict by username, or None."""
    return next((u for u in users.values() if u["username"] == username), None)


# ----------------------------------------------------------------------
# AUTH / USER
# ----------------------------------------------------------------------

def register(email: str, username: str, password: str) -> str:
    """Register a new user."""
    if not (email and username and password):
        return "Missing fields."

    if find_user_by_username(username):
        return "Username taken."

    uid = str(uuid4())
    user_obj = {
        "id": uid,
        "email": email,
        "username": username,
        "password": hash_pw(password),
        "bio": "",
        "profile_pic": None,
        "banner": None,
        "private": False,
        "created": time.time(),
    }

    users[uid] = user_obj
    followers[uid] = set()
    following[uid] = set()
    notifications[uid] = []

    return f"User created. ID={uid}"


def login(username: str, password: str) -> str:
    """Authenticate user and return JWT."""
    user = find_user_by_username(username)
    if user and user["password"] == hash_pw(password):
        return generate_token(user["id"])

    return "Invalid login."


# ----------------------------------------------------------------------
# FOLLOW SYSTEM
# ----------------------------------------------------------------------

def follow(token: str, target_username: str) -> str:
    data = verify_token(token)
    if not data:
        return "Invalid token."

    uid = data["uid"]
    target = find_user_by_username(target_username)

    if not target:
        return "User not found."

    tid = target["id"]
    if uid == tid:
        return "Can't follow yourself."

    following[uid].add(tid)
    followers[tid].add(uid)

    notifications[tid].append({
        "type": "follow",
        "from": users[uid]["username"],
        "ts": time.time()
    })

    return f"You now follow {target_username}."


def unfollow(token: str, target_username: str) -> str:
    data = verify_token(token)
    if not data:
        return "Invalid token."

    uid = data["uid"]
    target = find_user_by_username(target_username)

    if not target:
        return "User not found."

    tid = target["id"]
    following[uid].discard(tid)
    followers[tid].discard(uid)

    return "Unfollowed."


# ----------------------------------------------------------------------
# TWEETS
# ----------------------------------------------------------------------

def create_tweet(token: str, text: str, parent: Optional[str] = None,
                 media: Optional[str] = None, quote: Optional[str] = None) -> str:
    data = verify_token(token)
    if not data:
        return "Invalid token."

    if not text:
        return "Tweet cannot be empty."

    if len(text) > MAX_TWEET_LENGTH:
        return "Tweet too long."

    uid = data["uid"]
    tid = str(uuid4())

    tweets[tid] = {
        "id": tid,
        "user": uid,
        "text": text,
        "media": media,
        "parent": parent,
        "quote": quote,
        "likes": set(),
        "retweets": set(),
        "ts": time.time(),
    }

    # Notify reply owner
    if parent and parent in tweets:
        owner = tweets[parent]["user"]
        notifications[owner].append({
            "type": "reply",
            "from": users[uid]["username"],
            "tweet": tid,
            "ts": time.time()
        })

    return f"Tweet posted. ID={tid}"


# ----------------------------------------------------------------------
# ENGAGEMENT
# ----------------------------------------------------------------------

def like_tweet(token: str, tweet_id: str) -> str:
    data = verify_token(token)
    if not data:
        return "Invalid token."

    if tweet_id not in tweets:
        return "Tweet not found."

    tweets[tweet_id]["likes"].add(data["uid"])
    return "Liked."


def retweet(token: str, tweet_id: str) -> str:
    data = verify_token(token)
    if not data:
        return "Invalid token."

    if tweet_id not in tweets:
        return "Tweet not found."

    tweets[tweet_id]["retweets"].add(data["uid"])
    return "Retweeted."


# ----------------------------------------------------------------------
# FEED
# ----------------------------------------------------------------------

def home_feed(token: str) -> List[Dict[str, Any]]:
    data = verify_token(token)
    if not data:
        return "Invalid token."

    uid = data["uid"]
    visible_users = following[uid] | {uid}

    timeline = [
        t for t in tweets.values()
        if t["user"] in visible_users
    ]

    timeline.sort(key=lambda x: x["ts"], reverse=True)

    return [
        {
            "id": t["id"],
            "user": users[t["user"]]["username"],
            "text": t["text"],
            "likes": len(t["likes"]),
            "retweets": len(t["retweets"]),
            "timestamp": t["ts"],
        }
        for t in timeline
    ]


# ----------------------------------------------------------------------
# SEARCH
# ----------------------------------------------------------------------

def search_tweets(keyword: str) -> List[Dict[str, Any]]:
    key = keyword.lower()
    return [t for t in tweets.values() if key in t["text"].lower()]


def search_users(keyword: str) -> List[Dict[str, Any]]:
    key = keyword.lower()
    return [u for u in users.values() if key in u["username"].lower()]


# ----------------------------------------------------------------------
# NOTIFICATIONS
# ----------------------------------------------------------------------

def get_notifications(token: str) -> Any:
    data = verify_token(token)
    if not data:
        return "Invalid token."
    return notifications[data["uid"]]


# ----------------------------------------------------------------------
# MODERATION
# ----------------------------------------------------------------------

def report_tweet(tweet_id: str) -> str:
    if tweet_id not in tweets:
        return "Tweet not found."
    return f"Tweet {tweet_id} reported."


# ----------------------------------------------------------------------
# TESTING
# ----------------------------------------------------------------------

if __name__ == "__main__":
    print("Registering test user...")
    print(register("a@test.com", "asher", "pass123"))

    print("\nLogging in...")
    token = login("asher", "pass123")
    print("Token:", token)

    print("\nPosting tweet...")
    print(create_tweet(token, "Hello Twitter!"))

    print("\nFeed:")
    print(home_feed(token))
