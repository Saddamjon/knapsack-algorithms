def value_density(value: int, weight: int) -> float:
    """
    Ценность на единицу веса. Для предметов с нулевым весом возвращает +inf
    (если у них есть ценность), чтобы не было деления на ноль.
    """
    if weight <= 0:
        return float("inf") if value > 0 else 0.0
    return value / weight
