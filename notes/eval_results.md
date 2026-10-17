# Résultats d'évaluation — 2026-10-17 22:12

Modèle : `qwen2.5:3b` · 3 exécutions par cas · durée : 1259 s
*(après revue 2 — steps A à D : contexte Ollama 8192, réessais sans ré-append,
note lue sur « Total : n/20 », banque de secours ; machine refroidie 10 min.
Toutes les 24 corrections ont produit un Grade : plus aucune erreur de
parsing/timeout. Les 3 cas manqués sont les biais connus du 3b.)*

| Cas | Attendu | min / max | Pass |
|---|---|---|---|
| Maths T · suites — bonne réponse | ≥ 14 | 14.0 / 15.0 | ✅ |
| Maths T · suites — réponse fausse | ≤ 8 |  8.0 /  8.0 | ✅ |
| Maths 1re · 2nd degré — bonne réponse | ≥ 14 | 12.0 / 13.0 | ❌ |
| Maths 1re · 2nd degré — réponse fausse | ≤ 8 |  8.0 /  8.0 | ✅ |
| Physique T · MRUA — bonne réponse | ≥ 14 | 15.0 / 15.0 | ✅ |
| Physique T · MRUA — réponse fausse | ≤ 8 | 11.0 / 11.0 | ❌ |
| Philo T · intro dissert — bonne réponse | ≥ 14 | 11.0 / 12.0 | ❌ |
| Philo T · intro dissert — réponse fausse | ≤ 8 |  8.0 /  8.0 | ✅ |

**Succès global : NON**
