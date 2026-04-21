from pydantic import BaseModel, Field, field_validator
from typing import List
from datetime import date


class Truck(BaseModel):
    id: str = Field(..., min_length=1)
    max_weight_lbs: int = Field(..., gt=0)
    max_volume_cuft: int = Field(..., gt=0)


class Order(BaseModel):
    id: str = Field(..., min_length=1)
    payout_cents: int = Field(..., ge=0)
    weight_lbs: int = Field(..., ge=0)
    volume_cuft: int = Field(..., ge=0)
    origin: str = Field(..., min_length=1)
    destination: str = Field(..., min_length=1)
    pickup_date: date
    delivery_date: date
    is_hazmat: bool = False

    @field_validator("delivery_date")
    @classmethod
    def delivery_after_pickup(cls, v, info):
        if "pickup_date" in info.data and v < info.data["pickup_date"]:
            raise ValueError("delivery_date must be >= pickup_date")
        return v


class OptimizeRequest(BaseModel):
    truck: Truck
    orders: List[Order] = Field(..., min_length=0, max_length=22)


class OptimizeResponse(BaseModel):
    truck_id: str
    selected_order_ids: List[str]
    total_payout_cents: int
    total_weight_lbs: int
    total_volume_cuft: int
    utilization_weight_percent: float
    utilization_volume_percent: float
