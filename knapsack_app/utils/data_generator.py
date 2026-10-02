from dataclasses import dataclass
from typing import List, Tuple, Optional
import csv
import io
import random


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

    Используется собственный генератор, поэтому глобальное состояние random
    (и, например, генетический алгоритм) не затрагивается.
    """
    rng = random.Random(random_seed)

    return [
        Item(
            weight=rng.randint(min_weight, max_weight),
            value=rng.randint(min_value, max_value),
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


_DELIMITERS = (",", ";", "\t")
_ENCODINGS = ("utf-8-sig", "cp1251")


def _decode(raw: bytes) -> str:
    """
    Декодирует содержимое файла: UTF-8 (с BOM или без), затем Windows-1251.
    """
    for encoding in _ENCODINGS:
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="replace")


def _detect_delimiter(text: str) -> str:
    """
    Определяет разделитель по первой непустой строке: запятая, точка с запятой
    (так сохраняет Excel с русской локалью) или табуляция.
    """
    for line in text.splitlines():
        if line.strip():
            counts = {d: line.count(d) for d in _DELIMITERS}
            best = max(_DELIMITERS, key=lambda d: counts[d])
            return best if counts[best] > 0 else ","
    return ","


def load_items_from_csv(path: str) -> List[Item]:
    """
    Загружает предметы из CSV-файла.

    Формат файла:
    - каждая строка описывает один предмет;
    - два столбца: вес, ценность (в таком порядке);
    - разделитель: запятая, точка с запятой или табуляция;
    - кодировка: UTF-8 (в том числе с BOM) или Windows-1251;
    - первая строка может быть заголовком (если в ней нечисловые значения).

    Пример:
        weight,value
        3,10
        5,20
        2,7
    """
    items: List[Item] = []

    with open(path, "rb") as f:
        text = _decode(f.read())

    reader = csv.reader(io.StringIO(text), delimiter=_detect_delimiter(text))
    for row in reader:
        # Обрезаем пробелы.
        cells = [cell.strip() for cell in row]
        if not any(cells):
            continue

        if len(cells) < 2:
            # Недостаточно данных в строке — пропускаем.
            continue

        w_str, v_str = cells[0], cells[1]

        try:
            weight = int(w_str)
            value = int(v_str)
        except ValueError:
            # Нечисловые значения: заголовок (первая строка) или некорректная
            # строка — в любом случае пропускаем.
            continue

        if weight <= 0 or value < 0:
            # Логически неверные данные — пропускаем.
            continue

        items.append(Item(weight=weight, value=value))

    return items


__all__ = ["Item", "generate_items", "items_to_lists", "load_items_from_csv"]
