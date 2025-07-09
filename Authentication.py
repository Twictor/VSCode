import psycopg
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import jwt
import hashlib
import secrets
import string

# Database connection setup
def get_connection():
    return psycopg.connect(
        dbname="postgres",
        user="postgres",
        password="postgres",
        host="localhost",
        port="5432",
        autocommit=True
    )
    
# JWT settings
JWT_SECRET = '1oRf5isc_tlXfHMyiAqX1tW36jqSv8_yj_kCfec5K2w'
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION = timedelta(days=1)

def generate_salt():
    return ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(16))

def hash_password(password: str, salt: str) -> str:
    return hashlib.sha256((password + salt).encode()).hexdigest()

def generate_jwt_token(user_id: int, role: str) -> str:
    payload = {
        'user_id': user_id,
        'role': role,
        'exp': datetime.utcnow() + JWT_EXPIRATION
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def verify_jwt_token(token: str) -> Optional[Dict]:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.PyJWTError:
        return None

@dataclass
class User:
    id: int
    email: str
    phone: str
    first_name: str
    last_name: str
    role: str
    password_hash: str
    salt: str

    @classmethod
    def create_table(cls):
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        id SERIAL PRIMARY KEY,
                        email VARCHAR(255) NOT NULL UNIQUE,
                        phone VARCHAR(20) NOT NULL,
                        first_name VARCHAR(100) NOT NULL,
                        last_name VARCHAR(100) NOT NULL,
                        role VARCHAR(20) NOT NULL CHECK (role IN ('admin', 'customer', 'driver', 'support')),
                        password_hash VARCHAR(255) NOT NULL,
                        salt VARCHAR(32) NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                """)

    @classmethod
    def create(
        cls,
        email: str,
        phone: str,
        password: str,
        first_name: str,
        last_name: str,
        role: str = 'customer'
    ) -> 'User':
        salt = generate_salt()
        password_hash = hash_password(password, salt)
               
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO users 
                    (email, phone, first_name, last_name, role, password_hash, salt)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    RETURNING id, email, phone, first_name, last_name, role, password_hash, salt;
                    """,
                    (email, phone, first_name, last_name, role, password_hash, salt)
                )
                result = cur.fetchone()
                return User(*result)

    @classmethod
    def authenticate(cls, email: str, password: str) -> Optional['User']:
        user = cls.get_by_email(email)
        if not user:
            return None
            
        if user.password_hash != hash_password(password, user.salt):
            return None
            
        return user

    @classmethod
    def get_by_email(cls, email: str) -> Optional['User']:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id, email, phone, first_name, last_name, role, password_hash, salt
                    FROM users WHERE email = %s;
                    """,
                    (email,)
                )
                result = cur.fetchone()
                return User(*result) if result else None

    @classmethod
    def get_by_id(cls, user_id: int) -> Optional['User']:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id, email, phone, first_name, last_name, role, password_hash, salt
                    FROM users WHERE id = %s;
                    """,
                    (user_id,)
                )
                result = cur.fetchone()
                return User(*result) if result else None

    def generate_token(self) -> str:
        return generate_jwt_token(self.id, self.role)

def initialize_database():
    User.create_table()
    # Removed calls for non-existent classes

# Example usage
if __name__ == "__main__":
    initialize_database()
    
    # User creation
    user = User.create(
        email="user@example.com",  # Fixed email for consistency
        phone="+380938903502",
        password="securepassword",
        first_name="John",
        last_name="Doe"
    )
    print(f"Created user: {user}")
    
    # Authentication
    auth_user = User.authenticate("user@example.com", "securepassword")
    if auth_user:
        token = auth_user.generate_token()
        print(f"Auth successful. Token: {token}")
        
        # Token verification
        decoded = verify_jwt_token(token)
        print(f"Decoded token: {decoded}")
    else:
        print("Authentication failed")