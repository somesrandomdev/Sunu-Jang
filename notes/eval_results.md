# Résultats d'évaluation — 2026-10-17 20:22

Modèle : `qwen2.5:3b` · 3 exécutions par cas · durée : 1031 s
*(après correctif d'échappement — revue du 17 oct, commit 689acd2 ; machine refroidie 10 min)*

| Cas | Attendu | min / max | Pass |
|---|---|---|---|
| Maths T · suites — bonne réponse | ≥ 14 | 14.0 / 15.0 | ✅ |
| Maths T · suites — réponse fausse | ≤ 8 |  8.0 /  8.0 | ✅ |
| Maths 1re · 2nd degré — bonne réponse | ≥ 14 | 12.0 / 12.0 | ❌ |
| Maths 1re · 2nd degré — réponse fausse | ≤ 8 |  8.0 /  8.0 | ✅ |
| Physique T · MRUA — bonne réponse | ≥ 14 | 15.0 / 15.0 | ✅ |
| Physique T · MRUA — réponse fausse | ≤ 8 | 10.0 / 11.0 | ❌ |
| Philo T · intro dissert — bonne réponse | ≥ 14 | 11.0 / 12.0 | ❌ |
| Philo T · intro dissert — réponse fausse | ≤ 8 | erreur (timeout/parse) | ❌ |

**Succès global : NON**
