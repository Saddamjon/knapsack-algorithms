import heapq
from dataclasses import dataclass
from itertools import count
from typing import List, Tuple

from ._common import value_density


@dataclass
class Node:
    level: int
    value: int
    weight: int
    bound: float
    taken: List[int]


def _bound(
    node: Node, n: int, capacity: int, weights: List[int], values: List[int]
) -> float:
    """
    Оценка сверху по методу дробного рюкзака для текущего узла.
    """
    if node.weight > capacity:
        return 0

    bound_value = node.value
    total_weight = node.weight
    j = node.level
    while j < n and total_weight + weights[j] <= capacity:
        total_weight += weights[j]
        bound_value += values[j]
        j += 1

    if j < n:
        remaining = capacity - total_weight
        bound_value += values[j] * (remaining / weights[j])

    return bound_value


def solve_knapsack_branch_and_bound(
    weights: List[int], values: List[int], capacity: int
) -> Tuple[int, List[int]]:
    """
    Метод ветвей и границ для 0/1‑задачи о рюкзаке.

    Предметы заранее сортируются по убыванию отношения ценность/вес.
    Узлы обрабатываются по стратегии best-first (куча по значению оценки).
    """
    n = len(weights)
    if n == 0 or capacity <= 0:
        return 0, []

    items = sorted(
        range(n), key=lambda i: value_density(values[i], weights[i]), reverse=True
    )
    sorted_weights = [weights[i] for i in items]
    sorted_values = [values[i] for i in items]

    best_value = 0
    best_taken_sorted: List[int] = []

    root = Node(level=0, value=0, weight=0, bound=0.0, taken=[])
    root.bound = _bound(root, n, capacity, sorted_weights, sorted_values)

    # Кучa хранит (-оценка, порядковый номер, узел): порядковый номер нужен,
    # чтобы при равных оценках не сравнивать сами узлы.
    tie = count()
    heap: List[Tuple[float, int, Node]] = [(-root.bound, next(tie), root)]

    while heap:
        _, _, node = heapq.heappop(heap)

        if node.bound <= best_value or node.level >= n:
            continue

        idx = node.level
        next_weight = node.weight + sorted_weights[idx]
        next_value = node.value + sorted_values[idx]
        if next_weight <= capacity:
            taken_with = node.taken + [idx]
            if next_value > best_value:
                best_value = next_value
                best_taken_sorted = taken_with

            child_with = Node(
                level=idx + 1,
                value=next_value,
                weight=next_weight,
                bound=0.0,
                taken=taken_with,
            )
            child_with.bound = _bound(
                child_with, n, capacity, sorted_weights, sorted_values
            )
            if child_with.bound > best_value:
                heapq.heappush(heap, (-child_with.bound, next(tie), child_with))

        # Ветка: не берем предмет.
        child_without = Node(
            level=idx + 1,
            value=node.value,
            weight=node.weight,
            bound=0.0,
            taken=list(node.taken),
        )
        child_without.bound = _bound(
            child_without, n, capacity, sorted_weights, sorted_values
        )
        if child_without.bound > best_value:
            heapq.heappush(heap, (-child_without.bound, next(tie), child_without))

    # Переводим индексы обратно к исходному порядку.
    selected_original = [items[i] for i in best_taken_sorted]
    selected_original.sort()
    return best_value, selected_original


__all__ = ["solve_knapsack_branch_and_bound"]
