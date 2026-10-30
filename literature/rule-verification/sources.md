# Sources for RF-14 (issue #69), round 1

Every source the evidence files cite, with what was read and where the copy is. "Read" says how much
of the source was seen: **full text** (PDF cached and searched), **abstract** (from Europe PMC's API,
cached as JSON), or **page** (an official web page, cached as HTML). Claims taken from an abstract
are marked so in the evidence files; nothing beyond the abstract is claimed for those.

Access notes: HAL, mediaTUM and the University of Turku's portal answered with a bot check (Anubis)
on 2026-10-30, so Olivier et al. 2013, Knorr et al. 2016 and Nummenmaa et al. 2009 were read from
Europe PMC's abstracts instead. Each can be fetched in a browser in minutes.

| Key | Source | Read | Cached copy |
| --- | --- | --- | --- |
| [Moussaid2009] | Moussaïd, M., Helbing, D., Garnier, S., Johansson, A., Combe, M., Theraulaz, G. (2009). Experimental study of the behavioural mechanisms underlying self-organization in human crowds. *Proc. R. Soc. B* 276(1668), 2755–2762. doi:10.1098/rspb.2009.0405. Experiments in France, 40 participants aged 18–30. | full text (arXiv 0908.3131) | `refs/rf14_moussaid2009_side_preference.pdf`, `.txt`; Crossref `refs/rf14_moussaid2009_crossref.json` |
| [Olivier2013] | Olivier, A.-H., Marin, A., Crétual, A., Berthoz, A., Pettré, J. (2013). Collision avoidance between two walkers: role-dependent strategies. *Gait & Posture* 38(4), 751–756. doi:10.1016/j.gaitpost.2013.03.017. Laboratory, France. | abstract | `refs/rf14_olivier2013_epmc.json` |
| [Knorr2016] | Knorr, A. G., Willacker, L., Hermsdörfer, J., Glasauer, S., Krüger, M. (2016). Influence of person- and situation-specific characteristics on collision avoidance behavior in human locomotion. *J. Exp. Psychol.: Hum. Percept. Perform.* 42(9), 1332–1343. doi:10.1037/xhp0000223. Laboratory, Germany. | abstract | `refs/rf14_knorr2016_epmc.json` |
| [Huber2014] | Huber, M., Su, Y.-H., Krüger, M., Faschian, K., Glasauer, S., Hermsdörfer, J. (2014). Adjustments of speed and path when avoiding collisions with another pedestrian. *PLoS ONE* 9(2), e89589. doi:10.1371/journal.pone.0089589. Laboratory, Germany. | full text | `refs/rf14_huber2014_speed_path.pdf`, `.txt` |
| [Rapos2021] | Rapos, V., Cinelli, M. E., Grunberg, R., Bourgaize, S., Crétual, A., Olivier, A.-H. (2021). Collision avoidance behaviours between older adult and young adult walkers. *Gait & Posture* 88, 210–215. doi:10.1016/j.gaitpost.2021.05.033. Laboratory, Canada; 17 older (68 ± 3 years) and 17 young (23 ± 2) adults. Already in `literature/demographic-personas/human-demographic-effects.md` (B3). | abstract | `refs/rf14_rapos2021_epmc.json`; Crossref `refs/cr_olderyoung.json` |
| [Nummenmaa2009] | Nummenmaa, L., Hyönä, J., Hietanen, J. K. (2009). I'll walk this way: eyes reveal the direction of locomotion and make passersby look and go the other way. *Psychological Science* 20(12), 1454–1458. doi:10.1111/j.1467-9280.2009.02464.x. Eye tracking, animated walker, Finland. | abstract | `refs/rf14_nummenmaa2009_epmc.json` |
| [Arminen2023] | Arminen, I. A. T., Heino, A. S. M. (2023). Civil inattention—On the sources of relational segregation. *Frontiers in Sociology* 8, 1212090. doi:10.3389/fsoc.2023.1212090. Video of passers-by, Helsinki. Operationalises Goffman's civil inattention. | full text | `refs/rf14_arminen2023_civil_inattention.pdf`, `.txt` |
| [Valuch2015] | Valuch, C., Pflüger, L. S., Wallner, B., Laeng, B., Ansorge, U. (2015). Using eye tracking to test for individual differences in attention to attractive faces. *Frontiers in Psychology* 6, 42. doi:10.3389/fpsyg.2015.00042. Laboratory, photographs, Austria. | full text | `refs/rf14_valuch2015_attractiveness_gaze.pdf`, `.txt` |
| [Echeverria2026] | Echeverría-Huarte, I., Feliciani, C., Shi, Z., Nishinari, K., Sánchez, A., Garcimartín, A., Zuriguel, I. (2026). Individual locomotor bias drives counterclockwise motion in pedestrian crowds. *Nature Communications*. doi:10.1038/s41467-026-73713-w. Experiments in Spain and Japan, with a questionnaire on avoidance direction in Japan. | page (full text HTML) | `refs/echeverria2026_locomotor_bias.html` (cached before this issue) |
| [Jung2013] | Jung, H. S., Jung, H. S. (2013). Survey of Korean pedestrians' natural preference for walking directions. *Applied Ergonomics* 44(6), 1015–1023. doi:10.1016/j.apergo.2013.04.003. Observation in 10 situations and a survey of 600, Korea. | abstract | `refs/rf14_korea2013_epmc.json` |
| [CircleAntipode2019] | Authors at HKUST and Beijing Jiaotong University (2019). Go left or right? Explore the side preference behavior with circle antipode experiments. arXiv 1912.10870. 64 participants, 960 samples, Beijing, December 2017. `[preprint]` | full text | `refs/rf14_circle_antipode2019.pdf`, `.txt` |
| [MOT2024] | Ministry of Transport, Singapore (12 November 2024). Written reply to Parliamentary Question on community standards to improve etiquette for motorised and non-motorised users and pedestrians in public places. **Official guidance, not a study.** | page | `refs/rf14_mot_pq_footpaths.html` |
| [LTA2020] | Land Transport Authority, Singapore (August 2020). Path safety a shared responsibility (media reply: four safety tips for pedestrians added to the Code of Conduct). **Official guidance, not a study.** | page | `refs/rf14_lta_path_safety_2020.html` |

Cited from the repository, not fetched again: RF-10's screen (`llm_negotiation/runs/rf10_round1_head_on/screen_report.md`),
RF-11's extraction (`llm_negotiation/runs/rf11_round1_head_on/extraction_report.md`), RF-31's translation
(`llm_negotiation/runs/rf31_round1_head_on/translation_report.md`), RF-18 and RF-33's evaluation
(`llm_negotiation/runs/rf18_round1_realistic/evaluation_report.md`).

**Under the user's decision of 2026-10-30 (published studies only)**, the two Singapore government pages
are not evidence of how people behave. They are cited only for what is *advised*, which is what the
agents' "keep left in Singapore" debriefs claim.

## Looked for, not found

- A published study of which side pedestrians keep in **Singapore** (or Malaysia, Hong Kong, the UK or
  Australia, other left-driving places) by observation. None found in two searches (`search-log.md`).
- A study of whether people give way more to someone with a **cane**, a **suitcase** or a **phone**.
  None found; Rapos2021 is about age only.
- A study counting how often pedestrians **stop or back up** in head-on meetings outside the laboratory.
- A study measuring **signalling (nods, waves) between acquaintances and strangers** when passing.
  Cary (1978), "Does civil inattention exist in pedestrian passing?", is the classic test; it is not
  in Europe PMC and was not fetched.
- Wolff (1973), "Notes on the behavior of pedestrians" (in *People in Places*), a book chapter: its
  citation was confirmed, its content was not read.
