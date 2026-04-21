"""FastAPI application for Truck Load Optimizer."""

from fastapi import FastAPI, HTTPException, status
from src.models import OptimizeRequest, OptimizeResponse
from src.optimizer import LoadOptimizer

app = FastAPI(
    title="Truck Load Optimizer",
    description="Optimize truck loading to maximize carrier payout",
    version="1.0.0",
)

optimizer = LoadOptimizer()


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.post(
    "/api/v1/load-optimizer/optimize",
    response_model=OptimizeResponse,
    status_code=status.HTTP_200_OK,
)
async def optimize_load(request: OptimizeRequest):
    """
    Optimize truck loading to maximize carrier payout while respecting constraints.

    Constraints:
    - All orders must have the same origin and destination
    - Weight must not exceed truck capacity
    - Volume must not exceed truck capacity
    - Hazmat orders cannot be combined with other orders
    - Pickup date <= delivery date

    Returns the optimal subset of orders that maximizes payout.
    """
    try:
        # Validate request has at least a truck
        if not request.truck:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Truck information is required",
            )

        # Run optimization
        selected_ids, total_payout, total_weight, total_volume = optimizer.optimize(
            request.truck, request.orders
        )

        # Calculate utilization percentages
        weight_util = (
            (total_weight / request.truck.max_weight_lbs * 100)
            if request.truck.max_weight_lbs > 0
            else 0
        )
        volume_util = (
            (total_volume / request.truck.max_volume_cuft * 100)
            if request.truck.max_volume_cuft > 0
            else 0
        )

        return OptimizeResponse(
            truck_id=request.truck.id,
            selected_order_ids=selected_ids,
            total_payout_cents=total_payout,
            total_weight_lbs=total_weight,
            total_volume_cuft=total_volume,
            utilization_weight_percent=round(weight_util, 2),
            utilization_volume_percent=round(volume_util, 2),
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}",
        )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8080)
