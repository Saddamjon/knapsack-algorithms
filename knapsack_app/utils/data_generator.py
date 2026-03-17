from dataclasses import dataclass
from typing import List, Tuple, Optional
import random
import csv


@dataclass
class Item:
    weight: int
    value: int


def generate_items(
    n_items: int,
    min_weight: int = 1,
    max_weight: int = 20,
    min_value: int = 1,
    max_value: int = 100,
    random_seed: Optional[int] = None,
) -> List[Item]:
    """
    Генерирует случайные предметы с целыми весами и ценностями.
    """
    if random_seed is not None:
        random.seed(random_seed)

    return [
        Item(
            weight=random.randint(min_weight, max_weight),
            value=random.randint(min_value, max_value),
        )
        for _ in range(max(0, n_items))
    ]


def items_to_lists(items: List[Item]) -> Tuple[List[int], List[int]]:
    """
    Преобразует список объектов Item в отдельные списки весов и ценностей.
    """
    weights = [it.weight for it in items]
    values = [it.value for it in items]
    return weights, values


def load_items_from_csv(path: str) -> List[Item]:
    """
    Загружает предметы из CSV-файла.

    Формат файла:
    - каждая строка описывает один предмет;
    - два столбца: вес, ценность (в таком порядке);
    - первая строка может быть заголовком (если в ней нечисловые значения).

    Пример:
        weight,value
        3,10
        5,20
        2,7
    """
    items: List[Item] = []

    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        for row_idx, row in enumerate(reader):
            if not row:
                continue

            # Обрезаем пробелы.
            cells = [cell.strip() for cell in row]
            if len(cells) < 2:
                # Недостаточно данных в строке — пропускаем.
                continue

            w_str, v_str = cells[0], cells[1]

            # Пропускаем строку‑заголовок, если значения не являются числами.
            if row_idx == 0:
                try:
                    int(w_str)
                    int(v_str)
                except ValueError:
                    # Похоже на заголовок, переходим к следующей строке.
                    continue

            try:
                weight = int(w_str)
                value = int(v_str)
            except ValueError:
                # Невалидная строка — пропускаем.
                continue

            if weight <= 0 or value < 0:
                # Логически неверные данные — пропускаем.
                continue

            items.append(Item(weight=weight, value=value))

    return items


__all__ = ["Item", "generate_items", "items_to_lists", "load_items_from_csv"]

