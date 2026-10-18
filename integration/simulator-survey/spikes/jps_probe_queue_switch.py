"""Probe (issue #40): does switch_agent_journey take an agent out of a queue's enqueued() list?"""
import jupedsim as jps
import shapely

slots = [(2.0 + 0.8 * i, 3.0) for i in range(8)]
sim = jps.Simulation(model=jps.CollisionFreeSpeedModel(),
                     geometry=shapely.Polygon([(0, 0), (20, 0), (20, 8), (0, 8)]))
qid = sim.add_queue_stage(slots)
q = sim.get_stage(qid)
eid = sim.add_exit_stage(shapely.Polygon([(0, 2), (1, 2), (1, 4), (0, 4)]))
jd = jps.JourneyDescription([qid, eid])
jd.set_transition_for_stage(qid, jps.Transition.create_fixed_transition(eid))
qj = sim.add_journey(jd)
sid = sim.add_direct_steering_stage()
sj = sim.add_journey(jps.JourneyDescription([sid]))
ids = [sim.add_agent(jps.CollisionFreeSpeedModelAgentParameters(
    position=slots[i], journey_id=qj, stage_id=qid)) for i in range(5)]
sim.iterate(100)
print("before switch      ", q.enqueued(), "targeting", q.count_targeting())
sim.switch_agent_journey(ids[2], sj, sid)
sim.agent(ids[2]).target = (slots[2][0], 5.0)
print("right after switch ", q.enqueued(), "journey of id", ids[2], "=", sim.agent(ids[2]).journey_id)
sim.iterate(1)
print("after 1 iteration  ", q.enqueued(), "targeting", q.count_targeting())
sim.iterate(500)
print("after 5 s          ", q.enqueued(), "pos", tuple(round(c, 2) for c in sim.agent(ids[2]).position))
q.pop(1)
sim.iterate(500)
print("after pop + 5 s    ", q.enqueued(), "agents left", sim.agent_count())
