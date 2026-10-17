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

## Itération 2 — scoring explicite par question

- « correction_detaillee commence par Q1 : 4/4 — commentaire … ; la note est
  la somme des points » : le calcul explicite aide les petits modèles.
  → 2nd degré bonne : 13-14 → 15 ✓ ; 2nd degré fausse : 8 ✓ ; MRUA fausse et
  philo bonne inchangées (10-11 / 12).

## Robustesse code (accompagne les itérations)

- `Grade` : coercion de types voisins (correction_detaillee en liste → texte ;
  erreurs en chaîne → liste) — première cause d'échec après les timeouts.
- `chat_json(max_tokens=...)` : 900 (génération) / 520 (correction) — les
  petits modèles ignorent les consignes de concision (sorties observées à
  1884 tokens) ; borne la latence (corrections passées de 30-150 s à 25-60 s).
- Réparation générique des échappements JSON invalides (`\in`, `\Delta`…)

## Itérations 3-5 — règles métier (sciences / dissertation / citation de l'élève)

- « formule fausse dès le départ = 0 à la question », « résultat numérique
  final faux = 0 », « cite le passage fautif de l'élève », « Total : n/20 »,
  « applique le barème à la lettre ».
- Constat : **aucun effet** sur les deux cas récalcitrants avec qwen2.5:3b :
  - MRUA réponse fausse : 10-11/20 (devrait être ≤ 8) — le modèle ne lit pas
    la copie (confabule la bonne réponse) ;
  - Philo bonne réponse : 11-12/20 (devrait être ≥ 14) — sous-value la méthode.

## Verdict et options (CHECKPOINT)

`qwen2.5:3b` : rapide partout, juste sur les maths (suites, 2nd degré),
biaisé sur physique (trop laxiste) et dissertation (trop sévère).
`qwen2.5:7b` (testé sur ces 2 cas, prompts identiques) : **notes justes**
(8,0 et 14,0) mais ~50 % de dépassements du timeout de 120 s sur CPU 4 cœurs.

Options pour le reviewer :
1. Garder 3b par défaut (machine modeste) + note « indicative » (AI.md) ;
   6-7/8 cas à l'éval.
2. `LLM_MODEL=qwen2.5:7b` + `TIMEOUT_S=240` pour les machines rapides/GPU :
   éval probablement 8/8 — à confirmer par le reviewer sur sa machine.
3. Double modèle (génération 3b / correction 7b) : hors plan actuel
   (une seule variable `LLM_MODEL`), à décider.

Résultat officiel de la dernière itération : `notes/eval_results.md`.
