import random

import pytest

from algorithms.branch_and_bound import solve_knapsack_branch_and_bound
from algorithms.brute_force import MAX_ITEMS, solve_knapsack_bruteforce
from algorithms.dynamic_programming import MAX_TABLE_CELLS, solve_knapsack_dp
from algorithms.genetic import solve_knapsack_genetic
from algorithms.greedy import solve_knapsack_greedy
from utils.data_generator import generate_items, items_to_lists


def _random_instance(rng, max_items=10):
    n = rng.randint(0, max_items)
    weights = [rng.randint(1, 15) for _ in range(n)]
    values = [rng.randint(0, 50) for _ in range(n)]
    capacity = rng.randint(0, 40)
    return weights, values, capacity


def _check_solution(weights, values, capacity, value, items):
    """Решение допустимо: индексы уникальны, вес не больше вместимости, ценность сходится."""
    assert len(set(items)) == len(items)
    assert sum(weights[i] for i in items) <= capacity
    assert sum(values[i] for i in items) == value


@pytest.mark.parametrize("solver", [solve_knapsack_dp, solve_knapsack_branch_and_bound])
def test_exact_algorithms_match_bruteforce_on_random_instances(solver):
    rng = random.Random(2024)
    for _ in range(300):
        weights, values, capacity = _random_instance(rng)
        expected, _ = solve_knapsack_bruteforce(weights, values, capacity)

        value, items = solver(weights, values, capacity)

        assert value == expected, (weights, values, capacity)
        _check_solution(weights, values, capacity, value, items)


def test_greedy_is_feasible_and_never_better_than_optimum():
    rng = random.Random(7)
    for _ in range(200):
        weights, values, capacity = _random_instance(rng)
        optimum, _ = solve_knapsack_bruteforce(weights, values, capacity)

        value, items = solve_knapsack_greedy(weights, values, capacity)

        assert value <= optimum
        _check_solution(weights, values, capacity, value, items)


def test_zero_weight_items_do_not_crash():
    weights = [0, 3, 2]
    values = [5, 10, 7]
    optimum, _ = solve_knapsack_bruteforce(weights, values, 3)
    assert optimum == 15

    greedy_value, greedy_items = solve_knapsack_greedy(weights, values, 3)
    _check_solution(weights, values, 3, greedy_value, greedy_items)

    bb_value, bb_items = solve_knapsack_branch_and_bound(weights, values, 3)
    assert bb_value == optimum
    _check_solution(weights, values, 3, bb_value, bb_items)

    ga_value, ga_items = solve_knapsack_genetic(weights, values, 3, random_seed=1)
    assert greedy_value <= ga_value <= optimum
    _check_solution(weights, values, 3, ga_value, ga_items)


def test_bruteforce_refuses_too_many_items():
    n = MAX_ITEMS + 1
    with pytest.raises(ValueError):
        solve_knapsack_bruteforce([1] * n, [1] * n, 10)


def test_dp_refuses_huge_table():
    with pytest.raises(ValueError):
        solve_knapsack_dp([1, 2, 3], [1, 2, 3], MAX_TABLE_CELLS)


@pytest.mark.parametrize(
    "n_items, capacity", [(30, 50), (100, 50), (100, 300), (200, 100)]
)
def test_genetic_is_feasible_and_not_worse_than_greedy_on_large_inputs(n_items, capacity):
    # Раньше при случайных битах ГА возвращал 0 на таких входах:
    # почти все начальные особи были тяжелее вместимости.
    weights, values = items_to_lists(generate_items(n_items, random_seed=1))

    value, items = solve_knapsack_genetic(weights, values, capacity, random_seed=1)
    greedy_value, _ = solve_knapsack_greedy(weights, values, capacity)
    optimum, _ = solve_knapsack_dp(weights, values, capacity)

    _check_solution(weights, values, capacity, value, items)
    assert value > 0
    assert greedy_value <= value <= optimum


def test_genetic_does_not_touch_global_random_state():
    weights, values = [10, 20, 30], [60, 100, 120]

    random.seed(123)
    expected = [random.random() for _ in range(3)]

    random.seed(123)
    solve_knapsack_genetic(weights, values, 50, random_seed=42)
    actual = [random.random() for _ in range(3)]

    assert actual == expected


def test_generate_items_seed_does_not_touch_global_random_state():
    random.seed(5)
    expected = random.random()

    random.seed(5)
    generate_items(10, random_seed=99)

    assert random.random() == expected
