import numpy as np

def codage(ne, nj, j, x, y):
    """
    Fonction de codage d'une paire (j, x, y) en une variable propositionnelle unique
    """
    return ne**2 * j + x * ne + y + 1

def decodage(k, ne):
    """
    Fonction de décodage d'une variable propositionnelle en une paire (j, x, y)
    """
    k -= 1
    y = k % ne
    x = (k % ne**2 - y) // ne
    j = (k - x * ne - y) // ne**2
    return j, x, y    

def cnf_au_moins(liste):
    """
    Génère une clause de type "au moins un vrai" à partir d'une liste de variables propositionnelles
    """
    clause = ""
    for v in liste:
        clause += str(v) + " "
    return clause + str(0)

def cnf_au_plus(liste):
    """
    Génère des clauses de type "au plus un vrai" à partir d'une liste de variables propositionnelles
    """
    clause = ""
    for i in range(len(liste)):
        for j in range(i + 1, len(liste)):
            clause += "- " + str(liste[i]) + " -" + str(liste[j]) + " 0 \n"
    return clause[:-1]

def encoder_c1(ne, nj):        
    """
    Encode la contrainte C1 "chaque équipe ne peut jouer plus d'un match par jour"
    en un ensemble de contraintes de cardinalité
    """
    clauses = ""
    for xi in range(ne):        # Parcours pour chaque équipe
        for ji in range(nj):    # Pour un jour donné
            liste_x_j = []
            for yi in range(ne):    # Récupération de tous les matchs
                if yi != xi:
                    liste_x_j.append(codage(ne, nj, ji, xi, yi))  
                    liste_x_j.append(codage(ne, nj, ji, yi, xi))

            # Contrainte de cardinalité : au plus un vrai
            clauses += cnf_au_plus(liste_x_j) + "\n" 

    return clauses

""" 
Traduction de la contrainte C1 "chaque équipe ne peut jouer plus d'un match par jour" en un ensemble de contraintes de cardinalité :

Pour chaque jour ji et chaque équipe xi donnés, on a :
    Pour chaque paire de joueurs yi et yj, avec yi différent de xi et yj différent de xi :
        Au plus un vrai(M, ji, xi, yi ; M, ji, xi, yj ; M, ji, yi, xi ; M, ji, yj, xi)

En notation DIMACS, cela se traduit par :
    Pour chaque jour ji et chaque équipe xi :
        Pour chaque paire de joueurs yi et yj, avec yi différent de xi et yj différent de xi :
            -M ji xi yi -M ji xi yj 0
            -M ji xi yi -M ji yj xi 0
            -M ji xi yj -M ji yi xi 0
            -M ji yi xi -M ji yj xi 0

Où M est la variable propositionnelle représentant un match entre les joueurs xi et yi le jour ji.

Note : Les clauses doivent être générées pour toutes les combinaisons possibles de jours et d'équipes.

"""


print(encoder_c1(3,3))