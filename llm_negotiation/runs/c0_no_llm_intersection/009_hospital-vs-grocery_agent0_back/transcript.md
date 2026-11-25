# Transcript: 009_hospital-vs-grocery_agent0_back

- Experiment: `c0_no_llm_intersection`, condition C0
- Scenario: intersection (variant `agent0_back`)
- Seed: 24109; repeat 1
- Code: commit `50123f6d2e2387a3a89d328858510088af4b59fb`
- Negotiation: disabled (Strategy 1 only)

## Participants

| | agent 0 | agent 1 |
|---|---|---|
| starts | south | west |
| persona |  |  |
| age |  |  |
| gender |  |  |
| backstory |  |  |
| task | the emergency room | go grocery shopping |
| task type | hospital | grocery |
| maximum speed (m/s) | 0.3 | 0.3 |
| body width (m) | 0.2 | 0.2 |

## Outcome

- Run status: **completed**
- Went through first: agent 1; followed: agent 0
- Collisions: agent-agent 0, agent-wall 0; deadlock: no
- Time to goal: agent 0 11.4 s, agent 1 9.8 s; makespan 11.4 s
- Follower's lowest speed before the conflict region: 0.2667 m/s
- Mean deviation from the desired paths: 0 m
- Ground truth (hospital > airport > grocery): higher-priority agent is agent 0; it went first: no
