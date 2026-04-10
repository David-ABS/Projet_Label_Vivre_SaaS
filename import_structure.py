import pandas as pd
import sqlite3
import os

print("⏳ Début de l'importation de la table STRUCTURE...")

dossier_actuel = os.path.dirname(os.path.abspath(__file__))
chemin_csv = os.path.join(dossier_actuel, "jeux_de_donnees", "etablissements.csv")
chemin_bdd = os.path.join(dossier_actuel, "label_vivre.sqlite")

try:
    # 1. LECTURE : On utilise 'latin-1' pour les accents, et on saute les mauvaises lignes
    df_structure = pd.read_csv(
        chemin_csv, 
        sep=',', 
        encoding='latin-1', 
        engine='python', 
        on_bad_lines='skip'
    )
    
    # 2. NETTOYAGE : On supprime les caractères invisibles (NULs) et les espaces
    df_structure.columns = df_structure.columns.astype(str).str.replace('\x00', '').str.strip()

    # 3. INJECTION SQL
    conn = sqlite3.connect(chemin_bdd)
    df_structure.to_sql("STRUCTURE", conn, if_exists="replace", index=False)
    conn.close()

    print(f"✅ SUCCÈS TOTAL ! {len(df_structure)} établissements ont été ajoutés à la table STRUCTURE.")

except FileNotFoundError:
    print("❌ ERREUR : Le fichier est introuvable. As-tu bien mis 'etablissements.csv' dans le dossier 'jeux_de_donnees' ?")
except Exception as e:
    print(f"❌ ERREUR LORS DE L'IMPORTATION : {e}")