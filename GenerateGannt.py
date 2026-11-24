from request    import Request
from FCFS       import fcfs
from SJF        import sjf
from SRTF       import srtf
from Priority   import priority_schedule
from RoundRobin import round_robin

# Gantt chart + waiting time + turnaround time for every algorithm.
# The algorithm files are NOT changed. We give them a "tracked" request that
# writes down every time the CPU works on it, then we build the Gantt chart
# from those notes.


class TrackedRequest(Request):
    def __init__(self, name, arrival_time, burst_time, priority, department, log):
        self.log = log            # shared list for all requests of one run
        super().__init__(name, arrival_time, burst_time, priority, department)

    def __setattr__(self, attr, value):
        # preemptive algorithms (SRTF, Priority, RR) lower remaining_time
        # each time the request runs -> note (request, how long it ran)
        if attr == "remaining_time" and hasattr(self, "remaining_time"):
            if value < self.remaining_time:
                self.log.append((self, self.remaining_time - value))

        # FCFS and SJF never touch remaining_time, they only set completion_time
        # -> the request ran its whole burst in one go
        elif attr == "completion_time" and value > 0:
            if self.remaining_time == self.burst_time:
                self.log.append((self, self.burst_time))

        super().__setattr__(attr, value)


def build_gantt(log):
    """Turn the run log into blocks: (name, start, end). Idle CPU = 'IDLE'."""
    gantt = []
    time  = 0

    for p, run in log:
        start = max(time, p.Arrival_Time)    # CPU waits if the request is not here yet

        if start > time:
            gantt.append(("IDLE", time, start))

        end = start + run

        # SRTF / Priority run 1 unit at a time -> join blocks of the same request
        if gantt and gantt[-1][0] == p.name and gantt[-1][2] == start:
            gantt[-1] = (p.name, gantt[-1][1], end)
        else:
            gantt.append((p.name, start, end))

        time = end

    return gantt


def run_with_gantt(algo, requests):
    """Run one algorithm on copies of the requests and return (procs, gantt)."""
    log   = []
    procs = [TrackedRequest(r.name, r.Arrival_Time, r.burst_time,
                            r.priority, r.department, log) for r in requests]
    algo(procs)
    gantt = build_gantt(log)

    # check: the chart must end each request at the completion time of the algorithm
    for p in procs:
        last_end = max(end for name, start, end in gantt if name == p.name)
        if last_end != p.completion_time:
            print(f"Warning: {p.name} ends at {last_end} in the chart "
                  f"but completion time is {p.completion_time}")

    return procs, gantt


def print_gantt(gantt):
    top    = "+"
    middle = "|"
    times  = str(gantt[0][1])

    for name, start, end in gantt:
        width   = max(len(name) + 2, (end - start) * 2)
        top    += "-" * width + "+"
        middle += name.center(width) + "|"
        times  += str(end).rjust(width + 1)

    print(top)
    print(middle)
    print(top)
    print(times)


def print_times(procs):
    print(f"{'Process':<10} {'Dept':<12} {'AT':<5} {'BT':<5} {'CT':<5} {'WT':<5} {'TAT':<5}")
    for p in procs:
        print(f"{p.name:<10} {p.department:<12} {p.Arrival_Time:<5} {p.burst_time:<5} "
              f"{p.completion_time:<5} {p.waiting_time:<5} {p.turnaround_time:<5}")

    n       = len(procs)
    avg_wt  = sum(p.waiting_time for p in procs) / n
    avg_tat = sum(p.turnaround_time for p in procs) / n
    print(f"Average Waiting Time    = {avg_wt:.2f}")
    print(f"Average Turnaround Time = {avg_tat:.2f}")
    return avg_wt, avg_tat


def print_report(name, algo, requests):
    procs, gantt = run_with_gantt(algo, requests)
    print(f"\n========== {name} ==========")
    print("Gantt Chart:")
    print_gantt(gantt)
    print()
    print_times(procs)
    return procs, gantt


# one color per department (the label on each block also shows the process name)
DEPT_COLORS = {
    "Emergency":  "#2a78d6",
    "Laboratory": "#eb6834",
    "Radiology":  "#1baf7a",
    "Pharmacy":   "#eda100",
}
IDLE_COLOR = "#d6d5d0"


def draw_gantt(results, requests, file_name="gantt_charts.png", show=True):
    """Draw all Gantt charts in one picture with matplotlib (for the report)."""
    import matplotlib.pyplot as plt
    from matplotlib.patches import Patch

    dept_of = {r.name: r.department for r in requests}
    end_all = max(g[-1][2] for _, g, _ in results)

    fig, axes = plt.subplots(len(results), 1, figsize=(11, 1.7 * len(results) + 1))
    if len(results) == 1:
        axes = [axes]

    for ax, (name, gantt, avgs) in zip(axes, results):
        for proc, start, end in gantt:
            if proc == "IDLE":
                ax.broken_barh([(start, end - start)], (0, 1),
                               facecolors=IDLE_COLOR, edgecolor="white",
                               linewidth=2, hatch="//")
            else:
                ax.broken_barh([(start, end - start)], (0, 1),
                               facecolors=DEPT_COLORS.get(dept_of[proc], "#6250d6"),
                               edgecolor="white", linewidth=2)
                ax.text((start + end) / 2, 0.5, proc, ha="center", va="center",
                        fontsize=9, color="#0b0b0b")

        ticks = sorted({g[1] for g in gantt} | {g[2] for g in gantt})
        ax.set_xticks(ticks)
        ax.tick_params(axis="x", labelsize=8)
        ax.set_yticks([])
        ax.set_xlim(0, end_all)
        ax.set_title(f"{name}    (Avg WT = {avgs[0]:.2f},  Avg TAT = {avgs[1]:.2f})",
                     loc="left", fontsize=10)
        for side in ("top", "right", "left"):
            ax.spines[side].set_visible(False)

    axes[-1].set_xlabel("Time")
    legend = [Patch(facecolor=c, label=d) for d, c in DEPT_COLORS.items()]
    legend.append(Patch(facecolor=IDLE_COLOR, hatch="//", label="Idle"))
    fig.legend(handles=legend, loc="upper right", bbox_to_anchor=(0.99, 0.99),
               ncol=5, frameon=False, fontsize=9)
    fig.suptitle("Hospital Server OS Simulator - Gantt Charts", x=0.01, ha="left",
                 fontsize=12, fontweight="bold")
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    fig.savefig(file_name, dpi=150)
    print(f"\nGantt charts saved to {file_name}")

    if show:
        plt.show()
    plt.close(fig)


if __name__ == "__main__":
    # same requests as main.py
    requests = [
        Request("P1", 0, 8, 1, "Emergency"),
        Request("P2", 2, 4, 2, "Laboratory"),
        Request("P3", 4, 5, 3, "Radiology"),
        Request("P4", 6, 3, 4, "Pharmacy"),
    ]
    quantum = 2

    algorithms = [
        ("FCFS",                     fcfs),
        ("SJF (non-preemptive)",     sjf),
        ("SRTF",                     srtf),
        ("Priority (preemptive)",    priority_schedule),
        (f"Round Robin (q={quantum})", lambda r: round_robin(r, quantum)),
    ]

    print("Hospital Server OS Simulator - Gantt Charts and Performance")
    results = []
    for name, algo in algorithms:
        procs, gantt = print_report(name, algo, requests)
        avg_wt  = sum(p.waiting_time for p in procs) / len(procs)
        avg_tat = sum(p.turnaround_time for p in procs) / len(procs)
        results.append((name, gantt, (avg_wt, avg_tat)))

    try:
        draw_gantt(results, requests)
    except ImportError:
        print("\nInstall matplotlib to also get the Gantt chart picture:  pip install matplotlib")
