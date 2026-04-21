"""Tests for constraint validators."""

import pytest
from datetime import date
from src.models import Order, Truck
from src.constraints import (
    are_routes_compatible,
    check_time_conflicts,
    check_hazmat_compatibility,
    validate_order_combination,
    can_fit_in_truck,
)


def test_routes_compatible_same_route():
    orders = [
        Order(
            id="1",
            payout_cents=100,
            weight_lbs=1000,
            volume_cuft=500,
            origin="LA",
            destination="DL",
            pickup_date=date(2025, 12, 5),
            delivery_date=date(2025, 12, 9),
        ),
        Order(
            id="2",
            payout_cents=100,
            weight_lbs=1000,
            volume_cuft=500,
            origin="LA",
            destination="DL",
            pickup_date=date(2025, 12, 6),
            delivery_date=date(2025, 12, 10),
        ),
    ]
    assert are_routes_compatible(orders) is True


def test_routes_compatible_different_destination():
    orders = [
        Order(
            id="1",
            payout_cents=100,
            weight_lbs=1000,
            volume_cuft=500,
            origin="LA",
            destination="DL",
            pickup_date=date(2025, 12, 5),
            delivery_date=date(2025, 12, 9),
        ),
        Order(
            id="2",
            payout_cents=100,
            weight_lbs=1000,
            volume_cuft=500,
            origin="LA",
            destination="NYC",
            pickup_date=date(2025, 12, 6),
            delivery_date=date(2025, 12, 10),
        ),
    ]
    assert are_routes_compatible(orders) is False


def test_hazmat_alone():
    hazmat_order = [
        Order(
            id="1",
            payout_cents=100,
            weight_lbs=1000,
            volume_cuft=500,
            origin="LA",
            destination="DL",
            pickup_date=date(2025, 12, 5),
            delivery_date=date(2025, 12, 9),
            is_hazmat=True,
        )
    ]
    assert check_hazmat_compatibility(hazmat_order) is True


def test_hazmat_with_other_order():
    orders = [
        Order(
            id="1",
            payout_cents=100,
            weight_lbs=1000,
            volume_cuft=500,
            origin="LA",
            destination="DL",
            pickup_date=date(2025, 12, 5),
            delivery_date=date(2025, 12, 9),
            is_hazmat=True,
        ),
        Order(
            id="2",
            payout_cents=100,
            weight_lbs=1000,
            volume_cuft=500,
            origin="LA",
            destination="DL",
            pickup_date=date(2025, 12, 6),
            delivery_date=date(2025, 12, 10),
            is_hazmat=False,
        ),
    ]
    assert check_hazmat_compatibility(orders) is False


def test_can_fit_in_truck_success():
    truck = Truck(id="t1", max_weight_lbs=50000, max_volume_cuft=5000)
    orders = [
        Order(
            id="1",
            payout_cents=100,
            weight_lbs=10000,
            volume_cuft=1000,
            origin="LA",
            destination="DL",
            pickup_date=date(2025, 12, 5),
            delivery_date=date(2025, 12, 9),
        ),
        Order(
            id="2",
            payout_cents=100,
            weight_lbs=20000,
            volume_cuft=2000,
            origin="LA",
            destination="DL",
            pickup_date=date(2025, 12, 6),
            delivery_date=date(2025, 12, 10),
        ),
    ]
    assert can_fit_in_truck(orders, truck) is True


def test_can_fit_in_truck_exceeds_weight():
    truck = Truck(id="t1", max_weight_lbs=25000, max_volume_cuft=5000)
    orders = [
        Order(
            id="1",
            payout_cents=100,
            weight_lbs=20000,
            volume_cuft=1000,
            origin="LA",
            destination="DL",
            pickup_date=date(2025, 12, 5),
            delivery_date=date(2025, 12, 9),
        ),
        Order(
            id="2",
            payout_cents=100,
            weight_lbs=10000,
            volume_cuft=2000,
            origin="LA",
            destination="DL",
            pickup_date=date(2025, 12, 6),
            delivery_date=date(2025, 12, 10),
        ),
    ]
    assert can_fit_in_truck(orders, truck) is False


def test_can_fit_in_truck_exceeds_volume():
    truck = Truck(id="t1", max_weight_lbs=50000, max_volume_cuft=2500)
    orders = [
        Order(
            id="1",
            payout_cents=100,
            weight_lbs=10000,
            volume_cuft=1500,
            origin="LA",
            destination="DL",
            pickup_date=date(2025, 12, 5),
            delivery_date=date(2025, 12, 9),
        ),
        Order(
            id="2",
            payout_cents=100,
            weight_lbs=10000,
            volume_cuft=1200,
            origin="LA",
            destination="DL",
            pickup_date=date(2025, 12, 6),
            delivery_date=date(2025, 12, 10),
        ),
    ]
    assert can_fit_in_truck(orders, truck) is False
