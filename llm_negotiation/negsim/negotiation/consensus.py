"""Consensus: complementary stances on two consecutive turns.

The two agents have agreed when one says it will go first and the other, on the very next
or the very previous turn, says the first one should. The agreed leader is the agent whose
stance is ``I_GO_FIRST``.
"""

from __future__ import annotations

from typing import Optional, Sequence

from .parsing import Stance

SpeakerStance = tuple[int, Stance]


def agreed_leader(previous: SpeakerStance, current: SpeakerStance) -> Optional[int]:
    """The agent both turns agree should go first, or ``None`` if they do not agree."""
    (speaker_a, stance_a), (speaker_b, stance_b) = previous, current
    if speaker_a == speaker_b:
        return None
    if stance_a is Stance.I_GO_FIRST and stance_b is Stance.YOU_GO_FIRST:
        return speaker_a
    if stance_a is Stance.YOU_GO_FIRST and stance_b is Stance.I_GO_FIRST:
        return speaker_b
    return None


def find_consensus(turns: Sequence[SpeakerStance]) -> Optional[tuple[int, int]]:
    """First consensus in a sequence of turns, as ``(leader_id, index of the closing turn)``."""
    for index in range(1, len(turns)):
        leader = agreed_leader(turns[index - 1], turns[index])
        if leader is not None:
            return leader, index
    return None
