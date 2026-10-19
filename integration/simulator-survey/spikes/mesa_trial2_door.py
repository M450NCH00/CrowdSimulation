"""Mesa trial 2 (optional in the shortlist): a door as a capacity-one resource (issue #40).

Discrete form of boarding: one door, one person through at a time. Alighters and boarders
each form a line at the door. Whenever the door frees, a priority rule picks the side.
  alight_first   alighters first, then boarders
  simultaneous   either side, chosen at random each time (no convention)
A passage takes PASS_S on average (normal, sd 0.2 s). When the direction through the door
changes, SWITCH_S is added: two people meeting in the doorway sort themselves out.
PASS_S and SWITCH_S are ASSUMED INPUTS, not results: in a discrete model the cost of the
conflict has to be given; it cannot emerge from motion as in JuPedSim's trial 2.

Usage: python mesa_trial2_door.py
"""
import statistics

import mesa

PASS_S = 1.0
SWITCH_S = 1.5
N = 8


class Door(mesa.Model):
    def __init__(self, seed, policy):
        super().__init__(rng=seed)   # `seed=` is deprecated in 3.5.1 (FutureWarning)
        self.policy = policy
        self.lines = {"out": list(range(N)), "in": list(range(N))}
        self.last_dir, self.done_at = None, None
        self.schedule_event(self.free, at=0.0001)

    def priority(self):
        sides = [s for s in ("out", "in") if self.lines[s]]
        if self.policy == "alight_first" or len(sides) == 1:
            return sides[0]
        return sides[int(self.rng.integers(0, 2))]

    def free(self):
        if not (self.lines["out"] or self.lines["in"]):
            self.done_at = self.time
            return
        side = self.priority()
        self.lines[side].pop(0)
        dur = max(0.3, float(self.rng.normal(PASS_S, 0.2)))
        if self.last_dir is not None and side != self.last_dir:
            dur += SWITCH_S
        self.last_dir = side
        self.schedule_event(self.free, after=dur)


if __name__ == "__main__":
    for policy in ("alight_first", "simultaneous"):
        times = []
        for seed in range(30):
            m = Door(seed, policy)
            m.run_until(200)
            times.append(m.done_at)
        print(f"{policy:13s}: all through in {statistics.median(times):.2f} s median "
              f"(min {min(times):.2f}, max {max(times):.2f}; 30 seeds)")
