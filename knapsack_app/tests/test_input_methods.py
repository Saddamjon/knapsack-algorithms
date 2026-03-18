import pytest
import tempfile
import os
from pathlib import Path

from utils.data_generator import Item, load_items_from_csv


class TestLoadItemsFromCSV:
    """Тесты для загрузки предметов из CSV-файла."""

    def test_load_csv_valid_items(self):
        """Тест загрузки корректного CSV-файла с несколькими предметами."""
        csv_content = """weight,value
3,10
5,20
2,7
4,15"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(csv_content)
            f.flush()
            path = f.name

        try:
            items = load_items_from_csv(path)
            assert len(items) == 4
            assert items[0] == Item(weight=3, value=10)
            assert items[1] == Item(weight=5, value=20)
            assert items[2] == Item(weight=2, value=7)
            assert items[3] == Item(weight=4, value=15)
        finally:
            os.unlink(path)

    def test_load_csv_without_header(self):
        """Тест загрузки CSV без заголовка."""
        csv_content = """3,10
5,20
2,7"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(csv_content)
            f.flush()
            path = f.name

        try:
            items = load_items_from_csv(path)
            assert len(items) == 3
            assert items[0] == Item(weight=3, value=10)
            assert items[1] == Item(weight=5, value=20)
            assert items[2] == Item(weight=2, value=7)
        finally:
            os.unlink(path)

    def test_load_csv_with_spaces(self):
        """Тест загрузки CSV с пробелами вокруг значений."""
        csv_content = """weight, value
 3 , 10 
 5 , 20 
  2  ,  7  """
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(csv_content)
            f.flush()
            path = f.name

        try:
            items = load_items_from_csv(path)
            assert len(items) == 3
            assert items[0] == Item(weight=3, value=10)
            assert items[1] == Item(weight=5, value=20)
            assert items[2] == Item(weight=2, value=7)
        finally:
            os.unlink(path)

    def test_load_csv_empty_file(self):
        """Тест загрузки пустого CSV-файла."""
        csv_content = ""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(csv_content)
            f.flush()
            path = f.name

        try:
            items = load_items_from_csv(path)
            assert len(items) == 0
            assert items == []
        finally:
            os.unlink(path)

    def test_load_csv_only_header(self):
        """Тест загрузки CSV только с заголовком."""
        csv_content = """weight,value"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(csv_content)
            f.flush()
            path = f.name

        try:
            items = load_items_from_csv(path)
            assert len(items) == 0
        finally:
            os.unlink(path)

    def test_load_csv_with_empty_rows(self):
        """Тест загрузки CSV с пустыми строками."""
        csv_content = """weight,value
3,10

5,20

2,7"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(csv_content)
            f.flush()
            path = f.name

        try:
            items = load_items_from_csv(path)
            assert len(items) == 3
            assert items[0] == Item(weight=3, value=10)
            assert items[1] == Item(weight=5, value=20)
            assert items[2] == Item(weight=2, value=7)
        finally:
            os.unlink(path)

    def test_load_csv_ignores_invalid_rows(self):
        """Тест пропуска некорректных строк в CSV."""
        csv_content = """weight,value
3,10
invalid,data
5,20
abc,xyz
2,7"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(csv_content)
            f.flush()
            path = f.name

        try:
            items = load_items_from_csv(path)
            # Должны загрузиться только корректные значения
            assert len(items) == 3
            assert items[0] == Item(weight=3, value=10)
            assert items[1] == Item(weight=5, value=20)
            assert items[2] == Item(weight=2, value=7)
        finally:
            os.unlink(path)

    def test_load_csv_ignores_invalid_weights(self):
        """Тест пропуска строк с нулевым или отрицательным весом."""
        csv_content = """weight,value
3,10
0,20
-5,30
5,20"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(csv_content)
            f.flush()
            path = f.name

        try:
            items = load_items_from_csv(path)
            # Пропускаются строки с weight <= 0
            assert len(items) == 2
            assert items[0] == Item(weight=3, value=10)
            assert items[1] == Item(weight=5, value=20)
        finally:
            os.unlink(path)

    def test_load_csv_ignores_negative_values(self):
        """Тест пропуска строк с отрицательной ценностью."""
        csv_content = """weight,value
3,10
5,-20
2,7"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(csv_content)
            f.flush()
            path = f.name

        try:
            items = load_items_from_csv(path)
            # Пропускаются строки с value < 0
            assert len(items) == 2
            assert items[0] == Item(weight=3, value=10)
            assert items[1] == Item(weight=2, value=7)
        finally:
            os.unlink(path)

    def test_load_csv_allows_zero_value(self):
        """Тест что значение 0 допустимо для ценности."""
        csv_content = """weight,value
3,0
5,20
2,0"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(csv_content)
            f.flush()
            path = f.name

        try:
            items = load_items_from_csv(path)
            assert len(items) == 3
            assert items[0] == Item(weight=3, value=0)
            assert items[1] == Item(weight=5, value=20)
            assert items[2] == Item(weight=2, value=0)
        finally:
            os.unlink(path)

    def test_load_csv_file_not_found(self):
        """Тест ошибки при загрузке несуществующего файла."""
        with pytest.raises(OSError):
            load_items_from_csv("/nonexistent/path/file.csv")

    def test_load_csv_insufficient_columns(self):
        """Тест игнорирования строк с недостаточным числом столбцов."""
        csv_content = """weight
3
5
2,7"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(csv_content)
            f.flush()
            path = f.name

        try:
            items = load_items_from_csv(path)
            # Загружается только последняя строка с двумя столбцами
            assert len(items) == 1
            assert items[0] == Item(weight=2, value=7)
        finally:
            os.unlink(path)

    def test_load_csv_large_numbers(self):
        """Тест загрузки CSV с большими числами."""
        csv_content = """weight,value
1000000,5000000
999999,4999999
10000,50000"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(csv_content)
            f.flush()
            path = f.name

        try:
            items = load_items_from_csv(path)
            assert len(items) == 3
            assert items[0] == Item(weight=1000000, value=5000000)
            assert items[1] == Item(weight=999999, value=4999999)
            assert items[2] == Item(weight=10000, value=50000)
        finally:
            os.unlink(path)


class TestItemAdditionLogic:
    """Тесты логики добавления предметов вручную."""

    def test_create_valid_item(self):
        """Тест создания корректного предмета."""
        item = Item(weight=5, value=20)
        assert item.weight == 5
        assert item.value == 20

    def test_item_validation_positive_weight(self):
        """Тест что вес должен быть положительным."""
        # Корректный предмет
        item = Item(weight=1, value=0)
        assert item.weight > 0

    def test_item_validation_non_negative_value(self):
        """Тест что ценность может быть неотрицательной."""
        item = Item(weight=5, value=0)
        assert item.value >= 0

    def test_item_with_zero_value_is_valid(self):
        """Тест что предмет с нулевой ценностью допустим."""
        item = Item(weight=5, value=0)
        assert item.weight == 5
        assert item.value == 0

    def test_multiple_items_addition_simulation(self):
        """Тест добавления нескольких предметов в список."""
        items = []
        
        # Добавляем первый предмет
        items.append(Item(weight=3, value=10))
        assert len(items) == 1
        
        # Добавляем второй предмет
        items.append(Item(weight=5, value=20))
        assert len(items) == 2
        
        # Добавляем третий предмет
        items.append(Item(weight=2, value=7))
        assert len(items) == 3
        
        # Проверяем содержимое
        assert items[0] == Item(weight=3, value=10)
        assert items[1] == Item(weight=5, value=20)
        assert items[2] == Item(weight=2, value=7)

    def test_item_removal_from_list(self):
        """Тест удаления предмета из списка."""
        items = [
            Item(weight=3, value=10),
            Item(weight=5, value=20),
            Item(weight=2, value=7),
        ]
        
        assert len(items) == 3
        
        # Удаляем предмет с индексом 1
        del items[1]
        
        assert len(items) == 2
        assert items[0] == Item(weight=3, value=10)
        assert items[1] == Item(weight=2, value=7)

    def test_clear_items_list(self):
        """Тест очистки списка предметов."""
        items = [
            Item(weight=3, value=10),
            Item(weight=5, value=20),
            Item(weight=2, value=7),
        ]
        
        assert len(items) == 3
        items.clear()
        assert len(items) == 0

    def test_item_dataclass_equality(self):
        """Тест равенства объектов Item."""
        item1 = Item(weight=5, value=20)
        item2 = Item(weight=5, value=20)
        item3 = Item(weight=5, value=19)
        
        assert item1 == item2
        assert item1 != item3

    def test_duplicate_item_addition(self):
        """Тест добавления одинаковых предметов."""
        items = []
        item1 = Item(weight=5, value=20)
        item2 = Item(weight=5, value=20)
        
        items.append(item1)
        items.append(item2)
        
        assert len(items) == 2
        assert items[0] == items[1]
