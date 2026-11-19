def fcfs(requests):
    for p in requests:
        p.reset()

    procs = sorted(requests, key=lambda p: p.Arrival_Time)
    time  = 0

    for p in procs:
        if time < p.Arrival_Time:
            time = p.Arrival_Time

        p.response_time   = time - p.Arrival_Time
        time             += p.burst_time
        p.completion_time = time
        p.turnaround_time = p.completion_time - p.Arrival_Time
        p.waiting_time    = p.turnaround_time - p.burst_time
        p.handled         = True

    return procs
