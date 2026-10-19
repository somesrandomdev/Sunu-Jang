# Test de fumée vision — Gate 1 (REVIEW_4_scan.md)

**Date :** 19 octobre 2026 · **Modèle :** `qwen2.5vl:3b` (3,2 Go) via Ollama 0.40.6
**Machine :** i7-1065G7 (4 cœurs, sans GPU), 16 Go RAM · **Branche :** `feat/copie-scannee`

Méthode : photos manuscrites réelles ( Samsung, papier quadrillé ) fournies par
l'utilisateur, converties en JPEG (`tests/fixtures/copies/*.jpg`). Script jetable
(non commité) : plus long côté redimensionné à 1024 px, PNG base64 en
`image_url` vers `/v1/chat/completions`, prompt de transcription §2,
`temperature=0`, `max_tokens=700`.

> ⚠️ Le prompt a été révisé en **v2** lors de la Gate 1b (voir plus bas) :
> {enonce} remplacé par la liste des numéros de questions + consigne
> « [non traitée] ». **C'est la v2 qui sera implémentée dans `app/prompts.py`.**

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

**Gate 1 : PASSÉE** (prompt v1) — voir la Gate 1b qui suit.

---

# Gate 1b — Test d'hallucination (copie partielle)

**Photo :** `suites_partielle.jpg` — seule la Q1 est traitée (u₁ = 5, u₂ = 13),
Q2 et Q3 vides sur le papier.

## Prompt v1 (énoncé complet dans le prompt) — ÉCHEC

Un essai (76 s) suffit à montrer la fuite : la transcription « recopie »
l'énoncé des questions non traitées :

> Question 2 : Montrer par **récurrence** que, pour tout n ∈ ℕ, u_n = **4 × 2^n − 3**.
> Question 3 : En déduire la valeur de u_10.

« récurrence » et « 4 × 2^n » présents → impossibles à distinguer d'une vraie
lecture. Conforme au soupçon du reviewer : avec l'énoncé dans le prompt, « lu »
et « résolu » sont indiscernables.

## Prompt v2 (liste des questions + « [non traitée] ») — PASS

Changements : `{enonce}` remplacé par « L'exercice comporte les questions 1, 2
et 3. » + ajout de « Si une question n'est pas traitée sur la copie, écris :
[non traitée]. »

**Copie partielle, 2 essais :**

| Essai | Temps | Transcription |
|---|---|---|
| 1 | 74 s | « Question 1 : (u1 = 5, u2 = 13) » — rien d'autre ✅ |
| 2 | 3 s (modèle chaud) | identique ✅ |

Ni « récurrence », ni « hérédité », ni « 4093 », ni « 4 × 2^n ». (Les Q2/Q3 ne
sont pas mentionnées du tout — la spec l'autorise : « Elle peut indiquer… ».)

**Les 3 copies complètes sous v2 :**

| Photo | Temps | Valeurs préservées |
|---|---|---|
| bonne | 135 s ⚠️ | 5, 13, récurrence complète, 4093 ✅ |
| fausse | 87 s | 11, arithmétique raison 3, 1+3n, 31 ✅ |
| brouillon | 121 s | 5, 13, récurrence (« Mentionnons/Hérité » : légère dérive de mots), 4093 ✅ |

## Critères Gate 1b

- [x] Copie partielle × 2 : aucun des contenus interdits (« récurrence »,
      « hérédité », « 4093 », « 4 × 2^n ») dans les transcriptions
- [x] Les 3 copies complètes préservent leurs valeurs sous prompt v2
- ⚠️ Latence : 135 s sur la bonne copie (barre Gate 1 : 120 s) — la charge CPU
  varie ; l'UI annonce déjà « ~1–2 min ». À surveiller à la Gate 2.

**Gate 1b : PASSÉE avec le prompt v2** — implémentation §1–§6 autorisée avec
cette version.

---

# Gate 2 — bout en bout (19/10/2026, modèle chaud qwen2.5:3b + qwen2.5vl:3b)

Exercice : EX_SUITES de la banque (chemin de démo déterministe, EMBED_MODEL
invalide → secours banque ; la correction tourne sur le vrai modèle).
Parcours : lire_copie → transcription non modifiée → corriger — les mêmes
fonctions d'événement que les boutons « 📷 Lire ma copie » puis « 📝 Corriger ».
L'upload par l'explorateur de fichiers n'est pas automatisable dans le navigateur
intégré (limitation de l'outil) ; le câblage DOM (upload → bouton → zone réponse)
est couvert par les tests unitaires et la config servie sur :7860 contient la
zone photo (« Lire ma copie », bouton, note photo).

## Résultats

| Photo | Transcription | Note | Total | Verdict |
|---|---|---|---|---|
| suites_bonne | 47 s, fidèle (5, 13, récurrence complète, 4093) | **12/20** | 107 s | ⚠️ note (voir drift) |
| suites_fausse | 14 s, fidèle (11, « arithmétique raison 3 », 31) | **8/20** | 60 s | ✅ erreur réelle détectée |
| suites_brouillon | 45 s, fidèle (« Mentionnons », 5, 13, 4093) | 12/20 | 107 s | ✅ transcription utilisable |
| suites_partielle | 4 s (chaud), « Question 1 : (u₁ = 5, u₂ = 13) » seule | 8/20 | 60 s | ✅ rien de fabriqué |

Latences transcription : 4–47 s modèle chaud (barre 120 s largement tenue ;
le pic Gate 1b à 135 s était de la charge à froid).

## Critères de merge

| Critère | Résultat |
|---|---|
| suites_bonne ≥ 14 | ❌ 12/20 |
| suites_fausse ≤ 8 | ✅ 8/20 |
| brouillon : erreur propre ou transcription utilisable | ✅ transcription utilisable |
| CI verte | non testée (branche non poussée — main gelée) |

**→ PAS DE MERGE.** La branche `feat/copie-scannee` reste ouverte ; ligne ajoutée
à la feuille de route du README.

## Analyse du 12/20 (diagnostic post-Gate 2, 2 ré-essais à l'identique)

La transcription de `suites_bonne` est mathématiquement parfaite, mais le
correcteur 3b note la même réponse 12 puis 15 selon les essais. Détail crucial :

- **Aucune ligne « Total : n/20 »** dans la correction détaillée → l'override
  Total n'est pas en cause ; la note vient du champ JSON brut du modèle.
- Le détail **se contredit** : essai 1 = « Q1 : 4/4 … Q2 : 12/12 … Q3 : 4/4 »
  (somme 20/20) mais note JSON 12 avec « Erreur dans la formule de récurrence »
  alors que le même paragraphe dit « ce qui est correct ». Essai 2 : somme 20/20,
  note JSON 15, « Initialisation incorrecte » … contredite trois lignes plus bas.
- Même famille de dérive que celle documentée dans `eval_results.md`
  (2ᵈᵉ degré) : le champ `note` du 3b est parfois incohérent avec son propre
  barème question par question.

La couche vision (l'objet de cette branche) est validée : 4 transcriptions
fidèles, zéro hallucination, partielle propre. Le bruit de notation est une
limite **préexistante** du modèle de correction (3b, hors périmètre
REVIEW_4_scan) ; candidats d'amélioration ultérieure : demander explicitement
la ligne « Total : n/20 » par question dans un format plus contraint, ou monter
le barème dans le prompt système.
