import tkinter as tk
from tkinter import ttk, messagebox

from request    import Request
from FCFS       import fcfs
from SJF        import sjf
from SRTF       import srtf
from Priority   import priority_schedule
from RoundRobin import round_robin

DEPARTMENTS = ["Emergency", "ICU", "Surgery", "Radiology", "Pharmacy", "General"]
DEPT_PRIORITY = {d: i + 1 for i, d in enumerate(DEPARTMENTS)}
ALGORITHMS = ["FCFS", "SJF", "SRTF", "Priority", "Round Robin"]

# color palette
BG        = "#f4f6f9"
SIDEBAR   = "#1e2a3a"
WHITE     = "#ffffff"
ACCENT    = "#2563eb"
TEXT      = "#1f2937"
SUBTEXT   = "#6b7280"
BORDER    = "#e5e7eb"
ROW_ALT   = "#f9fafb"


class SchedulerApp(tk.Tk):
    def __init__(self, initial_requests=None):
        super().__init__()
        self.title("Hospital Request Scheduler")
        self.geometry("1150x700")
        self.configure(bg=BG)
        self.resizable(True, True)

        self.requests = list(initial_requests) if initial_requests else []
        self._counter = len(self.requests) + 1

        self._setup_styles()
        self._build_layout()
        self._refresh_table()

    def _setup_styles(self):
        style = ttk.Style(self)
        style.theme_use("clam")

        style.configure("Treeview",
                        background=WHITE,
                        foreground=TEXT,
                        fieldbackground=WHITE,
                        rowheight=28,
                        font=("Segoe UI", 9),
                        borderwidth=0)
        style.configure("Treeview.Heading",
                        background=BG,
                        foreground=SUBTEXT,
                        font=("Segoe UI", 9, "bold"),
                        relief="flat")
        style.map("Treeview",
                  background=[("selected", ACCENT)],
                  foreground=[("selected", WHITE)])
        style.configure("TCombobox", fieldbackground=WHITE, background=WHITE)

    def _build_layout(self):
        # left sidebar
        sidebar = tk.Frame(self, bg=SIDEBAR, width=220)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        tk.Label(sidebar, text="Scheduler",
                 bg=SIDEBAR, fg=WHITE,
                 font=("Segoe UI", 15, "bold"),
                 pady=20).pack(fill="x")

        tk.Label(sidebar, text="Hospital Request Manager",
                 bg=SIDEBAR, fg="#94a3b8",
                 font=("Segoe UI", 8),
                 wraplength=180).pack(padx=16)

        tk.Frame(sidebar, bg="#2d3f52", height=1).pack(fill="x", padx=16, pady=20)

        # nav buttons
        self._nav_frames = {}
        nav_items = [("Requests", "requests"), ("Run Algorithm", "run")]
        for label, key in nav_items:
            btn = tk.Button(sidebar, text=label,
                            bg=SIDEBAR, fg="#cbd5e1",
                            font=("Segoe UI", 10),
                            relief="flat", anchor="w",
                            padx=20, pady=10, cursor="hand2",
                            activebackground="#2d3f52",
                            activeforeground=WHITE,
                            command=lambda k=key: self._show_page(k))
            btn.pack(fill="x")

        # main content area
        self._content = tk.Frame(self, bg=BG)
        self._content.pack(side="left", fill="both", expand=True)

        # build pages
        self._pages = {}
        self._build_page_requests()
        self._build_page_run()
        self._show_page("requests")

    def _show_page(self, name):
        for page in self._pages.values():
            page.pack_forget()
        self._pages[name].pack(fill="both", expand=True)

    # page header helper
    def _page_header(self, parent, title, subtitle=""):
        hdr = tk.Frame(parent, bg=BG)
        hdr.pack(fill="x", padx=30, pady=(24, 10))
        tk.Label(hdr, text=title, bg=BG, fg=TEXT,
                 font=("Segoe UI", 16, "bold")).pack(anchor="w")
        if subtitle:
            tk.Label(hdr, text=subtitle, bg=BG, fg=SUBTEXT,
                     font=("Segoe UI", 9)).pack(anchor="w")
        tk.Frame(parent, bg=BORDER, height=1).pack(fill="x", padx=30, pady=(0, 16))

    # card container
    def _card(self, parent, **pack_kwargs):
        card = tk.Frame(parent, bg=WHITE, relief="flat",
                        highlightbackground=BORDER, highlightthickness=1)
        card.pack(**pack_kwargs)
        return card

    # small label above an entry
    def _field_label(self, parent, text):
        tk.Label(parent, text=text, bg=WHITE, fg=SUBTEXT,
                 font=("Segoe UI", 8)).pack(anchor="w")

    def _entry(self, parent, var, width=14):
        e = tk.Entry(parent, textvariable=var, width=width,
                     bg="#f9fafb", fg=TEXT, relief="flat",
                     font=("Segoe UI", 10),
                     highlightbackground=BORDER,
                     highlightthickness=1,
                     insertbackground=TEXT)
        e.pack(anchor="w", pady=(0, 10))
        return e

    def _button(self, parent, text, cmd, color=ACCENT):
        return tk.Button(parent, text=text, command=cmd,
                         bg=color, fg=WHITE,
                         font=("Segoe UI", 9, "bold"),
                         relief="flat", padx=14, pady=7,
                         cursor="hand2",
                         activebackground="#1d4ed8",
                         activeforeground=WHITE)

    # -------------------------------------------------------------------------
    # PAGE: Requests
    # -------------------------------------------------------------------------
    def _build_page_requests(self):
        page = tk.Frame(self._content, bg=BG)
        self._pages["requests"] = page

        self._page_header(page, "Requests",
                          "Add and manage hospital department requests")

        # form card
        form_card = self._card(page, fill="x", padx=30, pady=(0, 16))
        inner = tk.Frame(form_card, bg=WHITE, padx=20, pady=16)
        inner.pack(fill="x")

        tk.Label(inner, text="New Request", bg=WHITE, fg=TEXT,
                 font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(0, 12))

        row = tk.Frame(inner, bg=WHITE)
        row.pack(fill="x")

        # fields
        self.name_var    = tk.StringVar(value=f"P{self._counter}")
        self.arrival_var = tk.StringVar()
        self.burst_var   = tk.StringVar()
        self.priority_var = tk.StringVar(value="6")
        self.dept_var    = tk.StringVar(value="General")

        for label, var, w in [
            ("Process Name", self.name_var, 12),
            ("Arrival Time", self.arrival_var, 12),
            ("Burst Time",   self.burst_var, 12),
            ("Priority",     self.priority_var, 8),
        ]:
            col = tk.Frame(row, bg=WHITE)
            col.pack(side="left", padx=(0, 20))
            self._field_label(col, label)
            self._entry(col, var, w)

        # department dropdown
        col = tk.Frame(row, bg=WHITE)
        col.pack(side="left", padx=(0, 20))
        self._field_label(col, "Department")
        dept_cb = ttk.Combobox(col, textvariable=self.dept_var,
                               values=DEPARTMENTS, state="readonly",
                               width=14, font=("Segoe UI", 10))
        dept_cb.pack(anchor="w", pady=(0, 10))
        dept_cb.bind("<<ComboboxSelected>>", self._on_dept_change)

        # buttons
        btn_row = tk.Frame(inner, bg=WHITE)
        btn_row.pack(anchor="w", pady=(4, 0))
        self._button(btn_row, "Add Request",   self._add_request).pack(side="left", padx=(0, 8))
        self._button(btn_row, "Remove Selected", self._del_request, "#ef4444").pack(side="left", padx=(0, 8))
        self._button(btn_row, "Clear All",     self._clear_all, "#6b7280").pack(side="left")

        # table card
        tbl_card = self._card(page, fill="both", expand=True, padx=30, pady=(0, 24))
        tbl_inner = tk.Frame(tbl_card, bg=WHITE, padx=4, pady=4)
        tbl_inner.pack(fill="both", expand=True)

        cols = ("Name", "Department", "Arrival", "Burst", "Priority")
        self.req_tree = ttk.Treeview(tbl_inner, columns=cols,
                                     show="headings", height=14)
        widths = [100, 160, 100, 100, 100]
        for c, w in zip(cols, widths):
            self.req_tree.heading(c, text=c)
            self.req_tree.column(c, width=w, anchor="center")

        sb = ttk.Scrollbar(tbl_inner, orient="vertical",
                           command=self.req_tree.yview)
        self.req_tree.configure(yscrollcommand=sb.set)
        self.req_tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

    def _on_dept_change(self, _=None):
        self.priority_var.set(str(DEPT_PRIORITY.get(self.dept_var.get(), 6)))

    def _add_request(self):
        name = self.name_var.get().strip() or f"P{self._counter}"
        try:
            arrival = int(self.arrival_var.get())
            burst = int(self.burst_var.get())
            priority = int(self.priority_var.get())
        except ValueError:
            messagebox.showerror("Input Error", "Arrival, burst, and priority must be valid numbers.")
            return

        if burst <= 0:
            messagebox.showerror("Input Error", "Burst time must be greater than 0.")
            return
        if arrival < 0:
            messagebox.showerror("Input Error", "Arrival time cannot be negative.")
            return

        dept = self.dept_var.get()

        req = Request(name, arrival, burst, priority, dept)
        self.requests.append(req)
        self._counter += 1
        self.req_tree.insert("", "end",
                             values=(req.name, req.department,
                                     req.Arrival_Time, req.burst_time,
                                     req.priority))
        self.name_var.set(f"P{self._counter}")
        self.arrival_var.set("")
        self.burst_var.set("")

    def _del_request(self):
        for item in self.req_tree.selection():
            idx = self.req_tree.index(item)
            self.req_tree.delete(item)
            if idx < len(self.requests):
                del self.requests[idx]

    def _clear_all(self):
        self.requests.clear()
        self._counter = 1
        for item in self.req_tree.get_children():
            self.req_tree.delete(item)
        self.name_var.set("P1")

    def _refresh_table(self):
        for item in self.req_tree.get_children():
            self.req_tree.delete(item)
        for r in self.requests:
            self.req_tree.insert("", "end",
                                 values=(r.name, r.department,
                                         r.Arrival_Time, r.burst_time,
                                         r.priority))

    # -------------------------------------------------------------------------
    # PAGE: Run Algorithm
    # -------------------------------------------------------------------------
    def _build_page_run(self):
        page = tk.Frame(self._content, bg=BG)
        self._pages["run"] = page

        self._page_header(page, "Run Algorithm",
                          "Select a scheduling algorithm and view the results")

        # controls card
        ctrl_card = self._card(page, fill="x", padx=30, pady=(0, 16))
        ctrl_inner = tk.Frame(ctrl_card, bg=WHITE, padx=20, pady=16)
        ctrl_inner.pack(fill="x")

        row = tk.Frame(ctrl_inner, bg=WHITE)
        row.pack(fill="x")

        # algorithm picker
        col1 = tk.Frame(row, bg=WHITE)
        col1.pack(side="left", padx=(0, 24))
        self._field_label(col1, "Algorithm")
        self.algo_var = tk.StringVar(value=ALGORITHMS[0])
        ttk.Combobox(col1, textvariable=self.algo_var,
                     values=ALGORITHMS, state="readonly",
                     width=20, font=("Segoe UI", 10)).pack(anchor="w", pady=(0, 10))

        # quantum
        col2 = tk.Frame(row, bg=WHITE)
        col2.pack(side="left", padx=(0, 24))
        self._field_label(col2, "Time Quantum (RR)")
        self.quantum_var = tk.StringVar(value="2")
        self._entry(col2, self.quantum_var, 6)

        # run button aligned with fields
        col3 = tk.Frame(row, bg=WHITE)
        col3.pack(side="left", anchor="s", pady=(14, 0))
        self._button(col3, "Run", self._run_algorithm).pack()

        # results table
        tbl_card = self._card(page, fill="both", expand=True, padx=30, pady=(0, 24))
        tbl_inner = tk.Frame(tbl_card, bg=WHITE, padx=4, pady=4)
        tbl_inner.pack(fill="both", expand=True)

        cols = ("Name", "Department", "AT", "BT", "Priority",
                "CT", "TAT", "WT", "RT")
        self.res_tree = ttk.Treeview(tbl_inner, columns=cols,
                                     show="headings", height=14)
        widths = [80, 130, 60, 60, 70, 60, 60, 60, 60]
        for c, w in zip(cols, widths):
            self.res_tree.heading(c, text=c)
            self.res_tree.column(c, width=w, anchor="center")

        sb2 = ttk.Scrollbar(tbl_inner, orient="vertical",
                            command=self.res_tree.yview)
        self.res_tree.configure(yscrollcommand=sb2.set)
        self.res_tree.pack(side="left", fill="both", expand=True)
        sb2.pack(side="right", fill="y")

    def _run_algorithm(self):
        if not self.requests:
            messagebox.showwarning("No Requests", "Add at least one request first.")
            return

        try:
            quantum = int(self.quantum_var.get())
        except ValueError:
            messagebox.showerror("Error", "Time quantum must be a number.")
            return

        if quantum <= 0:
            messagebox.showerror("Error", "Time quantum must be greater than 0.")
            return

        algo = self.algo_var.get()
        if algo == "FCFS":
            procs = fcfs(self.requests)
        elif algo == "SJF":
            procs = sjf(self.requests)
        elif algo == "SRTF":
            procs = srtf(self.requests)
        elif algo == "Priority":
            procs = priority_schedule(self.requests)
        else:
            procs = round_robin(self.requests, quantum)

        for item in self.res_tree.get_children():
            self.res_tree.delete(item)
        for p in procs:
            self.res_tree.insert("", "end", values=(
                p.name, p.department,
                p.Arrival_Time, p.burst_time, p.priority,
                p.completion_time, p.turnaround_time,
                p.waiting_time, p.response_time,
            ))


if __name__ == "__main__":
    from request import Request
    requests = [
        Request("P1", 0, 8, 1, "Emergency"),
        Request("P2", 2, 4, 2, "ICU"),
        Request("P3", 4, 5, 3, "Surgery"),
        Request("P4", 6, 3, 6, "General"),
    ]
    app = SchedulerApp(requests)
    app.mainloop()
