import random
from typing import Callable, List, Tuple, Optional


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


def _select_population(
    population: List[List[int]],
    fitnesses: List[int],
    selection_size: int,
) -> List[List[int]]:
    """
    Турнирная селекция в популяции.
    """
    selected: List[List[int]] = []
    n = len(population)
    for _ in range(selection_size):
        i, j = random.randrange(n), random.randrange(n)
        if fitnesses[i] > fitnesses[j]:
            selected.append(population[i])
        else:
            selected.append(population[j])
    return selected


def _crossover(
    parent1: List[int],
    parent2: List[int],
    crossover_rate: float,
) -> Tuple[List[int], List[int]]:
    """
    Одноточечное скрещивание двух родителей.
    """
    if random.random() > crossover_rate or len(parent1) <= 1:
        return parent1[:], parent2[:]
    point = random.randint(1, len(parent1) - 1)
    child1 = parent1[:point] + parent2[point:]
    child2 = parent2[:point] + parent1[point:]
    return child1, child2


def _mutate(chromosome: List[int], mutation_rate: float) -> None:
    """
    Побитовая мутация хромосомы.
    """
    for i in range(len(chromosome)):
        if random.random() < mutation_rate:
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

    Параметры по умолчанию подобраны для наглядности, а не абсолютной оптимальности.
    """
    if random_seed is not None:
        random.seed(random_seed)

    n = len(weights)
    if n == 0 or capacity <= 0:
        return 0, []

    # Инициализация случайной популяции бинарных векторов.
    population: List[List[int]] = [
        [random.randint(0, 1) for _ in range(n)] for _ in range(population_size)
    ]

    best_chromosome: List[int] = []
    best_value = 0

    for _ in range(generations):
        fitnesses = [
            _fitness(chrom, weights, values, capacity) for chrom in population
        ]

        for chrom, fit in zip(population, fitnesses):
            if fit > best_value:
                best_value = fit
                best_chromosome = chrom[:]

        parents = _select_population(population, fitnesses, population_size)

        new_population: List[List[int]] = []
        for i in range(0, population_size, 2):
            parent1 = parents[i]
            parent2 = parents[min(i + 1, population_size - 1)]
            child1, child2 = _crossover(parent1, parent2, crossover_rate)
            _mutate(child1, mutation_rate)
            _mutate(child2, mutation_rate)
            new_population.extend([child1, child2])

        population = new_population[:population_size]

    if not best_chromosome:
        # Если все решения оказались некорректными, возвращаем пустой рюкзак.
        return 0, []

    selected_items = [i for i, bit in enumerate(best_chromosome) if bit]
    return best_value, selected_items


__all__ = ["solve_knapsack_genetic"]

