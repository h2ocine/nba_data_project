import os
import pandas as pd

def get_dataframes_csv_file(dossier):
    """ Get DataFrames from CSV files in a specified directory """
    dataframes = []  
    
    for fichier in os.listdir(dossier):
        chemin_fichier = os.path.join(dossier, fichier)
        
        if fichier.endswith(".csv"):  
            dataframe = pd.read_csv(chemin_fichier)  
            dataframes.append(dataframe)  
    
    return dataframes