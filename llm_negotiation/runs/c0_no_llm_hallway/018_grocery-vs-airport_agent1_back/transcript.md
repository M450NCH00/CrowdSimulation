# Transcript: 018_grocery-vs-airport_agent1_back

- Experiment: `c0_no_llm_hallway`, condition C0
- Scenario: hallway (variant `agent1_back`)
- Seed: 24218; repeat 1
- Code: commit `50123f6d2e2387a3a89d328858510088af4b59fb`
- Negotiation: disabled (Strategy 1 only)

## Participants

| | agent 0 | agent 1 |
|---|---|---|
| starts | west | east |
| persona |  |  |
| age |  |  |
| gender |  |  |
| backstory |  |  |
| task | go grocery shopping | reach the airport |
| task type | grocery | airport |
| maximum speed (m/s) | 1.3 | 1.3 |
| body width (m) | 0.5 | 0.5 |

## Outcome

- Run status: **completed**
- Went through first: agent 0; followed: agent 1
- Collisions: agent-agent 0, agent-wall 0; deadlock: no
- Time to goal: agent 0 6.9 s, agent 1 12.6 s; makespan 12.6 s
- Follower's lowest speed before the conflict region: 0.2284 m/s
- Mean deviation from the desired paths: 0.002315 m
- Ground truth (hospital > airport > grocery): higher-priority agent is agent 1; it went first: no
