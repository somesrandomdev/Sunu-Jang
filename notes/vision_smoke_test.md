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

---

# Gate 2 bis — après « note = somme des points par question » (19/10/2026, soir)

Correctif : `_note_depuis_correction` (app/tutor.py) — somme des lignes
« Qn : a/b » si chaque a ≤ b et Σb = 20, sinon « Total : n/20 », sinon note JSON.
Re-mesure : éval d'abord (6/8, aucune régression — voir `eval_results.md`), puis
les 4 photos en séquentiel, processus seul. Script jetable (scratchpad, non commité)
appelant `transcrire_copie` puis `grade_answer` sur EX_SUITES, avec un espion sur
`chat_json` pour relever la note JSON brute.

| Photo | Transcr. | Corr. | Lignes Q lues | Σ dénominateurs | Note JSON | Note finale | Attendu | Verdict |
|---|---|---|---|---|---|---|---|---|
| suites_bonne | 156 s | 72 s | Q1 4/4 seule | 4 → repli | 12 | **12** | ≥ 14 | ❌ |
| suites_fausse | 90 s | 86 s | Q1 4/4, Q3 4/4 | 8 → repli | 8 | **8** | ≤ 8 | ✅ |
| suites_brouillon | 127 s | 72 s | Q1 4/4, Q2 12/12, Q3 0/4 | 20 ✅ | 15 (Total 15/20) | **16** | — | ✅ utilisable |
| suites_partielle | 82 s | 66 s | Q1 4/4 seule | 4 → repli | 8 | **8** | ≤ 6 | ❌ |

## Analyse

- **Le correctif fait ce qu'il doit, mais ne s'est déclenché qu'une fois sur 4.**
  Sur bonne / fausse / partielle, le 3b n'a écrit qu'une partie des lignes
  « Qn : a/b » (le reste de la correction est en prose, sans points) : Σb ≠ 20 →
  repli correct sur la note JSON, qui reste fausse (12 pour bonne, 8 pour partielle).
  À la Gate 2, il avait écrit les 3 lignes (4 + 12 + 4) ; cette fois non — même
  instabilité de format d'un run à l'autre.
- **partielle** : seule la Q1 est traitée ; une notation juste serait 4/20. Le
  modèle écrit bien « Q1 : 4/4 » mais ne note pas les questions non traitées ;
  la note JSON (8) est trop généreuse.
- **brouillon** : la somme (16) l'emporte sur « Total : 15/20 » (ordre voulu) ;
  le détail est lui-même faux (« Q3 : 0/4 … 4093, ce qui est faux »).
- **Transcription bonne** : cette fois l'étape « − 6 + 3 » de l'hérédité est
  sautée (« 8 × 2ⁿ − 3 » directement) — elle était préservée aux Gates 1/2.
  Le résultat reste mathématiquement juste ; c'est le correcteur qui y voit des
  « erreurs » inexistantes.
- Latences transcription 82–156 s (modèle froid à chaque photo, processus seul) :
  au-dessus de la barre 120 s sur bonne et brouillon.

## Critères

| Critère | Résultat |
|---|---|
| suites_bonne ≥ 14 | ❌ 12 |
| suites_fausse ≤ 8 | ✅ 8 |
| suites_partielle ≤ 6 | ❌ 8 |

**→ toujours PAS DE MERGE.** Piste suivante (non implémentée, à décider) : le
barème d'EX_SUITES est connu (Q1 4, Q2 12, Q3 4) — on pourrait exiger une ligne
par question du barème dans le prompt, et/ou compter 0 pour une question du
barème absente du détail quand au moins une ligne Q est présente.

---

# Diagnostic notation (Step 1 de la review du 20/10) — extraits BRUTS

Protocole demandé : rejouer le chemin Gate 2 (transcription puis correction,
sans modification) pour `suites_bonne` et `suites_partielle`, et coller ici la
`correction_detaillee` brute **intégrale** avec la transcription envoyée au
correcteur. Aucun changement de code. État du code pendant ces runs : branche
avec le correctif 69c80bd (note = somme des lignes Qn) déjà actif.

Contexte machine : Ollama relancé avec `OLLAMA_KEEP_ALIVE=30m` et
`OLLAMA_MAX_LOADED_MODELS=2` (en plus de `OLLAMA_MODELS` et
`OLLAMA_CONTEXT_LENGTH=8192`). Deux tentatives ont échoué en APITimeoutError
(180 s) pendant le chargement à froid du modèle vision puis du modèle chat sur
machine encore chaude de la veille ; le chemin d'erreur a réagi comme prévu
(LLMError français, pas de stack trace côté élève). La 3ᵉ tentative, modèles
résidents, passe. Temps : transcription 21 s (bonne) / 59 s (partielle),
correction ~30-35 s.

## suites_bonne — transcription envoyée au correcteur (21 s)

```
1. \( u_1 = 2 \times 1 + 3 = 5 \)
   et \( u_2 = 2 \times 5 + 3 = 13 \)

2. Montrons par récurrence que \( u_n = 4 \times 2^n - 3 \).
   - Initialisation : \( u_0 = 1 \) et \( 4 \times 2^0 - 3 = 1 \), vrai au rang 0.
   - Hérédité : supposons \( u_n = 4 \times 2^n - 3 \).
      Alors \( u_{n+1} = 2u_n + 3 = 2(4 \times 2^n - 3) + 3 \)
      \( = 8 \times 2^n - 3 = 4 \times 2^{n+1} - 3 \).
   - Conclusion : pour tout \( n \), \( u_n = 4 \times 2^n - 3 \).

3. \( u_{10} = 4 \times 2^{10} - 3 = 4096 - 3 = 4093 \).
```

Note obtenue : **20/20** (total 56 s).

### correction_detaillee BRUTE (intégrale, non retouchée)

```
Q1 : 4/4 — L'élève a bien calculé $u_1$ et $u_2$ correctement. Pour la question
2, l'élève a bien noté l'initialisation et la hérédité, mais a commis une erreur
dans la formule de récurrence. Il a écrit $u_{n+1} = 2(4 \times 2^n - 3) + 3
= 8 \times 2^n - 3 = 4 \times 2^{n+1} - 3$ ce qui est faux. La formule correcte
serait $u_{n+1} = 2(4 \times 2^n - 3) + 3 = 8 \times 2^n - 3
= 4 \times 2^{n+1} - 3$. Pour la question 3, l'élève a bien calculé
$u_{10} = 4 \times 2^{10} - 3 = 4093$.

Q2 : 12/12 — L'élève a bien noté l'initialisation, la hérédité et la conclusion.
Il a bien noté que $u_0 = 1$ et $4 \times 2^0 - 3 = 1$, donc la propriété est
vraie pour $n = 0$. Il a bien noté que $u_{n+1} = 2u_n + 3 = 2(4 \times 2^n - 3)
+ 3 = 8 \times 2^n - 3 = 4 \times 2^{n+1} - 3$ ce qui est correct.

Q3 : 4/4 — L'élève a bien noté que $u_{10} = 4 \times 2^{10} - 3 = 4093$.
```

## suites_partielle — transcription envoyée au correcteur (59 s)

```
Question 1 : (u₁ = 5, u₂ = 13)
```

Note obtenue : **8/20** (total 89 s).

### correction_detaillee BRUTE (intégrale, non retouchée)

```
Q1 : 4/4 — L'élève a correctement calculé u1 et u2. Pour la question 2, il a
omis de démontrer par récurrence que u_n = 4 × 2^n - 3. Il ne devait pas
seulement calculer u1 et u2, mais aussi démontrer la formule par récurrence.
```

## Forme exacte des points, par question

- Forme observée dans les DEUX corrections : `Q1 : 4/4`, `Q2 : 12/12`,
  `Q3 : 4/4` — c'est-à-dire `Q<n> : <points>/<max>` (deux-points, barre
  directe, sans « points », sans gras, sans parenthèses). Aucune des variantes
  listées (`Question 2 : 12/12`, `**Q2** : 12/12`, `Q2 = 12/12`,
  `Q2 : 12 / 12 points`, `Q2 (12/12)`, `2) 12/12`) n'apparaît. C'est la même
  forme que celle qu'exploite `_note_depuis_correction` (commit 69c80bd).
- **La ligne « Total : n/20 » est ABSENTE de toutes les corrections capturées
  depuis la Gate 2 (6 au total)** : l'override Total ne déclenche jamais dans
  le flux photo.
- Pour la copie partielle, le modèle **n'écrit pas de lignes Q2/Q3 du tout**
  (pas de « Q2 : 0/12 ») : il n'existe aucune structure question-par-question
  exploitable pour les questions non traitées — seulement la prose (« il a
  omis de démontrer… »). Cohérent avec la Gate 2 bis.

## Lecture correcte des notes Step 1 (correction d'une analyse erronée
committée plus tôt dans cette section)

Ces runs tournent AVEC le correctif 69c80bd déjà en place. Donc :

1. **bonne = 20/20 vient de la SOMME des lignes Q** (4 + 12 + 4, Σdénominateurs
   = 20 → override), pas du champ JSON. La note affichée suit le détail quand
   le détail est complet — c'est le correctif qui fait son travail.
2. **partielle = 8/20 est la note JSON brute** : une seule ligne Q (Σb = 4 ≠ 20)
   → repli sur le JSON. La ligne chiffrée dit 4/4 ; les 4 points supplémentaires
   (8 − 4) ne sont écrits nulle part. La note sur-credit la copie, mais compter
   0 pour les questions absentes est une piste rejetée en Step 2 de la review.
3. **L'instabilité est dans le FORMAT de sortie, pas dans les lignes elles-mêmes** :
   quand le modèle écrit le barème complet, les lignes sont stables et somment à
   20/20 (Gate 2, diag 1, diag 2, Step 1 — 4 captures sur 5 ; la Gate 2 bis
   n'avait eu qu'« Q1 : 4/4 »). Ce qui varie d'un run à l'autre, c'est S'IL écrit
   toutes les lignes, et la note JSON quand il ne les écrit pas :
   12 (Gate 2, JSON), 12 (diag 1, JSON), 15 (diag 2, JSON), 8 (Step 1, JSON,
   copie partielle).
4. Incohérence token-level dans la ligne Q1 du Step 1 : le modèle qualifie
   « faux » une formule puis donne comme « formule correcte » exactement la
   même formule — sans impact sur les points (4/4) ici, mais c'est le même
   bruit que celui qui contredisait somme et note JSON avant correctif.

Conclusion (à valider avant tout correctif) : les lignes `Qn : a/b` sont le
signal fiable **quand elles sont toutes présentes** ; le point de fragilité
restant est le run où le modèle n'écrit qu'une partie du barème (repli JSON
bruité). C'est exactement le cas « Gate 2 bis » — et la piste « compter 0 »
pour ce cas est rejetée en Step 2.

---

# Gate 2 ×3 après Step A/B (revue 6, Step C2 — 20/10/2026, processus seul)

Chemin : `ui.lire_copie` → transcription non modifiée → `grade_answer` sur
EX_SUITES (banque), 3 runs par photo. Modèles gardés résidents
(`OLLAMA_KEEP_ALIVE=30m`, `OLLAMA_MAX_LOADED_MODELS=2`), préchauffage Step B.
Durée totale : ~24 min.

| Photo | Run | Note | Source | Transcr. | Correction | Total |
|---|---|---|---|---|---|---|
| bonne | 1 | 20/20 | points | 148 s | 62 s | 210 s |
| bonne | 2 | 20/20 | lignes | 42 s | 66 s | 108 s |
| bonne | 3 | 20/20 | lignes | 46 s | 51 s | 97 s |
| fausse | 1 | 0/20 | points | 95 s | 104 s | 200 s |
| fausse | 2 | 0/20 | points | 15 s | 65 s | 80 s |
| fausse | 3 | 0/20 | points | 13 s | 57 s | 70 s |
| brouillon | 1 | 20/20 | points | 117 s | 87 s | 203 s |
| brouillon | 2 | 20/20 | points | 46 s | 45 s | 91 s |
| brouillon | 3 | 20/20 | points | 45 s | 70 s | 115 s |
| partielle | 1 | 8/20 | points | 90 s | 66 s | 157 s |
| partielle | 2 | 8/20 | points | 4 s | 55 s | 59 s |
| partielle | 3 | 8/20 | points | 3 s | 76 s | 80 s |

## Attendu vs obtenu

| Critère | Attendu | Obtenu | Verdict |
|---|---|---|---|
| bonne ≥ 14 | 3/3 | **20/20/20** | ✅ 3/3 |
| fausse ≤ 8 | 3/3 | **0/0/0** | ✅ 3/3 |
| partielle ≤ 6 | 3/3 | **8/8/8** | ❌ 0/3 |
| brouillon utilisable | — | transcription fidèle | ✅ |

- **bonne** : 20/20 constant. La cascade de replis a travaillé : run 1 via le
  champ points, runs 2-3 le champ n'était pas exploitable (Σmax ≠ 20) mais les
  lignes « Qn » complètes ont pris le relais (« lignes ») — même note.
- **fausse** : 0/20 constant, source « points » ×3 — le modèle applique
  désormais la règle « résultat numérique faux = 0 » DANS le champ structuré
  (avant Step A il notait cette copie 4-8 en JSON et 10 en lignes).
- **partielle** : 8/20 STABLE (jamais ≤ 6). La copie ne traite que Q1
  (barème 4 + 12 + 4 : une notation barème-à-la-lettre donnerait 4) ; le
  modèle accorde 8 de façon constante via le champ points. C'est une
  sur-attribution stable, pas du bruit — décision à prendre : c'est le modèle
  qui juge « 8 », pas la mécanique de note.
- **brouillon** : transcription fidèle (récurrence complète, mêmes légères
  dérives de mots qu'aux Gates 1-2), note 20/20 ×3.
- Latence : premier run de chaque photo lent (90–148 s — rechargement vision
  après l'étape de correction), suivants 3–46 s. Corrections 45–104 s.

## Sources sur les 12 runs Gate 2

points 10/12 · lignes 2/12 · json 0/12 · total 0/12.

## Toutes mesures Step C confondues (24 runs d'eval + 12 runs Gate 2 = 36)

| Source | Runs | Part |
|---|---|---|
| points (champ JSON structuré) | 28 | 78 % |
| json (note brute, repli) | 6 | 17 % |
| lignes (« Qn : a/b ») | 2 | 5 % |
| total (« Total : n/20 ») | 0 | 0 % |
