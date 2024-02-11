import random

def melanger_lignes(nom_fichier_entree):
    with open(nom_fichier_entree, 'r') as fichier_entree:
        lignes = fichier_entree.readlines()
        random.shuffle(lignes)

    with open(nom_fichier_entree, 'w') as nom_fichier_entree:
        for ligne in lignes:
            nom_fichier_entree.write(ligne)

    print("Les lignes ont été mélangées avec succès.")

# Exemple d'utilisation
fichier_entree = "equipes.txt"

melanger_lignes(fichier_entree)