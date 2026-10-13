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

## Python packages

Used, not redistributed: PyYAML (MIT), matplotlib (matplotlib licence, optional), pytest
(MIT, tests only). Versions are pinned in `requirements.txt`.
