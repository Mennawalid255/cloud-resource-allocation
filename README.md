# cloud-resource-allocationx
# Cloud Resource Allocation

Task scheduling on cloud virtual machines using a **Genetic Algorithm (GA)** and a **Memetic Algorithm (MA)**, compared against **FCFS** and **Random** baselines.

[One or two sentences: what problem it solves, e.g. assign N tasks to M VMs to minimize makespan and cost.]

## Team

| Member | Role |
|---|---|
| Yahia | Cloud simulation and workloads |
| Menna | Genetic Algorithm |
| Yasser | Memetic Algorithm |
| Taha | Baselines and evaluation metrics |
| Samy | Research, experiments, visualization |
| Adel | Interface, architecture, documentation |

## Project structure

```
src/scheduler/
├── core/            # Shared formats, fitness function, config
├── simulation/      # Task/VM model and workload generator
├── algorithms/      # GA, MA, shared chromosome and repair code
├── baselines/       # FCFS, Random
├── evaluation/      # Metrics (makespan, cost, utilization...)
├── experiments/     # Experiment runner and configs
├── visualization/   # Plots
└── interface/       # Streamlit app
tests/               # pytest tests
```

## Setup

```bash
git clone https://github.com/Mennawalid255/cloud-resource-allocation.git
cd cloud-resource-allocation
pip install -r requirements.txt
pip install -e .
```

## Usage

```bash
pytest -v                                  # run tests
streamlit run src/scheduler/interface/app.py   # launch the UI
```

[Add the experiment command here once runner.py exists.]

## Shared contract

Every algorithm implements `run(tasks, vms) -> allocation`.

```python
task = {"id": "T1", "length": 1000, "memory": 2, "arrival_time": 0, "priority": 1}
vm = {"id": "VM1", "mips": 1000, "ram": 8, "cost_per_sec": 0.05}
allocation = {"T1": "VM1", "T2": "VM2"}
```

## Team workflow

1. Never push directly to `main`.
2. Create a branch: `feature/<member>-<topic>`.
3. Open a pull request and wait for the green CI check.
4. Changes to `src/scheduler/core/` need the whole team's agreement.
5. Every module ships with at least one test.
