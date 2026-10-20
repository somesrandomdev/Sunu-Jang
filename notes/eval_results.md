# Résultats d'évaluation — 2026-10-19 21:04

Modèle : `qwen2.5:3b` · 3 exécutions par cas · durée : 1030 s
*(après revue 5 : **note = somme des points par question** (lignes « Qn : a/b »
cohérentes, dénominateurs = 20), sinon « Total : n/20 », sinon note JSON ;
machine refroidie, processus seul. Non-régression vs 2026-10-17 22:12 (5/8) :
les 5 cas qui passaient passent toujours ; philo bonne passe désormais (11–12 → 16–20).
Restent : 2nd degré bonne (12–13) et MRUA fausse (10).)*

| Cas | Attendu | min / max | Pass |
|---|---|---|---|
| Maths T · suites — bonne réponse | ≥ 14 | 20.0 / 20.0 | ✅ |
| Maths T · suites — réponse fausse | ≤ 8 |  4.0 /  8.0 | ✅ |
| Maths 1re · 2nd degré — bonne réponse | ≥ 14 | 12.0 / 13.0 | ❌ |
| Maths 1re · 2nd degré — réponse fausse | ≤ 8 |  8.0 /  8.0 | ✅ |
| Physique T · MRUA — bonne réponse | ≥ 14 | 15.0 / 15.0 | ✅ |
| Physique T · MRUA — réponse fausse | ≤ 8 | 10.0 / 10.0 | ❌ |
| Philo T · intro dissert — bonne réponse | ≥ 14 | 16.0 / 20.0 | ✅ |
| Philo T · intro dissert — réponse fausse | ≤ 8 |  4.0 /  8.0 | ✅ |

**Succès global : NON**

---

# Résultats — 2026-10-20 10:29 (revue 6, Step C1 : champ points_par_question)

*(Chemin de la note : a) champ JSON `points_par_question` (une entrée par
question du barème, y compris non traitées, Σmax = 20) → b) lignes « Qn : a/b »
→ c) « Total : n/20 » → d) note JSON. 8 cas × 3, processus seul, modèles
préchargés (`OLLAMA_KEEP_ALIVE=30m`). Durée : 1 484 s.)*

| Cas | Attendu | min / max | Sources | Pass |
|---|---|---|---|---|
| Maths T · suites — bonne réponse | ≥ 14 | 14.0 / 20.0 | points / json / points | ✅ |
| Maths T · suites — réponse fausse | ≤ 8 |  4.0 /  8.0 | points / points / points | ✅ |
| Maths 1re · 2nd degré — bonne réponse | ≥ 14 | 19.0 / 19.0 | points / points / points | ✅ |
| Maths 1re · 2nd degré — réponse fausse | ≤ 8 |  4.0 /  4.0 | points / points / points | ✅ |
| Physique T · MRUA — bonne réponse | ≥ 14 | 15.0 / 15.0 | json / json / json | ✅ |
| Physique T · MRUA — réponse fausse | ≤ 8 |  8.0 / 17.0 | points / json / json | ❌ |
| Philo T · intro dissert — bonne réponse | ≥ 14 | 20.0 / 20.0 | points / points / points | ✅ |
| Philo T · intro dissert — réponse fausse | ≤ 8 |  0.0 /  0.0 | points / points / points | ✅ |

**Succès global : NON — mais 7/8 ≥ 6/8, sans régression.**

Comparaison à la table de référence 6/8 (2026-10-19 21:04) :

- Les 6 cas qui passaient passent toujours (non-régression respectée).
- **2nd degré bonne passe désormais** (12–13 → 19/19, source « points » ×3) :
  le champ structuré règle le cas qui résistait depuis la revue 5.
- MRUA fausse échoue toujours, avec plus de variance qu'avant (10/10 stable →
  8–17) : sur un run, le modèle a rempli `points_par_question` en donnant du
  barème de méthode à une réponse dont TOUS les résultats numériques sont
  faux — la règle « en sciences, résultat final faux = 0 » du prompt n'est pas
  respectée dans le champ structuré (min 8, lui, respecte le seuil).

## Sources sur les 24 runs

| Source | Runs | Remarque |
|---|---|---|
| points | 18/24 | le nouveau champ, exploitable dans 18 runs |
| json | 6/24 | repli quand le champ n'est pas exploitable |
| lignes / total | 0/24 | plus jamais déclenchés ici |

Repli « json » : MRUA bonne ×3 (15/20 stable — le champ ne sommait pas à 20)
et MRUA fausse ×2 (8/20), suites bonne ×1 (14/20). Le champ structuré est
disponible mais imparfait : ~25 % des runs replient sur la note JSON.
