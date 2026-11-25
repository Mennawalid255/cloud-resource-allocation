from scheduler.core.models import Allocation, Task, VM, fits


def run(tasks: list[Task], vms: list[VM]) -> Allocation:
    # STUB: replace with the real algorithm.
    allocation = {}
    for t in tasks:
        vm = next((v for v in vms if fits(t, v)), None)
        if vm is None:
            raise ValueError("task " + str(t["id"]) + " fits no VM")
        allocation[t["id"]] = vm["id"]
    return allocation
