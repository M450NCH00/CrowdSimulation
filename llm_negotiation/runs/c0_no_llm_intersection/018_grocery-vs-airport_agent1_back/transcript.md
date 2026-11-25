# Transcript: 018_grocery-vs-airport_agent1_back

- Experiment: `c0_no_llm_intersection`, condition C0
- Scenario: intersection (variant `agent1_back`)
- Seed: 24118; repeat 1
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
| task | go grocery shopping | catch a flight |
| task type | grocery | airport |
| maximum speed (m/s) | 0.3 | 0.3 |
| body width (m) | 0.2 | 0.2 |

## Outcome

- Run status: **completed**
- Went through first: agent 0; followed: agent 1
- Collisions: agent-agent 0, agent-wall 0; deadlock: no
- Time to goal: agent 0 9.8 s, agent 1 11.4 s; makespan 11.4 s
- Follower's lowest speed before the conflict region: 0.2667 m/s
- Mean deviation from the desired paths: 0 m
- Ground truth (hospital > airport > grocery): higher-priority agent is agent 1; it went first: no
