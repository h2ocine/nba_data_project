import numpy as np

def codage(ne,nj,j,x,y):
    return ne**2*j+x*ne+y+1

def decodage(k,ne):
    k -= 1
    y = (k % ne)
    x = ((k % ne**2) - y) / ne
    j = (k-x*ne-y)/ne**2
    return j,x,y    

def cnf_au_moins(liste):
    clause = ""
    for v in liste:
        clause += str(v) + " "
    return clause + str(0)

def cnf_au_plus(liste):
    clause = ""
    for i in range(len(liste)):
        for j in range(i+1, len(liste)):
            clause += "- " + str(liste[i]) + " -" + str(liste[j]) + " 0 \n"
    return clause[:-1]


def encoder_c1(ne,nj):        
        liste_j = []
    for ji in range(nj):
        liste_matchs_j = []
        for xi in range(ne):
            for yi in range(ne):
                if ( yi != xi ):
                    liste_matchs_j.append((ji,xi,yi))

        for xi in range(ne):
            liste = np.where(liste_matchs_j       )
            clauses += cnf_au_plus(liste) +"\n"
            
        liste_j.append(liste_matchs_j)



    return clauses