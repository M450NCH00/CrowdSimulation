"""Step 1 of track #55: LLM agents resolve a conflict (``docs/resolution.md``).

- :mod:`.view`: the ``View``, everything one agent is told at one decision point (D2);
- :mod:`.scenario`: the scenario interface, description side (D16); the plug-ins are in
  :mod:`.scenarios`;
- :mod:`.prompt`: the core template ``resolve_v1`` and the debrief ``resolve_debrief_v1``,
  rendered into messages (D2, D3, D8);
- :mod:`.adapter`: the opening view of a frozen two-person case;
- :mod:`.perceive`: views built from the running simulation, with the view cone, occlusion,
  hearing, signals and changes since the agent last looked (RF-17, #73);
- :mod:`.reply`: reading a reply (D1) and a debrief (D8);
- :mod:`.execute`: carrying the plans out in the simulator, in ``plan_only`` and ``plan_orca``
  (RF-4, #59), and ``advance`` for the protocol;
- :mod:`.outcomes`: the physical outcome columns and the report (RF-4);
- :mod:`.replay`: a session's plans replayed on its case's own run, rebuildable from the
  session record (RF-4, D13);
- :mod:`.protocol`: one session's encounter: the trigger, event-driven decision points, the
  three conditions, the end and the hand-over to ORCA, the debrief, the record (RF-3, #58);
- :mod:`.design`, :mod:`.experiment`, :mod:`.transcript`: the experiment layer ``resolution``
  (RF-3);
- :mod:`.mock`: mock-client policies for every path, and for a whole session.
"""
