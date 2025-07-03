import psycopg
from dataclasses import dataclass
from typing import List


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


@dataclass
class User:
    id: int
    name: str
    phone: str
    role: str

    @classmethod
    def create_table(cls):
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR(100) NOT NULL,
                        phone VARCHAR(20),
                        role VARCHAR(20)
                    );
                """)

    @classmethod
    def create(cls, name: str, phone: str, role: str) -> 'User':
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    (
                        "INSERT INTO users (name, phone, role) "
                        "VALUES (%s, %s, %s) "
                        "RETURNING id, name, phone, role;"
                    ),
                    (name, phone, role)
                )
                result = cur.fetchone()
                return User(*result)

    @classmethod
    def get_all(cls) -> List['User']:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT id, name, phone, role FROM users;")
                return [User(*row) for row in cur.fetchall()]

    @classmethod
    def filter(cls, **kwargs) -> List['User']:
        with get_connection() as conn:
            with conn.cursor() as cur:
                conditions = " AND ".join([f"{k} = %s" for k in kwargs])
                query = (
                    "SELECT id, name, phone, role FROM users WHERE "
                    f"{conditions};"
                )
                cur.execute(query, tuple(kwargs.values()))
                return [User(*row) for row in cur.fetchall()]

    @classmethod
    def delete(cls, **kwargs) -> int:
        with get_connection() as conn:
            with conn.cursor() as cur:
                conditions = " AND ".join([f"{k} = %s" for k in kwargs])
                query = f"DELETE FROM users WHERE {conditions} RETURNING id;"
                cur.execute(query, tuple(kwargs.values()))
                return len(cur.fetchall())

    def update(self, **kwargs):
        with get_connection() as conn:
            with conn.cursor() as cur:
                set_clause = ", ".join([f"{k} = %s" for k in kwargs])
                query = (
                    f"UPDATE users SET {set_clause} WHERE id = %s "
                    "RETURNING id, name, phone, role;"
                )
                params = tuple(kwargs.values()) + (self.id,)
                cur.execute(query, params)
                result = cur.fetchone()
                if result:
                    self.name = result[1]
                    self.phone = result[2]
                    self.role = result[3]


@dataclass
class Dish:
    id: int
    name: str
    description: str
    price: float

    @classmethod
    def create_table(cls):
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS dishes (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR(100) NOT NULL,
                        description TEXT,
                        price DECIMAL(10, 2) NOT NULL
                    );
                """)

    @classmethod
    def create(cls, name: str, description: str, price: float) -> 'Dish':
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    (
                        "INSERT INTO dishes (name, description, price) "
                        "VALUES (%s, %s, %s) "
                        "RETURNING id, name, description, price;"
                    ),
                    (name, description, price)
                )
                result = cur.fetchone()
                return Dish(*result)

    @classmethod
    def get_all(cls) -> List['Dish']:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT id, name, description, price FROM dishes;")
                return [Dish(*row) for row in cur.fetchall()]

    @classmethod
    def filter(cls, **kwargs) -> List['Dish']:
        with get_connection() as conn:
            with conn.cursor() as cur:
                conditions = " AND ".join([f"{k} = %s" for k in kwargs])
                query = (
                    "SELECT id, name, description, price FROM dishes WHERE "
                    f"{conditions};"
                )
                cur.execute(query, tuple(kwargs.values()))
                return [Dish(*row) for row in cur.fetchall()]

    @classmethod
    def delete(cls, **kwargs) -> int:
        with get_connection() as conn:
            with conn.cursor() as cur:
                conditions = " AND ".join([f"{k} = %s" for k in kwargs])
                query = f"DELETE FROM dishes WHERE {conditions} RETURNING id;"
                cur.execute(query, tuple(kwargs.values()))
                return len(cur.fetchall())

    def update(self, **kwargs):
        with get_connection() as conn:
            with conn.cursor() as cur:
                set_clause = ", ".join([f"{k} = %s" for k in kwargs])
                query = (
                    f"UPDATE dishes SET {set_clause} WHERE id = %s "
                    "RETURNING id, name, description, price;"
                )
                params = tuple(kwargs.values()) + (self.id,)
                cur.execute(query, params)
                result = cur.fetchone()
                if result:
                    self.name = result[1]
                    self.description = result[2]
                    self.price = result[3]


@dataclass
class Order:
    id: int
    user_id: int
    status: str
    created_at: str

    @classmethod
    def create_table(cls):
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS orders (
                        id SERIAL PRIMARY KEY,
                        user_id INTEGER REFERENCES users(id),
                        status VARCHAR(20) NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                """)

    @classmethod
    def create(cls, user_id: int, status: str) -> 'Order':
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    (
                        "INSERT INTO orders (user_id, status) "
                        "VALUES (%s, %s) "
                        "RETURNING id, user_id, status, created_at;"
                    ),
                    (user_id, status)
                )
                result = cur.fetchone()
                return Order(*result)

    @classmethod
    def get_all(cls) -> List['Order']:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT id, user_id, status, created_at FROM orders;"
                )
                return [Order(*row) for row in cur.fetchall()]

    @classmethod
    def filter(cls, **kwargs) -> List['Order']:
        with get_connection() as conn:
            with conn.cursor() as cur:
                conditions = " AND ".join([f"{k} = %s" for k in kwargs])
                query = (
                    "SELECT id, user_id, status, created_at FROM orders WHERE "
                    f"{conditions};"
                )
                cur.execute(query, tuple(kwargs.values()))
                return [Order(*row) for row in cur.fetchall()]

    @classmethod
    def delete(cls, **kwargs) -> int:
        with get_connection() as conn:
            with conn.cursor() as cur:
                conditions = " AND ".join([f"{k} = %s" for k in kwargs])
                query = f"DELETE FROM orders WHERE {conditions} RETURNING id;"
                cur.execute(query, tuple(kwargs.values()))
                return len(cur.fetchall())

    def update(self, **kwargs):
        with get_connection() as conn:
            with conn.cursor() as cur:
                set_clause = ", ".join([f"{k} = %s" for k in kwargs])
                query = (
                    f"UPDATE orders SET {set_clause} WHERE id = %s "
                    "RETURNING id, user_id, status, created_at;"
                )
                params = tuple(kwargs.values()) + (self.id,)
                cur.execute(query, params)
                result = cur.fetchone()
                if result:
                    self.user_id = result[1]
                    self.status = result[2]
                    self.created_at = result[3]


@dataclass
class OrderItem:
    id: int
    order_id: int
    dish_id: int
    quantity: int
    price_at_order: float

    @classmethod
    def create_table(cls):
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS order_items (
                        id SERIAL PRIMARY KEY,
                        order_id INTEGER REFERENCES orders(id),
                        dish_id INTEGER REFERENCES dishes(id),
                        quantity INTEGER NOT NULL,
                        price_at_order DECIMAL(10, 2) NOT NULL
                    );
                """)

    @classmethod
    def create(
        cls,
        order_id: int,
        dish_id: int,
        quantity: int,
        price_at_order: float
    ) -> 'OrderItem':
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    (
                        (
                            "INSERT INTO order_items "
                            "(order_id, dish_id, quantity, price_at_order) "
                            "VALUES (%s, %s, %s, %s) "
                            "RETURNING id, order_id, dish_id, quantity, "
                            "price_at_order;"
                        )
                    ),
                    (order_id, dish_id, quantity, price_at_order)
                )
                result = cur.fetchone()
                return OrderItem(*result)

    @classmethod
    def get_all(cls) -> List['OrderItem']:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT id, order_id, dish_id, quantity, price_at_order "
                    "FROM order_items;"
                )
                return [OrderItem(*row) for row in cur.fetchall()]

    @classmethod
    def filter(cls, **kwargs) -> List['OrderItem']:
        with get_connection() as conn:
            with conn.cursor() as cur:
                conditions = " AND ".join([f"{k} = %s" for k in kwargs])
                query = (
                    "SELECT id, order_id, dish_id, quantity, price_at_order "
                    f"FROM order_items WHERE {conditions};"
                )
                cur.execute(query, tuple(kwargs.values()))
                return [OrderItem(*row) for row in cur.fetchall()]

    @classmethod
    def delete(cls, **kwargs) -> int:
        with get_connection() as conn:
            with conn.cursor() as cur:
                conditions = " AND ".join([f"{k} = %s" for k in kwargs])
                query = (
                    f"DELETE FROM order_items WHERE {conditions} RETURNING id;"
                )
                cur.execute(query, tuple(kwargs.values()))
                return len(cur.fetchall())

    def update(self, **kwargs):
        with get_connection() as conn:
            with conn.cursor() as cur:
                set_clause = ", ".join([f"{k} = %s" for k in kwargs])
                query = (
                    f"UPDATE order_items SET {set_clause} "
                    "WHERE id = %s RETURNING id, order_id, dish_id, "
                    "quantity, price_at_order;"
                )
                params = tuple(kwargs.values()) + (self.id,)
                cur.execute(query, params)
                result = cur.fetchone()
                if result:
                    self.order_id = result[1]
                    self.dish_id = result[2]
                    self.quantity = result[3]
                    self.price_at_order = result[4]


def initialize_database():
    User.create_table()
    Dish.create_table()
    Order.create_table()
    OrderItem.create_table()


if __name__ == "__main__":
    initialize_database()

    # Example usage:
    # Create users
    user1 = User.create("John Doe", "+3809365211", "USER")
    user2 = User.create("Marry", "+380934567890", "USER")
    
    # Get all users
    all_users = User.get_all()
    print("All users:")
    for user in all_users:
        print(user)
    
    # Filter users
    users_with_role = User.filter(role="USER")
    print("\nUsers with role USER:")
    for user in users_with_role:
        print(user)
    
    # Create dishes
    salad = Dish.create("Salad", "Fresh vegetables", 5.99)
    pizza = Dish.create("Pizza", "Pepperoni pizza", 12.99)
    
    # Create order
    order = Order.create(user1.id, "PENDING")
    
    # Add items to order
    OrderItem.create(order.id, salad.id, 2, salad.price)
    OrderItem.create(order.id, pizza.id, 1, pizza.price)
    
    # Update order status
    order.update(status="COMPLETED")
    
    # Get all order items
    order_items = OrderItem.filter(order_id=order.id)
    print("\nOrder items:")
    for item in order_items:
        print(item)