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

def dflist_to_csv(df_list, folder):
    """take a list of data frames and create a csv file for each data frame"""
    folder = os.path.normpath(folder) 
    
    if not os.path.exists(folder):
        os.makedirs(folder)
    
    for df in df_list:
        file_name = df['Title'][0].replace(" ", "-")
        file_path = os.path.join(folder, f"{file_name}.csv")
        
        if not os.path.exists(file_path):
            df.to_csv(file_path, index=False)