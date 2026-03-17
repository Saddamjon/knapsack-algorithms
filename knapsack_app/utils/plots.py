from typing import Dict, List, Tuple

import matplotlib.pyplot as plt
import numpy as np

from .performance import AlgorithmResult


def plot_algorithm_comparison(results: List[AlgorithmResult]) -> None:
    """
    Столбиковая диаграмма сравнения времени выполнения алгоритмов.
    """
    names = [r.name for r in results]
    times = [r.elapsed for r in results]

    fig, ax = plt.subplots(figsize=(8, 5))
    x = np.arange(len(names))
    ax.bar(x, times, color="#4F8EF7")
    ax.set_xticks(x)
    ax.set_xticklabels(names, rotation=20)
    ax.set_ylabel("Время (сек)")
    ax.set_title("Сравнение времени работы алгоритмов")
    ax.grid(axis="y", linestyle="--", alpha=0.5)
    plt.tight_layout()
    plt.show()


def plot_time_vs_items(
    data: Dict[str, Tuple[List[int], List[float]]],
) -> None:
    """
    Линейный график зависимости времени работы от числа предметов.
    """
    fig, ax = plt.subplots(figsize=(8, 5))
    for name, (xs, ys) in data.items():
        ax.plot(xs, ys, marker="o", label=name)
    ax.set_xlabel("Количество предметов")
    ax.set_ylabel("Время (сек)")
    ax.set_title("Зависимость времени от количества предметов")
    ax.grid(True, linestyle="--", alpha=0.5)
    ax.legend()
    plt.tight_layout()
    plt.show()


def plot_time_vs_capacity(
    data: Dict[str, Tuple[List[int], List[float]]],
) -> None:
    """
    Линейный график зависимости времени работы от вместимости рюкзака.
    """
    fig, ax = plt.subplots(figsize=(8, 5))
    for name, (xs, ys) in data.items():
        ax.plot(xs, ys, marker="o", label=name)
    ax.set_xlabel("Вместимость рюкзака")
    ax.set_ylabel("Время (сек)")
    ax.set_title("Зависимость времени от вместимости рюкзака")
    ax.grid(True, linestyle="--", alpha=0.5)
    ax.legend()
    plt.tight_layout()
    plt.show()


__all__ = [
    "plot_algorithm_comparison",
    "plot_time_vs_items",
    "plot_time_vs_capacity",
]

