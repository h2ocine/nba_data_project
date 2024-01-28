import numpy as np
import re
from typing import List

# --------------------------------------------------------------------------------------------------
# Fonctions utiles 
def eliminer_doublons(clauses):
    """
    Elimine les doublons des clauses dans une liste de clause sous format chaine de String
    """
    lignes = clauses.split("0")
    lignes_uniques = set()

    for ligne in lignes:
        # convertir la ligne en une liste de nombres entiers triés
        numeros = sorted(map(int, ligne.split()))
        # convertir la liste triée en une chaîne de caractères
        ligne_triee = " ".join(map(str, numeros))
        # ajouter la ligne triée à l'ensemble
        lignes_uniques.add(ligne_triee)

    lignes_sans_doublons = " 0 ".join(lignes_uniques)
    return lignes_sans_doublons[3::]  + " 0 "

def transforme_liste(clauses: str) -> List[int]:
    """
    Transforme un String de clauses en une liste de clauses représenté en int 
    """
    regex = r"(-?\d+)\s+" 
    clauses = re.findall(regex, clauses)
    liste_clauses = []
    clause = []
    for element in clauses:
        if element == "0": # Fin de la clause
            liste_clauses.append(clause) # Ajouter la clause dans la liste
            clause = []
        else:
            clause.append(int(element)) # Ajouter l'élément de la clause dans la liste

    return liste_clauses

def generer_fichier_cnf(clauses):
    """
    Génére un fichier cnf à partir d'un string de clauses
    """
    clauses_list = transforme_liste(clauses)
    contenu = []
    contenu.append("c Fichier CNF généré")
    contenu.append("c")
    contenu.append("p cnf {} {}".format(max(map(abs, [var for clause in clauses_list for var in clause])), len(clauses_list)))

    for clause in clauses_list:
        contenu.append(" ".join(map(str, clause)) + " 0")

    fichier_cnf = "\n".join(contenu)

    with open("exemple.cnf", "w") as f:
        f.write(fichier_cnf)


# --------------------------------------------------------------------------------------------------


# 2.1  
"""
Exprimer en fonction de ne et nj le nombre de variables propositionnelles utilisées : 

si on consifère qu'une equipe peut jouer contre elle même : nj * (ne ^ 2)
sinon : nj - ne * (ne - 1) 
"""

# 2.2 
def codage(ne, nj, j, x, y):
    """
    Fonction de codage d'une paire (j, x, y) en une variable propositionnelle unique
    """
    return ne**2 * j + x * ne + y + 1

# 2.3 
def decodage(k, ne):
    """
    Fonction de décodage d'une variable propositionnelle en une paire (j, x, y)
    """
    k -= 1
    y = k % ne
    x = (k % ne**2 - y) // ne
    j = (k - x * ne - y) // ne**2
    return j, x, y    

# 3.1.1
def cnf_au_moins(liste):
    """
    Génère une clause de type "au moins un vrai" à partir d'une liste de variables propositionnelles
    """
    clause = ""
    for v in liste:
        clause += str(v) + " "
    if(clause != ""):
        clause += str(0)
    return clause

# 3.1. 
def cnf_au_plus(liste):
    """
    Génère des clauses de type "au plus un vrai" à partir d'une liste de variables propositionnelles
    """
    clause = ""
    for i in range(len(liste)):
        for j in range(i + 1, len(liste)):
            clause += "-" + str(liste[i]) + " -" + str(liste[j]) + " 0 \n"
    return clause[:-1]

# 3.2.1
""" 
Traduction de la contrainte C1 "chaque équipe ne peut jouer plus d'un match par jour" en un ensemble de contraintes de cardinalité :

Pour chaque jour ji et chaque équipe xi donnés, on a :
    Pour chaque paire de joueurs yi et yj, avec yi différent de xi et yj différent de xi :
        Au plus un vrai(M, ji, xi, yi ; M, ji, xi, yj ; M, ji, yi, xi ; M, ji, yj, xi)
"""

# 3.2.2 
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

    return eliminer_doublons(clauses)

# 3.2.3 
"""
Indiquer le nombre de contraintes et de clauses générés pour 3 équipes sur 4 jours et expliciter ces contraintes : 
"""
ne = 3
nj = 4
clauses_c1 = encoder_c1(ne,nj)
print('Pour 3 équipes sur 4 jours : ')
print(f'La contrainte c1 génére : {len(clauses_c1.split("0")) - 1} clauses')
print(f'Les clauses générés sont : \n{clauses_c1}\n')

# 3.2.4
"""
4. Traduire la contrainte C2 ”Sur la dur´ee du championnat, chaque ´equipe doit rencontrer l’ensemble
des autres ´equipes une fois `a domicile et une fois `a l’ext´erieur, soit exactement 2 matchs par ´equipe
adverse.” en un ensemble de contraintes de cardinalit´es.


Pour chaque equipe xi : 
    Pour chaque equipe yi différent de xi :
        Il existe j tel que :  (M, j, xi, yi) and (M, j, yi, xi)

En notation DIMACS, cela se traduit par :
    Pour chaque equipe xi : 
        Pour chaque equipe yi différent de xi :
            # Pour les matchs aller
            cnf_au_plus(M j1 xi yi  M j2 xi yi  M j3 xi yi ... M jnj xi yi 0)
            cnf_au_moins(M j1 xi yi  M j2 xi yi  M j3 xi yi ... M jnj xi yi 0)

            # Pour les matchs retour
            cnf_au_plus(M j1 xi yi  M j2 xi yi  M j3 xi yi ... M jnj xi yi 0)
            cnf_au_moins(M j1 yi xi M j2 yi xi  M j3 yi xi ... M jnj yi xi 0)

Où M est la variable propositionnelle représentant un match entre les joueurs xi et yi le jour ji.

"""

# 3.2.5
def encoder_c2(ne, nj):  
    """
    Encode la contrainte C2 "Sur la durée du championnat, chaque équipe doit rencontrer l'ensemble
    des autres équipes une fois `a domicile et une fois à l'extérieur, soit exactement 2 matchs par équipe
    adverse."
    en un ensemble de contraintes de cardinalité
    """
    clauses = ""
    for xi in range(ne):
        for yi in range(xi + 1,ne):
            matchs_aller = []  # Tout les matchs à domicile de xi avec yi
            matchs_retour = [] # Tout les matchs à l'exterieur de xi avec yi
            for ji in range(nj):
                matchs_aller.append(codage(ne, nj, ji, xi, yi))
                matchs_retour.append(codage(ne, nj, ji, yi, xi))
            # Ajout des clauses
            clauses += cnf_au_moins(matchs_aller) + '\n' + cnf_au_plus(matchs_aller) + '\n' + cnf_au_moins(matchs_retour) + '\n' + cnf_au_plus(matchs_retour) + '\n'
    return eliminer_doublons(clauses)

# 3.2.6 
"""
Indiquer le nombre de contraintes et de clauses générés pour 3 équipes sur 4 jours et expliciter ces contraintes : 
"""
ne = 3
nj = 4
clauses_c2 = encoder_c2(ne,nj)
print('Pour 3 équipes sur 4 jours : ')
print(f'La contrainte c2 génére : {len(clauses_c2.split("0")) - 1} clauses')
print(f'Les clauses générés sont : \n{clauses_c2}\n')

# 3.2.7 
def encoder(ne,nj):
    """
    Encode toutes les contraintes C1 et C2 pour ne et nj donnée.
    """
    return eliminer_doublons(encoder_c1(ne,nj) + encoder_c2(ne,nj))

ne = 3
nj = 4
clauses= encoder(ne,nj)
print('Pour 3 équipes sur 4 jours : ')
print(f'Les contraites c1 et c2 générent : {len(clauses.split(" 0")) - 1} clauses')
print(f'Les clauses générés sont : \n{clauses}\n')

# Générérer le fichier cnf 
generer_fichier_cnf(clauses)