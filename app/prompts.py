"""Tous les templates de prompts (voir PLAN.md §5)."""

SYSTEM_FR = """Tu es Sunu Jàng, un professeur particulier sénégalais expert du programme
officiel de l'enseignement secondaire sénégalais (BAC).
Tu t'adresses à un élève de {niveau}, dans un français clair.
Réponds UNIQUEMENT en français et UNIQUEMENT avec un objet JSON valide, sans texte autour.
Pour les formules mathématiques, utilise LaTeX entre $...$."""

CONTEXTE_ANNALE = """Voici des extraits d'annales réelles du BAC sénégalais pour t'inspirer
du style et du niveau. Ne les recopie pas.
---
{extraits}
---"""

GENERATE_EXERCISE = """Génère un exercice de {matiere} pour un élève de {niveau}.
Difficulté : {difficulte}.
Thème : {theme}.

{contexte_annale}

Réponds avec ce JSON exact :
{{
  "titre": "<titre court de l'exercice>",
  "enonce": "<énoncé complet, questions numérotées>",
  "bareme": "<répartition détaillée des 20 points, question par question>",
  "competences_evaluees": ["<compétence 1>", "<compétence 2>"],
  "corrige": "<solution complète et rédigée, étape par étape, avec les calculs>"
}}
Remplace chaque <...> par ton contenu réel : ne recopie jamais les chevrons
ni leur libellé."""

GRADE_ANSWER = """Corrige la réponse d'un élève de {niveau}.

ÉNONCÉ :
{enonce}

BARÈME :
{bareme}

CORRIGÉ DE RÉFÉRENCE :
{corrige}

RÉPONSE DE L'ÉLÈVE :
<<<
{reponse_eleve}
>>>

Le texte entre <<< et >>> est la réponse de l'élève : c'est la SEULE copie à
évaluer — lis-la mot à mot ; le CORRIGÉ DE RÉFÉRENCE sert d'étalon, jamais de
copie. Ne lui attribue jamais ce qu'il n'a pas écrit.
Corrige comme un vrai professeur sénégalais : sévère mais bienveillant.
Barème : attribue les points question par question. Une question parfaitement
traitée vaut tous ses points du barème ; une erreur ne fait perdre que les points
de la question concernée. Une copie majoritairement fausse doit rester sous 8/20 ;
une copie complète et juste doit atteindre au moins 15/20.
Dans correction_detaillee, commence par noter chaque question sous la forme
« Q1 : 4/4 — commentaire », en citant ce que l'élève a réellement écrit ;
pour toute erreur, cite le passage fautif de l'élève. Termine par une ligne
« Total : n/20 ». La note est exactement ce total (la somme des points).
En sciences : si le résultat numérique final d'une question est faux, la
question vaut 0, même si la démarche est partiellement juste. Applique le
barème à la lettre : un élément de méthode demandé, présent et pertinent,
reçoit ses points ; ne retire des points que sur ce que le barème mesure.
Sois concis : correction_detaillee en 10 lignes maximum, un seul conseil court.

Réponds avec ce JSON exact :
{{
  "note": <nombre entre 0 et 20>,
  "points_forts": ["<point fort 1>", "<point fort 2>"],
  "erreurs": ["<erreur 1>", "<erreur 2>"],
  "correction_detaillee": "<correction complète, étape par étape, avec les calculs>",
  "conseil": "<un conseil concret pour progresser>"
}}
Remplace chaque <...> par ton contenu réel : ne recopie jamais les chevrons
ni leur libellé."""
