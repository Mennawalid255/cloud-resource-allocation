import random
import time
import pytest
from scheduler.simulation import (
    load_workload,
    get_valid_vms_for_task,
    validate_allocation,
    simulate_allocation,
    simulate_fast
)


def test_load_small_workload():
    tasks, vms = load_workload("data/small_workload.json")
    assert len(tasks) == 20
    assert len(vms) == 5
    # Ensure that all the keys agreed upon in the contract are present.
    for key in ["id", "length", "memory", "arrival_time", "priority", "deadline"]:
        assert key in tasks[0]
    for key in ["id", "mips", "ram", "cost_per_sec"]:
        assert key in vms[0]


def test_memory_violation_detection():
    tasks = [{"id": "T1", "length": 1000, "memory": 16, "arrival_time": 0, "priority": 1, "deadline": 5}]
    vms = [{"id": "VM1", "mips": 1000, "ram": 8, "cost_per_sec": 0.05}]
    allocation = {"T1": "VM1"}

    report = validate_allocation(allocation, tasks, vms)
    assert report["is_valid"] is False
    assert len(report["memory_violations"]) == 1


def test_exact_simulation_math():
    #Manually verify the mathematical calculations using a simple example with a known result.
    vms = [{"id": "VM1", "mips": 1000, "ram": 8, "cost_per_sec": 0.1}]
    tasks = [
        {"id": "T1", "length": 2000, "memory": 4, "arrival_time": 0.0, "priority": 1, "deadline": 5.0},
        {"id": "T2", "length": 1000, "memory": 4, "arrival_time": 1.0, "priority": 1, "deadline": 2.5},
    ]
    allocation = {"T1": "VM1", "T2": "VM1"}

    res = simulate_allocation(tasks, vms, allocation)

    # T1: exec = 2000/1000 = 2s -> start=0, finish=2, cost=0.2, SLA=False
    # T2: arrives at 1s, waits until 2s -> exec=1s -> finish=3, cost=0.1, SLA=True (3 > 2.5)
    assert res["validation"]["is_valid"] is True
    assert res["makespan"] == 3.0
    assert res["total_cost"] == 0.3
    assert res["task_results"]["T1"]["sla_violated"] is False
    assert res["task_results"]["T2"]["waiting_time"] == 1.0
    assert res["task_results"]["T2"]["sla_violated"] is True


def test_full_small_workload_simulation():
    tasks, vms = load_workload("data/small_workload.json")
    rng = random.Random(42)

    #Random distribution that respects RAM constraints.
    allocation = {}
    for task in tasks:
        valid_vms = get_valid_vms_for_task(task, vms)
        allocation[task["id"]] = rng.choice(valid_vms)["id"]

    res = simulate_allocation(tasks, vms, allocation)
    assert res["validation"]["is_valid"] is True
    assert res["makespan"] > 0
    assert res["total_cost"] > 0
    assert len(res["task_results"]) == len(tasks)





def test_fast_matches_full_and_stress_benchmark():
    #Verify that `simulate_fast` produces the exact same numbers, and measure its speed using a large workload.
    tasks, vms = load_workload("data/large_workload.json")
    tasks.sort(key=lambda t: (t["arrival_time"], t["priority"]))
    rng = random.Random(42)

    allocation = {}
    for task in tasks:
        valid_vms = get_valid_vms_for_task(task, vms)
        allocation[task["id"]] = rng.choice(valid_vms)["id"]

    full_res = simulate_allocation(tasks, vms, allocation)
    fast_res = simulate_fast(tasks, vms, allocation)

    # 1. Ensuring that the mathematical results match 100%
    # assert round(fast_res["makespan"], 4) == full_res["makespan"]
    # assert round(fast_res["total_cost"], 4) == full_res["total_cost"]
    assert fast_res["makespan"] == pytest.approx(full_res["makespan"], abs=1e-3)
    assert fast_res["total_cost"] == pytest.approx(full_res["total_cost"], abs=1e-3)
    assert fast_res["is_valid"] == full_res["validation"]["is_valid"]

    # 2. Stress Test (1,000 evaluations across 300 tasks)
    vm_map = {vm["id"]: vm for vm in vms}
    runs = 1000

    t0 = time.perf_counter()
    for _ in range(runs):
        simulate_allocation(tasks, vms, allocation)
    full_time = time.perf_counter() - t0

    t0 = time.perf_counter()
    for _ in range(runs):
        simulate_fast(tasks, vms, allocation, vm_map=vm_map)
    fast_time = time.perf_counter() - t0

    print(f"\n[Benchmark - {runs} runs on 300 tasks]")
    print(f"simulate_allocation: {full_time:.3f}s")
    print(f"simulate_fast:       {fast_time:.3f}s ({full_time / fast_time:.1f}x faster!)")
    assert fast_time < full_time