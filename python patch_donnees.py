import sqlite3
import pandas as pd
import numpy as np
import os

print(" Ajout des colonnes manquantes dans la base de données...")

dossier_actuel = os.path.dirname(os.path.abspath(__file__))
chemin_bdd = os.path.join(dossier_actuel, "label_vivre.sqlite")

try:
    conn = sqlite3.connect(chemin_bdd)
    
    # 1. On lit la table actuelle
    df = pd.read_sql_query("SELECT * FROM DONNEES_LIMESURVEY_NETTOYEES", conn)
    
    # 2. On extrait l'année (les 4 premiers caractères de la date)
    df['Annee'] = df['Date de soumission'].astype(str).str[:4]
    
    # 3. On simule des Id_structure (entre 1 et 31) pour que les filtres marchent 
    # (Comme mentionné dans ton alerte "Données simulées")
    np.random.seed(42) # Pour avoir toujours la même simulation
    df['Id_structure'] = np.random.randint(1, 32, size=len(df))
    
    # 4. On sauvegarde la table enrichie
    df.to_sql("DONNEES_LIMESURVEY_NETTOYEES", conn, if_exists="replace", index=False)
    conn.close()

    print(" SUCCÈS ! Les colonnes 'Annee' et 'Id_structure' ont été ajoutées.")

except Exception as e:
    print(f" ERREUR : {e}")