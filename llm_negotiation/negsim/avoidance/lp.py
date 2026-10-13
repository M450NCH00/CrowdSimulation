# This file is adapted from the RVO2 Library:
#
#     src/Agent.cc, functions linearProgram1, linearProgram2 and linearProgram3
#     https://github.com/snape/RVO2, commit 75822bba14462c2e872ca96423825017ecd24764
#
#     SPDX-FileCopyrightText: 2008 University of North Carolina at Chapel Hill
#     SPDX-License-Identifier: Apache-2.0
#
#     Licensed under the Apache License, Version 2.0 (the "License");
#     you may not use this file except in compliance with the License.
#     You may obtain a copy of the License at
#
#         https://www.apache.org/licenses/LICENSE-2.0
#
#     Unless required by applicable law or agreed to in writing, software
#     distributed under the License is distributed on an "AS IS" BASIS,
#     WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#     See the License for the specific language governing permissions and
#     limitations under the License.
#
# Changes made for this project (2026-10-13, issue #26): translated from C++ to Python;
# lines are plain tuples instead of a Line class; double precision, with the parallel-line
# tolerance tightened to match; the solvers return their result instead of writing through
# a reference; a single entry point, solve(), reports whether the fallback was used;
# zero-length vectors are guarded where the original divides; and one tie is resolved
# differently. When the direction being optimised is exactly perpendicular to a line, every
# point of the line is equally good. The original then returns the line's left end, which
# is a velocity at the maximum speed; this version returns the slowest of those equally
# good velocities (see _linear_program_1). The optimum's value is the same.
# A copy of the licence is in llm_negotiation/LICENSES/Apache-2.0.txt; see also
# llm_negotiation/THIRD_PARTY_NOTICES.md.
"""ORCA's linear programs: the velocity nearest the preferred one that every half-plane allows.

A constraint is a directed line ``(px, py, dx, dy)``: a point on the line and a unit
direction. The velocities it allows are those on the line or to its **left**. The first
``n_hard`` lines given to :func:`solve` are the walls' and are never relaxed.

``linear_program_2`` is the paper's program (van den Berg et al., "Reciprocal n-body
collision avoidance", Sec 5.1, eqs. 7 and 8): minimise the distance to the preferred
velocity inside the disc of the maximum speed and all the half-planes, adding the
half-planes one at a time. ``linear_program_3`` is the fallback of Sec 5.3 for when no
velocity satisfies them all: it finds the velocity that least violates the worst-violated
agent half-plane (eq. 10), still inside every wall half-plane ("the constraints of the
obstacles are not relaxed", Sec 5.4).
"""

from __future__ import annotations

import math
from typing import NamedTuple, Optional, Sequence

Line = tuple[float, float, float, float]
Vec = tuple[float, float]

#: Two unit directions whose cross product is no larger than this are treated as parallel.
#: RVO2 uses 1e-5 in single precision (``Vector2.cc:45``); this is its double-precision
#: counterpart.
PARALLEL_EPS = 1e-9
#: A direction objective whose component along a line is no larger than this has no
#: preference between the points of that line.
NO_PREFERENCE_EPS = 1e-12


class LPResult(NamedTuple):
    velocity: Vec
    #: True if a velocity satisfying every half-plane exists and was returned.
    feasible: bool
    #: Index of the first half-plane that could not be satisfied; ``None`` if feasible.
    failed_line: Optional[int]


def _linear_program_1(
    lines: Sequence[Line], line_no: int, radius: float, opt: Vec, direction_opt: bool
) -> Optional[Vec]:
    """Optimise along line ``line_no`` subject to the lines before it and the speed disc.

    Returns ``None`` if no point of the line satisfies them.
    """
    px, py, dx, dy = lines[line_no]
    dot = px * dx + py * dy
    discriminant = dot * dot + radius * radius - (px * px + py * py)
    if discriminant < 0.0:
        return None  # the line misses the disc of the maximum speed
    root = math.sqrt(discriminant)
    t_left, t_right = -dot - root, -dot + root

    for i in range(line_no):
        qx, qy, ex, ey = lines[i]
        denominator = dx * ey - dy * ex
        numerator = ex * (py - qy) - ey * (px - qx)
        if abs(denominator) <= PARALLEL_EPS:
            if numerator < 0.0:
                return None  # parallel, and this line lies wholly outside line i
            continue
        t = numerator / denominator
        if denominator >= 0.0:
            t_right = min(t_right, t)
        else:
            t_left = max(t_left, t)
        if t_left > t_right:
            return None

    if direction_opt:
        along = opt[0] * dx + opt[1] * dy
        if along > NO_PREFERENCE_EPS:
            t = t_right
        elif along < -NO_PREFERENCE_EPS:
            t = t_left
        else:
            # Every allowed point of the line is equally far in the direction asked for.
            # Take the slowest: the one nearest the origin of velocity space.
            t = t_left if -dot < t_left else t_right if -dot > t_right else -dot
    else:
        t = dx * (opt[0] - px) + dy * (opt[1] - py)
        t = t_left if t < t_left else t_right if t > t_right else t
    return (px + t * dx, py + t * dy)


def linear_program_2(
    lines: Sequence[Line], radius: float, opt: Vec, direction_opt: bool = False
) -> tuple[int, Vec]:
    """The two-dimensional program. Returns ``(index of the failing line, result)``.

    The index equals ``len(lines)`` on success. With ``direction_opt`` the objective is to
    go as far as possible in the unit direction ``opt`` instead of as near as possible to
    the point ``opt``; the fallback uses that form.
    """
    ox, oy = opt
    if direction_opt:
        result = (ox * radius, oy * radius)
    elif ox * ox + oy * oy > radius * radius:
        length = math.hypot(ox, oy)
        result = (ox / length * radius, oy / length * radius)
    else:
        result = (ox, oy)

    for i, (px, py, dx, dy) in enumerate(lines):
        if dx * (py - result[1]) - dy * (px - result[0]) > 0.0:
            # The current optimum is on the wrong side of line i; the new one lies on it.
            found = _linear_program_1(lines, i, radius, opt, direction_opt)
            if found is None:
                return i, result
            result = found
    return len(lines), result


def linear_program_3(
    lines: Sequence[Line], n_hard: int, begin: int, radius: float, result: Vec
) -> Vec:
    """The fallback: minimise the largest violation of the lines from ``n_hard`` on.

    ``result`` is where the two-dimensional program stopped, and ``begin`` the line it
    stopped at. The first ``n_hard`` lines stay hard.
    """
    distance = 0.0
    for i in range(begin, len(lines)):
        px, py, dx, dy = lines[i]
        if dx * (py - result[1]) - dy * (px - result[0]) > distance:
            # result violates line i by more than the current worst: re-optimise on the
            # locus where the violation of line i equals that of each earlier line.
            projected: list[Line] = list(lines[:n_hard])
            for j in range(n_hard, i):
                qx, qy, ex, ey = lines[j]
                determinant = dx * ey - dy * ex
                if abs(determinant) <= PARALLEL_EPS:
                    if dx * ex + dy * ey > 0.0:
                        continue  # same direction: line i is the tighter one already
                    point = (0.5 * (px + qx), 0.5 * (py + qy))
                else:
                    t = (ex * (py - qy) - ey * (px - qx)) / determinant
                    point = (px + t * dx, py + t * dy)
                bx, by = ex - dx, ey - dy
                length = math.hypot(bx, by)
                if length == 0.0:
                    continue
                projected.append((point[0], point[1], bx / length, by / length))

            previous = result
            failed, result = linear_program_2(projected, radius, (-dy, dx), True)
            if failed < len(projected):
                # In principle this cannot happen: the previous result is feasible for
                # this program by construction. If rounding makes it fail, keep it.
                result = previous
            distance = dx * (py - result[1]) - dy * (px - result[0])
    return result


def solve(lines: Sequence[Line], n_hard: int, max_speed: float, preferred: Vec) -> LPResult:
    """New velocity for one agent.

    ``lines[:n_hard]`` are wall half-planes and ``lines[n_hard:]`` agent half-planes.
    If every half-plane can be satisfied the result is the allowed velocity nearest
    ``preferred`` and ``feasible`` is true. Otherwise the fallback is used: the result
    satisfies the walls and violates the agents' half-planes as little as possible, and
    it does not depend on ``preferred``.
    """
    failed, velocity = linear_program_2(lines, max_speed, preferred)
    if failed == len(lines):
        return LPResult(velocity, True, None)
    return LPResult(linear_program_3(lines, n_hard, failed, max_speed, velocity), False, failed)


def violation(line: Line, velocity: Vec) -> float:
    """How far ``velocity`` is on the forbidden side of ``line``; zero or less if allowed."""
    px, py, dx, dy = line
    return dx * (py - velocity[1]) - dy * (px - velocity[0])
