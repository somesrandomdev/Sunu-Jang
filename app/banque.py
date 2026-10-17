"""Banque d'exercices rédigés à la main.

Secours de démonstration : si la génération échoue (machine modeste, modèle
chargé lentement), l'interface propose un exercice de cette banque au lieu
d'échouer — clairement étiqueté « exercice de la banque », jamais présenté
comme généré. La correction, elle, reste toujours exécutée en direct.

Les mêmes exercices servent de cas figés au jeu d'évaluation (scripts/eval.py).
"""

from app.schemas import Exercise

EX_SUITES = Exercise(
    titre="Suites numériques (Maths, Terminale)",
    enonce=(
        "Soit la suite $(u_n)$ définie par $u_0 = 1$ et, pour tout entier naturel $n$, "
        "$u_{n+1} = 2u_n + 3$.\n\n"
        "1. Calculer $u_1$ et $u_2$.\n"
        "2. Montrer par récurrence que, pour tout $n \\in \\mathbb{N}$, "
        "$u_n = 4 \\times 2^n - 3$.\n"
        "3. En déduire la valeur de $u_{10}$."
    ),
    bareme=(
        "Q1 : 4 points (2 pts par terme). "
        "Q2 : 12 points (initialisation 4 pts, hérédité 6 pts, conclusion 2 pts). "
        "Q3 : 4 points."
    ),
    competences_evaluees=["Raisonnement par récurrence", "Calcul sur les suites"],
    corrige=(
        "1. $u_1 = 2 \\times 1 + 3 = 5$ ; $u_2 = 2 \\times 5 + 3 = 13$.\n"
        "2. Initialisation : $u_0 = 1$ et $4 \\times 2^0 - 3 = 1$, donc la propriété est vraie "
        "pour $n = 0$.\n"
        "Hérédité : supposons $u_n = 4 \\times 2^n - 3$ pour un certain $n$. Alors "
        "$u_{n+1} = 2u_n + 3 = 2(4 \\times 2^n - 3) + 3 = 8 \\times 2^n - 3$ "
        "$= 4 \\times 2^{n+1} - 3$ : la propriété est héréditaire.\n"
        "Conclusion : pour tout $n \\in \\mathbb{N}$, $u_n = 4 \\times 2^n - 3$.\n"
        "3. $u_{10} = 4 \\times 2^{10} - 3 = 4 \\times 1024 - 3 = 4093$."
    ),
)

EX_SECOND_DEGRE = Exercise(
    titre="Équation du second degré (Maths, Première)",
    enonce=(
        "On considère l'équation $(E) : x^2 - 5x + 6 = 0$, d'inconnue réelle $x$.\n\n"
        "1. Calculer le discriminant $\\Delta$.\n"
        "2. Résoudre $(E)$ dans $\\mathbb{R}$.\n"
        "3. Factoriser le trinôme $x^2 - 5x + 6$.\n"
        "4. Dresser le tableau de signes de $x^2 - 5x + 6$ sur $\\mathbb{R}$."
    ),
    bareme=(
        "Q1 : 5 points. Q2 : 5 points. Q3 : 4 points. Q4 : 6 points "
        "(tableau complet avec racines et signes)."
    ),
    competences_evaluees=["Discriminant", "Factorisation", "Étude de signe"],
    corrige=(
        "1. $\\Delta = b^2 - 4ac = (-5)^2 - 4 \\times 1 \\times 6 = 25 - 24 = 1 > 0$.\n"
        "2. Deux racines réelles : $x_1 = \\dfrac{5 - 1}{2} = 2$ et "
        "$x_2 = \\dfrac{5 + 1}{2} = 3$. "
        "L'ensemble des solutions est $S = \\{2 ; 3\\}$.\n"
        "3. $x^2 - 5x + 6 = (x - 2)(x - 3)$.\n"
        "4. Le trinôme est du signe de $a = 1 > 0$ sauf entre les racines : "
        "positif sur $]-\\infty ; 2[ \\cup ]3 ; +\\infty[$, nul en $2$ et $3$, "
        "négatif sur $]2 ; 3[$."
    ),
)

EX_MOUVEMENT = Exercise(
    titre="Mouvement rectiligne uniformément accéléré (Physique-Chimie, Terminale)",
    enonce=(
        "Un mobile ponctuel se déplace sur un axe $(O, \\vec{\\imath})$. À l'instant "
        "$t = 0$ s, il passe à l'abscisse $x_0 = 0$ m avec une vitesse $v_0 = 2$ m/s. "
        "Son accélération est constante : $a = 3$ m/s².\n\n"
        "1. Donner l'équation horaire $x(t)$ du mouvement.\n"
        "2. Calculer la vitesse du mobile à $t = 4$ s.\n"
        "3. Calculer la distance parcourue entre $t = 0$ et $t = 4$ s."
    ),
    bareme="Q1 : 7 points (équation générale 4 pts, application 3 pts). "
    "Q2 : 6 points. Q3 : 7 points (formule 3 pts, calcul 3 pts, unité 1 pt).",
    competences_evaluees=["Équations horaires", "MRUA"],
    corrige=(
        "1. Pour un MRUA : $x(t) = \\dfrac{1}{2}at^2 + v_0 t + x_0$. Avec les données : "
        "$x(t) = 1{,}5t^2 + 2t$ (en m).\n"
        "2. $v(t) = v_0 + at = 2 + 3t$, donc $v(4) = 2 + 12 = 14$ m/s.\n"
        "3. $x(4) = 1{,}5 \\times 16 + 2 \\times 4 = 24 + 8 = 32$ m. "
        "La distance parcourue est $32$ m."
    ),
)

EX_DISSERT = Exercise(
    titre="Introduction de dissertation (Philosophie, Terminale)",
    enonce=(
        "Sujet : « La liberté est-elle une illusion ? »\n\n"
        "Consigne : rédigez uniquement l'introduction de la dissertation "
        "(accroche, analyse du sujet et dégagement du paradoxe, problématique, "
        "annonce du plan). Ne rédigez ni le développement ni la conclusion."
    ),
    bareme="Accroche : 4 points. Analyse du sujet et paradoxe : 6 points. "
    "Problématique : 6 points. Annonce du plan : 4 points.",
    competences_evaluees=["Méthode de la dissertation", "Problématisation"],
    corrige=(
        "Accroche : chaque matin, je choisis mes vêtements, mon trajet, mes amis ; "
        "cette impression de choisir semble aller de soi.\n"
        "Analyse : la liberté désigne le pouvoir d'agir selon sa propre volonté, sans "
        "contrainte extérieure. Mais cette volonté elle-même a des causes : habitudes, "
        "éducation, désirs que je n'ai pas choisis. Le paradoxe apparaît : je me sens "
        "libre, mais tout semble déterminé.\n"
        "Problématique : la liberté est-elle réelle ou n'est-elle que l'illusion d'un "
        "sujet qui croit choisir alors qu'il est déterminé ?\n"
        "Annonce du plan : nous verrons d'abord que la liberté peut être dénoncée comme "
        "une illusion (Spinoza), puis qu'elle est une réalité de la conscience (Sartre), "
        "avant de nous demander si liberté et déterminisme peuvent se concilier."
    ),
)

# Un exercice de secours par matière proposée dans l'interface (clés = libellés UI).
BANQUE_PAR_MATIERE = {
    "Maths": EX_SUITES,
    "Physique-Chimie": EX_MOUVEMENT,
    "Philosophie": EX_DISSERT,
}
