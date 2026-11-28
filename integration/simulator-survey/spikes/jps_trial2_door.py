"""JuPedSim trial 2: a bus or train door (issue #40). Throwaway spike code.

A platform (y 0..6) and a vehicle interior (y 7..10) joined by one 1.0 m door opening.
At ARRIVE_S the vehicle "arrives": alighters appear inside it, heading for the platform exit.
Boarders wait on the platform in a waiting set and, once the set is released, walk into
the vehicle (an exit stage at its back wall = "seated").

Policies:
  alight_first  boarders wait beside the door; released once nobody is left inside
  simultaneous  boarders wait beside the door; released when the vehicle arrives
  crowd_front   boarders wait IN FRONT of the door; released when the vehicle arrives

Usage: python jps_trial2_door.py <policy> [cfs|sfm]
Prints whether everyone got through, the time it took, and whether progress stalled
(no agent moved more than 0.05 m in STALL_S seconds) - a deadlock.
"""
import math
import sys

import jupedsim as jps
import shapely

DT = 0.01
ARRIVE_S = 2.0
END_S = 120.0
STALL_S = 10.0
N_BOARD, N_ALIGHT = 8, 8

platform = shapely.box(0, 0, 20, 6)
door = shapely.box(9.5, 6, 10.5, 7)
vehicle = shapely.box(6, 7, 14, 10)
area = shapely.union_all([platform, door, vehicle])


def run(policy, model_name):
    if model_name == "sfm":
        model = jps.SocialForceModel()
        params = lambda pos, j, s: jps.SocialForceModelAgentParameters(
            position=pos, journey_id=j, stage_id=s, desired_speed=1.2, radius=0.2)
    else:
        model = jps.CollisionFreeSpeedModel()
        params = lambda pos, j, s: jps.CollisionFreeSpeedModelAgentParameters(
            position=pos, journey_id=j, stage_id=s, desired_speed=1.2, radius=0.2)
    sim = jps.Simulation(model=model, geometry=area, dt=DT)

    if policy == "crowd_front":
        waits = [(9.6 + 0.8 * (i % 2), 5.3 - 0.8 * (i // 2)) for i in range(N_BOARD)]
    else:   # four each side of the door, leaving it clear
        waits = [(8.8 - 0.8 * (i // 2), 5.3 - 0.8 * (i % 2)) for i in range(4)] + \
                [(11.2 + 0.8 * (i // 2), 5.3 - 0.8 * (i % 2)) for i in range(4)]
    wait_id = sim.add_waiting_set_stage(waits)
    wait = sim.get_stage(wait_id)
    seat_id = sim.add_exit_stage(shapely.box(6, 9.5, 14, 10))
    jb = jps.JourneyDescription([wait_id, seat_id])
    jb.set_transition_for_stage(wait_id, jps.Transition.create_fixed_transition(seat_id))
    board_journey = sim.add_journey(jb)
    out_id = sim.add_exit_stage(shapely.box(0, 0, 1, 6))
    alight_journey = sim.add_journey(jps.JourneyDescription([out_id]))

    boarders = [sim.add_agent(params(p, board_journey, wait_id)) for p in waits]
    alighters = []
    released = False
    last_pos, last_move_t = {}, 0.0
    done_t = None
    while sim.elapsed_time() < END_S - 1e-9:
        t = sim.elapsed_time()
        if not alighters and t >= ARRIVE_S - 1e-9:
            alighters = [sim.add_agent(params((7.0 + 0.8 * i, 8.5 if i % 2 else 8.0),
                                              alight_journey, out_id)) for i in range(N_ALIGHT)]
        if alighters and not released:
            inside = [a for a in sim.agents() if a.id in alighters and a.position[1] > 6.0]
            if policy != "alight_first" or not inside:
                wait.state = jps.WaitingSetState.INACTIVE
                released = True
                print(f"{policy}/{model_name}: boarders released at {t:.2f} s")
        sim.iterate()
        pos = {a.id: a.position for a in sim.agents()}
        if any(math.dist(p, last_pos.get(i, (1e9, 1e9))) > 0.05 for i, p in pos.items()):
            last_pos, last_move_t = pos, sim.elapsed_time()
        if alighters and sim.agent_count() == 0:
            done_t = sim.elapsed_time()
            break
        if sim.elapsed_time() - last_move_t > STALL_S:
            break
    left = sim.agent_count()
    stuck = [(a.id in boarders and "boarder" or "alighter",
              tuple(round(c, 2) for c in a.position)) for a in sim.agents()]
    print(f"{policy}/{model_name}: all through = {left == 0}, "
          f"time = {done_t if done_t is None else round(done_t - ARRIVE_S, 2)} s after arrival, "
          f"stalled = {left > 0 and sim.elapsed_time() < END_S - 1e-9}, left = {left}")
    if stuck:
        print("   remaining:", stuck[:6])


if __name__ == "__main__":
    run(sys.argv[1] if len(sys.argv) > 1 else "simultaneous",
        sys.argv[2] if len(sys.argv) > 2 else "cfs")
