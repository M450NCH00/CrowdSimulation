"""JuPedSim trial 3: the two adapters in miniature, plus determinism (issue #40). Throwaway.

Scene: a 30 x 6 m corridor, 40 people walking to an exit at the right end.
  Perception adapter: every iteration, read each agent's position, velocity and place in
    a queue. CFS states expose no velocity, so it is a difference of positions; with the
    social force model the state's own `velocity` is compared with that difference.
  Action adapter, at 5 s:
    A. agent 1 (exit journey): set `agent.target` -> expected "ignored" outside direct steering
    B. agent 2: switch_agent_journey to an exit at the LEFT end -> when does it turn?
    C. agent 3: model.desired_speed 1.2 -> 0.4 -> when does its speed change?
    D. agent 4 (direct-steering journey): new target -> when does it turn?
  Determinism: the same scene run twice; every position at every iteration is hashed.

Usage: python jps_trial3_adapters.py [cfs|sfm]
"""
import hashlib
import math
import struct
import sys

import jupedsim as jps
import shapely

DT = 0.01
ACT_AT = 500          # iteration of the action (5 s)
END = 1500


def build(model_name, act="ABCD"):
    sfm = model_name == "sfm"
    sim = jps.Simulation(model=jps.SocialForceModel() if sfm else jps.CollisionFreeSpeedModel(),
                         geometry=shapely.box(0, 0, 30, 6), dt=DT)
    P = jps.SocialForceModelAgentParameters if sfm else jps.CollisionFreeSpeedModelAgentParameters
    right = sim.add_exit_stage(shapely.box(29, 0, 30, 6))
    left = sim.add_exit_stage(shapely.box(0, 0, 1, 6))
    j_right = sim.add_journey(jps.JourneyDescription([right]))
    j_left = sim.add_journey(jps.JourneyDescription([left]))
    steer = sim.add_direct_steering_stage()
    j_steer = sim.add_journey(jps.JourneyDescription([steer]))
    ids = []
    for k in range(40):
        pos = (3.0 + 0.9 * (k // 5), 1.0 + 1.0 * (k % 5))
        j, s = (j_steer, steer) if k == 3 else (j_right, right)
        ids.append(sim.add_agent(P(position=pos, journey_id=j, stage_id=s, desired_speed=1.2)))
    sim.agent(ids[3]).target = (28.0, 3.0)
    h = hashlib.sha256()
    prev = {}
    probe = {name: [] for name in "ABCD"}
    vel_err = []
    while sim.iteration_count() < END and sim.agent_count():
        if sim.iteration_count() == ACT_AT:
            if "A" in act:
                sim.agent(ids[0]).target = (0.0, 0.0)
            if "B" in act:
                sim.switch_agent_journey(ids[1], j_left, left)
            if "C" in act:
                sim.agent(ids[2]).model.desired_speed = 0.4
            if "D" in act:   # turn towards the wall
                sim.agent(ids[3]).target = (sim.agent(ids[3]).position[0], 0.5)
        sim.iterate()
        # ---- perception adapter: one record per agent per iteration ----
        situation = {}
        for a in sim.agents():
            x, y = a.position
            px, py = prev.get(a.id, (x, y))
            v = ((x - px) / DT, (y - py) / DT)
            situation[a.id] = {"pos": (x, y), "vel": v, "queue_place": None}
            if sfm and a.id in prev:
                mv = a.model.velocity
                vel_err.append(math.dist(mv, v))
            # hash by spawn index, not id: ids may differ between Simulation objects
            h.update(struct.pack("<idd", ids.index(a.id), x, y))
        prev = {i: r["pos"] for i, r in situation.items()}
        n = sim.iteration_count()
        if ACT_AT - 2 <= n <= ACT_AT + 300:
            for name, aid in zip("ABCD", ids[:4]):
                if aid in situation:
                    probe[name].append((n, situation[aid]["vel"]))
    return h.hexdigest(), probe, vel_err


def report(model_name):
    digest1, p_act, vel_err = build(model_name)
    digest2, _, _ = build(model_name)
    digest_a, _, _ = build(model_name, act="A")
    digest0, _, _ = build(model_name, act="")
    print(f"[{model_name}] determinism: run1 == run2: {digest1 == digest2} ({digest1[:12]})")
    print(f"[{model_name}] A. target set on an exit-journey agent only: whole run differs from "
          f"a run with no action? {digest_a != digest0}")
    for name, what in (("B", "heading x-sign flips"), ("C", "speed < 0.6"), ("D", "vy < -0.3")):
        first = None
        for n, (vx, vy) in p_act[name]:
            if n <= ACT_AT:
                continue
            hit = {"B": vx < 0, "C": 0 < math.hypot(vx, vy) < 0.6, "D": vy < -0.3}[name]
            if hit:
                first = n
                break
        delay = None if first is None else first - ACT_AT
        print(f"[{model_name}] {name}. first iteration where {what}: +{delay} "
              f"({None if delay is None else round(delay * DT, 2)} s)")
    if vel_err:
        print(f"[{model_name}] state velocity vs difference of positions: "
              f"max |diff| = {max(vel_err):.2e} m/s over {len(vel_err)} samples")


if __name__ == "__main__":
    report(sys.argv[1] if len(sys.argv) > 1 else "cfs")
