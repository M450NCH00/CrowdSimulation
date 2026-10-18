"""JuPedSim trial 1, route "own queue" (issue #40). Throwaway spike code.

The built-in NotifiableQueueStage cannot insert part-way, and keeps agents listed after
they leave (see jps_probe_queue_switch.py). Here the queue ORDER lives in a Python list
that this script owns, and JuPedSim only moves people: every queuer is on a direct-
steering journey and is steered to the slot of its index in the list. Serving = pop the
head and switch it to an exit journey. Admit = list.insert; refuse = list.append.

Usage: python jps_trial1_ownqueue.py [admit|refuse]
"""
import sys

import jupedsim as jps
import shapely

DT = 0.01
SERVICE_S = 10.0
NEWCOMER_AT_S = 30.0
END_S = 80.0
slots = [(2.0 + 0.8 * i, 3.0) for i in range(14)]


def run(decision):
    sim = jps.Simulation(model=jps.CollisionFreeSpeedModel(),
                         geometry=shapely.Polygon([(0, 0), (20, 0), (20, 8), (0, 8)]), dt=DT)
    steer_id = sim.add_direct_steering_stage()
    steer_journey = sim.add_journey(jps.JourneyDescription([steer_id]))
    exit_id = sim.add_exit_stage(shapely.Polygon([(0, 2), (1, 2), (1, 4), (0, 4)]))
    exit_journey = sim.add_journey(jps.JourneyDescription([exit_id]))

    def spawn(pos):
        return sim.add_agent(jps.CollisionFreeSpeedModelAgentParameters(
            position=pos, journey_id=steer_journey, stage_id=steer_id))

    line = [spawn(slots[i]) for i in range(10)]          # the queue, head first
    names = {aid: f"P{i + 1}" for i, aid in enumerate(line)}
    newcomer, next_service = None, SERVICE_S
    while sim.elapsed_time() < END_S - 1e-9:
        t = sim.elapsed_time()
        if t >= next_service - 1e-9 and line:
            head = line.pop(0)
            sim.switch_agent_journey(head, exit_journey, exit_id)
            if head == newcomer:
                print(round(t, 2), "newcomer served")
            next_service += SERVICE_S
        if newcomer is None and t >= NEWCOMER_AT_S - 1e-9:
            newcomer = spawn((slots[2][0], 5.0))
            names[newcomer] = "NEW"
            print(t, "newcomer arrives; line", [names[a] for a in line])
            # --- the decision point an action adapter would fill ---
            if decision == "admit":
                line.insert(2, newcomer)
            else:
                line.append(newcomer)
        for i, aid in enumerate(line):                     # perception -> action, every step
            sim.agent(aid).target = slots[i]
        sim.iterate()
        if sim.iteration_count() % 1000 == 0:
            print(round(sim.elapsed_time(), 1), [names[a] for a in line])
    if newcomer in line:
        p = sim.agent(newcomer).position
        print("newcomer final position", tuple(round(c, 2) for c in p), "index", line.index(newcomer))


if __name__ == "__main__":
    run(sys.argv[1] if len(sys.argv) > 1 else "admit")
