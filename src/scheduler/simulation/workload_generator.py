import json
import os
import random
from scheduler.simulation.vm_factory import generate_vms
def generate_tasks(num_tasks: int, max_vm_ram: int = 32, seed: int = 42) -> list[dict]:
    #Generating tasks with diverse specifications and a reasonable deadline.
    rng = random.Random(seed + 1)
    
    memory_choices = [m for m in [1, 2, 4, 8, 16] if m <= max_vm_ram]
    tasks = []
    
    for i in range(1, num_tasks + 1):
        length = rng.randint(500, 10000)          # in the MI unit
        arrival_time = round(rng.uniform(0, num_tasks * 0.5), 2)
        
        #A logical deadline calculation based on task length (assuming an average speed of ~1500 MIPS)
        estimated_exec = length / 1500.0
        deadline = round(arrival_time + estimated_exec * rng.uniform(1.5, 3.0), 2)

        task = {
            "id": f"T{i}",
            "length": length,
            "memory": rng.choice(memory_choices), # in the GB unit
            "arrival_time": arrival_time,         # in the Second unit
            "priority": rng.randint(1, 3),        # high = 3, low = 1
            "deadline": deadline,                 # in the Second unit
        }
        tasks.append(task)
        
    # (Sorting tasks by arrival time, then by priority)
    tasks.sort(key=lambda t: (t["arrival_time"], t["priority"]))
    return tasks


def save_workload(filepath: str, tasks: list[dict], vms: list[dict]) -> None:
    #Saving tasks and VMs to a JSON file.
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump({"vms": vms, "tasks": tasks}, f, indent=2)


def load_workload(filepath: str) -> tuple[list[dict], list[dict]]:
    #Read the JSON file and return (tasks, vms).
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data["tasks"], data["vms"]


def generate_all_scenarios(output_dir: str = "data", seed: int = 42) -> None:
    #Generating the 3 primary scenarios for the project.
    scenarios = {
        "small_workload.json":  {"num_tasks": 20,  "num_vms": 5},
        "medium_workload.json": {"num_tasks": 100, "num_vms": 15},
        "large_workload.json":  {"num_tasks": 300, "num_vms": 30},
    }

    for filename, cfg in scenarios.items():
        vms = generate_vms(cfg["num_vms"], seed=seed)
        max_ram = max(vm["ram"] for vm in vms)
        tasks = generate_tasks(cfg["num_tasks"], max_vm_ram=max_ram, seed=seed)
        
        path = os.path.join(output_dir, filename)
        save_workload(path, tasks, vms)
        print(f"[OK] Generated {path} -> {len(tasks)} tasks, {len(vms)} VMs")


if __name__ == "__main__":
    generate_all_scenarios()