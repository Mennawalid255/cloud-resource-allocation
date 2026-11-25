import random

from scheduler.algorithms.common.chromosome import random_chromosome
from scheduler.algorithms.ga.ga import run_with_history
from scheduler.core.fitness import evaluate, reference_values

TASKS = [{"id": "T" + str(i), "length": 500 * (i + 1), "memory": 2,
          "arrival_time": 0, "priority": 1} for i in range(10)]
VMS = [
    {"id": "VM1", "mips": 1000, "ram": 8, "cost_per_sec": 0.05},
    {"id": "VM2", "mips": 2000, "ram": 8, "cost_per_sec": 0.10},
    {"id": "VM3", "mips": 3000, "ram": 16, "cost_per_sec": 0.20},
]


def test_fitness_never_gets_worse():
    random.seed(1)
    _, history = run_with_history(TASKS, VMS, generations=30)
    assert all(b <= a for a, b in zip(history, history[1:]))


def test_ga_beats_random():
    random.seed(1)
    refs = reference_values(TASKS, VMS)
    _, history = run_with_history(TASKS, VMS, generations=50)
    random_fit = evaluate(random_chromosome(TASKS, VMS), TASKS, VMS, refs)
    assert history[-1] <= random_fit