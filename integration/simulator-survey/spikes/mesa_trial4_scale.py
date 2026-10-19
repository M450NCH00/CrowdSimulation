"""Mesa trial 4: 1,000 and 10,000 queueing agents (issue #40). Throwaway.

(a) Event-driven: N people arrive (Poisson) and queue at 10 counters (shortest line);
    service is exponential. Run until all are served; report time per event.
(b) Step-based: N agents in 10 lines; on every step each agent reads its place in its line
    and asks a stand-in decider whether to stay (a perception + decision pass per agent,
    in Python). Report time per step, over 20 steps.
Wall-clock start and end are printed for the sleep check.

Usage: python mesa_trial4_scale.py [reps]
"""
import datetime
import statistics
import sys
import time

import mesa

COUNTERS = 10


class Shopper(mesa.Agent):
    def step(self):
        line = self.model.lines[self.line_no]
        place = line.index(self) if self.model.with_index else self.place
        self.model.decisions += decide({"place": place, "waited": self.model.time - self.arrived})


def decide(situation):
    return 1 if situation["place"] > 50 and situation["waited"] > 1e9 else 0


class Counter:
    # Mesa holds scheduled callbacks by WEAK reference, and schedule_event passes no
    # arguments: a lambda or functools.partial is collected at once and raises
    # "function must be alive at Event creation". So each counter is a live object whose
    # bound method is scheduled.
    def __init__(self, model, k):
        self.model, self.k = model, k

    def serve(self):
        self.model.serve(self.k)


class EventQueues(mesa.Model):
    def __init__(self, n, seed):
        super().__init__(rng=seed)
        self.n, self.lines, self.events, self.served = n, [[] for _ in range(COUNTERS)], 0, 0
        self.counters = [Counter(self, k) for k in range(COUNTERS)]
        self.schedule_event(self.arrive, after=float(self.rng.exponential(0.1)))
        self.arrived = 0

    def arrive(self):
        self.events += 1
        a = Shopper(self)
        a.arrived = self.time
        k = min(range(COUNTERS), key=lambda i: len(self.lines[i]))
        self.lines[k].append(a)
        if len(self.lines[k]) == 1:
            self.schedule_event(self.counters[k].serve, after=float(self.rng.exponential(1.0)))
        self.arrived += 1
        if self.arrived < self.n:
            self.schedule_event(self.arrive, after=float(self.rng.exponential(0.1)))

    def serve(self, k):
        self.events += 1
        self.lines[k].pop(0).remove()
        self.served += 1
        if self.lines[k]:
            self.schedule_event(self.counters[k].serve, after=float(self.rng.exponential(1.0)))


class StepQueues(mesa.Model):
    def __init__(self, n, seed, with_index):
        super().__init__(rng=seed)
        self.with_index, self.decisions = with_index, 0
        self.lines = [[] for _ in range(COUNTERS)]
        for i in range(n):
            a = Shopper(self)
            a.arrived, a.line_no, a.place = 0.0, i % COUNTERS, len(self.lines[i % COUNTERS])
            self.lines[a.line_no].append(a)

    def step(self):
        self.agents.shuffle_do("step")


def event_run(n, seed):
    m = EventQueues(n, seed)
    t0 = time.perf_counter()
    # Not run_until(1e9): Model also fires its default step() every 1.0 time unit, so that
    # would be a billion no-op steps (first attempt; it ran past 10 minutes). Run in chunks.
    while m.served < n:
        m.run_for(100)
    dt = time.perf_counter() - t0
    assert m.served == n
    return dt / m.events, m.events


def step_run(n, seed, with_index):
    m = StepQueues(n, seed, with_index)
    m.step()   # warm-up
    t0 = time.perf_counter()
    for _ in range(20):
        m.step()
    return (time.perf_counter() - t0) / 20


if __name__ == "__main__":
    reps = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    print("start", datetime.datetime.now().isoformat(timespec="seconds"))
    for n in (1000, 10000):
        ev = [event_run(n, s) for s in range(reps)]
        st = [step_run(n, s, False) for s in range(reps)]
        sti = [step_run(n, s, True) for s in range(reps)]
        print(f"N={n:>5}: (a) {statistics.median(e[0] for e in ev) * 1e6:6.1f} us/event "
              f"({ev[0][1]} events, run total {statistics.median(e[0] * e[1] for e in ev):.3f} s); "
              f"(b) {statistics.median(st) * 1e3:7.2f} ms/step with a stored place, "
              f"{statistics.median(sti) * 1e3:8.2f} ms/step with list.index (reps {reps})")
    print("end", datetime.datetime.now().isoformat(timespec="seconds"))
