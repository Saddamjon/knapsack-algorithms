import time
import tkinter as tk

import pytest

pytest.importorskip("customtkinter")


@pytest.fixture(scope="module")
def _window():
    # Одно окно на весь модуль: повторное создание и уничтожение корневых окон Tk
    # в одном процессе иногда ломает поиск tk.tcl.
    from gui.main_window import MainWindow

    try:
        window = MainWindow()
    except tk.TclError as exc:
        pytest.skip(f"Нет графического окружения для Tk: {exc}")
    window.withdraw()
    yield window
    window.destroy()


def _close_toplevels(window) -> None:
    for child in window.winfo_children():
        if child.winfo_class() == "Toplevel":
            child.destroy()


@pytest.fixture
def app(_window):
    """Окно в чистом состоянии: без данных, результатов и дочерних окон."""
    _close_toplevels(_window)
    _window.current_data.items = None
    _window._update_items_table([])
    for entry in (
        _window.capacity_entry,
        _window.n_items_entry,
        _window.new_weight_entry,
        _window.new_value_entry,
    ):
        entry.delete(0, "end")
    yield _window
    _close_toplevels(_window)


def _wait_until_idle(window, timeout: float = 20.0) -> None:
    """Прокачивает цикл событий Tk, пока не закончатся фоновые вычисления."""
    deadline = time.time() + timeout
    while window._busy:
        window.update()
        assert time.time() < deadline, "Вычисление не завершилось вовремя"
        time.sleep(0.01)
    window.update()


def _type(entry, text: str) -> None:
    entry.delete(0, "end")
    entry.insert(0, text)


def test_generate_and_solve_with_every_algorithm(app):
    _type(app.capacity_entry, "50")
    _type(app.n_items_entry, "12")
    app.on_generate_data()
    assert len(app.current_data.items) == 12

    for name in (
        "Brute Force",
        "Dynamic Programming",
        "Branch and Bound",
        "Greedy",
        "Genetic",
    ):
        app.algorithm_combo.set(name)
        app.on_solve()
        _wait_until_idle(app)

        text = app.result_value_label.cget("text")
        assert text.startswith("Максимальная ценность: ")
        assert text.split(": ")[1].isdigit()


def test_add_and_remove_items(app):
    _type(app.new_weight_entry, "3")
    _type(app.new_value_entry, "10")
    app.on_add_item()
    _type(app.new_weight_entry, "5")
    _type(app.new_value_entry, "20")
    app.on_add_item()

    assert [(i.weight, i.value) for i in app.current_data.items] == [(3, 10), (5, 20)]
    assert len(app.items_tree.get_children()) == 2

    app.items_tree.selection_set(app.items_tree.get_children()[0])
    app.on_remove_selected_item()

    assert [(i.weight, i.value) for i in app.current_data.items] == [(5, 20)]


def test_compare_with_many_items_does_not_hang(app):
    # 40 предметов: раньше полный перебор делал 2^40 шагов и окно зависало.
    _type(app.capacity_entry, "100")
    _type(app.n_items_entry, "40")
    app.on_generate_data()

    app.on_compare()
    _wait_until_idle(app)

    windows = [w for w in app.winfo_children() if w.winfo_class() == "Toplevel"]
    assert windows, "Окно сравнения не открылось"


def test_plot_performance_with_small_inputs_opens_window(app):
    _type(app.capacity_entry, "1")
    _type(app.n_items_entry, "1")

    app.on_plot_performance()
    _wait_until_idle(app)

    windows = [w for w in app.winfo_children() if w.winfo_class() == "Toplevel"]
    assert windows
