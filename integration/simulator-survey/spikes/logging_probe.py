"""What logging each simulator offers out of the box (issue #40). Throwaway.

JuPedSim: SqliteTrajectoryWriter -> list its tables and columns, and the frames written.
Mesa: DataCollector -> model- and agent-level reporters as pandas DataFrames.

Usage: python logging_probe.py <output-dir>   (the SQLite file is written there)
"""
import pathlib
import sqlite3
import sys

import jupedsim as jps
import mesa
import shapely

out = pathlib.Path(sys.argv[1]) / "probe_trajectory.sqlite"
out.unlink(missing_ok=True)
writer = jps.SqliteTrajectoryWriter(output_file=out, every_nth_frame=10)
sim = jps.Simulation(model=jps.CollisionFreeSpeedModel(), geometry=shapely.box(0, 0, 10, 4),
                     trajectory_writer=writer)
ex = sim.add_exit_stage(shapely.box(9, 0, 10, 4))
j = sim.add_journey(jps.JourneyDescription([ex]))
for k in range(5):
    sim.add_agent(jps.CollisionFreeSpeedModelAgentParameters(position=(1, 0.6 + 0.7 * k),
                                                             journey_id=j, stage_id=ex))
sim.iterate(200)
# Without this the 20 frames are lost: the writer commits every 100 writes by default
# (commit_every_nth_write) and nothing flushes it at exit (first run: 0 rows).
writer.close()
con = sqlite3.connect(out)
for (name,) in con.execute("select name from sqlite_master where type='table'"):
    cols = [r[1] for r in con.execute(f"pragma table_info({name})")]
    n = con.execute(f"select count(*) from {name}").fetchone()[0]
    print(f"jupedsim sqlite table {name}: {n} rows, columns {cols}")
con.close()


class M(mesa.Model):
    def __init__(self):
        super().__init__(rng=1)
        self.line = [mesa.Agent(self) for _ in range(5)]
        self.dc = mesa.DataCollector(model_reporters={"line_length": lambda m: len(m.line)},
                                     agent_reporters={"place": lambda a: a.model.line.index(a)
                                                      if a in a.model.line else None})

    def step(self):
        self.dc.collect(self)
        if self.line:
            self.line.pop(0).remove()


m = M()
m.run_for(3)
print("mesa model vars:\n", m.dc.get_model_vars_dataframe())
print("mesa agent vars:\n", m.dc.get_agent_vars_dataframe().head(8))
print("mesa logging module:", [n for n in dir(mesa.mesa_logging) if not n.startswith("_")][:12])
