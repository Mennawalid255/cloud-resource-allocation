import random
#Provisioning VMs with various specifications (economical, medium, powerful).
def generate_vms(num_vms: int, seed: int = 42) -> list[dict]:
    rng = random.Random(seed)
    
    # 3 Different categories of servers, to create a balance between speed and cost.
    vm_tiers = [
        {"mips_range": (500, 1000),  "ram_choices": [4, 8],      "cost_range": (0.02, 0.05)},  # اقتصادي
        {"mips_range": (1200, 2000), "ram_choices": [8, 16],     "cost_range": (0.06, 0.12)},  # متوسط
        {"mips_range": (2500, 4000), "ram_choices": [16, 32],    "cost_range": (0.15, 0.30)},  # قوي
    ]

    vms = []
    for i in range(1, num_vms + 1):
        tier = vm_tiers[(i - 1) % len(vm_tiers)]  # Balanced distribution among groups
        vm = {
            "id": f"VM{i}",
            "mips": rng.randint(*tier["mips_range"]),
            "ram": rng.choice(tier["ram_choices"]),
            "cost_per_sec": round(rng.uniform(*tier["cost_range"]), 3),
        }
        vms.append(vm)
    return vms