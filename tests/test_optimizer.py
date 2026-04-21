"""Tests for the load optimizer algorithm."""

import pytest
from datetime import date
from src.models import Order, Truck
from src.optimizer import LoadOptimizer


@pytest.fixture
def optimizer():
    return LoadOptimizer()


@pytest.fixture
def truck():
    return Truck(id="truck-123", max_weight_lbs=44000, max_volume_cuft=3000)


def test_optimize_backtracking_empty_orders(optimizer, truck):
    selected, payout, weight, volume = optimizer.optimize_backtracking(truck, [])
    assert selected == []
    assert payout == 0
    assert weight == 0
    assert volume == 0

def test_optimize_empty_orders(optimizer, truck):
    """Test with no orders."""
    selected, payout, weight, volume = optimizer.optimize(truck, [])
    assert selected == []
    assert payout == 0
    assert weight == 0
    assert volume == 0


def test_optimize_backtracking_single_order_fits(optimizer, truck):
    orders = [
        Order(
            id="ord-001",
            payout_cents=250000,
            weight_lbs=18000,
            volume_cuft=1200,
            origin="Los Angeles, CA",
            destination="Dallas, TX",
            pickup_date=date(2025, 12, 5),
            delivery_date=date(2025, 12, 9),
            is_hazmat=False,
        )
    ]
    selected, payout, weight, volume = optimizer.optimize_backtracking(truck, orders)
    assert selected == ["ord-001"]
    assert payout == 250000
    assert weight == 18000
    assert volume == 1200

def test_optimize_single_order_fits(optimizer, truck):
    """Test with a single order that fits."""
    orders = [
        Order(
            id="ord-001",
            payout_cents=250000,
            weight_lbs=18000,
            volume_cuft=1200,
            origin="Los Angeles, CA",
            destination="Dallas, TX",
            pickup_date=date(2025, 12, 5),
            delivery_date=date(2025, 12, 9),
            is_hazmat=False,
        )
    ]
    selected, payout, weight, volume = optimizer.optimize(truck, orders)
    assert selected == ["ord-001"]
    assert payout == 250000
    assert weight == 18000
    assert volume == 1200


def test_optimize_backtracking_single_order_exceeds_weight(optimizer, truck):
    orders = [
        Order(
            id="ord-001",
            payout_cents=250000,
            weight_lbs=50000,
            volume_cuft=1200,
            origin="Los Angeles, CA",
            destination="Dallas, TX",
            pickup_date=date(2025, 12, 5),
            delivery_date=date(2025, 12, 9),
            is_hazmat=False,
        )
    ]
    selected, payout, weight, volume = optimizer.optimize_backtracking(truck, orders)
    assert selected == []
    assert payout == 0

def test_optimize_single_order_exceeds_weight(optimizer, truck):
    """Test with a single order that exceeds weight."""
    orders = [
        Order(
            id="ord-001",
            payout_cents=250000,
            weight_lbs=50000,
            volume_cuft=1200,
            origin="Los Angeles, CA",
            destination="Dallas, TX",
            pickup_date=date(2025, 12, 5),
            delivery_date=date(2025, 12, 9),
            is_hazmat=False,
        )
    ]
    selected, payout, weight, volume = optimizer.optimize(truck, orders)
    assert selected == []
    assert payout == 0


def test_optimize_backtracking_assignment_example(optimizer, truck):
    orders = [
        Order(
            id="ord-001",
            payout_cents=250000,
            weight_lbs=18000,
            volume_cuft=1200,
            origin="Los Angeles, CA",
            destination="Dallas, TX",
            pickup_date=date(2025, 12, 5),
            delivery_date=date(2025, 12, 9),
            is_hazmat=False,
        ),
        Order(
            id="ord-002",
            payout_cents=180000,
            weight_lbs=12000,
            volume_cuft=900,
            origin="Los Angeles, CA",
            destination="Dallas, TX",
            pickup_date=date(2025, 12, 4),
            delivery_date=date(2025, 12, 10),
            is_hazmat=False,
        ),
        Order(
            id="ord-003",
            payout_cents=320000,
            weight_lbs=30000,
            volume_cuft=1800,
            origin="Los Angeles, CA",
            destination="Dallas, TX",
            pickup_date=date(2025, 12, 6),
            delivery_date=date(2025, 12, 8),
            is_hazmat=True,
        ),
    ]
    selected, payout, weight, volume = optimizer.optimize_backtracking(truck, orders)
    assert set(selected) == {"ord-001", "ord-002"}
    assert payout == 430000
    assert weight == 30000
    assert volume == 2100

def test_optimize_assignment_example(optimizer, truck):
    """Test the exact example from the assignment."""
    orders = [
        Order(
            id="ord-001",
            payout_cents=250000,
            weight_lbs=18000,
            volume_cuft=1200,
            origin="Los Angeles, CA",
            destination="Dallas, TX",
            pickup_date=date(2025, 12, 5),
            delivery_date=date(2025, 12, 9),
            is_hazmat=False,
        ),
        Order(
            id="ord-002",
            payout_cents=180000,
            weight_lbs=12000,
            volume_cuft=900,
            origin="Los Angeles, CA",
            destination="Dallas, TX",
            pickup_date=date(2025, 12, 4),
            delivery_date=date(2025, 12, 10),
            is_hazmat=False,
        ),
        Order(
            id="ord-003",
            payout_cents=320000,
            weight_lbs=30000,
            volume_cuft=1800,
            origin="Los Angeles, CA",
            destination="Dallas, TX",
            pickup_date=date(2025, 12, 6),
            delivery_date=date(2025, 12, 8),
            is_hazmat=True,
        ),
    ]
    selected, payout, weight, volume = optimizer.optimize(truck, orders)
    
    # Expected: ord-001 + ord-002 = 430,000 cents
    assert set(selected) == {"ord-001", "ord-002"}
    assert payout == 430000
    assert weight == 30000
    assert volume == 2100


def test_optimize_backtracking_hazmat_alone(optimizer, truck):
    orders = [
        Order(
            id="ord-001",
            payout_cents=100000,
            weight_lbs=5000,
            volume_cuft=300,
            origin="LA",
            destination="DL",
            pickup_date=date(2025, 12, 5),
            delivery_date=date(2025, 12, 9),
            is_hazmat=False,
        ),
        Order(
            id="ord-002",
            payout_cents=500000,
            weight_lbs=10000,
            volume_cuft=500,
            origin="LA",
            destination="DL",
            pickup_date=date(2025, 12, 5),
            delivery_date=date(2025, 12, 9),
            is_hazmat=True,
        ),
    ]
    selected, payout, weight, volume = optimizer.optimize_backtracking(truck, orders)
    assert selected == ["ord-002"]
    assert payout == 500000

def test_optimize_hazmat_alone(optimizer, truck):
    """Test that hazmat orders are selected alone."""
    orders = [
        Order(
            id="ord-001",
            payout_cents=100000,
            weight_lbs=5000,
            volume_cuft=300,
            origin="LA",
            destination="DL",
            pickup_date=date(2025, 12, 5),
            delivery_date=date(2025, 12, 9),
            is_hazmat=False,
        ),
        Order(
            id="ord-002",
            payout_cents=500000,
            weight_lbs=10000,
            volume_cuft=500,
            origin="LA",
            destination="DL",
            pickup_date=date(2025, 12, 5),
            delivery_date=date(2025, 12, 9),
            is_hazmat=True,
        ),
    ]
    selected, payout, weight, volume = optimizer.optimize(truck, orders)
    
    # Should pick the higher-payout hazmat alone
    assert selected == ["ord-002"]
    assert payout == 500000


def test_optimize_backtracking_different_routes_incompatible(optimizer, truck):
    orders = [
        Order(
            id="ord-001",
            payout_cents=250000,
            weight_lbs=18000,
            volume_cuft=1200,
            origin="Los Angeles, CA",
            destination="Dallas, TX",
            pickup_date=date(2025, 12, 5),
            delivery_date=date(2025, 12, 9),
            is_hazmat=False,
        ),
        Order(
            id="ord-002",
            payout_cents=180000,
            weight_lbs=12000,
            volume_cuft=900,
            origin="Los Angeles, CA",
            destination="New York, NY",
            pickup_date=date(2025, 12, 4),
            delivery_date=date(2025, 12, 10),
            is_hazmat=False,
        ),
    ]
    selected, payout, weight, volume = optimizer.optimize_backtracking(truck, orders)
    assert selected == ["ord-001"]
    assert payout == 250000

def test_optimize_different_routes_incompatible(optimizer, truck):
    """Test that orders with different routes are not combined."""
    orders = [
        Order(
            id="ord-001",
            payout_cents=250000,
            weight_lbs=18000,
            volume_cuft=1200,
            origin="Los Angeles, CA",
            destination="Dallas, TX",
            pickup_date=date(2025, 12, 5),
            delivery_date=date(2025, 12, 9),
            is_hazmat=False,
        ),
        Order(
            id="ord-002",
            payout_cents=180000,
            weight_lbs=12000,
            volume_cuft=900,
            origin="Los Angeles, CA",
            destination="New York, NY",
            pickup_date=date(2025, 12, 4),
            delivery_date=date(2025, 12, 10),
            is_hazmat=False,
        ),
    ]
    selected, payout, weight, volume = optimizer.optimize(truck, orders)
    
    # Should pick the highest payout order alone
    assert selected == ["ord-001"]
    assert payout == 250000


def test_optimize_backtracking_multiple_valid_combinations(optimizer, truck):
    orders = [
        Order(
            id="ord-001",
            payout_cents=100000,
            weight_lbs=5000,
            volume_cuft=300,
            origin="LA",
            destination="DL",
            pickup_date=date(2025, 12, 5),
            delivery_date=date(2025, 12, 9),
            is_hazmat=False,
        ),
        Order(
            id="ord-002",
            payout_cents=100000,
            weight_lbs=5000,
            volume_cuft=300,
            origin="LA",
            destination="DL",
            pickup_date=date(2025, 12, 5),
            delivery_date=date(2025, 12, 9),
            is_hazmat=False,
        ),
        Order(
            id="ord-003",
            payout_cents=150000,
            weight_lbs=10000,
            volume_cuft=600,
            origin="LA",
            destination="DL",
            pickup_date=date(2025, 12, 5),
            delivery_date=date(2025, 12, 9),
            is_hazmat=False,
        ),
    ]
    selected, payout, weight, volume = optimizer.optimize_backtracking(truck, orders)
    assert set(selected) == {"ord-001", "ord-002", "ord-003"}
    assert payout == 350000

def test_optimize_multiple_valid_combinations(optimizer, truck):
    """Test that highest revenue is selected among valid combinations."""
    orders = [
        Order(
            id="ord-001",
            payout_cents=100000,
            weight_lbs=5000,
            volume_cuft=300,
            origin="LA",
            destination="DL",
            pickup_date=date(2025, 12, 5),
            delivery_date=date(2025, 12, 9),
            is_hazmat=False,
        ),
        Order(
            id="ord-002",
            payout_cents=100000,
            weight_lbs=5000,
            volume_cuft=300,
            origin="LA",
            destination="DL",
            pickup_date=date(2025, 12, 5),
            delivery_date=date(2025, 12, 9),
            is_hazmat=False,
        ),
        Order(
            id="ord-003",
            payout_cents=100000,
            weight_lbs=5000,
            volume_cuft=300,
            origin="LA",
            destination="DL",
            pickup_date=date(2025, 12, 5),
            delivery_date=date(2025, 12, 9),
            is_hazmat=False,
        ),
    ]
    selected, payout, weight, volume = optimizer.optimize(truck, orders)
    
    # Should select all 3 orders
    assert len(selected) == 3
    assert payout == 300000


def test_optimize_pareto_empty_orders(optimizer, truck):
    """Test Pareto optimization with no orders."""
    pareto = optimizer.optimize_pareto(truck, [])
    assert pareto == []


def test_optimize_pareto_single_order(optimizer, truck):
    """Test Pareto optimization with single order."""
    orders = [
        Order(
            id="ord-001",
            payout_cents=250000,
            weight_lbs=18000,
            volume_cuft=1200,
            origin="LA",
            destination="DL",
            pickup_date=date(2025, 12, 5),
            delivery_date=date(2025, 12, 9),
            is_hazmat=False,
        )
    ]
    pareto = optimizer.optimize_pareto(truck, orders)
    assert len(pareto) == 1
    assert pareto[0]['ids'] == ["ord-001"]
    assert pareto[0]['revenue_cents'] == 250000
    assert 0 < pareto[0]['utilization_pct'] < 100


def test_optimize_pareto_multiple_solutions(optimizer, truck):
    """Test Pareto optimization with multiple non-dominated solutions."""
    orders = [
        Order(
            id="ord-001",
            payout_cents=100000,
            weight_lbs=5000,
            volume_cuft=300,
            origin="LA",
            destination="DL",
            pickup_date=date(2025, 12, 5),
            delivery_date=date(2025, 12, 9),
            is_hazmat=False,
        ),
        Order(
            id="ord-002",
            payout_cents=150000,
            weight_lbs=8000,
            volume_cuft=400,
            origin="LA",
            destination="DL",
            pickup_date=date(2025, 12, 5),
            delivery_date=date(2025, 12, 9),
            is_hazmat=False,
        ),
    ]
    pareto = optimizer.optimize_pareto(truck, orders)
    # Should have 2 Pareto solutions: both together (highest revenue),
    # and ord-002 alone (better revenue than ord-001)
    assert len(pareto) >= 1
    # First should be both (highest revenue)
    assert set(pareto[0]['ids']) == {"ord-001", "ord-002"}
    assert pareto[0]['revenue_cents'] == 250000



def test_optimize_pareto_hazmat_constraint(optimizer, truck):
    """Test that Pareto respects hazmat constraints."""
    orders = [
        Order(
            id="ord-001",
            payout_cents=100000,
            weight_lbs=5000,
            volume_cuft=300,
            origin="LA",
            destination="DL",
            pickup_date=date(2025, 12, 5),
            delivery_date=date(2025, 12, 9),
            is_hazmat=False,
        ),
        Order(
            id="ord-002",
            payout_cents=500000,
            weight_lbs=10000,
            volume_cuft=500,
            origin="LA",
            destination="DL",
            pickup_date=date(2025, 12, 5),
            delivery_date=date(2025, 12, 9),
            is_hazmat=True,
        ),
    ]
    pareto = optimizer.optimize_pareto(truck, orders)
    # Should have 1 solution: hazmat alone (dominates regular alone on revenue)
    assert len(pareto) >= 1
    # First should be hazmat alone (highest revenue and doesn't combine with others)
    assert pareto[0]['ids'] == ["ord-002"]
    assert pareto[0]['revenue_cents'] == 500000


def test_optimize_weighted_revenue_only(optimizer, truck):
    """Test weighted optimization with revenue focus (default)."""
    orders = [
        Order(
            id="ord-001",
            payout_cents=100000,
            weight_lbs=5000,
            volume_cuft=300,
            origin="LA",
            destination="DL",
            pickup_date=date(2025, 12, 5),
            delivery_date=date(2025, 12, 9),
            is_hazmat=False,
        ),
        Order(
            id="ord-002",
            payout_cents=150000,
            weight_lbs=8000,
            volume_cuft=400,
            origin="LA",
            destination="DL",
            pickup_date=date(2025, 12, 5),
            delivery_date=date(2025, 12, 9),
            is_hazmat=False,
        ),
    ]
    selected, payout, weight, volume = optimizer.optimize_weighted(truck, orders, weight_revenue=1.0, weight_utilization=0.0)
    # Should prefer highest revenue
    assert set(selected) == {"ord-001", "ord-002"}
    assert payout == 250000


def test_optimize_weighted_balanced(optimizer, truck):
    """Test weighted optimization with balanced revenue/utilization."""
    orders = [
        Order(
            id="ord-001",
            payout_cents=100000,
            weight_lbs=5000,
            volume_cuft=300,
            origin="LA",
            destination="DL",
            pickup_date=date(2025, 12, 5),
            delivery_date=date(2025, 12, 9),
            is_hazmat=False,
        ),
        Order(
            id="ord-002",
            payout_cents=100000,
            weight_lbs=5000,
            volume_cuft=300,
            origin="LA",
            destination="DL",
            pickup_date=date(2025, 12, 5),
            delivery_date=date(2025, 12, 9),
            is_hazmat=False,
        ),
    ]
    selected, payout, weight, volume = optimizer.optimize_weighted(truck, orders, weight_revenue=1.0, weight_utilization=1.0)
    # Should still prefer both for higher overall score
    assert set(selected) == {"ord-001", "ord-002"}
    assert payout == 200000


def test_optimize_weighted_invalid_weights(optimizer, truck):
    """Test that negative weights raise error."""
    orders = [
        Order(
            id="ord-001",
            payout_cents=100000,
            weight_lbs=5000,
            volume_cuft=300,
            origin="LA",
            destination="DL",
            pickup_date=date(2025, 12, 5),
            delivery_date=date(2025, 12, 9),
            is_hazmat=False,
        )
    ]
    with pytest.raises(ValueError):
        optimizer.optimize_weighted(truck, orders, weight_revenue=-1.0, weight_utilization=0.0)


