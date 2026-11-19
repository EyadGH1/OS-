from request    import Request
from FCFS       import fcfs
from SJF        import sjf
from SRTF       import srtf
from Priority   import priority_schedule
from RoundRobin import round_robin

requests = [
    Request("P1", 0, 8, 1, "Emergency"),
    Request("P2", 2, 4, 2, "ICU"),
    Request("P3", 4, 5, 3, "Surgery"),
    Request("P4", 6, 3, 6, "General"),
]

def print_results(name, procs):
    print(f"\n--- {name} ---")
    print(f"{'Process':<10} {'AT':<5} {'BT':<5} {'CT':<5} {'TAT':<5} {'WT':<5} {'RT':<5}")
    for p in procs:
        print(f"{p.name:<10} {p.Arrival_Time:<5} {p.burst_time:<5} "
              f"{p.completion_time:<5} {p.turnaround_time:<5} "
              f"{p.waiting_time:<5} {p.response_time:<5}")

if __name__ == "__main__":
    print_results("FCFS",              fcfs(requests))
    print_results("SJF",               sjf(requests))
    print_results("SRTF",              srtf(requests))
    print_results("Priority",          priority_schedule(requests))
    print_results("Round Robin (q=2)", round_robin(requests, quantum=2))
