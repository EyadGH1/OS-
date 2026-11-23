def priority_schedule(requests):
    for p in requests:
        p.reset()

    n    = len(requests)
    done = 0
    time = 0

    while done < n:
        # get arrived processes that are not finished yet
        candidates = [p for p in requests if p.Arrival_Time <= time and p.remaining_time > 0]

        if not candidates:
            time += 1
            continue

        # lowest number = highest priority (Emergency = 1), tie broken by arrival
        candidates.sort(key=lambda p: (p.priority, p.Arrival_Time))
        cur = candidates[0]

        if cur.response_time == -1:
            cur.response_time = time - cur.Arrival_Time

        cur.remaining_time -= 1
        time += 1

        if cur.remaining_time == 0:
            cur.completion_time  = time
            cur.turnaround_time  = cur.completion_time - cur.Arrival_Time
            cur.waiting_time     = cur.turnaround_time - cur.burst_time
            cur.handled          = True
            done += 1

    return requests
