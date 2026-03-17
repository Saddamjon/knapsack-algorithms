from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple, Callable

import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

from algorithms.brute_force import solve_knapsack_bruteforce
from algorithms.dynamic_programming import solve_knapsack_dp
from algorithms.branch_and_bound import solve_knapsack_branch_and_bound
from algorithms.greedy import solve_knapsack_greedy
from algorithms.genetic import solve_knapsack_genetic
from utils.data_generator import Item, generate_items, items_to_lists, load_items_from_csv
from utils.performance import (
    AlgorithmFunc,
    AlgorithmResult,
    benchmark_vs_capacity,
    benchmark_vs_items,
    compare_algorithms,
)
from utils.plots import (
    plot_algorithm_comparison,
    plot_time_vs_capacity,
    plot_time_vs_items,
)


ALGORITHMS: Dict[str, AlgorithmFunc] = {
    "Brute Force": solve_knapsack_bruteforce,
    "Dynamic Programming": solve_knapsack_dp,
    "Branch and Bound": solve_knapsack_branch_and_bound,
    "Greedy": solve_knapsack_greedy,
    "Genetic": solve_knapsack_genetic,
}


@dataclass
class CurrentData:
    capacity: int = 0
    items: List[Item] | None = None


class MainWindow(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Решение задачи о рюкзаке")
        self.geometry("1000x600")
        self.minsize(900, 520)

        ctk.set_appearance_mode("system")
        ctk.set_default_color_theme("blue")

        self.current_data = CurrentData()

        self._build_layout()
        self._build_menu()

    # Разметка основного окна.

    def _build_layout(self) -> None:
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=2)
        self.grid_rowconfigure(0, weight=1)

        left_frame = ctk.CTkFrame(self)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        left_frame.grid_columnconfigure(0, weight=1)

        title_label = ctk.CTkLabel(
            left_frame,
            text="Параметры задачи о рюкзаке",
            font=ctk.CTkFont(size=16, weight="bold"),
        )
        title_label.grid(row=0, column=0, pady=(10, 20))

        cap_label = ctk.CTkLabel(left_frame, text="Вместимость рюкзака:")
        cap_label.grid(row=1, column=0, sticky="w", padx=10)
        self.capacity_entry = ctk.CTkEntry(left_frame, placeholder_text="например, 50")
        self.capacity_entry.grid(row=2, column=0, sticky="ew", padx=10, pady=(0, 10))

        n_label = ctk.CTkLabel(left_frame, text="Количество предметов:")
        n_label.grid(row=3, column=0, sticky="w", padx=10)
        self.n_items_entry = ctk.CTkEntry(left_frame, placeholder_text="например, 10")
        self.n_items_entry.grid(row=4, column=0, sticky="ew", padx=10, pady=(0, 10))

        self.generate_button = ctk.CTkButton(
            left_frame,
            text="Сгенерировать данные",
            command=self.on_generate_data,
        )
        self.generate_button.grid(row=5, column=0, sticky="ew", padx=10, pady=(5, 5))

        self.load_csv_button = ctk.CTkButton(
            left_frame,
            text="Загрузить CSV",
            command=self.on_load_csv,
        )
        self.load_csv_button.grid(row=6, column=0, sticky="ew", padx=10, pady=(0, 15))

        algo_label = ctk.CTkLabel(left_frame, text="Алгоритм:")
        algo_label.grid(row=7, column=0, sticky="w", padx=10)

        self.algorithm_combo = ctk.CTkComboBox(
            left_frame,
            values=list(ALGORITHMS.keys()),
            state="readonly",
        )
        self.algorithm_combo.set("Dynamic Programming")
        self.algorithm_combo.grid(row=8, column=0, sticky="ew", padx=10, pady=(0, 20))

        self.solve_button = ctk.CTkButton(
            left_frame,
            text="Решить задачу",
            command=self.on_solve,
        )
        self.solve_button.grid(row=9, column=0, sticky="ew", padx=10, pady=(0, 10))

        self.compare_button = ctk.CTkButton(
            left_frame,
            text="Сравнить алгоритмы",
            command=self.on_compare,
        )
        self.compare_button.grid(row=10, column=0, sticky="ew", padx=10, pady=(0, 10))

        self.plot_button = ctk.CTkButton(
            left_frame,
            text="Построить графики",
            command=self.on_plot_performance,
        )
        self.plot_button.grid(row=11, column=0, sticky="ew", padx=10, pady=(0, 10))

        right_frame = ctk.CTkFrame(self)
        right_frame.grid(row=0, column=1, sticky="nsew", padx=(0, 10), pady=10)
        right_frame.grid_columnconfigure(0, weight=1)
        right_frame.grid_rowconfigure(0, weight=3)
        right_frame.grid_rowconfigure(1, weight=0)
        right_frame.grid_rowconfigure(2, weight=1)

        table_frame = ctk.CTkFrame(right_frame)
        table_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

        columns = ("index", "weight", "value")
        self.items_tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            height=10,
        )
        self.items_tree.heading("index", text="#")
        self.items_tree.heading("weight", text="Вес")
        self.items_tree.heading("value", text="Ценность")
        self.items_tree.column("index", width=50, anchor="center")
        self.items_tree.column("weight", width=80, anchor="center")
        self.items_tree.column("value", width=100, anchor="center")
        self.items_tree.grid(row=0, column=0, sticky="nsew")

        scrollbar = ttk.Scrollbar(
            table_frame,
            orient="vertical",
            command=self.items_tree.yview,
        )
        self.items_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=0, column=1, sticky="ns")

        edit_frame = ctk.CTkFrame(right_frame)
        edit_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 5))
        edit_frame.grid_columnconfigure(0, weight=0)
        edit_frame.grid_columnconfigure(1, weight=0)
        edit_frame.grid_columnconfigure(2, weight=0)
        edit_frame.grid_columnconfigure(3, weight=1)

        new_item_label = ctk.CTkLabel(edit_frame, text="Новый предмет:")
        new_item_label.grid(row=0, column=0, padx=(5, 5), pady=5, sticky="w")

        self.new_weight_entry = ctk.CTkEntry(edit_frame, width=80, placeholder_text="вес")
        self.new_weight_entry.grid(row=0, column=1, padx=(5, 5), pady=5)

        self.new_value_entry = ctk.CTkEntry(edit_frame, width=80, placeholder_text="ценность")
        self.new_value_entry.grid(row=0, column=2, padx=(5, 5), pady=5)

        self.add_item_button = ctk.CTkButton(
            edit_frame,
            text="Добавить",
            width=80,
            command=self.on_add_item,
        )
        self.add_item_button.grid(row=0, column=3, padx=(5, 5), pady=5, sticky="w")

        self.remove_item_button = ctk.CTkButton(
            edit_frame,
            text="Удалить выбранный",
            width=140,
            command=self.on_remove_selected_item,
        )
        self.remove_item_button.grid(row=0, column=4, padx=(5, 5), pady=5, sticky="w")

        self.clear_items_button = ctk.CTkButton(
            edit_frame,
            text="Очистить список",
            width=130,
            command=self.on_clear_items,
        )
        self.clear_items_button.grid(row=0, column=5, padx=(5, 5), pady=5, sticky="w")

        results_frame = ctk.CTkFrame(right_frame)
        results_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=(0, 10))
        results_frame.grid_columnconfigure(1, weight=1)

        self.result_value_label = ctk.CTkLabel(
            results_frame,
            text="Максимальная ценность: -",
            anchor="w",
        )
        self.result_value_label.grid(
            row=0, column=0, columnspan=2, sticky="w", padx=10, pady=(10, 5)
        )

        self.result_time_label = ctk.CTkLabel(
            results_frame,
            text="Время выполнения: -",
            anchor="w",
        )
        self.result_time_label.grid(
            row=1, column=0, columnspan=2, sticky="w", padx=10, pady=(0, 5)
        )

        selected_label = ctk.CTkLabel(
            results_frame,
            text="Выбранные предметы (индексы):",
            anchor="w",
        )
        selected_label.grid(row=2, column=0, sticky="nw", padx=10, pady=(5, 5))

        self.selected_items_text = ctk.CTkTextbox(results_frame, height=80)
        self.selected_items_text.grid(
            row=2, column=1, sticky="nsew", padx=10, pady=(5, 10)
        )
        self.selected_items_text.configure(state="disabled")

    def _build_menu(self) -> None:
        menu_bar = tk.Menu(self)

        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Загрузить CSV...", command=self.on_load_csv)
        menu_bar.add_cascade(label="Файл", menu=file_menu)

        help_menu = tk.Menu(menu_bar, tearoff=0)
        help_menu.add_command(
            label="Формат CSV файла...", command=self.show_csv_help
        )
        menu_bar.add_cascade(label="Справка", menu=help_menu)

        self.configure(menu=menu_bar)

    # Вспомогательные методы.

    def _read_capacity(self) -> int | None:
        try:
            cap = int(self.capacity_entry.get())
            if cap <= 0:
                raise ValueError
            return cap
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректную вместимость (> 0).")
            return None

    def _read_n_items(self) -> int | None:
        try:
            n = int(self.n_items_entry.get())
            if n <= 0:
                raise ValueError
            return n
        except ValueError:
            messagebox.showerror(
                "Ошибка", "Введите корректное количество предметов (> 0)."
            )
            return None

    def _update_items_table(self, items: List[Item]) -> None:
        for row in self.items_tree.get_children():
            self.items_tree.delete(row)

        for idx, item in enumerate(items):
            self.items_tree.insert(
                "", "end", values=(idx, item.weight, item.value)
            )

    def _set_n_items(self, n: int) -> None:
        self.n_items_entry.delete(0, "end")
        self.n_items_entry.insert(0, str(n))

    def _ensure_items_list(self) -> None:
        if self.current_data.items is None:
            self.current_data.items = []

    def _refresh_items_from_current(self) -> None:
        if self.current_data.items is None:
            self._update_items_table([])
            self._set_n_items(0)
        else:
            self._update_items_table(self.current_data.items)
            self._set_n_items(len(self.current_data.items))

    def _show_result(
        self,
        result: AlgorithmResult,
    ) -> None:
        self.result_value_label.configure(
            text=f"Максимальная ценность: {result.max_value}"
        )
        self.result_time_label.configure(
            text=f"Время выполнения: {result.elapsed:.6f} сек"
        )
        self.selected_items_text.configure(state="normal")
        self.selected_items_text.delete("1.0", "end")
        if result.selected_items:
            self.selected_items_text.insert(
                "end", ", ".join(str(i) for i in result.selected_items)
            )
        else:
            self.selected_items_text.insert("end", "нет выбранных предметов")
        self.selected_items_text.configure(state="disabled")

    # Обработчики событий.

    def on_generate_data(self) -> None:
        capacity = self._read_capacity()
        if capacity is None:
            return
        n_items = self._read_n_items()
        if n_items is None:
            return

        items = generate_items(n_items)
        self.current_data.capacity = capacity
        self.current_data.items = items
        self._update_items_table(items)

    def on_add_item(self) -> None:
        """
        Добавляет новый предмет из полей ввода справа.
        """
        w_text = self.new_weight_entry.get().strip()
        v_text = self.new_value_entry.get().strip()

        if not w_text or not v_text:
            messagebox.showerror("Ошибка", "Укажите вес и ценность предмета.")
            return

        try:
            weight = int(w_text)
            value = int(v_text)
        except ValueError:
            messagebox.showerror(
                "Ошибка", "Вес и ценность должны быть целыми числами."
            )
            return

        if weight <= 0 or value < 0:
            messagebox.showerror(
                "Ошибка",
                "Вес должен быть > 0, ценность должна быть ≥ 0.",
            )
            return

        self._ensure_items_list()
        self.current_data.items.append(Item(weight=weight, value=value))
        self._refresh_items_from_current()

        # Очищаем поля ввода для удобства.
        self.new_weight_entry.delete(0, "end")
        self.new_value_entry.delete(0, "end")

    def on_remove_selected_item(self) -> None:
        """
        Удаляет выбранный в таблице предмет.
        """
        if self.current_data.items is None:
            return

        selection = self.items_tree.selection()
        if not selection:
            messagebox.showwarning(
                "Нет выбора", "Выберите строку в таблице, которую нужно удалить."
            )
            return

        # Предполагаем, что каждая строка отображает индекс предмета.
        item_id = selection[0]
        values = self.items_tree.item(item_id, "values")
        if not values:
            return

        try:
            index = int(values[0])
        except (ValueError, IndexError):
            return

        if 0 <= index < len(self.current_data.items):
            del self.current_data.items[index]
            self._refresh_items_from_current()

    def on_clear_items(self) -> None:
        """
        Полностью очищает список предметов.
        """
        if self.current_data.items is None or not self.current_data.items:
            return

        if not messagebox.askyesno(
            "Подтверждение", "Вы уверены, что хотите очистить все предметы?"
        ):
            return

        self.current_data.items = []
        self._refresh_items_from_current()

    def on_load_csv(self) -> None:
        """
        Обработчик загрузки данных из CSV-файла.
        """
        path = filedialog.askopenfilename(
            title="Выберите CSV-файл с предметами",
            filetypes=(("CSV файлы", "*.csv"), ("Все файлы", "*.*")),
        )
        if not path:
            return

        try:
            items = load_items_from_csv(path)
        except OSError as exc:
            messagebox.showerror(
                "Ошибка чтения файла",
                f"Не удалось открыть файл:\n{exc}",
            )
            return

        if not items:
            messagebox.showerror(
                "Пустые данные",
                "В выбранном файле не удалось найти ни одной корректной строки.\n"
                "Проверьте формат CSV (см. меню «Справка → Формат CSV файла...»).",
            )
            return

        self.current_data.items = items
        self._update_items_table(items)
        self._set_n_items(len(items))

        messagebox.showinfo(
            "Данные загружены",
            f"Успешно загружено {len(items)} предметов из файла.\n"
            "Теперь задайте вместимость рюкзака и выберите алгоритм.",
        )

    def show_csv_help(self) -> None:
        """
        Показывает инструкцию по формату CSV файла.
        """
        messagebox.showinfo(
            "Формат CSV файла",
            "Файл должен быть в формате CSV (разделитель — запятая).\n\n"
            "Каждая строка описывает один предмет и содержит ДВА столбца:\n"
            "  1) вес (целое число > 0)\n"
            "  2) ценность (целое число ≥ 0)\n\n"
            "Первая строка может быть заголовком, например:\n"
            "  weight,value\n"
            "  3,10\n"
            "  5,20\n"
            "  2,7\n\n"
            "Пустые строки и строки с некорректными значениями будут пропущены.",
        )

    def on_solve(self) -> None:
        if self.current_data.items is None:
            messagebox.showwarning(
                "Нет данных",
                "Сначала сгенерируйте данные (кнопка «Сгенерировать данные»).",
            )
            return

        capacity = self._read_capacity()
        if capacity is None:
            return
        self.current_data.capacity = capacity

        algo_name = self.algorithm_combo.get()
        func = ALGORITHMS.get(algo_name)
        if func is None:
            messagebox.showerror("Ошибка", "Выберите корректный алгоритм.")
            return

        weights, values = items_to_lists(self.current_data.items)
        from utils.performance import measure_algorithm

        result = measure_algorithm(algo_name, func, weights, values, capacity)
        self._show_result(result)

    def on_compare(self) -> None:
        if self.current_data.items is None:
            messagebox.showwarning(
                "Нет данных",
                "Сначала сгенерируйте данные (кнопка «Сгенерировать данные»).",
            )
            return

        capacity = self._read_capacity()
        if capacity is None:
            return
        self.current_data.capacity = capacity

        weights, values = items_to_lists(self.current_data.items)
        results = compare_algorithms(ALGORITHMS, weights, values, capacity)

        # Таблица результатов в отдельном окне.
        top = ctk.CTkToplevel(self)
        top.title("Сравнение алгоритмов")
        top.geometry("600x300")

        tree = ttk.Treeview(
            top,
            columns=("name", "value", "time"),
            show="headings",
        )
        tree.heading("name", text="Алгоритм")
        tree.heading("value", text="Макс. ценность")
        tree.heading("time", text="Время (сек)")
        tree.column("name", width=200, anchor="w")
        tree.column("value", width=120, anchor="center")
        tree.column("time", width=120, anchor="center")
        tree.pack(fill="both", expand=True, padx=10, pady=10)

        for r in results:
            tree.insert(
                "",
                "end",
                values=(r.name, r.max_value, f"{r.elapsed:.6f}"),
            )

        # График сравнения времени.
        plot_algorithm_comparison(results)

    def on_plot_performance(self) -> None:
        if self.current_data.items is None:
            messagebox.showwarning(
                "Нет данных",
                "Сначала сгенерируйте данные (кнопка «Сгенерировать данные»).",
            )
            return

        capacity = self._read_capacity()
        n_items = self._read_n_items()
        if capacity is None or n_items is None:
            return

        # Диапазоны по умолчанию ориентированы на учебные эксперименты.
        items_range = list(range(max(5, n_items // 2), n_items * 2 + 1, max(1, n_items // 4)))
        capacity_range = list(
            range(max(10, capacity // 2), capacity * 2 + 1, max(1, capacity // 4))
        )

        data_items = benchmark_vs_items(ALGORITHMS, base_capacity=capacity, items_range=items_range)
        plot_time_vs_items(data_items)

        data_capacity = benchmark_vs_capacity(
            ALGORITHMS,
            n_items=n_items,
            capacity_range=capacity_range,
        )
        plot_time_vs_capacity(data_capacity)


def run_app() -> None:
    app = MainWindow()
    app.mainloop()


__all__ = ["MainWindow", "run_app"]

