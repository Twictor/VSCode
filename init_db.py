import psycopg
from django.conf import settings
import os
import sys

# Добавляем путь к проекту в PYTHONPATH
sys.path.append('C:/Users/Admin/myproject')  # Укажите полный путь к вашему проекту

# Устанавливаем переменную окружения Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')  # Замените myproject на имя вашего проекта

import django
django.setup()
def get_connection():
    return psycopg.connect(
        dbname=settings.DATABASES['default']['NAME'],
        user=settings.DATABASES['default']['USER'],
        password=settings.DATABASES['default']['PASSWORD'],
        host=settings.DATABASES['default']['HOST'],
        port=settings.DATABASES['default']['PORT'],
        autocommit=True
    )

def initialize_database():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    password VARCHAR(128) NOT NULL,
                    first_name VARCHAR(100) NOT NULL,
                    last_name VARCHAR(100) NOT NULL,
                    phone VARCHAR(20),
                    role VARCHAR(10) NOT NULL DEFAULT 'customer'
                );
            """)
            print("Таблица users создана/проверена")

if __name__ == "__main__":
    import os
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ваш_проект.settings")
    import django
    django.setup()
    initialize_database()