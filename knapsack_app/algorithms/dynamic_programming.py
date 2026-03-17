from typing import List, Tuple


def solve_knapsack_dp(
    weights: List[int], values: List[int], capacity: int
) -> Tuple[int, List[int]]:
    """
    Классическое динамическое программирование для 0/1‑задачи о рюкзаке.

    Использует таблицу размеров (n+1) × (capacity+1), где n — число предметов.
    """
    n = len(weights)
    if n == 0 or capacity <= 0:
        return 0, []

    # dp[i][w] — максимальная ценность, используя первые i предметов и вместимость рюкзака w.
    dp = [[0] * (capacity + 1) for _ in range(n + 1)]

    for i in range(1, n + 1):
        w_i = weights[i - 1]
        v_i = values[i - 1]
        for w in range(capacity + 1):
            if w_i <= w:
                dp[i][w] = max(dp[i - 1][w], dp[i - 1][w - w_i] + v_i)
            else:
                dp[i][w] = dp[i - 1][w]

    max_value = dp[n][capacity]
    w = capacity
    selected: List[int] = []
    for i in range(n, 0, -1):
        if dp[i][w] != dp[i - 1][w]:
            selected.append(i - 1)
            w -= weights[i - 1]

    selected.reverse()
    return max_value, selected


__all__ = ["solve_knapsack_dp"]

