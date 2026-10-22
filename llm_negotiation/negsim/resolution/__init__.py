"""Step 1 of track #55: LLM agents resolve a conflict (``docs/resolution.md``).

- :mod:`.view`: the ``View``, everything one agent is told at one decision point (D2);
- :mod:`.scenario`: the scenario interface, description side (D16); the plug-ins are in
  :mod:`.scenarios`;
- :mod:`.prompt`: the core template ``resolve_v1`` and the debrief ``resolve_debrief_v1``,
  rendered into messages (D2, D3, D8);
- :mod:`.adapter`: the opening view of a frozen two-person case (RF-17 builds views from the
  simulation);
- :mod:`.reply`: reading a reply (D1) and a debrief (D8);
- :mod:`.mock`: mock-client policies for every path.
"""
