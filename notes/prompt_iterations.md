# Itérations de prompts — M2

Modèle : `qwen2.5:3b` (choix provisoire du Checkpoint 1). Chaque changement
ci-dessous ne touche QUE `app/prompts.py` (règle du plan, §6 M2).

## Baseline (prompts §5 verbatim) — 2026-10-17 13:36

8 cas × 3 runs, durée 1664 s → **2/8 cas passés** (`notes/eval_results.md`).

Diagnostic (sorties brutes capturées dans `notes/brut_eval.log`) :

1. **4 cas « erreur (timeout/parse) »** : en réalité des **timeouts** — toutes
   les sorties brutes capturées sont du JSON valide. Cause : `correction_detaillee`
   beaucoup trop longue (le modèle rédige 15+ lignes de LaTeX) → > 120 s.
2. **Philo bonne réponse = 12/20** : le modèle sous-note les copies complètes
   (il sanctionne un détail et plafonne la note).
3. **Écho du template** : le modèle recopiait les libellés du template JSON
   (« étape par étape », « répartition des points sur 20 ») en début de champ.

## Itération 1 — GRADE_ANSWER + GENERATE_EXERCISE

- Placeholders du template JSON remplacés par des `<...>` explicites +
  consigne « ne recopie jamais les chevrons ni leur libellé » (anti-écho).
- Consigne de concision : « correction_detaillee en 10 lignes maximum,
  un seul conseil court » (anti-timeout).
- Calibration du barème : « question par question ; copie majoritairement
  fausse < 8/20 ; copie complète et juste ≥ 15/20 » (anti-laxisme / anti-sévrité).

Résultat : voir la dernière table dans `notes/eval_results.md`.
