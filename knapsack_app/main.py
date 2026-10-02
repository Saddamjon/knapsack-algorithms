import os
import sys

# Пакеты gui, algorithms и utils лежат рядом с этим файлом. Добавляем папку в
# sys.path, чтобы запуск работал и как `python knapsack_app/main.py`,
# и как `python -m knapsack_app.main` из корня репозитория.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gui.main_window import run_app  # noqa: E402


def main() -> None:
    run_app()


if __name__ == "__main__":
    main()
