import random
import string
from decimal import Decimal
def generate_ticket_number():
    """Генерирует уникальный номер билета."""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

def get_ticket_type(zone):
    """Определяет тип билета на основе зоны."""

    return f"Билет для зоны {zone.zone_type}"

def calculate_ticket_cost(event, zone):
    """Рассчитывает стоимость билета."""

    return event.event_cost * zone.zone_multiplier  
