#check if VM RAMs are enough for task or not
def check_memory_constraint(task: dict, vm: dict) -> bool:
    return task["memory"] <= vm["ram"]

#return list of VMs that can run the task
def get_valid_vms_for_task(task: dict, vms: list[dict]) -> list[dict]:
    return [vm for vm in vms if check_memory_constraint(task, vm)]

#Examine the entire distribution and return a detailed report on violations. 
def validate_allocation(
    allocation: dict[str, str],
    tasks: list[dict],
    vms: list[dict],
) -> dict:
    vm_map = {vm["id"]: vm for vm in vms}
    task_map = {task["id"]: task for task in tasks}

    missing_tasks = []
    invalid_vms = []
    memory_violations = []

    for task_id, task in task_map.items():
        if task_id not in allocation:
            missing_tasks.append(task_id)
            continue

        vm_id = allocation[task_id]
        if vm_id not in vm_map:
            invalid_vms.append({"task_id": task_id, "vm_id": vm_id})
            continue

        vm = vm_map[vm_id]
        if not check_memory_constraint(task, vm):
            memory_violations.append({
                "task_id": task_id,
                "vm_id": vm_id,
                "required_ram": task["memory"],
                "available_ram": vm["ram"],
            })

    total_violations = len(missing_tasks) + len(invalid_vms) + len(memory_violations)

    return {
        "is_valid": total_violations == 0,
        "total_violations": total_violations,
        "missing_tasks": missing_tasks,
        "invalid_vms": invalid_vms,
        "memory_violations": memory_violations,
    }


def calculate_execution_time(task: dict, vm: dict) -> float:
    # Calculating the execution time of a task on a specific VM in seconds (length / MIPS).
    return task["length"] / vm["mips"]


def simulate_allocation(
    tasks: list[dict],
    vms: list[dict],
    allocation: dict[str, str],
) -> dict:
    # Simulate the execution of tasks on VMs based on the given allocation.
    # Execution on each VM occurs sequentially, ordered first by arrival time and then by priority.
    validation = validate_allocation(allocation, tasks, vms)

    vm_map = {vm["id"]: vm for vm in vms}

    # Grouping tasks assigned to each VM
    vm_queues: dict[str, list[dict]] = {vm["id"]: [] for vm in vms}
    for task in tasks:
        vm_id = allocation.get(task["id"])
        if vm_id in vm_queues:
            vm_queues[vm_id].append(task)

    task_results: dict[str, dict] = {}
    vm_results: dict[str, dict] = {}

    for vm_id, queued_tasks in vm_queues.items():
        vm = vm_map[vm_id]
        # Ordering tasks on the VM based on arrival time, followed by priority (1 being the highest priority).
        queued_tasks.sort(key=lambda t: (t["arrival_time"], t["priority"]))

        current_time = 0.0
        total_busy_time = 0.0
        total_vm_cost = 0.0

        for task in queued_tasks:
            exec_time = calculate_execution_time(task, vm)
            start_time = max(task["arrival_time"], current_time)
            finish_time = start_time + exec_time
            waiting_time = start_time - task["arrival_time"]
            response_time = finish_time - task["arrival_time"]
            cost = exec_time * vm["cost_per_sec"]

            deadline = task.get("deadline")
            sla_violated = (finish_time > deadline) if deadline is not None else False

            task_results[task["id"]] = {
                "task_id": task["id"],
                "vm_id": vm_id,
                "arrival_time": task["arrival_time"],
                "start_time": round(start_time, 4),
                "execution_time": round(exec_time, 4),
                "finish_time": round(finish_time, 4),
                "waiting_time": round(waiting_time, 4),
                "response_time": round(response_time, 4),
                "cost": round(cost, 4),
                "deadline": deadline,
                "sla_violated": sla_violated,
            }

            current_time = finish_time
            total_busy_time += exec_time
            total_vm_cost += cost

        vm_results[vm_id] = {
            "vm_id": vm_id,
            "num_tasks": len(queued_tasks),
            "busy_time": round(total_busy_time, 4),
            "finish_time": round(current_time, 4),
            "total_cost": round(total_vm_cost, 4),
        }

    makespan = max((v["finish_time"] for v in vm_results.values()), default=0.0)
    total_cost = round(sum(v["total_cost"] for v in vm_results.values()), 4)

    return {
        "validation": validation,
        "makespan": round(makespan, 4),
        "total_cost": total_cost,
        "task_results": task_results,
        "vm_results": vm_results,
    }


def simulate_fast(
    tasks: list[dict],
    vms: list[dict],
    allocation: dict[str, str],
    vm_map: dict[str, dict] | None = None,
) -> dict:
    # A highly optimized version of the simulator, specifically for Member 2 (GA) and Member 3 (MA),
    # designed to be called tens of thousands of times within the fitness function.
    # (Assumes that the tasks are pre-sorted by arrival_time, followed by priority.)
    if vm_map is None:
        vm_map = {vm["id"]: vm for vm in vms}

    vm_free_time = {vm_id: 0.0 for vm_id in vm_map}
    total_cost = 0.0
    sla_violations = 0
    memory_violations = 0
    missing_or_invalid = 0

    for task in tasks:
        vm_id = allocation.get(task["id"])
        vm = vm_map.get(vm_id) if vm_id is not None else None

        if vm is None:
            missing_or_invalid += 1
            continue

        if task["memory"] > vm["ram"]:
            memory_violations += 1

        exec_time = task["length"] / vm["mips"]
        arrival = task["arrival_time"]
        free_t = vm_free_time[vm_id]

        start_time = arrival if arrival > free_t else free_t
        finish_time = start_time + exec_time

        vm_free_time[vm_id] = finish_time
        total_cost += exec_time * vm["cost_per_sec"]

        deadline = task.get("deadline")
        if deadline is not None and finish_time > deadline:
            sla_violations += 1

    makespan = max(vm_free_time.values(), default=0.0)

    return {
        "makespan": makespan,
        "total_cost": total_cost,
        "sla_violations": sla_violations,
        "memory_violations": memory_violations,
        "is_valid": (memory_violations == 0 and missing_or_invalid == 0),
    }