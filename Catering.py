import uuid
from dataclasses import dataclass
import random
import abc
import queue
import threading
import time
from datetime import datetime, timedelta
from typing import Literal, Dict, List, Tuple

CHECK_ORDER_DELAY = 2
ARCHIVE_CHECK_INTERVAL = 10

OrderRequestBody = Tuple[str, datetime]
DeliveryProvider = Literal["Uklon", "Uber"]
OrderDeliveryStatus = Literal["ongoing", "finished"]

@dataclass
class DeliveryOrder:
    order_name: str
    number: uuid.UUID | None = None

class Storage:
    def __init__(self):
        self.lock = threading.Lock()
        self.dishes = [
            {
                "id": 1,
                "name": "Salad",
                "value": 1099,
                "restaurant": "Silpo",
            },
            {
                "id": 2,
                "name": "Soda",
                "value": 199,
                "restaurant": "Silpo",
            },
            {
                "id": 3,
                "name": "Pizza",
                "value": 599,
                "restaurant": "Kvadrat",
            },
        ]
        self.providers = ["uklon", "uber"]
        self.active_deliveries: Dict[str, int] = {"uklon": 0, "uber": 0}
        self.archived_orders: Dict[str, datetime] = {}
        self.active_orders: Dict[uuid.UUID, Tuple[str, OrderDeliveryStatus]] = {}

storage = Storage()

class DeliveryService(abc.ABC):
    def __init__(self, order: DeliveryOrder):
        self._order: DeliveryOrder = order

    @abc.abstractmethod
    def ship(self) -> None:
        """Resolve the order with concrete provider"""

    def _ship(self, delay: float):
        def _callback():
            time.sleep(delay)
            with storage.lock:
                storage.active_orders[self._order.number] = (
                    self.__class__.__name__.lower(), "finished"
                )
                storage.archived_orders[self._order.order_name] = datetime.now()
                storage.active_deliveries[self.__class__.__name__.lower()] -= 1
            print(f"🚚 DELIVERED {self._order}")

        thread = threading.Thread(target=_callback)
        thread.start()

class Uklon(DeliveryService):
    def ship(self) -> None:
        provider_name = self.__class__.__name__.lower()
        self._order.number = uuid.uuid4()
        
        with storage.lock:
            storage.active_orders[self._order.number] = (provider_name, "ongoing")
            storage.active_deliveries[provider_name] += 1

        delay: float = random.randint(1, 3)
        print(f"\n\t🚚 {provider_name} Shipping {self._order} with {delay} delay")
        self._ship(delay)

class Uber(DeliveryService):
    def ship(self) -> None:
        provider_name = self.__class__.__name__.lower()
        self._order.number = uuid.uuid4()
        
        with storage.lock:
            storage.active_orders[self._order.number] = (provider_name, "ongoing")
            storage.active_deliveries[provider_name] += 1

        delay: float = random.randint(3, 5)
        print(f"\n\t🚚 {provider_name} Shipping {self._order} with {delay} delay")
        self._ship(delay)

class Scheduler:
    def __init__(self):
        self.orders: queue.Queue[OrderRequestBody] = queue.Queue()
        
    @staticmethod
    def _service_dispatcher() -> type[DeliveryService]:
        return random.choice([Uklon, Uber])
            
    def ship_order(self, order_name: str) -> None:
        ConcreteDeliveryService = self._service_dispatcher()
        instance = ConcreteDeliveryService(order=DeliveryOrder(order_name=order_name))
        instance.ship()

    def process_orders(self) -> None:
        print("SCHEDULER PROCESSING...")
        while True:
            order = self.orders.get(True)
            time_to_wait = order[1] - datetime.now()
            if time_to_wait.total_seconds() > 0:
                self.orders.put(order)
                time.sleep(0.5)
            else:
                print(f"\n\t{order[0]} READY FOR DELIVERY")
                self.ship_order(order[0])

    def check_archived_orders(self) -> None:
        while True:
            time.sleep(ARCHIVE_CHECK_INTERVAL)
            with storage.lock:
                now = datetime.now()
                to_archive = [
                    name for name, end_time in storage.archived_orders.items()
                    if (now - end_time) >= timedelta(seconds=ARCHIVE_CHECK_INTERVAL)
                ]
                for name in to_archive:
                    print(f"\tARCHIVED ORDER: {name}")
                    del storage.archived_orders[name]

    def add_order(self, order: OrderRequestBody) -> None:
        self.orders.put(order)
        print(f"\n\t{order[0]} ADDED FOR PROCESSING")

def main():
    scheduler = Scheduler()

    # Start order processing thread
    order_thread = threading.Thread(target=scheduler.process_orders, daemon=True)
    order_thread.start()
    
    # Start archived orders cleaner thread
    archiver_thread = threading.Thread(target=scheduler.check_archived_orders, daemon=True)
    archiver_thread.start()

    while True:
        order_details = input("Enter order details: ")
        data = order_details.split(" ")
        if len(data) != 2 or not data[1].isdigit():
            print("Please enter in format: <order_name> <seconds>, e.g. A 5")
            continue
        order_name = data[0]
        delay = datetime.now() + timedelta(seconds=int(data[1]))
        scheduler.add_order(order=(order_name, delay))

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nExiting...")
        raise SystemExit(0)