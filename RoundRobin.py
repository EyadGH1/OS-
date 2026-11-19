from collections import deque


def round_robin(requests, quantum=2):
    for p in requests:
        p.reset()

    procs      = sorted(requests, key=lambda p: p.Arrival_Time)
    queue      = deque()
    time       = 0
    idx        = 0
    n          = len(procs)
    done_count = 0

    while idx < n and procs[idx].Arrival_Time <= time:
        queue.append(procs[idx])
        idx += 1

    while done_count < n:
        if not queue:
            time = procs[idx].Arrival_Time
            while idx < n and procs[idx].Arrival_Time <= time:
                queue.append(procs[idx])
                idx += 1
            continue

        p = queue.popleft()

        if p.response_time == -1:
            p.response_time = time - p.Arrival_Time

        run              = min(quantum, p.remaining_time)
        time            += run
        p.remaining_time -= run

        while idx < n and procs[idx].Arrival_Time <= time:
            queue.append(procs[idx])
            idx += 1

        if p.remaining_time == 0:
            p.completion_time  = time
            p.turnaround_time  = p.completion_time - p.Arrival_Time
            p.waiting_time     = p.turnaround_time - p.burst_time
            p.handled          = True
            done_count        += 1
        else:
            queue.append(p)

    return procs
