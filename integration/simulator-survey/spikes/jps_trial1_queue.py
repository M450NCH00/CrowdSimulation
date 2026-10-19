"""JuPedSim trial 1: a queue with a newcomer (issue #40). Throwaway spike code.

Ten people queue at a counter that serves one at a time (one pop every SERVICE_S).
At 30 s a newcomer arrives beside position 3 and tries to join ahead of it.
Three ways to resolve the attempt are tried, one per run:

  steer   - the newcomer walks to the gap ahead of position 3 under direct steering,
            without the queue knowing (what "cutting in" looks like physically)
  refuse  - the newcomer is switched into the queue journey: JuPedSim sends them to
            the first free slot, i.e. the back
  admit   - the queue is rebuilt so the newcomer becomes position 3: positions >= 3
            step back one slot under direct steering, the newcomer joins, then they
            rejoin the queue in their old order

Usage: python jps_trial1_queue.py [steer|refuse|admit]
"""
import sys

import jupedsim as jps
import shapely

DT = 0.01
SERVICE_S = 10.0          # one person served every 10 s
NEWCOMER_AT_S = 30.0
END_S = 80.0
SLOT = 0.8                # spacing of waiting positions (m)
N_QUEUE = 10
N_SLOTS = 14

slots = [(2.0 + SLOT * i, 3.0) for i in range(N_SLOTS)]   # slots[0] is the head
area = shapely.Polygon([(0, 0), (20, 0), (20, 8), (0, 8)])
exit_poly = shapely.Polygon([(0, 2), (1, 2), (1, 4), (0, 4)])


def run(mode):
    sim = jps.Simulation(model=jps.CollisionFreeSpeedModel(), geometry=area, dt=DT)
    queue_id = sim.add_queue_stage(slots)
    queue = sim.get_stage(queue_id)
    exit_id = sim.add_exit_stage(exit_poly)
    jq = jps.JourneyDescription([queue_id, exit_id])
    jq.set_transition_for_stage(queue_id, jps.Transition.create_fixed_transition(exit_id))
    queue_journey = sim.add_journey(jq)
    steer_id = sim.add_direct_steering_stage()
    steer_journey = sim.add_journey(jps.JourneyDescription([steer_id]))

    names = {}
    for i in range(N_QUEUE):   # spawn each person on their own slot, head first
        aid = sim.add_agent(jps.CollisionFreeSpeedModelAgentParameters(
            position=slots[i], journey_id=queue_journey, stage_id=queue_id))
        names[aid] = f"P{i + 1}"

    newcomer = None
    rebuild = None            # state of the admit choreography
    next_service = SERVICE_S
    log = []

    while sim.elapsed_time() < END_S - 1e-9:
        t = sim.elapsed_time()
        if t >= next_service - 1e-9:
            queue.pop(1)
            next_service += SERVICE_S
        if newcomer is None and t >= NEWCOMER_AT_S - 1e-9:
            order = queue.enqueued()
            gap = ((slots[1][0] + slots[2][0]) / 2, 3.0)
            if mode == "steer":
                newcomer = sim.add_agent(jps.CollisionFreeSpeedModelAgentParameters(
                    position=(slots[2][0], 5.0), journey_id=steer_journey, stage_id=steer_id))
                sim.agent(newcomer).target = gap
            elif mode == "refuse":
                newcomer = sim.add_agent(jps.CollisionFreeSpeedModelAgentParameters(
                    position=(slots[2][0], 5.0), journey_id=queue_journey, stage_id=queue_id))
            elif mode == "admit_readd":
                # Remove positions >= 3 and add them back after the newcomer, so the
                # queue enqueues them in add order. Their ids change.
                behind = order[2:]
                kept = [(names[a], sim.agent(a).position) for a in behind]
                for aid in behind:
                    sim.mark_agent_for_removal(aid)
                sim.iterate()                        # removal happens at the next iterate
                newcomer = sim.add_agent(jps.CollisionFreeSpeedModelAgentParameters(
                    position=(slots[2][0], 5.0), journey_id=queue_journey, stage_id=queue_id))
                for name, pos in kept:
                    aid = sim.add_agent(jps.CollisionFreeSpeedModelAgentParameters(
                        position=pos, journey_id=queue_journey, stage_id=queue_id))
                    names[aid] = name
            elif mode == "admit":
                newcomer = sim.add_agent(jps.CollisionFreeSpeedModelAgentParameters(
                    position=(slots[2][0], 5.0), journey_id=steer_journey, stage_id=steer_id))
                behind = order[2:]               # position 3 onwards step back one slot
                for k, aid in enumerate(behind):
                    sim.switch_agent_journey(aid, steer_journey, steer_id)
                    sim.agent(aid).target = slots[k + 3]
                sim.agent(newcomer).target = slots[2]
                rebuild = {"behind": behind, "phase": "make_gap", "t0": t}
            names[newcomer] = "NEW"
            log.append((round(t, 2), "newcomer arrives; queue", [names[a] for a in order]))
        if rebuild and rebuild["phase"] == "make_gap" and t - rebuild["t0"] >= 3.0:
            # Gap made: the newcomer joins first, then the rest in their old order.
            # First attempt switched all of them in one go: JuPedSim did NOT enqueue
            # them in switch order and the newcomer ended at the back (see work log).
            # So rejoin one at a time, each only once the previous one is enqueued.
            rebuild["pending"] = [newcomer] + rebuild["behind"]
            rebuild["phase"] = "rejoining"
            rebuild["current"] = None
        if rebuild and rebuild["phase"] == "rejoining":
            cur = rebuild["current"]
            if cur is None or cur in queue.enqueued():
                if rebuild["pending"]:
                    rebuild["current"] = rebuild["pending"].pop(0)
                    sim.switch_agent_journey(rebuild["current"], queue_journey, queue_id)
                else:
                    rebuild["phase"] = "done"
                    log.append((round(t, 2), "rebuild done; queue",
                                [names[a] for a in queue.enqueued()]))
        sim.iterate()
        if sim.iteration_count() % 500 == 0:   # every 5 s
            log.append((round(sim.elapsed_time(), 2), "queue",
                        [names[a] for a in queue.enqueued()]))

    for row in log:
        print(*row)
    if newcomer is not None and newcomer in [a.id for a in sim.agents()]:
        p = sim.agent(newcomer).position
        print("newcomer final position", tuple(round(c, 2) for c in p))


if __name__ == "__main__":
    run(sys.argv[1] if len(sys.argv) > 1 else "refuse")
