import pytest

from utils.data_generator import Item, load_items_from_csv


def _load(tmp_path, content: str, encoding: str = "utf-8"):
    path = tmp_path / "items.csv"
    path.write_bytes(content.encode(encoding))
    return load_items_from_csv(str(path))


EXPECTED = [Item(3, 10), Item(5, 20), Item(2, 7)]


def test_utf8_bom_without_header_keeps_first_row(tmp_path):
    # Excel («CSV UTF-8») добавляет BOM; раньше из-за него терялась первая строка.
    assert _load(tmp_path, "3,10\n5,20\n2,7\n", "utf-8-sig") == EXPECTED


def test_utf8_bom_with_header(tmp_path):
    assert _load(tmp_path, "weight,value\n3,10\n5,20\n2,7\n", "utf-8-sig") == EXPECTED


def test_semicolon_delimiter(tmp_path):
    # Excel с русской локалью сохраняет CSV с точкой с запятой.
    assert _load(tmp_path, "weight;value\n3;10\n5;20\n2;7\n") == EXPECTED


def test_tab_delimiter(tmp_path):
    assert _load(tmp_path, "weight\tvalue\n3\t10\n5\t20\n2\t7\n") == EXPECTED


def test_windows_1251_header(tmp_path):
    content = "вес;ценность\n3;10\n5;20\n2;7\n"
    assert _load(tmp_path, content, "cp1251") == EXPECTED


def test_crlf_line_endings_and_blank_lines(tmp_path):
    assert _load(tmp_path, "weight,value\r\n\r\n3,10\r\n5,20\r\n\r\n2,7\r\n") == EXPECTED


def test_invalid_rows_are_skipped(tmp_path):
    content = "3,10\nabc,5\n0,5\n4,-1\n5\n5,20\n"
    assert _load(tmp_path, content) == [Item(3, 10), Item(5, 20)]


def test_missing_file_raises_oserror(tmp_path):
    with pytest.raises(OSError):
        load_items_from_csv(str(tmp_path / "nope.csv"))
