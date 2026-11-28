"""Mesa trials 1 and 3: a queue with a newcomer, and the two adapters (issue #40). Throwaway.

Discrete-event queue: the line is a Python list owned by the model. Ten people queue at a
counter; service takes a random time (exponential, mean 10 s, from the model's seeded rng);
background arrivals join the back at random intervals. At 30 s a newcomer arrives and asks to
join ahead of position 3.

Trial 3 lives here too:
  perception adapter  situation()  -> a plain dict: order, arrival times, time waited, features
  action adapter      apply()      -> "admit" inserts at the asked position, "refuse" appends
The decider is a stand-in for a rule engine. The decision is applied (a) inside a scheduled
event, and (b) with --in-step, inside Model.step(), which Mesa calls every 1.0 time unit.

Determinism: the event log of two runs with the same seed is compared, and one other seed.

Usage: python mesa_trial1_queue.py [admit|refuse] [--in-step]
"""
import sys

import mesa
from mesa.time import Schedule


class Person(mesa.Agent):
    def __init__(self, model, name, age):
        super().__init__(model)
        self.name, self.age, self.arrived = name, age, model.time


def decider(situation):
    """Stand-in for the rule engine: Situation -> Decision."""
    return {"action": situation["policy"]}


class QueueModel(mesa.Model):
    def __init__(self, seed, policy, in_step=False):
        super().__init__(rng=seed)   # `seed=` is deprecated in 3.5.1 (FutureWarning)
        self.policy, self.in_step = policy, in_step
        self.line, self.log, self.pending = [], [], None
        for i in range(10):
            self.line.append(Person(self, f"P{i + 1}", int(self.rng.integers(18, 80))))
        self.schedule_event(self.serve, after=float(self.rng.exponential(10.0)))
        self.schedule_event(self.background_arrival, after=float(self.rng.exponential(12.0)))
        self.schedule_event(self.newcomer_arrives, at=30.0)

    def serve(self):
        if self.line:
            p = self.line.pop(0)
            self.log.append((round(self.time, 3), "served", p.name))
            p.remove()
        self.schedule_event(self.serve, after=float(self.rng.exponential(10.0)))

    def background_arrival(self):
        p = Person(self, f"B{len(self.log)}", int(self.rng.integers(18, 80)))
        self.line.append(p)
        self.log.append((round(self.time, 3), "joined back", p.name))
        self.schedule_event(self.background_arrival, after=float(self.rng.exponential(12.0)))

    # ---- perception adapter ----
    def situation(self, newcomer, asks_position):
        return {
            "conflict_type": "one_at_a_time_access/queue",
            "policy": self.policy,
            "asks_position": asks_position,
            "order": [p.name for p in self.line],
            "time_waited": {p.name: self.time - p.arrived for p in self.line},
            "features": {p.name: {"age": p.age} for p in self.line + [newcomer]},
        }

    # ---- action adapter ----
    def apply(self, decision, newcomer, asks_position):
        if decision["action"] == "admit":
            self.line.insert(asks_position - 1, newcomer)
        else:
            self.line.append(newcomer)
        self.log.append((round(self.time, 3), decision["action"],
                         f"{newcomer.name} now at {self.line.index(newcomer) + 1}"))

    def newcomer_arrives(self):
        newcomer = Person(self, "NEW", 70)
        if self.in_step:
            self.pending = newcomer          # decided at the next step() instead
        else:
            self.apply(decider(self.situation(newcomer, 3)), newcomer, 3)

    def step(self):
        if self.pending is not None:
            newcomer, self.pending = self.pending, None
            self.apply(decider(self.situation(newcomer, 3)), newcomer, 3)


def run(seed, policy, in_step, until=120.0):
    m = QueueModel(seed, policy, in_step)
    m.run_until(until)
    return m.log


if __name__ == "__main__":
    policy = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else "admit"
    in_step = "--in-step" in sys.argv
    log = run(42, policy, in_step)
    for row in log:
        if row[0] <= 80:
            print(*row)
    print("same seed, same log:", log == run(42, policy, in_step))
    print("other seed, different log:", log != run(43, policy, in_step))
