import pandas as pd
import sqlite3
import os

print(" Début de l'importation de la table STRUCTURE...")

dossier_actuel = os.path.dirname(os.path.abspath(__file__))
chemin_csv = os.path.join(dossier_actuel, "jeux_de_donnees", "etablissements.csv")
chemin_bdd = os.path.join(dossier_actuel, "label_vivre.sqlite")

try:
    # 1. LECTURE : On utilise ENFIN le bon séparateur (;)
    df_structure = pd.read_csv(
        chemin_csv, 
        sep=';',  # <--- La clé du mystère était ici !
        encoding='utf-8', 
        engine='python', 
        on_bad_lines='skip'
    )
    
    # 2. DESTRUCTION DES COLONNES FANTÔMES (les fameux ;;;;;;)
    # On supprime toutes les colonnes qu'Excel a rajoutées et que Pandas nomme "Unnamed"
    df_structure = df_structure.loc[:, ~df_structure.columns.str.contains('^Unnamed')]
    
    # 3. NETTOYAGE DES NOMS DE COLONNES
    df_structure.columns = df_structure.columns.astype(str).str.replace('\x00', '').str.strip()

    # 4. DESTRUCTION DES LIGNES FANTÔMES
    nom_col = df_structure.columns[0]
    df_structure = df_structure.dropna(subset=[nom_col])
    df_structure = df_structure[df_structure[nom_col].astype(str).str.strip() != ""]

    # 5. INJECTION SQL
    conn = sqlite3.connect(chemin_bdd)
    df_structure.to_sql("STRUCTURE", conn, if_exists="replace", index=False)
    conn.close()

    print(f" SUCCÈS TOTAL ! {len(df_structure)} établissements ont été ajoutés à la table STRUCTURE.")

except Exception as e:
    print(f"❌ ERREUR : {e}")