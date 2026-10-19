"""JuPedSim trial 4: time per iteration at 1,000 and 10,000 agents (issue #40). Throwaway.

A plain corridor, 30 m wide, agents on a 1.4 m grid (about 0.5 per m^2), all walking to
an exit at the far end; the corridor's length grows with N so the density is the same.
Collision-free speed model, dt = 0.01 s. Per repetition (a fresh Simulation each time):
  - 10 warm-up iterations, then 100 timed iterations (= 1 simulated second);
  - then 10 iterations each followed by a perception pass in Python (read every agent's
    position), timed separately, to show the cost of the perception adapter.
Prints wall-clock start and end so the System log can be checked for sleep (Kernel-Power
506/507) in between.

Variant "bidir": closer to negsim's benchmark (llm_negotiation/README.md, benchmark section):
1.0 m grid (about 1 per m^2), and alternate columns walk to the opposite end, so two
crowds meet. Not the same scene as negsim's; the same density and a two-way flow.

Usage: python jps_trial4_scale.py [reps] [plain|bidir]
"""
import datetime
import statistics
import sys
import time

import jupedsim as jps
import shapely

DT = 0.01
SPACING = 1.4
ROWS = 20


def one(n, variant):
    spacing = 1.0 if variant == "bidir" else SPACING
    cols = -(-n // ROWS)
    length = cols * spacing + 10.0
    sim = jps.Simulation(model=jps.CollisionFreeSpeedModel(),
                         geometry=shapely.box(0, 0, length, 30), dt=DT)
    ex = sim.add_exit_stage(shapely.box(length - 1, 0, length, 30))
    j = sim.add_journey(jps.JourneyDescription([ex]))
    ex2 = sim.add_exit_stage(shapely.box(0, 0, 1, 30))
    j2 = sim.add_journey(jps.JourneyDescription([ex2]))
    for k in range(n):
        back = variant == "bidir" and (k // ROWS) % 2 == 1
        sim.add_agent(jps.CollisionFreeSpeedModelAgentParameters(
            position=(2.0 + spacing * (k // ROWS), 1.5 + spacing * (k % ROWS)),
            journey_id=j2 if back else j, stage_id=ex2 if back else ex))
    sim.iterate(10)
    t0 = time.perf_counter()
    sim.iterate(100)
    t_iter = (time.perf_counter() - t0) / 100
    t_perc = 0.0
    for _ in range(10):
        sim.iterate()
        t1 = time.perf_counter()
        snapshot = [(a.id, a.position) for a in sim.agents()]
        t_perc += time.perf_counter() - t1
    assert len(snapshot) == n
    return t_iter, t_perc / 10


if __name__ == "__main__":
    reps = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    variant = sys.argv[2] if len(sys.argv) > 2 else "plain"
    print("variant", variant)
    print("start", datetime.datetime.now().isoformat(timespec="seconds"))
    for n in (1000, 10000):
        rows = [one(n, variant) for _ in range(reps)]
        it = [r[0] for r in rows]
        pc = [r[1] for r in rows]
        print(f"N={n:>5}: iterate {statistics.median(it) * 1e3:7.2f} ms/iter "
              f"(min {min(it) * 1e3:.2f}, max {max(it) * 1e3:.2f}; reps {reps}) "
              f"= {statistics.median(it) * 100:.3f} s per simulated second; "
              f"perception pass {statistics.median(pc) * 1e3:.2f} ms")
    print("end", datetime.datetime.now().isoformat(timespec="seconds"))
