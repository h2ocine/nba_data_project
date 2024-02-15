"""
Projet IAMSI
Organisation d'un championnat
Hocine Kadem 21309534
Neil Benahmed 21200977
14/02/2024
"""

import re
from typing import List
import subprocess # Commandes systèmes 
import sys # Récupérer paramètres main
import math
import signal

# Balises de couleurs
ROUGE = '\033[91m'
BLEU = '\033[94m'
JAUNE = '\033[93m'
VERT = '\033[92m'
VIOLET = '\033[95m'
NOIR = '\033[0;30m'
BLEU = '\033[0;34m'
MAGENTA = '\033[0;35m'
CYAN = '\033[0;36m'
BLANC = '\033[0;37m'
CYAN_CLAIR = '\033[1;36m'
GRIS_FONCE = '\033[1;30m'
FIN = '\033[0m' # Balise de ferméture pour les balises des couleurs

# Fichier DIMACS généré/modifié
nom_fichier_cnf = 'clauses.cnf'

# Commande glucose 
commande_glucose = f'./glucose/simp/glucose -model {nom_fichier_cnf}'


# -------------------------------------------------------------------
# -------------------------------------------------------------------
# --------------------- Fonctions utilitaires -----------------------
# -------------------------------------------------------------------
# -------------------------------------------------------------------


def eliminer_doublons(clauses : str) -> str:
    """
    Elimine les doublons des clauses dans une liste de clause sous format chaine de String
    """
    lignes = clauses.split(" 0")
    lignes_uniques = []
    set_ligne_uniques = []

    for ligne in lignes:
        # Ajouter la ligne triée à l'ensemble
        if ligne != '':
            # Récupérer un set de variables dans la clauses (ligne) 
            nombres = ligne.split(" ")
            # print(nombres)

            ligne_tab = set()

            for e in nombres:
                if e != '0' and e != '' and e != "\n":

                    if e[0] == "\n":
                        e = e[1:]

                    if e[-1] == "\n":
                        e |e[:-1]
                    
                    ligne_tab |= {e}

            # Vérifier que le set de clauses n'est pas dans set_lignes_uniques
            if ligne_tab not in set_ligne_uniques:
                lignes_uniques.append(ligne) # Ajouter la ligne dans les lignes uniques
                set_ligne_uniques.append(ligne_tab) # Ajouter le set de clause dans set_lignes_uniques

    lignes_sans_doublons = " 0 ".join(lignes_uniques)
    return lignes_sans_doublons 


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

def generer_fichier_cnf(clauses : str):
    """
    Génére un fichier cnf à partir d'un string de clauses
    """
    clauses_list = transforme_liste(clauses)
    contenu = []

    # Ajout du Header
    contenu.append("c Fichier CNF généré")
    contenu.append("c")
    contenu.append("p cnf {} {}".format(max(map(abs, [var for clause in clauses_list for var in clause])), len(clauses_list)))

    # Ajout des clauses
    for clause in clauses_list:
        contenu.append(" ".join(map(str, clause)) + " 0")

    fichier_cnf = "\n".join(contenu)

    with open(nom_fichier_cnf, "w") as f:
        f.write(fichier_cnf)

def ajuster_taille(chaine : str, taille : int) -> str:
    """
    Ajoute des caractères ' ' à une chaine pour la rendre de taille taille
    """
    if len(chaine) >= taille:
        return chaine
    else:
        espaces_ajoutes = taille - len(chaine)
        return chaine + ' ' * espaces_ajoutes
    

# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# --------------------- Fonctions du projets & réponses aux questions ------------------------
# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
# Une explication plus détaillée des fonctions et des réponses aux questions se trouve dans le rapport du projet.

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
    k -= 1 # k = ne**2 * j + x * ne + ys
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
C1 : "chaque équipe ne peut jouer plus d'un match par jour"

Traduction :

Pour chaque jour ji et chaque équipe xi donnés, on a :
    Pour chaque paire de joueurs yi et yj, avec yi différent de xi et yj différent de xi :
        Au plus un vrai(M, ji, xi, yi ; M, ji, xi, yj ; M, ji, yi, xi ; M, ji, yj, xi)
"""


# 3.2.2 
def encoder_c1(ne, nj):        
    """
    Encode la contrainte C1 
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

Pour chaque equipe (3) et pour chaque jour (4 jours) : on a au plus 1 match parmis 4 matchs possible, donc on a (2 parmis 4) clauses = 6 clauses
Donc on a 3 * 4 * 6 = 72 clauses (avec les doublons).
On a aussi pour chaque jour 3 doublons donc on a 12 doublons. 
Donc on à finalement : 60 clauses
"""


# 3.2.4
"""
C2 : "Sur la durée du championnat, chaque équipe doit rencontrer l'ensemble
    des autres équipes une fois à domicile et une fois à l'extérieur, soit 
    exactement 2 matchs par équipe adverse."

Traduction :

Pour chaque equipe xi : 
    Pour chaque equipe yi différent de xi :
        Il existe j tel que :  (M, j, xi, yi) and (M, j, yi, xi)
"""


# 3.2.5
def encoder_c2(ne, nj):  
    """
    Encode la contrainte C2 
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

On à 3 (2 parmis 3) {xi,yi} : 
On calcule les cnf_au_moins : 1 contrainte par {xi,yi}
On calcule les cnf_au_plus : On a 4 jours, donc 2 parmis 4 = 6 contraintes par {xi,yi}
On multiplie * 2 car on le fait pour les matchs a domiciles et exterieurs :
Donc on aura : 
nombre de contraintes clause C2 avec 3 équipes sur 4 jours = 
3 * (1 + 6) * 2 = 42 contraintes
"""


# 3.2.7 
def encoder(ne,nj):
    """
    Encode toutes les contraintes C1 et C2 pour ne et nj donnée.
    """
    return eliminer_doublons(encoder_c1(ne,nj) + encoder_c2(ne,nj))


def affichage_contrainte(ne = 3, nj = 4, affichager_contrainte = False):
    """
    Affiche les informations sur les contraintes générées par les fonctions encoder_c1, encoder_c2 et encoder.

    Args:
        ne (int): Nombre d'équipes (par défaut : 3).
        nj (int): Nombre de jours (par défaut : 4).
        affichager_contrainte (bool): Indique si les clauses générées doivent être affichées (par défaut : False).
    """

    clauses_c1 = encoder_c1(ne,nj)
    clauses_c2 = encoder_c2(ne,nj)
    clauses= encoder(ne,nj)

    # Clauses de C1
    print(f'Pour {ne} équipes sur {nj} jours : ')
    print(f'La contrainte c1 génére : {len(clauses_c1.split(" 0")) - 1} clauses')
    if(affichager_contrainte):
        print(f'Les clauses générés par c1 sont : \n{clauses_c1}\n')

    # Clauses de C2
    print(f'Pour {ne} équipes sur {nj} jours : ')
    print(f'La contrainte c2 génére : {len(clauses_c2.split(" 0")) - 1} clauses')
    if(affichager_contrainte):
        print(f'Les clauses générés par c2 sont : \n{clauses_c2}\n')

    # Clauses de C1 et C2
    print(f'Pour {ne} équipes sur {nj} jours : ')
    print(f'Les contraites c1 et c2 générent : {len(clauses.split(" 0")) - 1} clauses')
    if(affichager_contrainte):
        print(f'Les clauses générés sont : \n{clauses}\n')
# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------


# 3.3 
"""
Utiliser glucose sur la CNF générée à la question précédente et
vérifier la première solution propsé pour 3 équipes sur 4 jours :

c restarts              : 1 (25 conflicts in avg)
c blocked restarts      : 0 (multiple: 0)
c last block at restart : 0
c nb ReduceDB           : 0
c nb removed Clauses    : 0
c average learnt size   : 3
c nb learnts DL2        : 3
c nb learnts size 2     : 3
c nb learnts size 1     : 3
c conflicts             : 25             (18382 /sec)
c decisions             : 29             (0.00 % random) (21324 /sec)
c propagations          : 159            (116912 /sec)
c nb reduced Clauses    : 3
c LCM                   : 0 / 0
c CPU time              : 0.00136 s

s UNSATISFIABLE
""" 


"""
Qu'est-il n'ecessaire d'ajouter aux deux contraintes C1 et C2 ?
--> On doit ajouter une contraite qu'une equipe ne peut pas jouer contre elle même
"""

# Ajout de la contrainte : 'une equipe ne peut pas jouer contre elle même'
def encoder_c3(ne, nj):  
    """
    Encode la contrainte C3 "une equipe ne peut pas jouer contre elle même"
    """
    clauses = ""
    for xi in range(ne):
        for ji in range(nj):
            clauses += "-" + str(codage(ne, nj, ji, xi, xi)) + " 0\n"
    return clauses


###############################################################################################################################################
###############################################################################################################################################
###############################################################################################################################################
###############################################################################################################################################
###############################################################################################################################################

def au_plus_k(variables, k):
    """Renvoie une clause (au format DIMACS) correspondant à la contrainte
    au plus k de ces variables sont vraies
    """
    from itertools import combinations

    clauses = []
    n = len(variables)
    for i in range(k + 1, n + 1):
        for c in combinations(variables, i):
            clause = [str(-x) for x in c] + ["0"]
            clauses.append(" ".join(clause))

    return clauses

def au_moins_k(variables, k):
    """Renvoie une clause (au format DIMACS) correspondant à la contrainte
    au moins k de ces variables sont vraies
    """
    n = len(variables)
    neg_variables = [-x for x in variables]
    return au_plus_k(neg_variables, n - k)


def encoder_c4(ne, nj, pext=50, pdom=40):
    """Renvoie des contraintes (au format DIMACS) correspondant aux contraintes
    des matchs le dimanche.
    On considère que le dimanche est le deuxième jour de la semaine (chiffres impairs).

    Indication : pour 3 équipes et 4 jours, cela génère 24 contraintes.
    """
    kext = int((ne - 1) * pext / 100)
    kdom = int((ne - 1) * pdom / 100)

    clauses = []
    str_clauses = ""
    domiciles = []
    exterieurs = []
    for x in range(ne):
        domiciles = []
        exterieurs = []
        for y in range(ne):
            if x != y:
                # Tous les matchs à domicile joués le dimanche
                domicile = [codage(ne, nj, j, x, y) for j in range(1, nj, 2)]
                domiciles.append(domicile)

                # Tous les matchs à l'extérieur joués le dimanche
                exterieur = [codage(ne, nj, j, y, x) for j in range(1, nj, 2)]
                exterieurs.append(exterieur)
        
        flattened_domicile = [v for domicile in domiciles for v in domicile]
        flattened_exterieur = [v for exterieur in exterieurs for v in exterieur]
        clauses.extend(au_moins_k(flattened_domicile, kdom))
        clauses.extend(au_moins_k(flattened_exterieur, kext))

    for cl in clauses:
        str_clauses += cl + '\n'
    return str_clauses


def encoder_c5(ne, nj):
    """Renvoie des contraintes (au format DIMACS) correspondant aux contraintes
    des matchs consécutifs.

    Note : cette implémentation est fausse, n'ayant pas bien compris comment récupérer
    la notion de matchs consécutifs.

    Parameters
    ----------
    ne : int
        Nombre d'équipes.
    nj : int
        Nombre de jours.

    Returns
    -------
    clauses : liste de str
        Contraintes générées.
    """
    matchs_domicile = []
    matchs_exterieur = []
    clauses = []
    str_clauses = ""

    for x in range(ne): 
        for j in range(nj-1):

            matchs_domicile = []
            matchs_exterieur = []

            for y in range(ne):
                matchs_domicile.append(codage(ne,nj,j,x,y))
                matchs_domicile.append(codage(ne,nj,j+1,x,y))
                matchs_domicile.append(codage(ne,nj,j+2,x,y))

                matchs_exterieur.append(codage(ne,nj,j,y, x))
                matchs_exterieur.append(codage(ne,nj,j+1,y,x))
                matchs_exterieur.append(codage(ne,nj,j+2,y,x))

            clauses.extend(au_plus_k(matchs_domicile, 2))
            clauses.extend(au_plus_k(matchs_exterieur, 2))

    for cl in clauses:
        str_clauses += cl + '\n'
    return str_clauses

###############################################################################################################################################
###############################################################################################################################################
###############################################################################################################################################
###############################################################################################################################################
###############################################################################################################################################


def encoder_bis(ne,nj, extend=False):
    """
    Encode les contraintes C1, C2 et C3 pour les valeurs données de ne et nj.
    
    Arguments :
    ne -- Valeur de ne à encoder
    nj -- Valeur de nj à encoder
    extend -- Indique si les contraintes C4 et C5 doivent également être encodées (par défaut False)
    
    Returns :
    Code encodé des contraintes C1, C2 et C3 (et éventuellement C4 et C5)
    """
    code_c1 = encoder_c1(ne,nj)
    code_c2 = encoder_c2(ne,nj)
    code_c3 = encoder_c3(ne,nj)
    if extend:
        code_c4 = encoder_c4(ne, nj)
        code_c5 = encoder_c5(ne,nj)

        return eliminer_doublons(code_c1 + code_c2 + code_c3 + code_c4 + code_c5)
    return eliminer_doublons(code_c1 + code_c2 + code_c3)


# 3.4 
def decoder(sortie_glucose : str, nom_fichier_equipe : str, ne : int) -> str:
    """
    Traduit un modèle rendu en une solution du problème de planning des matchs affichée lisiblement
    """
    try:
        with open(nom_fichier_equipe, 'r') as f:
            # Lire le fichier des noms des equipes
            noms_equipes = f.read()

            # On vérifie si on a une solution qui satifait nos contraintes
            if(sortie_glucose.find("UNSATISFIABLE") != -1):
                return f"{ROUGE}UNSAT (NON SATISFIABLE){FIN}"

            # On récupére l'indice ou se trouve le mot satsfiable
            indice_satisfiable = sortie_glucose.find("SATISFIABLE")

            # On récupére la solution du modele donnée par glucose 
            indice_solution = indice_satisfiable + len("SATISFIABLE") + 3
            modele_solution = sortie_glucose[indice_solution:-1] 

            # Récupérer la liste des matchs
            matchs_list = modele_solution.split(' ')[:-1]
            
            # Récupérer le noms des équipe dans une liste : 
            equipe_list = noms_equipes.split('\n')

            # Récupérer les jours et equipes de chaque matchs
            solution = ''
            num_match = 0
            jours = [] # Liste des codes des jours
            start=1

            print(f"{GRIS_FONCE}Match{FIN} | {GRIS_FONCE}Journée{FIN} |   {GRIS_FONCE}Jour{FIN}   | {GRIS_FONCE}Num jour{FIN} | {GRIS_FONCE}Equipe à domicile{FIN} | {GRIS_FONCE}Equipe à l'exterieur{FIN}")
            for match in matchs_list:
                if(int(match) >= 0): # Traitement des matchs joué (codes des matchs positif)
                    num_match += 1
                    jour, equipe1, equipe2 = decodage(int(match), ne)
                    if(jour not in jours):
                        jours.append(jour) 
                    j = jours.index(jour) # L'index du jour dans le tableaux des codes des jours représente le numero du jour
                    j += 1 # On commence par le jour 1
                    if start==1:
                        start=0
                        if jour%2==0:
                            solution += f' {ajuster_taille(str(num_match),3)}  |  {JAUNE}{ajuster_taille(str(j),3)}{FIN}    | {CYAN_CLAIR}Mercredi{FIN} |  {VERT}{ajuster_taille(str(jour+1),3)}{FIN}     | {BLEU}{ajuster_taille(equipe_list[equipe1],14)}{FIN}    | {ROUGE}{ajuster_taille(equipe_list[equipe2],12)}{FIN}\n'  
                        else:
                            solution += f' {ajuster_taille(str(num_match),3)}  |  {JAUNE}{ajuster_taille(str(j),3)}{FIN}    | {CYAN_CLAIR}Dimanche{FIN} |  {VERT}{ajuster_taille(str(jour+1),3)}{FIN}     | {BLEU}{ajuster_taille(equipe_list[equipe1],14)}{FIN}    | {ROUGE}{ajuster_taille(equipe_list[equipe2],12)}{FIN}\n'  
            
                    elif jour%2==0:
                        solution += f' {ajuster_taille(str(num_match),3)}  |  {JAUNE}{ajuster_taille(str(j),3)}{FIN}    | {CYAN_CLAIR}Mercredi{FIN} |  {VERT}{ajuster_taille(str(jour+1),3)}{FIN}     | {BLEU}{ajuster_taille(equipe_list[equipe1],14)}{FIN}    | {ROUGE}{ajuster_taille(equipe_list[equipe2],12)}{FIN}\n'  
                    else:
                        solution += f' {ajuster_taille(str(num_match),3)}  |  {JAUNE}{ajuster_taille(str(j),3)}{FIN}    | {CYAN_CLAIR}Dimanche{FIN} |  {VERT}{ajuster_taille(str(jour+1),3)}{FIN}     | {BLEU}{ajuster_taille(equipe_list[equipe1],14)}{FIN}    | {ROUGE}{ajuster_taille(equipe_list[equipe2],12)}{FIN}\n'  
        
            return solution + '\n'
        
    except FileNotFoundError:
        return f"Le fichier '{nom_fichier_equipe}' n'a pas été trouvé."
    except Exception as e:
        return f"Une erreur s'est produite : {str(e)}"
    

# 3.5
def read_ne_nj(nom_fichier_equipe : str):
    """
    Lecture du nombre des equipes ne et du nombre de jours nj
    """
    # Récupérer le nombre de jours
    while True:
        try:
            nj = int(input(f'{CYAN_CLAIR}Entrez le nombre de jours du championnat (nj) :{FIN}'))
            if nj <= 1:
                raise ValueError(f'{ROUGE}Le nombre de jours doit être supérieur à 1{FIN}')
            break # Sortir de la boucle si le nombre de jours est valide

        except ValueError as e:
            print(f'{ROUGE}Erreur : {str(e)}{FIN}')
    
    # Récupérer le nombre d'equipes
    while True:
        try:
            ne = int(input(f'{CYAN_CLAIR}Entrez le nombre d\'équipes qu\'on prend on compte (ne) : {FIN}'))
            
            with open(nom_fichier_equipe) as file:
                lignes = file.readlines()
                ne_total = len(lignes)  # Récupérer le nombre d'équipes dans le fichier

                if ne <= 0 or ne > ne_total:
                    raise ValueError(f'{ROUGE}Le nombre d\'équipes doit être compris entre 1 et {ne_total}')
            
            break  # Sortir de la boucle si le nombre d'équipes est valide
        
        except FileNotFoundError:
            print(f'{ROUGE}Le fichier {nom_fichier_equipe} n\'a pas été trouvé.{FIN}')
            break
        
        except ValueError as e:
            print(f'{ROUGE}Erreur : {str(e)}{FIN}')
    
    return ne, nj


def programme(nom_fichier_equipe : str, ne : int, nj : int, extend=False): 
    """
    Génére un modèle pour résoudre le problème de génération d'un championnat en utilisant le solveur Glucose.

    Arguments :
    nom_fichier_equipe -- Nom du fichier contenant les noms des équipes
    ne -- Nombre d'équipes
    nj -- Nombre de jours
    extend -- Indique si les contraintes C4 et C5 doivent être prises en compte (par défaut False)

    Returns :
    Le modèle résolu du problème
    """  
    print(f'{JAUNE}nombre d\'equipes = {ne}{FIN}')
    print(f'{JAUNE}nombre de jours = {nj}{FIN}')

    # Générer les clauses 
    clauses = encoder_bis(ne,nj)

    # Générer le fichier cnf
    generer_fichier_cnf(clauses)

    # Lancer  la commande glucose 
    resultat_commande = subprocess.run(commande_glucose, shell=True, capture_output=True, text=True)
    
    # Réupérer le résultat de la commande
    glucose_output = resultat_commande.stdout

    # Decoder le modèle 
    modele = decoder(glucose_output,nom_fichier_equipe,ne)

    # Afficher le modèle
    print(modele)

    return modele


def main_1(extend=False):
    """
    Point d'entrée principal du programme.

    Arguments :
    extend -- Indique si les contraintes C4 et C5 doivent être prises en compte (par défaut False)

    Returns :
    0 si l'exécution s'est déroulée correctement, -1 sinon.
    """
    if(sys.argv[1] == ""):    
        print(f'nom du fichier non ajouter en parametre de l\'appel')
        return -1
    
    # Lire le fichier d'equipes
    nom_fichier_equipe = sys.argv[1]

    # Lire si l'utilisateur veut contabiliser les contraites C4 et C5

    # Lire le nombre de d'equipe et le nombre de jour
    ne, nj = read_ne_nj(nom_fichier_equipe)

    programme(nom_fichier_equipe, ne, nj, extend)

    return 0


# Exercice 4

def min_nj(ne: int) -> int:
    """
    Retourne la valeur minimale de nj pour ne equipes en utilisant des appels SAT de façon itérative
    """
    nj = 2
    while True:
        # Générer les clauses
        clauses = encoder_bis(ne, nj)
        print("finis d'encoder")
        # Générer le fichier cnf
        generer_fichier_cnf(clauses)

        # Lancer la commande glucose

        process = subprocess.Popen(commande_glucose, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        try:
            # Attendre 10 secondes pour la fin de l'exécution de la commande
            glucose_output, _ = process.communicate(timeout=10)
        except subprocess.TimeoutExpired:
            print("Le calcul a pris plus de 10 secondes. Annuler la commande.")
            process.kill()
            nj += 1
            continue       
        # Récupérer le résultat de la commande
        glucose_output = glucose_output.decode()

        # On vérifie si on a une solution qui satisfait nos contraintes
        if glucose_output.find("UNSATISFIABLE") == -1:
            return nj
        else:
            print("unsat :c avec nj = ", nj)

        # On augmente nj jusqu'à trouver le nj qui satisfera les clauses
        nj += 1


def min_nj_dichotomique(ne: int) -> int:
    """
    Retourne la valeur minimale de nj pour ne equipes en utilisant une recherche dichotomique
    """
    nj_min = ne
    nj_max = math.perm(ne, 2)
    nj_mid = nj_min
    # Valeur maximale de nj à tester
    
    while nj_min < nj_max:
        nj_mid = (nj_min + nj_max) // 2
        print(f'{GRIS_FONCE}Calcule pour ne = {ne} et nj = {nj_mid}{FIN}')
        
        # Générer les clauses
        clauses = encoder_bis(ne, nj_mid)

        # Générer le fichier cnf
        generer_fichier_cnf(clauses)

        # Lancer la commande glucose
        resultat_commande = subprocess.run(commande_glucose, shell=True, capture_output=True, text=True)

        # Récupérer le résultat de la commande
        glucose_output = resultat_commande.stdout

        # On vérifie si on a une solution qui satisfait nos contraintes
        if glucose_output.find("UNSATISFIABLE") == -1:
            nj_max = nj_mid # SATISFIABLE
        else:
            nj_min = nj_mid + 1 # NON SATISFIABLE
    
    return nj_min


def min_nj_plusieurs_equipes(ne_min = 3,ne_max = 10):
    """
    Retourne la valeur minimale de nj pour le nombre d'equipe de ne_min à ne_max equipes en utilisant une recherche dichotomique
    """
    def handler(signum, frame):
        raise TimeoutError("Le délai d'attente est dépassé")

    timeout_duration = 10  # Durée du timeout en secondes

    for ne in range(ne_min, ne_max+1):
        signal.signal(signal.SIGALRM, handler)
        signal.alarm(timeout_duration)

        try:
            nj_min = min_nj_dichotomique(ne)
            signal.alarm(0)  # Annuler le timeout si la fonction se termine avant la limite
        except TimeoutError:
            print(f"{ROUGE}Le calcul pour {ne} équipes a pris plus de {timeout_duration} secondes. Annuler la commande.{FIN}")
            continue

        print(f"{VERT}Nombre minimal de jours pour {ne} équipes : {nj_min}{FIN}")


# ---------------------------------------------------
# ---------------------------------------------------
# --------------------- MAIN ------------------------
# ---------------------------------------------------
# ---------------------------------------------------
        

if __name__ == "__main__":

    if len(sys.argv) < 2: # Nom fichier equipes par défault
        sys.argv.append("equipes.txt") 

    while True:
        try:
            choix = int(input("Choisissez une option : \n1. Modèle pour la résolution du problème du championnat\n2. Nombre de jours minimum\n"))
            if choix == 2:
                min_nj_plusieurs_equipes()
                break
            elif choix == 1:
                while True:
                    prendre_en_compte = input("Voulez-vous prendre en compte C4 et C5 ? (1. oui/2. non)\n").lower()
                    if prendre_en_compte == 'oui' or prendre_en_compte == '1':
                        main_1(extend = True)
                        break
                    elif prendre_en_compte == 'non' or prendre_en_compte == '2':
                        main_1(extend = False)
                        break
                    else:
                        print("Option invalide. Veuillez réessayer.")
                break
            else:
                print("Option invalide. Veuillez réessayer.")
        except ValueError:
            print("Veuillez entrer un nombre valide.")

