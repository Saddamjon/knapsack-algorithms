from typing import Dict, List, Tuple

import numpy as np
from matplotlib.figure import Figure

from .performance import AlgorithmResult


def plot_algorithm_comparison(results: List[AlgorithmResult]) -> Figure:
    """
    Столбиковая диаграмма сравнения времени выполнения алгоритмов.

    Возвращает Figure (без pyplot), которую можно встроить в окно Tk или
    сохранить в файл. Пропущенные алгоритмы на диаграмму не попадают.
    """
    done = [r for r in results if not r.skipped]
    names = [r.name for r in done]
    times = [r.elapsed for r in done]

    fig = Figure(figsize=(8, 5), tight_layout=True)
    ax = fig.subplots()
    x = np.arange(len(names))
    ax.bar(x, times, color="#4F8EF7")
    ax.set_xticks(x)
    ax.set_xticklabels(names, rotation=20)
    ax.set_ylabel("Время (сек)")
    ax.set_title("Сравнение времени работы алгоритмов")
    ax.grid(axis="y", linestyle="--", alpha=0.5)
    return fig


def _line_plot(
    data: Dict[str, Tuple[List[int], List[float]]],
    xlabel: str,
    title: str,
) -> Figure:
    fig = Figure(figsize=(8, 5), tight_layout=True)
    ax = fig.subplots()
    for name, (xs, ys) in data.items():
        if xs:
            ax.plot(xs, ys, marker="o", label=name)
    ax.set_xlabel(xlabel)
    ax.set_ylabel("Время (сек)")
    ax.set_title(title)
    ax.grid(True, linestyle="--", alpha=0.5)
    if ax.get_legend_handles_labels()[0]:
        ax.legend()
    return fig


def plot_time_vs_items(
    data: Dict[str, Tuple[List[int], List[float]]],
) -> Figure:
    """
    Линейный график зависимости времени работы от числа предметов.
    """
    return _line_plot(
        data,
        xlabel="Количество предметов",
        title="Зависимость времени от количества предметов",
    )


def plot_time_vs_capacity(
    data: Dict[str, Tuple[List[int], List[float]]],
) -> Figure:
    """
    Линейный график зависимости времени работы от вместимости рюкзака.
    """
    return _line_plot(
        data,
        xlabel="Вместимость рюкзака",
        title="Зависимость времени от вместимости рюкзака",
    )


__all__ = [
    "plot_algorithm_comparison",
    "plot_time_vs_items",
    "plot_time_vs_capacity",
]
