from algorithms.brute_force import MAX_ITEMS
from algorithms.dynamic_programming import solve_knapsack_dp
from algorithms.brute_force import solve_knapsack_bruteforce
from algorithms.greedy import solve_knapsack_greedy
from utils.data_generator import generate_items, items_to_lists
from utils.performance import (
    AlgorithmResult,
    benchmark_vs_capacity,
    benchmark_vs_items,
    compare_algorithms,
    default_capacity_range,
    default_items_range,
)
from utils.plots import (
    plot_algorithm_comparison,
    plot_time_vs_capacity,
    plot_time_vs_items,
)

ALGORITHMS = {
    "Brute Force": solve_knapsack_bruteforce,
    "Dynamic Programming": solve_knapsack_dp,
    "Greedy": solve_knapsack_greedy,
}


def test_compare_skips_bruteforce_on_large_input_instead_of_hanging():
    n = MAX_ITEMS + 10
    weights, values = items_to_lists(generate_items(n, random_seed=1))

    results = {r.name: r for r in compare_algorithms(ALGORITHMS, weights, values, 50)}

    assert results["Brute Force"].skipped
    assert str(MAX_ITEMS) in results["Brute Force"].skipped_reason
    assert not results["Dynamic Programming"].skipped
    assert results["Dynamic Programming"].max_value >= results["Greedy"].max_value


def test_benchmark_vs_items_drops_points_where_algorithm_refuses():
    items_range = [5, 10, MAX_ITEMS + 5]

    data = benchmark_vs_items(ALGORITHMS, base_capacity=30, items_range=items_range)

    assert data["Brute Force"][0] == [5, 10]
    assert data["Greedy"][0] == items_range


def test_benchmark_vs_capacity_returns_point_per_capacity():
    data = benchmark_vs_capacity(
        {"Greedy": solve_knapsack_greedy}, n_items=10, capacity_range=[10, 20, 30]
    )

    assert data["Greedy"][0] == [10, 20, 30]
    assert len(data["Greedy"][1]) == 3


def test_default_ranges_are_never_empty():
    for n in (1, 2, 3, 5, 10, 20, 100):
        items_range = default_items_range(n)
        assert len(items_range) >= 3
        assert items_range == sorted(set(items_range))
        assert min(items_range) >= 2

    for capacity in (1, 2, 10, 50, 1000):
        capacity_range = default_capacity_range(capacity)
        assert len(capacity_range) >= 3
        assert capacity_range == sorted(set(capacity_range))
        assert min(capacity_range) >= 1


def test_time_axes_are_logarithmic_and_tolerate_zero_times():
    zero_result = AlgorithmResult(
        name="Greedy", max_value=1, selected_items=[0], elapsed=0.0
    )
    slow_result = AlgorithmResult(
        name="Brute Force", max_value=1, selected_items=[0], elapsed=0.5
    )
    figures = [
        plot_algorithm_comparison([zero_result, slow_result]),
        plot_time_vs_items({"Greedy": ([1, 2], [0.0, 0.0])}),
        plot_time_vs_capacity({"Greedy": ([10, 20], [0.0, 1e-5])}),
    ]

    for fig in figures:
        ax = fig.axes[0]
        assert ax.get_yscale() == "log"
        assert "логарифм" in ax.get_ylabel()


def test_plots_build_figures_without_pyplot():
    weights, values = items_to_lists(generate_items(10, random_seed=1))
    results = compare_algorithms(ALGORITHMS, weights, values, 30)

    assert plot_algorithm_comparison(results) is not None
    assert plot_time_vs_items(
        benchmark_vs_items(ALGORITHMS, 30, default_items_range(5))
    ) is not None
    assert plot_time_vs_capacity(
        benchmark_vs_capacity(ALGORITHMS, 8, default_capacity_range(20))
    ) is not None
