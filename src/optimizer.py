"""
Dynamic Programming and Backtracking Optimizers.

Implements multiple algorithms for optimal order selection:
1. DP with bitmask (O(2^n)) - iterates all subsets, maximizes revenue
2. Recursive backtracking with pruning (O(2^n)) - alternative algorithm
3. Pareto-optimal solutions (O(2^n)) - returns all non-dominated solutions

For n orders (n ≤ 22), each algorithm respects weight/volume/compatibility constraints.
Pareto solutions represent different trade-offs between revenue and utilization.
"""

from typing import List, Tuple, Dict
from src.models import Order, Truck
from src.constraints import validate_order_combination, can_fit_in_truck


class LoadOptimizer:
    def optimize_backtracking(
        self, truck: Truck, orders: List[Order]
    ) -> Tuple[List[str], int, int, int]:
        """
        Recursive backtracking with pruning to find optimal subset of orders.
        Returns:
            (selected_order_ids, total_payout_cents, total_weight_lbs, total_volume_cuft)
        """
        n = len(orders)
        best = {'revenue': 0, 'ids': [], 'weight': 0, 'volume': 0}

        def backtrack(idx, selected):
            # Prune: check constraints only if at least one order is selected
            if selected:
                is_valid, _ = validate_order_combination(selected)
                if not is_valid or not can_fit_in_truck(selected, truck):
                    return
                revenue = sum(o.payout_cents for o in selected)
                if revenue > best['revenue']:
                    best['revenue'] = revenue
                    best['ids'] = [o.id for o in selected]
                    best['weight'] = sum(o.weight_lbs for o in selected)
                    best['volume'] = sum(o.volume_cuft for o in selected)
            if idx == n:
                return
            # Include current order
            backtrack(idx + 1, selected + [orders[idx]])
            # Exclude current order
            backtrack(idx + 1, selected)

        backtrack(0, [])
        return best['ids'], best['revenue'], best['weight'], best['volume']

    def optimize_weighted(
        self, truck: Truck, orders: List[Order], weight_revenue: float = 1.0, weight_utilization: float = 0.0
    ) -> Tuple[List[str], int, int, int]:
        """
        Find optimal subset with configurable objective weights.

        Args:
            truck: Truck specifications
            orders: List of orders to optimize
            weight_revenue: Weight for revenue objective (default: 1.0)
            weight_utilization: Weight for utilization objective (default: 0.0)
                               Set to 1.0 for balanced, or adjust for preference

        Returns:
            (selected_order_ids, total_payout_cents, total_weight_lbs, total_volume_cuft)
        """
        if weight_revenue < 0 or weight_utilization < 0:
            raise ValueError("Weights must be non-negative")

        n = len(orders)
        if n == 0:
            return [], 0, 0, 0

        best_score = -1
        best_mask = 0

        for mask in range(1, 1 << n):
            selected_orders = [orders[i] for i in range(n) if mask & (1 << i)]

            is_valid, _ = validate_order_combination(selected_orders)
            if not is_valid:
                continue

            if not can_fit_in_truck(selected_orders, truck):
                continue

            revenue = sum(o.payout_cents for o in selected_orders)
            weight = sum(o.weight_lbs for o in selected_orders)
            volume = sum(o.volume_cuft for o in selected_orders)

            # Compute utilization: average of weight and volume utilization
            weight_util = weight / truck.max_weight_lbs
            volume_util = volume / truck.max_volume_cuft
            utilization = (weight_util + volume_util) / 2

            # Weighted score: revenue + alpha * utilization
            # Normalize utilization to [0, truck_capacity] scale for fair comparison
            score = weight_revenue * revenue + weight_utilization * (utilization * truck.max_weight_lbs)

            if score > best_score:
                best_score = score
                best_mask = mask

        if best_mask == 0:
            return [], 0, 0, 0

        selected_orders = [orders[i] for i in range(n) if best_mask & (1 << i)]
        selected_ids = [o.id for o in selected_orders]
        total_weight = sum(o.weight_lbs for o in selected_orders)
        total_volume = sum(o.volume_cuft for o in selected_orders)

        return selected_ids, sum(o.payout_cents for o in selected_orders), total_weight, total_volume

    def optimize(
        self, truck: Truck, orders: List[Order]
    ) -> Tuple[List[str], int, int, int]:
        """
        Find the optimal subset of orders that maximizes revenue using DP with bitmask.

        Returns:
            (selected_order_ids, total_payout_cents, total_weight_lbs, total_volume_cuft)
        """
        n = len(orders)

        # Edge case: no orders
        if n == 0:
            return [], 0, 0, 0

        # Single order
        if n == 1:
            order = orders[0]
            if can_fit_in_truck([order], truck):
                return [order.id], order.payout_cents, order.weight_lbs, order.volume_cuft
            return [], 0, 0, 0

        best_revenue = 0
        best_mask = 0

        # Iterate through all possible subsets (2^n)
        for mask in range(1, 1 << n):
            selected_orders = [orders[i] for i in range(n) if mask & (1 << i)]

            # Check constraints
            is_valid, _ = validate_order_combination(selected_orders)
            if not is_valid:
                continue

            # Check truck capacity
            if not can_fit_in_truck(selected_orders, truck):
                continue

            # Calculate revenue
            revenue = sum(o.payout_cents for o in selected_orders)

            # Track best solution
            if revenue > best_revenue:
                best_revenue = revenue
                best_mask = mask

        # Reconstruct solution
        if best_mask == 0:
            return [], 0, 0, 0

        selected_orders = [orders[i] for i in range(n) if best_mask & (1 << i)]
        selected_ids = [o.id for o in selected_orders]
        total_weight = sum(o.weight_lbs for o in selected_orders)
        total_volume = sum(o.volume_cuft for o in selected_orders)

        return selected_ids, best_revenue, total_weight, total_volume

    def optimize_pareto(
        self, truck: Truck, orders: List[Order]
    ) -> List[Dict[str, any]]:
        """
        Find all Pareto-optimal solutions (non-dominated by revenue vs. utilization).

        A solution is Pareto-optimal if no other solution has both:
        - Higher revenue AND
        - Higher utilization (weight+volume used as % of truck capacity)

        Returns:
            List of dicts with keys: ids, revenue_cents, weight_lbs, volume_cuft, utilization_pct
            Sorted by descending revenue.
        """
        n = len(orders)
        solutions = []

        for mask in range(1, 1 << n):
            selected_orders = [orders[i] for i in range(n) if mask & (1 << i)]

            # Check constraints
            is_valid, _ = validate_order_combination(selected_orders)
            if not is_valid:
                continue

            if not can_fit_in_truck(selected_orders, truck):
                continue

            # Calculate metrics
            revenue = sum(o.payout_cents for o in selected_orders)
            weight = sum(o.weight_lbs for o in selected_orders)
            volume = sum(o.volume_cuft for o in selected_orders)

            # Utilization: (weight/max_weight + volume/max_volume) / 2 * 100
            weight_util = weight / truck.max_weight_lbs
            volume_util = volume / truck.max_volume_cuft
            utilization_pct = ((weight_util + volume_util) / 2) * 100

            solution = {
                'ids': [o.id for o in selected_orders],
                'revenue_cents': revenue,
                'weight_lbs': weight,
                'volume_cuft': volume,
                'utilization_pct': utilization_pct
            }
            solutions.append(solution)

        # Filter to Pareto-optimal solutions
        pareto = []
        for sol in solutions:
            dominated = False
            for other in solutions:
                if (other['revenue_cents'] > sol['revenue_cents'] and
                    other['utilization_pct'] > sol['utilization_pct']):
                    dominated = True
                    break
            if not dominated:
                pareto.append(sol)

        # Sort by descending revenue
        pareto.sort(key=lambda x: x['revenue_cents'], reverse=True)
        return pareto

