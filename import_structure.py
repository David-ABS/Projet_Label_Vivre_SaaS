import pandas as pd
import sqlite3
import os

print(" Début de l'importation de la table STRUCTURE...")

dossier_actuel = os.path.dirname(os.path.abspath(__file__))
chemin_csv = os.path.join(dossier_actuel, "jeux_de_donnees", "etablissements.csv")
chemin_bdd = os.path.join(dossier_actuel, "label_vivre.sqlite")

try:
    # 1. LECTURE
    df_structure = pd.read_csv(
        chemin_csv, 
        sep=';',
        encoding='utf-8', 
        engine='python', 
        on_bad_lines='skip'
    )
    
    # 2. NETTOYAGE
    df_structure = df_structure.loc[:, ~df_structure.columns.str.contains('^Unnamed')]
    df_structure.columns = df_structure.columns.astype(str).str.replace('\x00', '').str.strip()

    nom_col = df_structure.columns[0]
    df_structure = df_structure.dropna(subset=[nom_col])
    df_structure = df_structure[df_structure[nom_col].astype(str).str.strip() != ""]

    # 3. LA CORRECTION : Ajout de la colonne Id_structure (Numérotation de 1 à N)
    df_structure.insert(0, 'Id_structure', range(1, len(df_structure) + 1))

    # 4. INJECTION SQL
    conn = sqlite3.connect(chemin_bdd)
    df_structure.to_sql("STRUCTURE", conn, if_exists="replace", index=False)
    conn.close()

    print(f" SUCCÈS TOTAL ! {len(df_structure)} établissements ajoutés avec leur Id_structure.")

except Exception as e:
    print(f" ERREUR : {e}")