class request: 
    def __init__(self,arrival_time, burst_time, priority, type, handled=False):
        self.Arrival_Time = arrival_time
        self.burst_time = burst_time
        self.priority = priority
        self.type = type
        self.handled = handled
    def get_arrival_time(self):
        return self.Arrival_Time
    def get_burst_time(self):
        return self.burst_time
    def get_priority(self):
        return self.priority
    def get_type(self):
        return self.type
    def is_handled(self):
        return self.handled
    def set_handled(self, handled):
        self.handled = handled