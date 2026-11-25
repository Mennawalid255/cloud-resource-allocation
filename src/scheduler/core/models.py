"""Shared data formats. Changing this file needs the whole team's approval."""
from typing import TypedDict


class Task(TypedDict):
    id: str
    length: float
    memory: float
    arrival_time: float
    priority: int


class VM(TypedDict):
    id: str
    mips: float
    ram: float
    cost_per_sec: float


Allocation = dict[str, str]


def fits(task, vm):
    return task["memory"] <= vm["ram"]


def validate_inputs(tasks, vms):
    if not tasks or not vms:
        raise ValueError("tasks and vms must be non-empty")
    for t in tasks:
        if not any(fits(t, v) for v in vms):
            raise ValueError("task " + str(t["id"]) + " fits no VM")


def validate_allocation(allocation, tasks, vms):
    vm_by_id = {v["id"]: v for v in vms}
    if set(allocation) != {t["id"] for t in tasks}:
        raise ValueError("every task must be assigned exactly once")
    for t in tasks:
        vm_id = allocation[t["id"]]
        if vm_id not in vm_by_id:
            raise ValueError("unknown VM " + str(vm_id))
        if not fits(t, vm_by_id[vm_id]):
            raise ValueError("task " + str(t["id"]) + " does not fit on " + str(vm_id))