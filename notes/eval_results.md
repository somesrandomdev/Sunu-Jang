# Résultats d'évaluation — 2026-10-17 22:12

Modèle : `qwen2.5:3b` · 3 exécutions par cas · durée : 1259 s
*(après revue 2 — steps A à D : contexte Ollama 8192, réessais sans ré-append,
note lue sur « Total : n/20 », banque de secours ; machine refroidie 10 min.
Toutes les 24 corrections ont produit un Grade : plus aucune erreur de
parsing/timeout. Cas manqués : 2nd degré bonne (analysé ci-dessous — dérive
du modèle, pas un effet Step C), MRUA fausse et philo bonne (biais connus
du 3b : trop laxiste en physique, trop sévère en dissertation).)*

## Analyse du cas « 2nd degré — bonne réponse » (revue 3, 18 oct)

Consigne de la revue : vérifier si l'échec est une régression du Step C
(note écrasée par un « Total » plus sévère que la note JSON). Trois runs,
avec les DEUX valeurs (script jetable, non commité ; Ollama 0.40.6) :

| Run | Note JSON | Total lu | Note finale |
|---|---|---|---|
| 0 | 11 | 11 | 11 |
| 1 | 12 | 12 | 12 |
| 2 | 11 | 11 | 11 |

**Conclusion : ce n'est PAS une régression du Step C.** Note JSON et « Total »
sont identiques sur les 3 runs — Step C ne change rien ici — et la note du
modèle est remontée sévère d'elle-même. Chronologie du cas : 15/15 (sonde
itération 2, 17 oct ~14:45) → 12-13 (éval 15:03, AVANT les steps B-D) →
12/12 (éval 20:22, avant aussi) → 12-13 (éval 22:12) → 11-12 (18 oct).
Étiquette honnête : **dérive du modèle d'une session à l'autre sur ce cas**
(instabilité de notation du 3b), pas un effet du correctif Step C.
Step C conservé : il corrige le cas inverse (note JSON ≠ somme des points,
par ex. MRUA 10/20 vs Total 4/20 observé le 17 oct après-midi).

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
