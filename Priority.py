def priority_schedule(requests):
    for p in requests:
        p.reset()

    ready     = []
    done      = []
    time      = 0
    remaining = list(requests)

    while remaining or ready:
        for p in [p for p in remaining if p.Arrival_Time <= time]:
            ready.append(p)
            remaining.remove(p)

        if not ready:
            time = min(p.Arrival_Time for p in remaining)
            continue

        # lower number = higher priority (Emergency = 1)
        ready.sort(key=lambda p: (p.priority, p.Arrival_Time))
        p = ready.pop(0)

        p.response_time   = time - p.Arrival_Time
        time             += p.burst_time
        p.completion_time = time
        p.turnaround_time = p.completion_time - p.Arrival_Time
        p.waiting_time    = p.turnaround_time - p.burst_time
        p.handled         = True
        done.append(p)

    return done
