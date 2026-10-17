# Test de fumée des modèles — CHECKPOINT 1

**Date :** 17 octobre 2026 · **Machine cible :** Intel i7-1065G7 (4 cœurs, 1,3 GHz),
16 Go RAM, **pas de GPU** — inférence CPU pure via Ollama 0.40.5.
Protocole (PLAN.md §6 M0) : pour chaque candidat, une génération
(Maths · Terminale · moyen · « suites numériques ») + une correction
(Maths Terminale, réponse volontairement fausse, note attendue ≤ 8),
prompts de §5 verbatim. Sorties brutes plus bas, dans l'ordre du tableau.

## Synthèse

| Modèle | Génération | Correction | Note (réponse fausse) | Verdict |
|---|---|---|---|---|
| **qwen2.5:3b** | ✅ 35 s (mais copie les placeholders du template) | ✅ 49 s | 0,0 ✅ (sévère) | **CHOIX PROVISOIRE** |
| llama3.2:3b | ❌ JSON invalide ×2 (154 s) | ✅ 76 s | 14,0 ❌ (trop laxiste) | rejeté |
| gemma3:4b | ❌ timeout 120 s | ❌ timeout 120 s | — | rejeté (trop lent) |
| qwen2.5:7b | ❌ timeout 120 s | ✅ 76 s | 8,0 ✅ | rejeté (trop lent) |
| llama3.1:8b | ❌ 119 s + réessai, puis timeout en correction | ❌ timeout 120 s | — | rejeté |
| mistral:7b | non testé | non testé | — | non testé (voir note) |

## Recommandation (à confirmer par le reviewer)

`LLM_MODEL=qwen2.5:3b` — le seul candidat qui tient le budget de 120 s en
génération ET corrige avec la bonne sévérité. Deux réserves :

1. **Qualité de génération** : il recopie parfois les placeholders du template
   JSON (« répartition des points sur 20 », corrigé = « solution complète, étape
   par étape »). C'est un problème de PROMPT, pas de code : l'itération M2
   (scripts/eval.py) doit le corriger en rendant le template moins imitable.
   Si l'éval n'y arrive pas, revenir au reviewer pour arbitrer
   (timeout > 120 s + qwen2.5:7b ?).
2. **mistral:7b non testé** : même classe (7B Q4) que qwen2.5:7b et
   llama3.1:8b, tous deux hors budget en génération ; tirage économisé pour
   tester les candidats 3-4B, plus adaptés à cette machine.

Toute la configuration passe par `LLM_MODEL` : changer de modèle ne touche
aucune ligne de code.

---


---

## Modèle : `qwen2.5:3b`

### Génération (Maths · Terminale · moyen · suites) — 35 s

**Titre :** Étudier la suite définie par $u_n = 2n^2 - 3n + 1$ pour $n \geq 1$

**Énoncé :**

Calculer la valeur de $u_4$ et déterminer la nature de la suite $u_n$.

**Barème :** répartition des points sur 20

**Compétences :** Comprendre la définition d'une suite, Calculer des termes d'une suite, Déterminer la nature d'une suite

**Corrigé (extrait) :**

Solution complète, étape par étape.

### Correction (réponse fausse attendue ≤ 8) — 49 s

**Note :** 0.0

**Points forts :** 

**Erreurs :** 1. Calcul de $u_1$ et $u_2$ incorrect : il faut utiliser la formule $u_{n+1} = 2u_n + 3$. ; 2. La réponse de récurrence est incorrecte : elle ne respecte pas la structure demandée. ; 3. La valeur de $u_{10}$ est incorrecte : elle ne correspond pas à la formule $u_n = 4 	imes 2^n - 3$.

**Correction détaillée (extrait) :** Voici comment corriger la réponse de l'élève :

**Conseil :** Réviser les formules de récurrence et les calculs de suite. Utiliser la formule $u_n = 4 	imes 2^n - 3$ pour déterminer $u_{10}$.


---

## Modèle : `qwen2.5:7b`

### Génération — ÉCHEC après 125 s

```
Le modèle local ne répond pas. Vérifiez qu'Ollama est lancé.
```

### Correction (réponse fausse attendue ≤ 8) — 76 s

**Note :** 8.0

**Points forts :** Calculs corrects pour u_1 et u_2 ; Réponse directe pour u_10

**Erreurs :** Mauvaise identification de la nature de la suite ; Absence de récurrence pour la question 2 ; Erreur dans l'expression de u_n

**Correction détaillée (extrait) :** étape par étape

**Conseil :** Pratiquez plus la récurrence et l'identification des types de suites.


---

## Modèle : `llama3.1:8b`

### Génération (Maths · Terminale · moyen · suites) — 119 s

**Titre :** Analyse d'une suite numérique

**Énoncé :**

Étudier la suite $(u_n)_{ninbbr}$ définie par $u_n = 2n^2 + 3n - 4$ et répondre aux questions suivantes :

a) Écrire la suite sous forme de liste et la numérototer.

b) Déterminer si la suite est arithmétique, géométrique ou ni l'un ni l'autre.

c) En déduire si la suite est convergente ou divergente.

**Barème :** 5 points pour l'expression de la suite, 5 points pour la détermination de la nature de la suite, 5 points pour la conclusion sur la convergence ou la divergence, 5 points pour la présentation et la clarté.

**Compétences :** Définition et expression d'une suite numérique, Analyse de la nature d'une suite numérique, Convergence ou divergence d'une suite numérique

**Corrigé (extrait) :**

La suite est exprimée sous forme de liste numérotée, et la nature de la suite est clairement identifiée. La conclusion sur la convergence ou la divergence est logique et correcte. La présentation est claire et facile à suivre.

### Correction — ÉCHEC après 120 s

```
Le modèle local ne répond pas. Vérifiez qu'Ollama est lancé.
```


---

## Modèle : `llama3.2:3b`

### Génération — ÉCHEC après 154 s

```
Le modèle n'a pas renvoyé de réponse exploitable après deux essais. Relancez la génération.
```

### Correction (réponse fausse attendue ≤ 8) — 76 s

**Note :** 14.0

**Points forts :** Réponse claire et concise

**Erreurs :** 1. u_1 = 2*1 + 3 = 5 et u_2 = 2*5 + 3 = 11. La réponse est incorrecte, la suite est définie par u_{n+1} = 2u_n + 3. ; 2. La suite n'est pas arithmétique de raison 3, mais plutôt une suite linéaire définie par u_{n+1} = 2u_n + 3. La formule générale est u_n = 4 \times 2^n - 3. ; 3. u_{10} = 1 + 3*10 = 31. La réponse est incorrecte, la formule générale est u_{10} = 4 \times 2^{10} - 3 = 4093.

**Correction détaillée (extrait) :** 1. u_1 = 2*1 + 3 = 5 et u_2 = 2*5 + 3 = 13. La réponse est incorrecte, la suite est définie par u_{n+1} = 2u_n + 3. 
2. La formule générale est u_n = 4 \times 2^n - 3. 
3. u_{10} = 4 \times 2^{10} - 3 = 4093.

**Conseil :** Pour progresser, il faut bien comprendre les séquences linéaires et les formules générales. Il faut également vérifier soigneusement ses réponses et utiliser les propriétés des séquences pour simplifier les calculs. Enfin, il faut pratiquer régulièrement pour améliorer ses compétences en mathématiques.


---

## Modèle : `gemma3:4b`

### Génération — ÉCHEC après 125 s

```
Le modèle local ne répond pas. Vérifiez qu'Ollama est lancé.
```

### Correction — ÉCHEC après 122 s

```
Le modèle local ne répond pas. Vérifiez qu'Ollama est lancé.
```
