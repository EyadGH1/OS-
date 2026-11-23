class Request:
    def __init__(self, name, arrival_time, burst_time, priority, department="Emergency"):
        self.name         = name
        self.Arrival_Time = arrival_time
        self.burst_time   = burst_time
        self.priority     = priority   # 1 = highest (Emergency)
        self.department   = department
        self.handled      = False

        # set during scheduling
        self.remaining_time  = burst_time
        self.completion_time = 0
        self.waiting_time    = 0
        self.turnaround_time = 0
        self.response_time   = -1

    def get_arrival_time(self):  return self.Arrival_Time
    def get_burst_time(self):    return self.burst_time
    def get_priority(self):      return self.priority
    def get_type(self):          return self.department
    def is_handled(self):        return self.handled
    def set_handled(self, h):    self.handled = h

    def reset(self):
        self.remaining_time  = self.burst_time
        self.completion_time = 0
        self.waiting_time    = 0
        self.turnaround_time = 0
        self.response_time   = -1
        self.handled         = False
