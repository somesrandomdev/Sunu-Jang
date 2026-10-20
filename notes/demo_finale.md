# Démo finale — Sunu Jàng (7 min + 3 min de questions)

Pitch de 7 minutes devant le jury, 3 minutes de questions. Tout tourne en local
sur le portable (CPU, pas de GPU). Le film de démo (1:45, youtu.be/tdOB__0e2DY)
couvre la génération ; le live couvre la photo de copie et la correction.

## Préparation (avant de monter)

| Quand | Action |
|---|---|
| T–30 min | Vérifier Ollama : `ollama ps` vide OK ; s'assurer que le serveur tourne avec `OLLAMA_MODELS=D:/ollama/models`, `OLLAMA_CONTEXT_LENGTH=8192`, `OLLAMA_KEEP_ALIVE=30m`, `OLLAMA_MAX_LOADED_MODELS=2` (le tray Ollama redémarre parfois SANS ces variables → tuer `ollama app.exe` + `ollama.exe` et relancer `ollama serve`). |
| T–10 min | `python -m app.ui` → le préchauffage (Step B) charge les deux modèles tout seul ; vérifier dans la console « Modèle préchauffé » ×2. |
| T–5 min | Cliquer « ✨ Nouvel exercice » (Maths, Terminale, moyen, thème « suites numériques ») pour que l'exercice soit prêt à l'écran — la génération n'est PAS faite en live (limite CPU documentée). Copier la bonne réponse tapée (démo/demo_reponses.txt) dans le presse-papiers. |
| T–2 min | Fenêtre du navigateur en plein écran sur l'app. Photo `tests/fixtures/copies/suites_fausse.jpg` prête dans le dossier Téléchargements. |

## Déroulé minute par minute

| Minute | Ce qu'on fait | Ce qu'on dit (l'essentiel) |
|---|---|---|
| 0:00–1:00 | **Le problème.** Diapos : un élève sénégalais, pas de prof disponible à 23 h, copies rendues une semaine plus tard. | « 180 000 candidats au BAC, des classes de 40 à 60 élèves. Un élève qui bloque à 23 h n'a personne à qui demander. Sunu Jàng : un professeur particulier IA, 100 % local, qui parle français et ancre ses exercices dans les vraies annales. » |
| 1:00–2:00 | **Génération (film).** Extraits du film : choix matière/niveau/thème → exercice affiché avec « Inspiré de : maths_S2_2023.pdf p.3 ». | « La génération avec annales est gourmande sur ce CPU : on la montre en film, elle tourne chez nous. Notez la source : jamais d'invention hors programme — le RAG montre de vraies annales au modèle. » |
| 2:00–4:30 | **LIVE — la photo de copie.** Upload `suites_fausse.jpg` → « 📷 Lire ma copie » → la transcription apparaît dans « Ta réponse » (l'erreur « la suite est arithmétique de raison 3 » est recopiée telle quelle) → « Corriger » → **0/20**, erreurs détaillées, correction complète. | « Sur papier comme en classe : je photographie ma copie. Un second modèle la transcrit — regardez, il recopie même ma faute, il ne corrige rien lui-même. Je vérifie la transcription (elle est modifiable : l'humain garde la main) et je me fais corriger. 0/20 : la règle "résultat final faux = 0" est appliquée, et surtout le détail explique POURQUOI. » Pendant que la correction tourne (~1 min), dérouler le discours : deux modèles, le vision ne note jamais. |
| 4:30–6:00 | **LIVE — la bonne réponse.** Coller la bonne réponse → « Corriger » → **20/20**, points forts → « ➡️ Exercice suivant » → la difficulté passe à « difficile ». | « Même exercice, bonne réponse : 20/20, et l'app s'adapte — difficulté suivante plus dure. La note est la somme des points que le modèle attribue question par question, pas un chiffre qu'il invente en vrac. » |
| 6:00–6:45 | **Open source + IA.** GitHub : MIT, `AI.md` (rôle exact de l'IA, licence du modèle vision), tests en CI, jeu d'évaluation fixe : 7/8 mesurés. | « Tout est open source et documenté — y compris ce qui ne marche pas encore : les limites sont écrites dans le README et AI.md, avec les mesures. » |
| 6:45–7:00 | **Feuille de route.** Wolof (bêta) puis Pulaar, Sérère ; plus d'annales ; tableau de bord enseignant. | « Un prof particulier pour chaque élève du Sénégal — en wolof ensuite. » |

### Plans de secours (par étape)

- **La transcription met plus de 2 min ou échoue** : les modèles sont chauds
  (préchauffage T–10 min, keep-alive 30 m) — 15 à 95 s mesurés. Si échec
  quand même : retenter « Lire ma copie » une fois ; sinon continuer au clavier
  (« je vous ai préparé la même réponse tapée ») et montrer le film.
- **La transcription contient une erreur visible** : la corriger EN LIVE —
  « c'est voulu : la transcription est modifiable, l'élève vérifie ».
- **« Corriger » dépasse 2 min** : narrer la correction détaillée qui s'affiche
  pendant qu'elle finit (le bouton reste bloqué, aucun crash).
- **« Exercice suivant » échoue à régénérer (limite CPU documentée)** : la
  difficulté « difficile » est DÉJÀ visible dans le menu déroulant avant la
  régénération — commenter ce point et enchaîner ; l'échec de génération
  affiche un message français propre, pas un crash.
- **Ollama meurt en plein live** : relancer `ollama serve` (commande préparée
  dans un terminal), les messages d'erreur de l'app guident ; dernier recours :
  le film + captures d'écran couvrent tout le parcours.

## Les 6 questions probables du jury

1. **« Et si le modèle note mal ? »**
   C'est mesuré et assumé : la note est **indicative**, l'élève voit toujours
   la correction détaillée question par question et se reporte à son prof en
   cas de doute. On a un jeu d'évaluation fixe (7/8 aujourd'hui) et les limites
   sont écrites noir sur blanc dans le README — y compris une copie partielle
   notée 8/20 pour un barème strict à 4.
2. **« Pourquoi 100 % local ? »**
   Trois raisons : le **coût** (aucun appel API payant par élève), la
   **confidentialité** (des photos de copies d'élèves mineurs ne quittent
   jamais l'établissement), et le **réseau** (ça marche sans internet fiable,
   sur un PC sans GPU).
3. **« Pourquoi deux modèles ? »**
   Lire une écriture manuscrite et évaluer des maths sont deux compétences
   différentes. Le modèle vision transcrit — **jamais** il ne note ; l'élève
   relit la transcription (modifiable), puis le modèle de chat corrige comme
   pour une réponse tapée. Test à l'appui : quand on donnait l'énoncé au
   modèle vision, il inventait les réponses aux questions non traitées ;
   ce prompt est corrigé et le test est documenté.
4. **« Combien ça coûte pour un lycée ? »**
   Le matériel : un PC standard récent suffit (CPU 4 cœurs, ~6 Go de RAM pour
   les deux modèles). Logiciel : Ollama + modèles gratuits, code MIT. Seule
   nuance : le modèle vision (transcription) est sous licence de recherche
   Qwen — l'usage éducatif/recherche est couvert, un usage commercial
   d'Alibaba Cloud nécessiterait un accord.
5. **« Comment empêchez-vous les hallucinations ? »**
   Couche par couche : à la **génération**, le RAG ancre l'exercice dans de
   vraies annales et la source est affichée ; à la **correction**, le modèle
   reçoit le corrigé de référence et le barème, répond en JSON validé par un
   schéma, et la note affichée est la somme de ses points par question — pas
   un chiffre libre ; à la **transcription**, le prompt ne contient pas
   l'énoncé (test anti-hallucination Gate 1b) et l'humain relit avant notation.
6. **« Et après le hackathon ? »**
   Trois priorités honnêtes : trouver 2–3 profs pilotes à Dakar pour tester
   avec de vrais élèves (le jeu d'éval ne remplace pas le terrain), ajouter
   les annales SVT/2ᵉ groupe, et le wolof — la langue dans laquelle les élèves
   raisonnent. Le code, les tests et les mesures de qualité sont déjà là pour
   que d'autres contributeurs s'y mettent.
