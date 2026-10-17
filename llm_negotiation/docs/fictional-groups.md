# Fictional groups (issue #32)

A person in a rule-generation session may belong to a **fictional group**: an `ethnic_group`
attribute that holds an invented label, such as `Kestrop`. It lets an experiment ask whether a
model treats people of its own group differently from people of another, with a label that
means nothing to it.

**What it can and cannot show.** Fictional groups can test in-group against out-group
effects, which have a human baseline in the minimal group paradigm (people favour their own
group even when the groups are arbitrary and meaningless); comparing a model with that
baseline is for the validation sub-issue (SI-6). **They cannot show how a model treats real
ethnicities.** A model's associations with real groups (stereotypes, or the absence of them)
are not touched by a label it has never seen, and nothing here measures them. Using real
groups, or describing fictional ones, would be a different experiment and is out of scope
(section 7).

**Ethics sign-off from the supervisor: pending unless recorded otherwise.** The ethnicity
factor is off by default in every experiment config, and no paid run may switch it on until
that sign-off is recorded in `CLAUDE.md` (section 6).

## 1. The attribute

- `ethnic_group` is a persona attribute (`negsim/personas/schema.py`) that holds **one label**
  from a configurable set: one capitalised word of 3 to 16 letters, with no spaces, digits or
  punctuation, so that no description can be written into it (`negsim/personas/groups.py`,
  `check_label`). A short list of real group names, nationalities and languages present in
  Singapore is refused outright (`REAL_GROUP_NAMES`): a guard against an obvious mistake, not
  the check of a label, which is the search of section 2.
- **A label carries nothing but itself**: no description, history, appearance or customs.
  The prompts say which group each person is in and nothing more.
- **Personal names stay banned**: the persona schema refuses name-like fields, and nothing
  here adds a name.
- An agent always knows its own group, and sees another's only when the session shows it,
  by a visibility switch of its own, apart from the one for age and gender (perception record
  version 3, `perception.md`, "The group"). It is **hidden by default**, and left out of a
  persona that does not give it, so every persona and log written before issue #32 is as it
  was.
- **The framing word** introduces the attribute in a prompt ("a member of the Kestrop ethnic
  group"). It is a setting of each experiment, recorded with every session; the default is
  "ethnic group". **A decision pending supervisor review** (DD86): "community" or "group"
  would frame the same labels differently, and the issue leaves the choice open.

## 2. The default labels, and how they were checked

| Label | Use | Nearest matches found | Echo of a Singapore community's words |
|---|---|---|---|
| `Kestrop` | default, first | the English surnames Westrop, Keast and Kestle; *Kestrosaurus*, an extinct genus; Kétpó, a town in Hungary | none found (see below on "kes") |
| `Dremmik` | default, second | Dremel, a tool brand; Dremmen, a former municipality in Germany; the English surnames Dimmick, Dymock, Dimmock; Drioma, a spirit of Slavic myth | none found |
| `Pellund` | default, third | Pellworm, a German island; "pell", an old English word (a hide, a roll of parchment) and an English surname; the Scandinavian given names Pelle, Pellervo | none found |
| `Brannoq` | spare | Brannock, an English surname; Brannockstown, a village in Ireland; Brännö, a Swedish island | **faint**: its first syllable sounds like Pulau Brani, an island of Singapore whose name is read as Malay *berani*, "brave" |

The order is the order of rotation (DD85). **What a label must pass**, as the issue words it:
it is not a real ethnonym, nationality, place name, language, or common word in English,
Malay, Chinese or Tamil. To that this project adds one rule of its own: a label must not echo
a word or a naming element of one of Singapore's communities, since a model could then map
the label onto a real local group. Every label was searched on the web for itself, and for
itself as a people, tribe, language, village, place or surname; and checked against the
languages of Singapore's communities.

**Why none can be read as Chinese** (an assessment from how the romanisations are spelled,
not a search result). No syllable of Mandarin pinyin, or of the Hokkien, Teochew and
Cantonese spellings used for Singapore's Chinese surnames, begins with a consonant cluster
such as `dr` or `tr`, or ends in `-s`, `-l` or `-nd`. However each label is split into
syllables, one of them does (`Kes|trop`, `Drem|mik`, `Pel|lund`), so none of the three can
be read as Chinese. **Malay and Tamil**: the searches found no word or name in either for any
of the three (2.1). The Malay word *kes* ("case", a borrowing of the English word) begins
`Kestrop`; a loan-word for a legal case says nothing about any community, so it is not
counted as an echo (an assessment).

### 2.1 The searches of 2026-10-17

Made with the session's web search tool, in its standard mode. What a search returns is data;
the result column is what it showed, read by me.

| Candidate | Query | Result | Verdict |
|---|---|---|---|
| Zorvel | `"Zorvel"` | No page with the word. Nearest: Zoryve (roflumilast, a prescription cream), Zorvolex (diclofenac), Zorvion (a cream), Zorelo (a company), Zorillor (a cartoon character), the spider genera *Zoroides* and *Zoropsis* | — |
| Zorvel | `Zorvel people OR tribe OR language OR village OR surname` | Nothing. Nearest: the Zoró, an Indigenous people of Brazil; the Zorathites of the Bible; the surnames Zorc, Zorzi, Zoric, Zorn | — |
| Zorvel | `Tamil male names ending in "vel" ...` | *Vel* (வேல்) is the Tamil word for spear, the weapon of the deity Murugan, and the root of Tamil names such as Velan and Thangavel ("gold" and "vel") | **rejected**: it ends in a Tamil naming element (the rule that rejected *Velorn*, 2.2) |
| Kestrop | `"Kestrop"` | No page with the word. Nearest: *Kestrosaurus*; Ketro, an eye drop; kestose, a sugar; Kétpó, Hungary | — |
| Kestrop | `Kestrop people OR tribe OR language OR village OR surname` | Nothing. Nearest: the surnames Westrop, Keast, Kestle | **kept** |
| Kestrop, Dremmik, Brannoq | `Malay words "kes" "trop" OR Malay meaning "kestrop" OR "dremmik" OR "brannoq"` | No Malay word for any of the three | — |
| Dremmik | `"Dremmik"` | No page with the word. Nearest: Dremel; Drioma | — |
| Dremmik | `Dremmik people OR tribe OR language OR village OR surname` | Nothing. Nearest: Dremmen, Heinsberg, Germany; the surnames Dymock, Dimmock, Dimmick, Dreher; the Russian family name Dremov | **kept** |
| Brannoq | `"Brannoq"` | No page with the word. Nearest: Brannockstown; Brännö; Brane | — |
| Brannoq | `Brannoq people OR tribe OR language OR village OR surname` | Nothing. Nearest: the surnames Brannock, Brannen, Brannan, Brannon, Brannick | — |
| Brannoq | `Pulau Brani Singapore island name meaning berani brave Malay` | Pulau Brani is an island of Singapore; its name is glossed "isle of the brave", from Malay *berani* (Infopedia, Wikipedia), though Infopedia gives a well as the origin | **spare only**: the echo is faint, but it is of a Singapore place |
| Thressik | `"Thressik"` | No page with the word. Nearest: Threshyk, a race of reptilian humanoids on a worldbuilding site; the Treres, a Thracian tribe; Thressa, a Thracian river | — |
| Thressik | `Thressik people OR tribe OR language OR village OR surname OR word` | Nothing. Nearest: the surnames Thresh, Thresher; Thracian tribes | **not used**: its nearest matches are an ancient people's names and a fictional race, and it rhymes with Dremmik |
| Vorlesk | `"Vorlesk"` | No page with the word. Nearest: German *vorlesen* ("to read aloud"), *Vorlesung* ("lecture") | **rejected**: it holds a German word stem nearly whole |
| Pellund | `"Pellund"` | No page with the word. Nearest: Pellworm; "pell" | — |
| Pellund | `Pellund people OR tribe OR language OR village OR surname OR place` | Nothing. Nearest: the English surnames Pell, Pells, Pelton, Pellatt, Pelling | — |
| Pellund | `"Pellund" Sweden OR Norway OR Denmark OR Finland` | Nothing; the given names Pelle and Pellervo | **kept** (replaces Zorvel) |
| Kestrop, Dremmik, Pellund | `"Kestrop" OR "Dremmik" OR "Pellund" Tamil OR Malay OR Chinese meaning word name` | No meaning in Tamil, Malay, Chinese or any other language. Nearest: the names Dren (Albanian *dre*, "deer") and Pelle | — |

Sources the results came from (the pages the search returned and the summaries used):
[Zoroides](https://en.wikipedia.org/wiki/Zoroides),
[Zorvolex](https://www.rxlist.com/zorvolex-drug.htm),
[Zoró](https://dice.missouri.edu/assets/docs/tupi/Zoro.pdf),
[Thangavel](https://britishsurnames.uk/surname/thangavel),
[Velan](https://www.ancestry.com/first-name-meaning/velan),
[Kestrosaurus](https://en.wikipedia.org/wiki/Kestrosaurus),
[Westrop](https://britishsurnames.uk/surname/westrop),
[Kestle](https://britishsurnames.uk/surname/kestle),
[Drioma](https://en.wikipedia.org/wiki/Drioma),
[Dremmen](https://en.wikipedia.org/wiki/Dremmen),
[Dimmick](https://britishsurnames.uk/surname/dimmick),
[Brannockstown](https://www.logainm.ie/en/1147),
[Brannock](https://britishsurnames.uk/surname/brannock),
[Pulau Brani, Infopedia](https://eresources.nlb.gov.sg/infopedia/articles/SIP_221_2005-01-18.html),
[Pulau Brani, Wikipedia](https://en.wikipedia.org/wiki/Pulau_Brani),
[Threshyk](https://www.worldanvil.com/w/spacial-tangent-janx/a/threshyk-article),
[Treres](https://en.wikipedia.org/wiki/Treres),
[Thresh](https://britishsurnames.uk/surname/thresh),
[Vorlesung](https://www.vocabulary.com/dictionary/de/Vorlesung),
[Pellworm](https://en.wikipedia.org/wiki/Pellworm),
[pell](https://en.wiktionary.com/wiki/pell),
[Pell](https://britishsurnames.uk/surname/pell),
[Pelle](https://www.nordicnames.de/wiki/Pelle),
[Dren](https://www.ancestry.com/first-name-meaning/dren).

### 2.2 The searches of 2026-10-16

The first set of searches is in `WORK_LOG-32.md` (the 2026-10-16 21:10 entry) as a summary;
its queries were not kept. As reported there: `Zorvel`, `Kestrop` and `Dremmik` passed, with
`Brannoq` as a spare; rejected were *Orvane* (the French river Orvanne, and a former commune of
that name), *Kelbrin* (Kilbrin, a parish in Cork), *Hollvek* (Höllviken, Sweden), *Fyrrel*
(the surnames Farrell, Ferrell), *Quorlan* (the Cornish place-name element *korlan*), and three
that passed the search but echo a word of a Singapore community: *Velorn* (Tamil *vel*),
*Tessivar* (the Tamil pronoun *ivar*), *Melvori* (*Melayu*). On 2026-10-17 `Zorvel` was
rejected by the rule that rejected *Velorn*: it ends in *vel* (2.1).

**A config may give its own labels.** Its labels must pass `check_label` (the form and the
guard list), and every label an experiment uses should be searched as above before a paid run;
`check_labels` cannot do that search.

## 3. Sessions with groups: the factors, the visibility, the framing

A rule-generation design switches the group on with `design.ethnicity` (`rule-generation.md`,
section 2), and then crosses three more factors with its six:

- **`group_pair`**: `same` (both people in one group) or `different`.
- **`label_rotation`**: which label person 1 gets, `0` to one less than the number of labels.
  Person 2 gets the same label, or in a `different` pair the next one round the set. With the
  default labels the six combinations are Kestrop–Kestrop, Dremmik–Dremmik, Pellund–Pellund,
  Kestrop–Dremmik, Dremmik–Pellund and Pellund–Kestrop: every label is person 1's and person
  2's equally often, in same pairs and in different ones, so no effect can be tied to one label.
  The rotation uses three of the six ordered different pairs (Kestrop is never person 2 to a
  Dremmik person 1); person 1 and person 2 are slots of the design, which the `mapping` and
  `order` factors move between the case's agents and the speaking order.
- **`ethnicity_visible`**: whether the two can see each other's group, as a switch of its own,
  apart from `demographics_visible`, so that the effects of seeing age and gender and of seeing
  a group can be told apart. When it is false the groups appear **nowhere** in what a model is
  shown, not even a person's own; the field glossary never lists the group either way, since no
  rule may read it (section 4).

Each session records the labels its people got (`personas`), its cell, its visibility and the
framing word (`framing`), in `design.jsonl` and its own record (`log-schema.md`,
"Rule-generation experiments"). The full factorial with the group is 3,456 cells per case and
condition (`rule-generation.md`, section 2); SI-3b will need a fraction of it.

## 4. No rule may read it

An agent may see another's group; **no rule may read it**. The rule loader refuses, as
`protected_attribute` and before every other check, any rule whose condition or role
assignment (its field, its role names and its tie policy included) names the group or anything
derived from it (`rule-format.md`, section 14). In rule generation such a rule is kept, in a
validation category of its own, `protected_attribute`: a model trying to condition a rule on
ethnicity is a finding, not an error to hide (`rule-generation.md`, section 6). Independently of
the loader, no field a rule can read is the group or derived from it, and no snapshot holds it
(`tests/test_protected_attribute.py`).

## 5. What is logged for analysis

A model can treat the two people differently without any rule reading their groups: in who
gives way. So every session of a rule-generation experiment, with the group on or off, has a
row in `outcomes.jsonl` (`negsim/rulegen/outcomes.py`; `log-schema.md`) with what to stratify by
(the cell, `group_pair`, `label_rotation`, `ethnicity_visible`, `demographics_visible`, the
framing, and each person's age, gender, urgency and group) and what came of it:

- the session's `outcome`;
- in condition A, **who proposed and who conceded**: each person's number of proposals,
  whose proposal was accepted (`proposed_by`) and who accepted the other's (`conceded_by`), and
  who said that no rule is possible;
- for the agreed (A) or stated (B) rule, its validation `category` and **what it does to each
  person on the case's own pair** (`effect`): it is loaded and matched on the case's snapshot
  with the session's people in it, and the row gives each person's role and directive, **who
  got the larger responsibility share** (or `equal`), who goes first through a single-file
  passage, and who backs up.

`summary.json` counts the sessions' outcomes by condition, group pair and whether the groups
were shown (`groups`). Nothing here judges an outcome; the analysis is SI-3b's.

## 6. Off by default, and the supervisor's sign-off

**Ethics sign-off from the supervisor: pending unless recorded otherwise.** The ethnicity
factor is disabled by default in every experiment config: a design without `design.ethnicity`,
or with `enabled: false`, has no groups, and running it needs `enabled: true`. No paid run may
switch it on until the sign-off is recorded in `CLAUDE.md`, and the experiment refuses one that
tries, before anything is sent (`refused_no_sign_off` in `invocations.jsonl`). It looks for this
sentence in `CLAUDE.md`, with the date filled in:

> Ethics sign-off for the fictional-group factor (issue #32): approved by the supervisor on YYYY-MM-DD

Only the user may add it, once the supervisor has approved; nothing in this issue does. A mock
run (no model, no spend) needs no sign-off, so that the pipeline can be rehearsed.

## 7. What fictional groups cannot show, and what is out of scope

- **Real ethnicities.** A fictional label cannot show how a model treats a real group. Any
  claim about a model and real ethnicities needs a different experiment, and an ethics review
  of its own.
- **Cultural description.** A described fictional group (a history, customs, an appearance)
  would test the description, not group membership; it is out of scope.
- **Names.** Banned throughout: a name carries gender and ethnicity cues that would be
  confounded with the attributes under study (`negsim/personas/schema.py`).
- **The labels are not neutral by construction.** A searched label is one with no meaning
  found, not one with no associations at all: every invented word sounds like something
  (section 2 lists what each sounds like). The rotation of labels across the design is what
  keeps any one label's sound from being read as an effect of group membership.
