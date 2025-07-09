import psycopg
from dataclasses import dataclass
from typing import Optional
from datetime import datetime, timedelta
import jwt
from jwt.exceptions import InvalidTokenError
from django.conf import settings

# Conf JWT
JWT_SECRET = getattr(settings, 'JWT_SECRET', 'your-secret-key')
JWT_ALGORITHM = 'HS256'
JWT_EXP_DELTA_SECONDS = 3600  # 1h


@dataclass
class AuthUser:
    id: int
    email: str
    password: str
    first_name: str
    last_name: str
    phone: str
    role: str

    @classmethod
    def get_by_email(cls, email: str) -> Optional['AuthUser']:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    (
                        (
                            "SELECT id, email, password, first_name, "
                            "last_name, phone, role "
                            "FROM users WHERE email = %s;"
                        )
                    ),
                    (email,)
                )
                result = cur.fetchone()
                if result:
                    return AuthUser(*result)
                return None

    def verify_password(self, password: str) -> bool:
        from django.contrib.auth.hashers import check_password
        return check_password(password, self.password)

    def generate_token(self) -> str:
        payload = {
            'user_id': self.id,
            'email': self.email,
            'role': self.role,
            'exp': datetime.utcnow() + timedelta(seconds=JWT_EXP_DELTA_SECONDS)
        }
        return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

    @staticmethod
    def verify_token(token: str) -> Optional[dict]:
        try:
            return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        except InvalidTokenError:
            return None


def get_connection():
    return psycopg.connect(
        dbname="postgres",
        user="postgres",
        password="postgres",
        host="localhost",
        port="5432",
        autocommit=True
    )