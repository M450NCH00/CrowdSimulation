# Third-party notices

## GameChat

`llm_negotiation/` reimplements the approach of

> V. Mahadevan, S. Zhang and R. Chandra, "GameChat: Multi-LLM Dialogue for Safe, Agile,
> and Socially Optimal Multi-Agent Navigation in Constrained Environments,"
> arXiv:2503.12333.

whose code is at `https://github.com/vgmahadevan/GameChat` (read at commit
`c49c35ac49f3e5f4a08b03638e943ca77763763c` of branch `main`).

**No source code from that repository was copied or adapted.** The repository was read,
not run, and everything under `negsim/` was written from the paper's description. No file
here therefore carries the repository's copyright header.

Three pieces of text are reproduced so that the paper's experiment can be replicated:

| What | Where it is here | Where it is from |
|---|---|---|
| The agents' initial prompt, one sentence removed | `negsim/negotiation/templates/gamechat_task_v1.yaml` (`system`, first paragraph) | The paper, Sec IV-C |
| The wording of the turn messages, "Other agent says: ..." and "Begin the conversation" | the same file (`turns`) | The repository, `main.py:85-92` |
| The fifteen task strings | `configs/tasks/gamechat_tasks.yaml` | The paper, Table I |

The numerical parameters of the doorway and intersection scenarios are also the paper's
and the repository's; each is attributed in `configs/scenarios/*.yaml`.

The repository is distributed under the MIT licence, with this notice:

```
MIT License

Copyright (c) 2022 Elena Oikonomou

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

The copyright line names the author of the project the GameChat repository was forked
from, not the GameChat authors; it is reproduced as it stands in the repository's
`LICENSE` file. See `docs/gamechat-notes.md`, section 2.2.

## RVO2 Library

The avoidance layer (`negsim/avoidance/`, issue #26) implements ORCA, from

> J. van den Berg, S. J. Guy, M. Lin and D. Manocha, "Reciprocal n-body collision
> avoidance", in *Robotics Research: The 14th International Symposium ISRR*, pp. 3–19,
> Springer, 2011.

whose reference implementation is the RVO2 Library, `https://github.com/snape/RVO2`, read
at commit `75822bba14462c2e872ca96423825017ecd24764` of branch `main`. The library was
read, not built, installed or run, and it is not a dependency of this project.

**One file here is adapted from it.**

| File here | Adapted from | What was changed |
|---|---|---|
| `negsim/avoidance/lp.py` | `src/Agent.cc`, the functions `linearProgram1`, `linearProgram2` and `linearProgram3` (lines 63 to 242) | Translated from C++ to Python. Lines are plain tuples instead of a `Line` class. Double precision, with the parallel-line tolerance tightened to match. The solvers return their result instead of writing through a reference. A single entry point, `solve`, reports whether the fallback was used. Zero-length vectors are guarded where the original divides. One tie is resolved differently: when the direction being optimised is exactly perpendicular to a line, the original returns the end of the line and this version returns the slowest of the equally good velocities. The algorithm is otherwise unchanged. |

That file carries the library's copyright and licence notice at its head, with the same
list of changes, as the licence requires of a modified file.

**Nothing else was copied or adapted.** The half-planes for agents and for walls
(`negsim/avoidance/orca.py`) were written from the paper and then compared with
`src/Agent.cc`; the neighbour search (`negsim/avoidance/neighbours.py`) is a grid written
for this project, where the library has a k-d tree. `docs/orca.md` says where this
implementation departs from the paper and from the library.

For checking, excerpts of the library are cached in
`refs/si1_rvo2_75822bb_excerpts.txt` at the repository root: the whole of `src/Agent.cc`
with its header, and the few lines of other files that `docs/orca.md` cites.

The library's source files are distributed under the Apache License, Version 2.0, with
this notice (from the head of `src/Agent.cc`):

```
SPDX-FileCopyrightText: 2008 University of North Carolina at Chapel Hill
SPDX-License-Identifier: Apache-2.0

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

Please send all bug reports to <geom@cs.unc.edu>.

The authors may be contacted via:

Jur van den Berg, Stephen J. Guy, Jamie Snape, Ming C. Lin, Dinesh Manocha
Dept. of Computer Science
201 S. Columbia St.
Frederick P. Brooks, Jr. Computer Science Bldg.
Chapel Hill, N.C. 27599-3175
United States of America

<https://gamma.cs.unc.edu/RVO2/>
```

A copy of the licence is in `LICENSES/Apache-2.0.txt`. The library has no `NOTICE` file.
Its README and citation file are under CC-BY-SA-4.0; nothing was taken from them.

## Menge

One file of the Menge crowd-simulation framework (`https://github.com/MengeCrowdSim/Menge`,
Apache-2.0), `examples/core/4square/4squareS.xml`, is cached unchanged as
`refs/si1_menge_4squareS.xml`. Some of the numbers in it are cited as settings used in
practice (`docs/parameters.md`). No code from Menge is used.

## Python packages

Used, not redistributed: PyYAML (MIT), matplotlib (matplotlib licence, optional), pytest
(MIT, tests only). Versions are pinned in `requirements.txt`.
