import random

from scheduler.algorithms.common.chromosome import (
    decode, random_chromosome, repair,
)
from scheduler.core.fitness import evaluate, reference_values


def tournament(population, fitnesses, k=3):
    picked = random.sample(range(len(population)), min(k, len(population)))
    return population[min(picked, key=lambda i: fitnesses[i])][:]


def crossover(p1, p2):
    if len(p1) < 2:
        return p1[:], p2[:]
    point = random.randint(1, len(p1) - 1)
    return p1[:point] + p2[point:], p2[:point] + p1[point:]


def mutate(chromosome, num_vms, rate):
    return [
        random.randrange(num_vms) if random.random() < rate else g
        for g in chromosome
    ]


def run_with_history(tasks, vms, population_size=50, generations=100,
                     crossover_rate=0.8, mutation_rate=0.1, elite_count=2):
    refs = reference_values(tasks, vms)
    population = [random_chromosome(tasks, vms) for _ in range(population_size)]
    best, best_fit, history = None, float("inf"), []

    for _ in range(generations):
        fits_ = [evaluate(c, tasks, vms, refs) for c in population]

        order = sorted(range(len(population)), key=lambda i: fits_[i])
        if fits_[order[0]] < best_fit:
            best, best_fit = population[order[0]][:], fits_[order[0]]
        history.append(best_fit)

        next_pop = [population[i][:] for i in order[:elite_count]]
        while len(next_pop) < population_size:
            p1 = tournament(population, fits_)
            p2 = tournament(population, fits_)
            if random.random() < crossover_rate:
                c1, c2 = crossover(p1, p2)
            else:
                c1, c2 = p1, p2
            for child in (c1, c2):
                child = mutate(child, len(vms), mutation_rate)
                next_pop.append(repair(child, tasks, vms))
        population = next_pop[:population_size]

    return decode(best, tasks, vms), history


def run(tasks, vms):
    """The team contract: run(tasks, vms) -> allocation."""
    allocation, _ = run_with_history(tasks, vms)
    return allocation
