import random

from scheduler.core.models import fits


def feasible_vms(task, vms):
    return [i for i, v in enumerate(vms) if fits(task, v)]


def random_chromosome(tasks, vms):
    """Only picks VMs with enough RAM, so it is always valid."""
    return [random.choice(feasible_vms(t, vms)) for t in tasks]


def repair(chromosome, tasks, vms):
    """Move any task on an incompatible VM to a random compatible one."""
    fixed = chromosome[:]
    for i, task in enumerate(tasks):
        if not fits(task, vms[fixed[i]]):
            fixed[i] = random.choice(feasible_vms(task, vms))
    return fixed


def decode(chromosome, tasks, vms):
    """Chromosome -> allocation dict {task_id: vm_id}."""
    return {t["id"]: vms[g]["id"] for t, g in zip(tasks, chromosome)}