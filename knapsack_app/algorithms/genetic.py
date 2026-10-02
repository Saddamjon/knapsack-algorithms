import random
from typing import List, Optional, Tuple

from ._common import value_density


def _fitness(
    chromosome: List[int],
    weights: List[int],
    values: List[int],
    capacity: int,
) -> int:
    """
    Функция приспособленности: суммарная ценность, если вес не превышает вместимость;
    при превышении возвращает 0.
    """
    total_weight = 0
    total_value = 0
    for bit, w, v in zip(chromosome, weights, values):
        if bit:
            total_weight += w
            if total_weight > capacity:
                return 0
            total_value += v
    return total_value


def _random_feasible(
    n: int, weights: List[int], capacity: int, rng: random.Random
) -> List[int]:
    """
    Допустимая случайная хромосома: предметы добавляются в случайном порядке,
    пока помещаются в рюкзак.

    Равномерно случайные биты почти всегда дают перегруженный рюкзак (вес больше
    вместимости), и тогда у всей популяции приспособленность равна 0 и отбор
    не работает.
    """
    chromosome = [0] * n
    total_weight = 0
    order = list(range(n))
    rng.shuffle(order)
    for i in order:
        if total_weight + weights[i] <= capacity:
            chromosome[i] = 1
            total_weight += weights[i]
    return chromosome


def _repair(
    chromosome: List[int],
    weights: List[int],
    capacity: int,
    worst_first: List[int],
) -> None:
    """
    Чинит хромосому после скрещивания и мутации: пока вес больше вместимости,
    убирает предметы с наименьшей ценностью на единицу веса.
    """
    total_weight = sum(w for bit, w in zip(chromosome, weights) if bit)
    if total_weight <= capacity:
        return
    for i in worst_first:
        if chromosome[i]:
            chromosome[i] = 0
            total_weight -= weights[i]
            if total_weight <= capacity:
                return


def _select_population(
    population: List[List[int]],
    fitnesses: List[int],
    selection_size: int,
    rng: random.Random,
) -> List[List[int]]:
    """
    Турнирная селекция в популяции.
    """
    selected: List[List[int]] = []
    n = len(population)
    for _ in range(selection_size):
        i, j = rng.randrange(n), rng.randrange(n)
        if fitnesses[i] > fitnesses[j]:
            selected.append(population[i])
        else:
            selected.append(population[j])
    return selected


def _crossover(
    parent1: List[int],
    parent2: List[int],
    crossover_rate: float,
    rng: random.Random,
) -> Tuple[List[int], List[int]]:
    """
    Одноточечное скрещивание двух родителей.
    """
    if rng.random() > crossover_rate or len(parent1) <= 1:
        return parent1[:], parent2[:]
    point = rng.randint(1, len(parent1) - 1)
    child1 = parent1[:point] + parent2[point:]
    child2 = parent2[:point] + parent1[point:]
    return child1, child2


def _mutate(chromosome: List[int], mutation_rate: float, rng: random.Random) -> None:
    """
    Побитовая мутация хромосомы.
    """
    for i in range(len(chromosome)):
        if rng.random() < mutation_rate:
            chromosome[i] = 1 - chromosome[i]


def solve_knapsack_genetic(
    weights: List[int],
    values: List[int],
    capacity: int,
    population_size: int = 80,
    generations: int = 100,
    crossover_rate: float = 0.8,
    mutation_rate: float = 0.02,
    random_seed: Optional[int] = None,
) -> Tuple[int, List[int]]:
    """
    Генетический алгоритм для 0/1 задачи о рюкзаке.

    Начальная популяция состоит из допустимых решений (одно из них — жадное),
    потомки после скрещивания и мутации «чинятся», лучшая особь сохраняется
    (элитизм). Поэтому результат всегда допустим и не хуже жадного алгоритма.

    Параметры по умолчанию подобраны для наглядности, а не абсолютной оптимальности.
    Генератор случайных чисел локальный: глобальный random не изменяется.
    """
    rng = random.Random(random_seed)

    n = len(weights)
    if n == 0 or capacity <= 0:
        return 0, []

    population_size = max(2, population_size)

    # Предметы от худшей плотности к лучшей — порядок удаления при починке.
    best_first = sorted(
        range(n), key=lambda i: value_density(values[i], weights[i]), reverse=True
    )
    worst_first = best_first[::-1]

    # Жадное решение попадает в начальную популяцию.
    greedy_chromosome = [0] * n
    total_weight = 0
    for i in best_first:
        if total_weight + weights[i] <= capacity:
            greedy_chromosome[i] = 1
            total_weight += weights[i]

    population: List[List[int]] = [greedy_chromosome] + [
        _random_feasible(n, weights, capacity, rng)
        for _ in range(population_size - 1)
    ]

    best_chromosome: List[int] = greedy_chromosome[:]
    best_value = _fitness(best_chromosome, weights, values, capacity)

    for _ in range(generations):
        fitnesses = [
            _fitness(chrom, weights, values, capacity) for chrom in population
        ]

        for chrom, fit in zip(population, fitnesses):
            if fit > best_value:
                best_value = fit
                best_chromosome = chrom[:]

        parents = _select_population(population, fitnesses, population_size, rng)

        # Элитизм: лучшая особь переходит в следующее поколение без изменений.
        new_population: List[List[int]] = [best_chromosome[:]]
        for i in range(0, population_size, 2):
            parent1 = parents[i]
            parent2 = parents[min(i + 1, population_size - 1)]
            child1, child2 = _crossover(parent1, parent2, crossover_rate, rng)
            _mutate(child1, mutation_rate, rng)
            _mutate(child2, mutation_rate, rng)
            _repair(child1, weights, capacity, worst_first)
            _repair(child2, weights, capacity, worst_first)
            new_population.extend([child1, child2])

        population = new_population[:population_size]

    # Последнее поколение тоже нужно оценить.
    for chrom in population:
        fit = _fitness(chrom, weights, values, capacity)
        if fit > best_value:
            best_value = fit
            best_chromosome = chrom[:]

    selected_items = [i for i, bit in enumerate(best_chromosome) if bit]
    return best_value, selected_items


__all__ = ["solve_knapsack_genetic"]
