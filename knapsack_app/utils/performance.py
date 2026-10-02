import time
from dataclasses import dataclass
from typing import Callable, Dict, List, Optional, Sequence, Tuple

from .data_generator import generate_items, items_to_lists


AlgorithmFunc = Callable[[List[int], List[int], int], Tuple[int, List[int]]]


@dataclass
class AlgorithmResult:
    name: str
    max_value: int
    selected_items: List[int]
    elapsed: float
    # Заполняется, если алгоритм отказался работать на этих данных
    # (например, полный перебор на большом числе предметов).
    skipped_reason: Optional[str] = None

    @property
    def skipped(self) -> bool:
        return self.skipped_reason is not None


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

    ValueError алгоритма (слишком большой вход) пробрасывается наружу.
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

    Алгоритм, отказавшийся работать на таком входе, попадает в список с
    заполненным skipped_reason.
    """
    results: List[AlgorithmResult] = []
    for name, func in algorithms.items():
        try:
            res = measure_algorithm(
                name, func, weights, values, capacity, repeats=repeats
            )
        except ValueError as exc:
            res = AlgorithmResult(
                name=name,
                max_value=0,
                selected_items=[],
                elapsed=0.0,
                skipped_reason=str(exc),
            )
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

    Точки, на которых алгоритм отказался работать (ValueError), пропускаются.
    """
    result: Dict[str, Tuple[List[int], List[float]]] = {
        name: ([], []) for name in algorithms
    }

    for n_items in items_range:
        items = generate_items(n_items, random_seed=random_seed)
        weights, values = items_to_lists(items)
        for name, func in algorithms.items():
            try:
                res = measure_algorithm(name, func, weights, values, base_capacity)
            except ValueError:
                continue
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

    Точки, на которых алгоритм отказался работать (ValueError), пропускаются.
    """
    items = generate_items(n_items, random_seed=random_seed)
    weights, values = items_to_lists(items)

    result: Dict[str, Tuple[List[int], List[float]]] = {
        name: ([], []) for name in algorithms
    }

    for cap in capacity_range:
        for name, func in algorithms.items():
            try:
                res = measure_algorithm(name, func, weights, values, cap)
            except ValueError:
                continue
            xs, ys = result[name]
            xs.append(cap)
            ys.append(res.elapsed)

    return result


def _spread(center: int, minimum: int) -> List[int]:
    """
    Диапазон от center/2 до 2*center примерно из семи точек (не меньше трёх).
    """
    start = max(minimum, center // 2)
    stop = max(start + 2, center * 2)
    step = max(1, (stop - start) // 6)
    values = list(range(start, stop + 1, step))
    if values[-1] != stop:
        values.append(stop)
    return values


def default_items_range(n_items: int) -> List[int]:
    """Диапазон чисел предметов для графика по умолчанию (всегда непустой)."""
    return _spread(n_items, minimum=2)


def default_capacity_range(capacity: int) -> List[int]:
    """Диапазон вместимостей для графика по умолчанию (всегда непустой)."""
    return _spread(capacity, minimum=1)


__all__ = [
    "AlgorithmFunc",
    "AlgorithmResult",
    "measure_algorithm",
    "compare_algorithms",
    "benchmark_vs_items",
    "benchmark_vs_capacity",
    "default_items_range",
    "default_capacity_range",
]
