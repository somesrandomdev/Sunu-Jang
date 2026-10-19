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
