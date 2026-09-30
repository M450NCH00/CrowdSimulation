# G3 — Cheap talk: does communication change the outcome?

Prepared for issue [#20](https://github.com/M450NCH00/CrowdSimulation/issues/20).
Companion files: [`g1-conflict-games-conventions.md`](g1-conflict-games-conventions.md),
[`g2-norm-emergence.md`](g2-norm-emergence.md),
[`g4-game-theoretic-crowd-models.md`](g4-game-theoretic-crowd-models.md),
[`g5-llm-agents-game-theory.md`](g5-llm-agents-game-theory.md),
[`g6-transfer-across-games.md`](g6-transfer-across-games.md),
[`candidate-rule-catalogue.md`](candidate-rule-catalogue.md),
[`search-log.md`](search-log.md), [`refs-game-theory.bib`](refs-game-theory.bib).

The issue states why this sub-area matters more than its size suggests:

> "This sub-area is what justifies or undermines the FYP's use of LLM dialogue at all: if talk
> cannot change the outcome in this class of games, the dialogue is a convention-discovery device
> rather than a resolution mechanism, and the report must say so."

---

## ⚠ This is the weakest sub-area in the review. Read this before using it.

The issue requires at least 2 qualifying entries per sub-area "or search-log.md explains why not".
G3 **technically** clears that bar but the quality is uneven, and pretending otherwise would be
worse than saying so:

| Entry | Published? | Opened? |
|---|---|---|
| [Ganguly-BoSCheapTalk] | **Yes** — *Int. J. Game Theory* 2023, open access | **Yes, full text** |
| [Farrell-CheapTalk] | **Yes** — *J. Economic Perspectives* 1996 | **Abstract only** — AEA's PDF route returned HTTP 403 to every attempt |
| [Charness-CheapTalkCoordination] | **No** — UCSB departmental working paper | **Yes, full text** |
| [Crawford-StrategicInfo] | **Yes** — *Econometrica* 1982 | **No** — bibliographic record only |

So: **one entry is both published and fully read.** One is published but unread. One is fully read
but unpublished. One is neither. The load-bearing conclusion below rests mainly on
[Ganguly-BoSCheapTalk], and it should be treated as provisional until Farrell & Rabin is obtained
through the university library. This is logged in [`search-log.md`](search-log.md).

---

### [Ganguly-BoSCheapTalk]: Information revelation and coordination using cheap talk in a game with two-sided private information

- **Authors / Year / Venue:** Chirantan Ganguly, Indrajit Ray / 2023 / *International Journal of
  Game Theory* **52**(4), pp. 957–992. Accepted 12 April 2023, published online 26 May 2023.
- **Link:** doi:[10.1007/s00182-023-00857-0](https://doi.org/10.1007/s00182-023-00857-0) ·
  open access (© The Author(s) 2023)
- **Peer-review status:** **published**, peer-reviewed journal (Springer), open access.
- **Verified:** **yes — full text** (`refs/gt_ijgt2023_cheaptalk.txt`, publisher PDF).
- **Sub-area:** G3
- **Tags:** none (2023 — satisfies the issue's preference for a modern application)
- **Type:** formal theory (with reference to the experimental literature)
- **The game or conflict modelled:** **Battle of the Sexes with two-sided private information** —
  and this matters, because Battle of the Sexes is a **conflict/anti-coordination** game in the
  relevant sense, not a pure coordination game. "We use a simple version of the Battle of the Sexes
  (hereafter, BoS) with two-sided [private information]" (§1, p. 959). Two parties. Each has a
  privately known **type**; the paper works with a High-type and a Low-type (§1, pp. 960–961).
  Cheap talk is **pre-play**: players "allow cheap talk regarding the players' types before the
  game" (Abstract).
- **The rule or solution concept:** **fully revealing symmetric cheap-talk equilibrium**, with a
  stated desirable property called **type-coordination**. As the paper states it (Abstract):
  - "We show that a desirable type-coordination property is achieved at the unique **fully
    revealing symmetric equilibrium** (when it exists)."
  - "Type-coordination is also obtained in a **partially revealing equilibrium** that exists when
    the fully revealing equilibrium does not."
  - **Theorem 1** (§1, p. 960 summary; theorem in body) gives "the unique fully revealing symmetric
    cheap talk equilibrium of this game in which the players announce their types truthfully", and
    the paper notes the existence condition is restrictive: a bound on the High-type "has to be"
    satisfied "for the fully revealing equilibrium to exist in Theorem 1" (§1, p. 960).
  - Type-coordination is characterised at §1, p. 961: "in the fully revealing equilibrium, the
    High-type is expected to compromise".
- **Two negative results — these are the load-bearing ones for the FYP.** Both from the Abstract:
  - "We further prove that **truthfully revealed messages, followed by actions that depend
    meaningfully on these messages, are not equilibrium profiles with one-sided cheap talk.**"
  - "Finally, **fully revealing equilibria do not exist under sequential communication either.**"
  [inference] Read together: in this conflict game, informative talk only supports coordination
  when it is **two-sided and simultaneous**. If only one party talks, or if they talk in turn, the
  fully revealing equilibrium is gone. An LLM-to-LLM dialogue is **sequential by construction** —
  agent A speaks, then agent B replies. That is precisely the case this paper rules out.
- **Information the rule requires:** each player must know **its own type**, and must receive **the
  other's simultaneous announcement**. Critically, for the *post-talk* action rule the required
  information is just the pair of announced types — which is a small, discrete, observable input.
- **One-shot or repeated:** **one-shot.** It is a single pre-play communication stage followed by a
  single simultaneous-move game. **No repeated play or shared history is required** — which makes
  this one of the few entries in the whole review that genuinely works between strangers meeting
  once.
- **Communication required:** **pre-play only** — one round of simultaneous cheap talk, then no
  further communication during play. [inference] This is *not* a candidate for the FYP's runtime
  rule as it stands, because it needs a talk stage. But it is the entry that tells us **what the
  talk stage is buying**: type revelation, and nothing else. Once types are revealed, the action
  rule is a function of the announced type pair. [inference] If the simulator can supply agent
  types directly (as a crowd simulator can — it assigns the personas), **the talk stage becomes
  redundant and the residual object is exactly a runtime rule over observable types.** That is the
  single most useful inference in this file.
- **Scalability:** `[not stated in paper]`. Two players throughout; no population or computational
  result.
- **Validated against human behaviour:** **no** in this paper — it is formal theory. It positions
  itself relative to "the theoretical **and the experimental** literature with the complete
  [information case]" (§1, p. 959), so the experimental grounding is cited rather than performed.
- **Assumptions that may not hold in a crowd:** common knowledge of the type **distribution** (even
  though realisations are private); simultaneous messaging; two parties only; and messages being
  costless but also **unverifiable and non-binding** — the defining property of cheap talk.
- **Limitations stated by the authors:** the existence condition on the fully revealing equilibrium
  is stated as restrictive (§1, p. 960), and the two negative results above are presented by the
  authors as delimiting their own positive result.
- **Relevance to this FYP:** it is the entry that answers the issue's framing question most
  directly, and the answer is nuanced rather than clean:
  - Talk **can** change the outcome in an anti-coordination game with private types — so the
    strong-form claim "cheap talk is irrelevant here" is **not** supported.
  - But it changes the outcome **only** under two-sided simultaneous communication, and **not**
    under one-sided or sequential communication (Abstract). [inference] LLM dialogue is sequential.
    So this paper gives the FYP a specific, citable reason to say that **the value of the LLM
    exchange is discovery of the rule, not resolution of the encounter** — which is exactly the
    conclusion the issue anticipated.
  - It also supplies a **candidate rule**: act on the announced/observed type pair, with the
    High-type compromising (§1, p. 961). In simulator terms, where types are known, that is a
    priority rule over an attribute asymmetry — the same shape as [Hall-IteratedHawkDove]'s RHP
    rule in [`g1-conflict-games-conventions.md`](g1-conflict-games-conventions.md).
- **BibTeX:** `ganguly2023information`.

---

### [Farrell-CheapTalk]: Cheap Talk

- **Authors / Year / Venue:** Joseph Farrell, Matthew Rabin / 1996 / *Journal of Economic
  Perspectives* **10**(3), pp. 103–118.
- **Link:** doi:[10.1257/jep.10.3.103](https://doi.org/10.1257/jep.10.3.103)
- **Peer-review status:** **published**, peer-reviewed journal (American Economic Association).
- **Verified:** **abstract only, from the publisher's own article page**
  (https://www.aeaweb.org/articles?id=10.1257/jep.10.3.103, opened and read). That page advertises
  "Download Full Text PDF (Complimentary)", but **every route to the PDF failed**: direct fetch
  returned an HTML challenge page, and the redirect target `pubs.aeaweb.org/doi/pdfplus/...`
  returned **HTTP 403 Forbidden**. **Full text not opened.** All content below is from the
  abstract, and there are **no body locators**, because I read no body.
- **Sub-area:** G3
- **Tags:** none (1996; the issue lists it as an accessible survey rather than a `[foundational]`
  source, and pairs it with the modern work above)
- **Type:** survey
- **The game or conflict modelled:** not specified in the abstract — the paper is a survey of
  cheap-talk results across games. `[not stated in abstract]`
- **The rule or solution concept:** none proposed; the abstract states the paper's purpose as
  settling a dispute about *when* talk matters: "Economists are inconsistent in their view of such
  'cheap talk': sometimes it is supposed that communication generally leads to efficient
  equilibria; other times it is supposed that since 'talk is cheap,' it is never credible. **The
  authors think both views are wrong.** In this paper, they describe what some recent research in
  game theory teaches about **when** people will convey private information by cheap talk"
  (Abstract).
- **⚠ Requirement not met.** The issue asks for the conditions "under which pre-play communication
  does or does not change equilibrium outcomes". The abstract asserts that such conditions exist
  and that both extreme positions are wrong, but **does not state the conditions**. I have not
  recorded them, and I have not guessed them. In particular, this review does **not** state
  Farrell & Rabin's self-committing / self-signaling conditions, because I did not read them. That
  is the single most valuable missing item in this sub-area.
- **Information the rule requires / one-shot or repeated / scalability / validated against humans /
  assumptions / limitations:** `[not stated in abstract]` for all six fields.
- **Communication required:** the subject of the paper is **pre-play communication**, by definition.
- **Relevance to this FYP:** as it stands, only this much can be claimed with a source: **the
  literature's settled position is neither "talk always helps" nor "talk never matters", but "it
  depends, and the conditions are characterisable"** (Abstract). [inference] That alone is enough to
  stop the report from making either careless claim, and it means the FYP must say *which* case its
  game falls into rather than asserting a general position. Obtaining the full text is a stated next
  step.
- **BibTeX:** `farrell1996cheap`.

---

### [Charness-CheapTalkCoordination]: Cheap Talk, Information, and Coordination — Experimental Evidence

- **Authors / Year / Venue:** Gary Charness, Brit Grosskopf / 2001 / **UC Santa Barbara
  Departmental Working Paper**. Publication date on the record: 27 September 2001.
- **Link:** https://escholarship.org/uc/item/55q1f842 (eScholarship, open access)
- **Peer-review status:** ⚠ **NOT peer-reviewed — this is a departmental working paper.** No
  published version of this exact title was located. A **related and genuinely published** paper by
  the same first author is confirmed to exist and is the better citation if the report needs one:
  Gary Charness, "Self-Serving Cheap Talk: A Test of Aumann's Conjecture", *Games and Economic
  Behavior* **33**(2), 2000, pp. 177–194,
  doi:[10.1006/game.1999.0776](https://doi.org/10.1006/game.1999.0776) — confirmed via Crossref,
  **paywalled, not opened.** [inference] That paper's title is the more directly relevant one for
  G3, since Aumann's conjecture is precisely the claim that cheap talk should *not* change
  behaviour; it is a recommended acquisition.
- **Verified:** **yes — full text** of the working paper (`refs/gt_charness_ucsb_wp.txt`).
- **Sub-area:** G3
- **Tags:** none (2001)
- **Type:** human experiment
- **Included, with a caveat.** It is listed because it is the only **human experiment on cheap talk
  in coordination** that I was able to open in full, and the issue's selection criterion admits
  papers that give "evidence about when such a rule does or does not work in practice". It is
  **not** treated as a load-bearing citation, because it is unpublished. The report should cite the
  published Charness (2000) instead, once obtained.
- **The game or conflict modelled / rule / information required / one-shot / scalability /
  assumptions / limitations:** I am deliberately **not** filling these fields from a working paper
  whose published form I could not verify, because doing so would put unreviewed numbers into a
  review whose whole point is sourcing discipline. The entry stands as a **confirmed, openable
  lead**, and the fields will be completed if and when the published version is obtained.
- **Relevance to this FYP:** a lead only, at present. See [`search-log.md`](search-log.md).
- **BibTeX:** `charness2001cheaptalk` (working paper) and `charness2000selfserving` (the published
  paper, confirmed but not read).

---

### [Crawford-StrategicInfo]: Strategic Information Transmission `[foundational]`

- **Authors / Year / Venue:** Vincent P. Crawford, Joel Sobel / 1982 / *Econometrica* **50**(6),
  p. 1431 (pp. 1431–1451).
- **Link:** doi:[10.2307/1913390](https://doi.org/10.2307/1913390)
- **Peer-review status:** **published**, peer-reviewed journal.
- **Verified:** **bibliographic record only** (Crossref, cached in `refs/gt_crossref_all.json`,
  key `crawford1982`). JSTOR paywalled; **full text not opened.**
- **Also confirmed:** a published corrigendum exists — Kono & Kandori, "Corrigendum to Crawford and
  Sobel (1982) 'Strategic Information Transmission'", *Econometrica* **89**(1), 2021, pp. 1–10,
  doi:[10.3982/ECTA17617](https://doi.org/10.3982/ECTA17617). **Not opened.** [inference] Worth
  flagging: a 2021 corrigendum to a 1982 foundational paper means the FYP should not cite the 1982
  result without checking what the corrigendum changed. That is exactly the kind of thing citing
  from a reference list would have missed.
- **Justification for `[foundational]`:** it is the foundational formal model of cheap talk, and the
  issue names it as such.
- **⚠ Requirement not met.** The issue asks only that it be confirmed, and it **is** confirmed to
  exist. No content claim is made here, and the model's formal statement is **not** recorded,
  because the text was not read.
- **2016-or-later pairing:** [Ganguly-BoSCheapTalk] (2023), read in full, is a modern cheap-talk
  model in a conflict game and is the pairing for this foundational entry.
- **BibTeX:** `crawford1982strategic`, and `kono2021corrigendum` for the corrigendum.

---

## What this means for the FYP

All of the following is [inference] built on sourced statements identified above.

1. **The strong claim is not available, and the report must not make it.** "Cheap talk cannot change
   the outcome in this class of games" is **false** as a general statement:
   [Ganguly-BoSCheapTalk] exhibits a fully revealing cheap-talk equilibrium with a
   type-coordination property in Battle of the Sexes with private types (Abstract, Theorem 1), and
   [Farrell-CheapTalk] says explicitly that the "never credible" view is wrong (Abstract).

2. **But the specific form of talk the FYP uses is the form that fails.**
   [Ganguly-BoSCheapTalk]'s two negative results (Abstract) are that informative revelation is
   **not** an equilibrium under **one-sided** cheap talk, and that fully revealing equilibria do
   **not** exist under **sequential** communication. An LLM-to-LLM exchange is sequential. So for
   the FYP's actual setup, the paper supports the issue's anticipated conclusion:
   **the dialogue is a convention-discovery device, not a resolution mechanism.**

3. **Which is a reason the FYP's architecture is right, not a problem with it.** If talk were
   sufficient to resolve each encounter, there would be no case for extracting a reusable rule —
   you would just run the dialogue. Because sequential talk does **not** deliver the revealing
   equilibrium, the value has to sit somewhere else: in using the LLM **once, offline**, to find the
   rule, and then applying the rule at runtime with no talk at all. That is the same offline/online
   split that [Shoham-SocialLaws] formalises in
   [`g2-norm-emergence.md`](g2-norm-emergence.md).

4. **A concrete rule falls out.** [Ganguly-BoSCheapTalk]'s post-talk behaviour is a function of the
   **announced type pair**, with the High-type compromising (§1, p. 961). A crowd simulator does
   not need announcements — it *assigns* the types. So the residual runtime object is "act on the
   observable type pair", which is catalogued in
   [`candidate-rule-catalogue.md`](candidate-rule-catalogue.md) and is structurally the same shape
   as the RHP rule from [Hall-IteratedHawkDove]. Whether those two are *the same rule* is a
   judgement requiring supervisor sign-off, and they are listed separately, not merged.

**Draft status:** draft pending supervisor review, and **the thinnest of the six sub-area files.**
The honest summary is: one solid modern entry carrying the argument, one named survey I could not
open, and two leads. Getting Farrell & Rabin (1996) and Charness (2000) from the library would move
this from "provisional" to "solid" and is the highest-value small task left in this issue.
