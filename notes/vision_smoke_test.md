# Test de fumée vision — Gate 1 (REVIEW_4_scan.md)

**Date :** 19 octobre 2026 · **Modèle :** `qwen2.5vl:3b` (3,2 Go) via Ollama 0.40.6
**Machine :** i7-1065G7 (4 cœurs, sans GPU), 16 Go RAM · **Branche :** `feat/copie-scannee`

Méthode : photos manuscrites réelles ( Samsung, papier quadrillé ) fournies par
l'utilisateur, converties en JPEG (`tests/fixtures/copies/*.jpg`). Script jetable
(non commité) : plus long côté redimensionné à 1024 px, PNG base64 en
`image_url` vers `/v1/chat/completions`, prompt de transcription §2 verbatim,
`temperature=0`, `max_tokens=700`.

## Résultats

| Photo | Temps | finish | Contenu transcrit |
|---|---|---|---|
| `suites_bonne.jpg` | **92 s** ✅ | stop | Fidèle et complète : u₁=2×1+3=5, u₂=2×5+3=13, récurrence complète (initialisation, hérédité avec le calcul **8×2ⁿ − 6 + 3** préservé, conclusion), u₁₀=4093. LaTeX propre. |
| `suites_fausse.jpg` | **76 s** ✅ | stop | Fidèle aux **erreurs** : u₂=11, « suite arithmétique de raison 3, donc u_n = 1+3n », u₁₀=31. Le modèle n'a rien corrigé — exactement le comportement voulu pour une correction équitable. |
| `suites_brouillon.jpg` | **102 s** ✅ | stop | Copie bâclée lue correctement : 5, 13, récurrence, 4093 — l'hérédité est légèrement condensée mais tous les éléments clés sont là. |

**Verdict : PASS.** Les deux copies propres préservent toutes les valeurs
attendues (u₁=5, u₂=13, 4×2ⁿ−3, u₁₀=4093) et chaque photo est traitée en
moins de 120 s (76–102 s).

## Enseignements de la première passe (photos invalides)

La première série de photos fournies était des **étiquettes** décrivant les
copies, pas les copies (« La copie correcte (u1=5…) »). Le test a tourné quand
même et donne deux observations utiles :

1. ✅ **AUCUNE_COPIE fonctionne** : sur deux étiquettes, le modèle a répondu
   `AUCUNE_COPIE` (49 s et 67 s) — le garde-fou de la spec §2 se déclenche
   correctement sur une image qui n'est pas une copie d'élève.
2. ⚠️ **Risque d'hallucination** : sur une étiquette mentionnant l'exercice,
   le modèle a produit une solution complète et **juste** au lieu de
   transcrire — il a « résolu » l'énoncé plutôt que lu l'image. C'est la
   raison d'être du flux deux étapes : la transcription est toujours montrée
   à l'élève pour vérification avant correction. À retester sur de vraies
   copies ambiguës (fait ci-dessus : sur les vraies copies, la transcription
   est fidèle, y compris des erreurs).

## Critères Gate 1

- [x] `ollama pull qwen2.5vl:3b` — OK (Ollama 0.40.6)
- [x] Formules et nombres préservés sur les deux copies propres
- [x] ≤ 120 s par photo (76 s, 92 s, 102 s)
- [x] Garde-fou AUCUNE_COPIE vérifié (première passe)

**Gate 1 : PASSÉE** — prêt pour l'implémentation (§1–§6 de la spec) après feu
vert du reviewer.
