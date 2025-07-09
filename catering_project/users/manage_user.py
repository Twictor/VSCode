import sys
import os

# Добавляем корень проекта в PYTHONPATH
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Добавляем в sys.path
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

# Указываем Django settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

# Инициализируем Django
import django
django.setup()

# Импортируем модель
from users.models import User

from datetime import datetime, timedelta, timezone
import jwt

# JWT настройки
JWT_SECRET = 'your_very_secure_secret_key_here'
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION = timedelta(days=1)

def generate_jwt_token(user_id, role):
    payload = {
        'user_id': user_id,
        'role': role,
        'exp': datetime.now(timezone.utc) + JWT_EXPIRATION
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def verify_jwt_token(token):
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.PyJWTError:
        return None

if __name__ == "__main__":
    test_email = "test_user@example.com"
    test_password = "VerySecurePassword123"

    # Проверяем, существует ли пользователь
    if User.objects.filter(email=test_email).exists():
        user = User.objects.get(email=test_email)
        print("⚠️ User already exists.")
    else:
        user = User.objects.create_user(
            email=test_email,
            password=test_password,
            phone_number="1234567890",
            first_name="Test",
            last_name="User"
        )
        print("✅ User created.")

    # Аутентификация
    if user.check_password(test_password):
        print("🔐 Password is valid.")
        token = generate_jwt_token(user.id, user.role)
        print(f"📦 JWT Token:\n{token}")

        # Верификация токена
        decoded = verify_jwt_token(token)
        print("🪪 Decoded token payload:")
        print(decoded)
    else:
        print("❌ Invalid password.")
