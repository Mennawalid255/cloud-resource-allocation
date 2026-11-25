from scheduler.core.models import fits

ALPHA = 0.5
BETA = 0.5


def reference_values(tasks, vms):
    """Fixed normalization values for one problem instance."""
    makespan_ref = sum(t["length"] for t in tasks) / sum(v["mips"] for v in vms)
    cost_ref = sum(
        min(t["length"] / v["mips"] * v["cost_per_sec"] for v in vms if fits(t, v))
        for t in tasks
    )
    return cost_ref or 1.0, makespan_ref or 1.0


def evaluate(chromosome, tasks, vms, refs=None, alpha=ALPHA, beta=BETA):
    """Lower is better. chromosome[i] = index of the VM for tasks[i]."""
    cost_ref, makespan_ref = refs or reference_values(tasks, vms)
    loads = [0.0] * len(vms)
    cost = 0.0
    for task, vm_index in zip(tasks, chromosome):
        vm = vms[vm_index]
        if not fits(task, vm):
            return float("inf")
        time = task["length"] / vm["mips"]
        loads[vm_index] += time
        cost += time * vm["cost_per_sec"]
    return alpha * cost / cost_ref + beta * max(loads) / makespan_ref