from request    import Request
from FCFS       import fcfs
from SJF        import sjf
from SRTF       import srtf
from Priority   import priority_schedule
from RoundRobin import round_robin

# (name, arrival, burst, priority, department)
tests = [
    ("Test 1: normal", [
        ("P1", 0, 6, 2, "Laboratory"),
        ("P2", 1, 8, 3, "Radiology"),
        ("P3", 2, 3, 1, "Emergency"),
        ("P4", 3, 2, 4, "Pharmacy"),
    ]),
    ("Test 2: long emergency", [
        ("P1", 0, 10, 3, "Radiology"),
        ("P2", 1, 9,  1, "Emergency"),
        ("P3", 2, 2,  2, "Laboratory"),
    ]),
    ("Test 3: one long and many short", [
        ("P1", 0, 12, 3, "Radiology"),
        ("P2", 1, 2,  2, "Laboratory"),
        ("P3", 2, 2,  4, "Pharmacy"),
        ("P4", 3, 2,  2, "Laboratory"),
        ("P5", 4, 2,  4, "Pharmacy"),
    ]),
    ("Test 4: all arrive at 0", [
        ("P1", 0, 5, 2, "Laboratory"),
        ("P2", 0, 3, 3, "Radiology"),
        ("P3", 0, 4, 1, "Emergency"),
        ("P4", 0, 1, 4, "Pharmacy"),
    ]),
]

algorithms = [
    ("FCFS",        fcfs),
    ("SJF",         sjf),
    ("SRTF",        srtf),
    ("Priority",    priority_schedule),
    ("Round Robin", lambda r: round_robin(r, quantum=2)),
]

def compare(name, data):
    print(f"\n--- {name} ---")
    print(f"{'Algorithm':<13} {'Avg WT':<8} {'Avg TAT':<8} {'Emg WT':<8} {'Max WT':<8} {'Max-Min':<8}")

    for algo_name, algo in algorithms:
        procs = [Request(*row) for row in data]
        algo(procs)

        wt  = [p.waiting_time for p in procs]
        tat = [p.turnaround_time for p in procs]

        emg = "-"
        for p in procs:
            if p.department == "Emergency":
                emg = p.waiting_time

        print(f"{algo_name:<13} {sum(wt) / len(wt):<8.2f} {sum(tat) / len(tat):<8.2f} "
              f"{str(emg):<8} {max(wt):<8} {max(wt) - min(wt):<8}")

if __name__ == "__main__":
    for name, data in tests:
        compare(name, data)
