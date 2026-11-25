import pytest
from scheduler.algorithms.ga import ga
from scheduler.algorithms.ma import ma
from scheduler.baselines import fcfs, random_alloc
from scheduler.core.interface import run_checked

TASKS = [
    {"id": "T1", "length": 1000, "memory": 2, "arrival_time": 0, "priority": 1},
    {"id": "T2", "length": 2000, "memory": 4, "arrival_time": 0, "priority": 1},
    {"id": "T3", "length": 1500, "memory": 1, "arrival_time": 0, "priority": 1},
]
VMS = [
    {"id": "VM1", "mips": 1000, "ram": 8, "cost_per_sec": 0.05},
    {"id": "VM2", "mips": 2000, "ram": 8, "cost_per_sec": 0.10},
    {"id": "VM3", "mips": 3000, "ram": 16, "cost_per_sec": 0.20},
]


@pytest.mark.parametrize("algo", [ga, ma, fcfs, random_alloc])
def test_algorithm_obeys_contract(algo):
    # run_checked raises ValueError on any contract violation
    run_checked(algo.run, TASKS, VMS)
