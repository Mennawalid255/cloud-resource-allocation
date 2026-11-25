"""Shared data formats. Changing this file needs the whole team's approval."""
from typing import TypedDict


class Task(TypedDict):
    id: str
    length: float        # million instructions (MI)
    memory: float        # GB of RAM required
    arrival_time: float  # seconds
    priority: int


class VM(TypedDict):
    id: str
    mips: float          # million instructions per second
    ram: float           # GB of RAM available
    cost_per_sec: float


# Maps task id -> vm id, e.g. {"T1": "VM1", "T2": "VM2"}
Allocation = dict[str, str]

TASK_KEYS = {"id", "length", "memory", "arrival_time", "priority"}
VM_KEYS = {"id", "mips", "ram", "cost_per_sec"}


def fits(task: Task, vm: VM) -> bool:
    """True if the VM has enough RAM for the task."""
    return task["memory"] <= vm["ram"]


def validate_inputs(tasks: list[Task], vms: list[VM]) -> None:
    """Raise ValueError if tasks/VMs are malformed."""
    if not tasks or not vms:
        raise ValueError("tasks and vms must be non-empty")
    for t in tasks:
        missing = TASK_KEYS - set(t)
        if missing:
            raise ValueError(f"task {t.get('id')} is missing {missing}")
    for v in vms:
        missing = VM_KEYS - set(v)
        if missing:
            raise ValueError(f"vm {v.get('id')} is missing {missing}")
        if v["mips"] <= 0:
            raise ValueError(f"vm {v['id']} has non-positive mips")
    for t in tasks:
        if not any(fits(t, v) for v in vms):
            raise ValueError(f"task {t['id']} fits no VM")


def validate_allocation(allocation: Allocation, tasks: list[Task], vms: list[VM]) -> None:
    """Raise ValueError if the allocation breaks the contract."""
    task_ids = {t["id"] for t in tasks}
    vm_by_id = {v["id"]: v for v in vms}
    if set(allocation) != task_ids:
        raise ValueError("every task must be assigned exactly once")
    for t in tasks:
        vm_id = allocation[t["id"]]
        if vm_id not in vm_by_id:
            raise ValueError(f"task {t['id']} assigned to unknown VM {vm_id}")
        if not fits(t, vm_by_id[vm_id]):
            raise ValueError(f"task {t['id']} does not fit on {vm_id} (RAM)")
