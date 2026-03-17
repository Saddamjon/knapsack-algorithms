import pytest

from algorithms.brute_force import solve_knapsack_bruteforce
from algorithms.branch_and_bound import solve_knapsack_branch_and_bound
from algorithms.dynamic_programming import solve_knapsack_dp
from algorithms.genetic import solve_knapsack_genetic
from algorithms.greedy import solve_knapsack_greedy


def test_greedy_empty_and_zero_capacity():
    assert solve_knapsack_greedy([], [], 10) == (0, [])

    weights = [1, 2]
    values = [10, 20]
    value, items = solve_knapsack_greedy(weights, values, 0)
    assert value == 0
    assert items == []


def test_greedy_simple_optimal_case():
    weights = [2, 3, 4, 5]
    values = [3, 4, 5, 8]
    capacity = 5

    value, items = solve_knapsack_greedy(weights, values, capacity)

    assert value == 8
    assert items == [3]


def test_greedy_suboptimal_compared_to_dp():
    # Пример, где жадный алгоритм даёт заведомо неоптимальное решение.
    weights = [10, 20, 30]
    values = [60, 100, 120]
    capacity = 50

    greedy_value, greedy_items = solve_knapsack_greedy(weights, values, capacity)
    dp_value, dp_items = solve_knapsack_dp(weights, values, capacity)

    assert dp_value == 220
    assert dp_items == [1, 2]

    assert greedy_value == 160
    assert greedy_items == [0, 1]


def test_dp_empty_and_zero_capacity():
    assert solve_knapsack_dp([], [], 10) == (0, [])

    weights = [1, 2, 3]
    values = [10, 20, 30]
    value, items = solve_knapsack_dp(weights, values, 0)
    assert value == 0
    assert items == []


def test_dp_matches_bruteforce_on_small_instance():
    weights = [2, 3, 4, 5]
    values = [3, 4, 5, 8]
    capacity = 5

    bf_value, bf_items = solve_knapsack_bruteforce(weights, values, capacity)
    dp_value, dp_items = solve_knapsack_dp(weights, values, capacity)

    assert dp_value == bf_value
    assert dp_items == bf_items


def test_bruteforce_basic_cases():
    assert solve_knapsack_bruteforce([], [], 10) == (0, [])

    weights = [1, 2]
    values = [10, 20]
    value, items = solve_knapsack_bruteforce(weights, values, 0)
    assert value == 0
    assert items == []

    weights = [10, 20, 30]
    values = [60, 100, 120]
    capacity = 50

    value, items = solve_knapsack_bruteforce(weights, values, capacity)
    assert value == 220
    assert items == [1, 2]


def test_branch_and_bound_empty_and_zero_capacity():
    assert solve_knapsack_branch_and_bound([], [], 10) == (0, [])

    weights = [1, 2]
    values = [10, 20]
    value, items = solve_knapsack_branch_and_bound(weights, values, 0)
    assert value == 0
    assert items == []


def test_branch_and_bound_matches_bruteforce_on_small_instance():
    weights = [2, 3, 4, 5]
    values = [3, 4, 5, 8]
    capacity = 5

    bf_value, bf_items = solve_knapsack_bruteforce(weights, values, capacity)
    bb_value, bb_items = solve_knapsack_branch_and_bound(weights, values, capacity)

    assert bb_value == bf_value
    # Сопоставляем именно индексы исходных предметов.
    assert sorted(bb_items) == sorted(bf_items)


def test_genetic_empty_and_zero_capacity():
    assert solve_knapsack_genetic([], [], 10) == (0, [])

    weights = [1, 2, 3]
    values = [10, 20, 30]
    value, items = solve_knapsack_genetic(
        weights, values, 0, population_size=10, generations=10, random_seed=123
    )
    assert value == 0
    assert items == []


def test_genetic_respects_capacity_and_is_deterministic_with_seed():
    weights = [10, 20, 30]
    values = [60, 100, 120]
    capacity = 50

    # Оптимальное значение для контроля качества решения ГА.
    optimal_value, optimal_items = solve_knapsack_bruteforce(
        weights, values, capacity
    )
    assert optimal_value == 220
    assert optimal_items == [1, 2]

    value1, items1 = solve_knapsack_genetic(
        weights,
        values,
        capacity,
        population_size=40,
        generations=120,
        crossover_rate=0.8,
        mutation_rate=0.02,
        random_seed=42,
    )

    # Проверяем, что решение не нарушает ограничение по весу
    total_weight1 = sum(weights[i] for i in items1)
    total_value1 = sum(values[i] for i in items1)
    assert total_weight1 <= capacity
    assert value1 == total_value1

    # С фиксированным seed алгоритм должен быть детерминированным.
    value2, items2 = solve_knapsack_genetic(
        weights,
        values,
        capacity,
        population_size=40,
        generations=120,
        crossover_rate=0.8,
        mutation_rate=0.02,
        random_seed=42,
    )
    assert value2 == value1
    assert items2 == items1

    # При разумных параметрах ГА должен давать хорошее, пусть и не обязательно оптимальное решение.
    assert value1 <= optimal_value
    assert value1 > 0

