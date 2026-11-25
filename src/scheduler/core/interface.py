"""Every algorithm (GA, MA, FCFS, Random) exposes:

    def run(tasks: list[Task], vms: list[VM]) -> Allocation

Rules:
- Do not mutate `tasks` or `vms`.
- Return a complete, RAM-feasible allocation.
- Randomized algorithms use Python's `random` module, so seeding
  `random.seed(...)` makes them reproducible.
"""
from typing import Callable

from scheduler.core.models import (
    Allocation, Task, VM, validate_allocation, validate_inputs,
)

Algorithm = Callable[[list[Task], list[VM]], Allocation]


def run_checked(run_fn: Algorithm, tasks: list[Task], vms: list[VM]) -> Allocation:
    """Validate inputs, run the algorithm, validate its output.
    The experiment runner and UI should call algorithms through this."""
    validate_inputs(tasks, vms)
    allocation = run_fn(tasks, vms)
    validate_allocation(allocation, tasks, vms)
    return allocation
