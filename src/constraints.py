"""Constraint validators for order compatibility and feasibility."""

from typing import List
from datetime import date
from src.models import Order, Truck


def are_routes_compatible(orders: List[Order]) -> bool:
    """Check if all orders have the same origin and destination."""
    if not orders:
        return True
    first_origin = orders[0].origin
    first_destination = orders[0].destination
    return all(
        o.origin == first_origin and o.destination == first_destination
        for o in orders
    )


def check_time_conflicts(orders: List[Order]) -> bool:
    """
    Check for overlapping time windows.
    Simplified: all pickups <= deliveries within the group (individual validation done in model).
    For now, we allow any non-overlapping pickup/delivery dates as compatible.
    """
    if len(orders) <= 1:
        return True

    pickup_dates = [o.pickup_date for o in orders]
    delivery_dates = [o.delivery_date for o in orders]

    earliest_pickup = min(pickup_dates)
    latest_delivery = max(delivery_dates)

    return earliest_pickup <= latest_delivery


def check_hazmat_compatibility(orders: List[Order]) -> bool:
    """
    Hazmat orders must be alone.
    If any order is hazmat, the selection must contain exactly one order.
    """
    hazmat_count = sum(1 for o in orders if o.is_hazmat)
    if hazmat_count == 0:
        return True
    if hazmat_count > 0:
        return len(orders) == 1
    return True


def validate_order_combination(orders: List[Order]) -> tuple[bool, str]:
    """Validate if a combination of orders is feasible."""
    if not orders:
        return True, ""

    if not are_routes_compatible(orders):
        return False, "Orders must have matching origin and destination"

    if not check_time_conflicts(orders):
        return False, "Order time windows conflict"

    if not check_hazmat_compatibility(orders):
        return False, "Hazmat orders cannot be combined with other orders"

    return True, ""


def can_fit_in_truck(orders: List[Order], truck: Truck) -> bool:
    """Check if orders fit within truck weight and volume constraints."""
    total_weight = sum(o.weight_lbs for o in orders)
    total_volume = sum(o.volume_cuft for o in orders)
    return total_weight <= truck.max_weight_lbs and total_volume <= truck.max_volume_cuft
