from itertools import product
from typing import List, Tuple


def solve_knapsack_bruteforce(
    weights: List[int], values: List[int], capacity: int
) -> Tuple[int, List[int]]:
    """
    Полный перебор для 0/1‑задачи о рюкзаке.

    Возвращает пару (максимальная ценность, список индексов выбранных предметов).
    """
    n = len(weights)
    if n == 0 or capacity <= 0:
        return 0, []

    best_value = 0
    best_mask: List[int] = []

    # Перебираем все возможные наборы (2^n комбинаций).
    for mask in product([0, 1], repeat=n):
        total_weight = 0
        total_value = 0
        for i, bit in enumerate(mask):
            if bit:
                total_weight += weights[i]
                if total_weight > capacity:
                    # Если превысили вместимость, дальше этот набор не рассматриваем.
                    total_value = -1
                    break
                total_value += values[i]

        if total_value > best_value:
            best_value = total_value
            best_mask = [i for i, bit in enumerate(mask) if bit]

    return best_value, best_mask


__all__ = ["solve_knapsack_bruteforce"]

