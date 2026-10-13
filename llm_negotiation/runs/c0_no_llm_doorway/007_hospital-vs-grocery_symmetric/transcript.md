# Transcript: 007_hospital-vs-grocery_symmetric

- Experiment: `c0_no_llm_doorway`, condition C0
- Scenario: doorway (variant `symmetric`)
- Seed: 24007; repeat 1
- Code: commit `50123f6d2e2387a3a89d328858510088af4b59fb`
- Negotiation: disabled (Strategy 1 only)

## Participants

| | agent 0 | agent 1 |
|---|---|---|
| starts | north | south |
| persona |  |  |
| age |  |  |
| gender |  |  |
| backstory |  |  |
| task | the hospital | the grocery store |
| task type | hospital | grocery |
| maximum speed (m/s) | 0.3 | 0.3 |
| body width (m) | 0.2 | 0.2 |

## Outcome

- Run status: **completed**
- Went through first: agent 0; followed: agent 1
- Collisions: agent-agent 0, agent-wall 0; deadlock: no
- Time to goal: agent 0 10 s, agent 1 11.8 s; makespan 11.8 s
- Follower's lowest speed before the conflict region: 0.2363 m/s
- Mean deviation from the desired paths: 0.000287 m
- Ground truth (hospital > airport > grocery): higher-priority agent is agent 0; it went first: yes
