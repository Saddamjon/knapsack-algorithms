from typing import List, Tuple


def solve_knapsack_greedy(
    weights: List[int], values: List[int], capacity: int
) -> Tuple[int, List[int]]:
    """
    Жадный алгоритм: берёт предметы по убыванию отношения ценность/вес.

    Для 0/1‑задачи о рюкзаке даёт приближённое решение.
    """
    n = len(weights)
    if n == 0 or capacity <= 0:
        return 0, []

    items = list(range(n))
    items.sort(key=lambda i: values[i] / weights[i], reverse=True)

    total_weight = 0
    total_value = 0
    selected: List[int] = []

    for i in items:
        if total_weight + weights[i] <= capacity:
            total_weight += weights[i]
            total_value += values[i]
            selected.append(i)

    selected.sort()
    return total_value, selected


__all__ = ["solve_knapsack_greedy"]

