"""Integration tests for the FastAPI application."""

import pytest
from fastapi.testclient import TestClient
from datetime import date
from src.main import app

@pytest.fixture
def client():
    return TestClient(app)


def test_health_check(client):
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_optimize_example_from_assignment(client):
    """Test the exact example from the assignment."""
    payload = {
        "truck": {"id": "truck-123", "max_weight_lbs": 44000, "max_volume_cuft": 3000},
        "orders": [
            {
                "id": "ord-001",
                "payout_cents": 250000,
                "weight_lbs": 18000,
                "volume_cuft": 1200,
                "origin": "Los Angeles, CA",
                "destination": "Dallas, TX",
                "pickup_date": "2025-12-05",
                "delivery_date": "2025-12-09",
                "is_hazmat": False,
            },
            {
                "id": "ord-002",
                "payout_cents": 180000,
                "weight_lbs": 12000,
                "volume_cuft": 900,
                "origin": "Los Angeles, CA",
                "destination": "Dallas, TX",
                "pickup_date": "2025-12-04",
                "delivery_date": "2025-12-10",
                "is_hazmat": False,
            },
            {
                "id": "ord-003",
                "payout_cents": 320000,
                "weight_lbs": 30000,
                "volume_cuft": 1800,
                "origin": "Los Angeles, CA",
                "destination": "Dallas, TX",
                "pickup_date": "2025-12-06",
                "delivery_date": "2025-12-08",
                "is_hazmat": True,
            },
        ],
    }
    response = client.post("/api/v1/load-optimizer/optimize", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    assert data["truck_id"] == "truck-123"
    assert set(data["selected_order_ids"]) == {"ord-001", "ord-002"}
    assert data["total_payout_cents"] == 430000
    assert data["total_weight_lbs"] == 30000
    assert data["total_volume_cuft"] == 2100
    assert abs(data["utilization_weight_percent"] - 68.18) < 0.01
    assert abs(data["utilization_volume_percent"] - 70.0) < 0.01


def test_optimize_no_orders(client):
    """Test with empty orders list."""
    payload = {
        "truck": {"id": "truck-123", "max_weight_lbs": 44000, "max_volume_cuft": 3000},
        "orders": [],
    }
    response = client.post("/api/v1/load-optimizer/optimize", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    assert data["selected_order_ids"] == []
    assert data["total_payout_cents"] == 0
    assert data["total_weight_lbs"] == 0
    assert data["total_volume_cuft"] == 0


def test_optimize_invalid_date_format(client):
    """Test with invalid date format."""
    payload = {
        "truck": {"id": "truck-123", "max_weight_lbs": 44000, "max_volume_cuft": 3000},
        "orders": [
            {
                "id": "ord-001",
                "payout_cents": 250000,
                "weight_lbs": 18000,
                "volume_cuft": 1200,
                "origin": "Los Angeles, CA",
                "destination": "Dallas, TX",
                "pickup_date": "2025/12/05",
                "delivery_date": "2025-12-09",
                "is_hazmat": False,
            }
        ],
    }
    response = client.post("/api/v1/load-optimizer/optimize", json=payload)
    assert response.status_code == 422


def test_optimize_negative_weight(client):
    """Test with negative weight (should fail validation)."""
    payload = {
        "truck": {"id": "truck-123", "max_weight_lbs": 44000, "max_volume_cuft": 3000},
        "orders": [
            {
                "id": "ord-001",
                "payout_cents": 250000,
                "weight_lbs": -100,
                "volume_cuft": 1200,
                "origin": "Los Angeles, CA",
                "destination": "Dallas, TX",
                "pickup_date": "2025-12-05",
                "delivery_date": "2025-12-09",
                "is_hazmat": False,
            }
        ],
    }
    response = client.post("/api/v1/load-optimizer/optimize", json=payload)
    assert response.status_code == 422


def test_optimize_delivery_before_pickup(client):
    """Test with delivery date before pickup date."""
    payload = {
        "truck": {"id": "truck-123", "max_weight_lbs": 44000, "max_volume_cuft": 3000},
        "orders": [
            {
                "id": "ord-001",
                "payout_cents": 250000,
                "weight_lbs": 18000,
                "volume_cuft": 1200,
                "origin": "Los Angeles, CA",
                "destination": "Dallas, TX",
                "pickup_date": "2025-12-09",
                "delivery_date": "2025-12-05",
                "is_hazmat": False,
            }
        ],
    }
    response = client.post("/api/v1/load-optimizer/optimize", json=payload)
    assert response.status_code == 422


def test_optimize_missing_truck(client):
    """Test with missing truck in request."""
    payload = {"orders": []}
    response = client.post("/api/v1/load-optimizer/optimize", json=payload)
    assert response.status_code == 422


def test_optimize_exceeds_max_orders(client):
    """Test with more than 22 orders."""
    orders = [
        {
            "id": f"ord-{i:03d}",
            "payout_cents": 100000,
            "weight_lbs": 1000,
            "volume_cuft": 100,
            "origin": "LA",
            "destination": "DL",
            "pickup_date": "2025-12-05",
            "delivery_date": "2025-12-09",
            "is_hazmat": False,
        }
        for i in range(23)
    ]
    payload = {
        "truck": {"id": "truck-123", "max_weight_lbs": 100000, "max_volume_cuft": 10000},
        "orders": orders,
    }
    response = client.post("/api/v1/load-optimizer/optimize", json=payload)
    assert response.status_code == 422
