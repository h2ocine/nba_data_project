import os
import pandas as pd
import numbers
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# --------------   Calcul

def is_numeric(value):
    return isinstance(value, numbers.Number)

# -------------- Data load




# Fonction pour vérifier les problèmes dans les données
def check_data_problems(file_path_template, columns_to_check, start_year=2001, end_year=2023):
    for year in range(start_year, end_year + 1):
        year_str = f"{year}-{str(year + 1)[-2:]}"  # Format des années ex: 2001-02
        file_path = file_path_template.format(year_str)
        
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            continue
        
        # Charger les données
        df = pd.read_csv(file_path)
        
        # Initialiser une liste pour stocker les problèmes
        problems = []
        
        # Valeurs manquantes
        missing_values = df.isnull().sum()
        if missing_values.any():
            problems.append(f"Missing values:\n{missing_values[missing_values > 0]}")
        
        # Doublons
        duplicated_count = df.duplicated().sum()
        if duplicated_count > 0:
            problems.append(f"Duplicated rows: {duplicated_count}")
        
        # Vérifier les colonnes numériques spécifiques
        for column in columns_to_check:
            for value in df[column]:
                if not is_numeric(value):
                    problems.append(f"Non-numeric values in column {column}")


        # Si des problèmes ont été trouvés, les imprimer
        if problems:
            print(f"\nProblems in file {file_path}:")
            for problem in problems:
                print(problem)



# Nouvelle fonction pour analyser les corrélations entre les variables
def analyze_correlations(df, variables):
    corr = df[variables].corr()
    plt.figure(figsize=(12, 10))
    sns.heatmap(corr, annot=True, cmap='coolwarm', fmt='.2f')
    plt.title('Correlation Matrix')
    plt.show()

# Load data and group by years for teamstats
def load_all_data_teams(file_path_template, start_year=2001, end_year=2022):
    all_data = []
    for year in range(start_year, end_year + 1):
        year_str = f"{year}-{str(year + 1)[-2:]}"  # Format des années ex: 2001-02
        file_path = file_path_template.format(year_str)
        
        if os.path.exists(file_path):
            df = pd.read_csv(file_path)
            df['Year'] = year
            all_data.append(df)
        else:
            print(f"File not found: {file_path}")
    
    if all_data:
        return pd.concat(all_data, ignore_index=True)
    else:
        return pd.DataFrame()

# Fonction pour filtrer les colonnes numériques spécifiques
def filter_selected_columns(df, selected_columns):
    return df[selected_columns]

# Fonction pour calculer les statistiques descriptives par année
def descriptive_stats(df, groupby_col='Year'):
    numeric_df = df.select_dtypes(include=[np.number])
    return numeric_df.groupby(groupby_col).agg(['mean', 'median', 'std', 'min', 'max'])




# Plots :  

# Fonction pour visualiser chaque variable séparément en grille
def plot_all_variables(df, variables, stat, y_label, title_prefix):
    num_plots = len(variables)
    num_cols = 5  # Nombre de colonnes dans la grille
    num_rows = (num_plots + num_cols - 1) // num_cols  # Calculer le nombre de lignes nécessaires
    
    plt.figure(figsize=(15, num_rows * 5))
    
    for i, col in enumerate(variables):
        if (col, stat) in df.columns:
            plt.subplot(num_rows, num_cols, i + 1)
            sns.lineplot(x=df.index, y=df[(col, stat)], label=col)
            plt.title(f"{title_prefix} {col} Over Time")
            plt.xlabel('Year')
            plt.ylabel(y_label)
            plt.legend()
            plt.grid(True)
    
    plt.tight_layout()
    plt.show()

def plot_violin_plots(df, variables):
    num_plots = len(variables)
    num_cols = 5  # Nombre de colonnes dans la grille
    num_rows = (num_plots + num_cols - 1) // num_cols  # Calculer le nombre de lignes nécessaires
    
    plt.figure(figsize=(15, num_rows * 5))
    
    for i, col in enumerate(variables):
        if col in df.columns:
            plt.subplot(num_rows, num_cols, i + 1)
            sns.violinplot(y=col, data=df)
            plt.title(f"Distribution of {col}")
            plt.xlabel('All Data')
            plt.ylabel(col)
            plt.grid(True)
    
    plt.tight_layout()
    plt.show()

def plot_distributions_and_relations(df, variables):
    sns.pairplot(df[variables])
    plt.suptitle('Distributions and Relations Between Variables', y=1.02)
    plt.show()
# Old utils files



def get_dataframes_csv_file(dossier):
    """ Get DataFrames from CSV files in a specified directory """
    dataframes = []  
    
    for fichier in os.listdir(dossier):
        chemin_fichier = os.path.join(dossier, fichier)
        
        if fichier.endswith(".csv"):  
            dataframe = pd.read_csv(chemin_fichier)  
            dataframes.append(dataframe)  
    
    return dataframes
