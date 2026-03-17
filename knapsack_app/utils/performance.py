import time
from dataclasses import dataclass
from typing import Callable, Dict, List, Sequence, Tuple, Optional

import numpy as np

from .data_generator import Item, generate_items, items_to_lists


AlgorithmFunc = Callable[[List[int], List[int], int], Tuple[int, List[int]]]


@dataclass
class AlgorithmResult:
    name: str
    max_value: int
    selected_items: List[int]
    elapsed: float


def measure_algorithm(
    name: str,
    func: AlgorithmFunc,
    weights: List[int],
    values: List[int],
    capacity: int,
    repeats: int = 1,
) -> AlgorithmResult:
    """
    Измеряет время выполнения одного алгоритма и возвращает результат.
    """
    best_value = 0
    best_items: List[int] = []

    start = time.perf_counter()
    for _ in range(max(1, repeats)):
        value, items = func(weights, values, capacity)
        if value > best_value:
            best_value = value
            best_items = items
    end = time.perf_counter()

    elapsed = (end - start) / max(1, repeats)
    return AlgorithmResult(
        name=name,
        max_value=best_value,
        selected_items=best_items,
        elapsed=elapsed,
    )


def compare_algorithms(
    algorithms: Dict[str, AlgorithmFunc],
    weights: List[int],
    values: List[int],
    capacity: int,
    repeats: int = 1,
) -> List[AlgorithmResult]:
    """
    Запускает набор алгоритмов на одинаковых данных и возвращает список результатов.
    """
    results: List[AlgorithmResult] = []
    for name, func in algorithms.items():
        res = measure_algorithm(name, func, weights, values, capacity, repeats=repeats)
        results.append(res)
    return results


def benchmark_vs_items(
    algorithms: Dict[str, AlgorithmFunc],
    base_capacity: int,
    items_range: Sequence[int],
    random_seed: Optional[int] = None,
) -> Dict[str, Tuple[List[int], List[float]]]:
    """
    Строит зависимость времени работы алгоритмов от числа предметов.

    Возвращает словарь:
        имя_алгоритма -> (список n_items, список средних времен)
    """
    rng_seed = random_seed
    result: Dict[str, Tuple[List[int], List[float]]] = {
        name: ([], []) for name in algorithms
    }

    for n_items in items_range:
        items = generate_items(n_items, random_seed=rng_seed)
        weights, values = items_to_lists(items)
        for name, func in algorithms.items():
            res = measure_algorithm(name, func, weights, values, base_capacity)
            xs, ys = result[name]
            xs.append(n_items)
            ys.append(res.elapsed)

    return result


def benchmark_vs_capacity(
    algorithms: Dict[str, AlgorithmFunc],
    n_items: int,
    capacity_range: Sequence[int],
    random_seed: Optional[int] = None,
) -> Dict[str, Tuple[List[int], List[float]]]:
    """
    Строит зависимость времени работы алгоритмов от вместимости рюкзака.
    """
    items = generate_items(n_items, random_seed=random_seed)
    weights, values = items_to_lists(items)

    result: Dict[str, Tuple[List[int], List[float]]] = {
        name: ([], []) for name in algorithms
    }

    for cap in capacity_range:
        for name, func in algorithms.items():
            res = measure_algorithm(name, func, weights, values, cap)
            xs, ys = result[name]
            xs.append(cap)
            ys.append(res.elapsed)

    return result


__all__ = [
    "AlgorithmFunc",
    "AlgorithmResult",
    "measure_algorithm",
    "compare_algorithms",
    "benchmark_vs_items",
    "benchmark_vs_capacity",
]

