import pandas as pd
import sqlite3
import os

print(" Début de l'importation de la table STRUCTURE...")

dossier_actuel = os.path.dirname(os.path.abspath(__file__))

# Le fichier établissement.csv est en réalité un fichier Excel (.xlsx renommé)
# On le lit avec openpyxl directement
chemin_fichier = os.path.join(dossier_actuel, "jeux_de_donnees", "etablissement.xlsx")
chemin_bdd = os.path.join(dossier_actuel, "label_vivre.sqlite")

try:
    # 1. LECTURE comme Excel (le fichier est un .xlsx renommé en .csv)
    df_structure = pd.read_excel(chemin_fichier, engine='openpyxl')

    # 2. NETTOYAGE des noms de colonnes
    df_structure.columns = df_structure.columns.str.strip()
    df_structure['Structure'] = df_structure['Structure'].str.strip()
    df_structure['Type'] = df_structure['Type'].str.strip()
    df_structure['Région'] = df_structure['Région'].str.strip()
    df_structure['Département'] = df_structure['Département'].str.strip()

    # 3. AJOUT de l'Id_structure (généré automatiquement)
    df_structure.insert(0, 'Id_structure', range(1, len(df_structure) + 1))

    # 4. INJECTION SQL
    conn = sqlite3.connect(chemin_bdd)
    df_structure.to_sql("STRUCTURE", conn, if_exists="replace", index=False)
    conn.close()

    print(f" SUCCÈS ! {len(df_structure)} établissements ajoutés à la table STRUCTURE.")
    print()
    print(df_structure[['Id_structure', 'Structure', 'Type']].to_string())

except Exception as e:
    print(f" ERREUR : {e}")