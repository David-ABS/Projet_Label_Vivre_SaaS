import sqlite3
import pandas as pd

print(" VÉRIFICATION DE LA BASE DE DONNÉES...")

# 1. On se connecte à la base
connexion = sqlite3.connect('label_vivre.sqlite')

# 2. On compte le nombre total de lignes injectées
curseur = connexion.cursor()
curseur.execute("SELECT COUNT(*) FROM DONNEES_LIMESURVEY_NETTOYEES")
total_lignes = curseur.fetchone()[0]

# 3. On demande à voir les 5 premières lignes
df_extrait = pd.read_sql_query("SELECT * FROM DONNEES_LIMESURVEY_NETTOYEES LIMIT 5", connexion)

connexion.close()

print(f"\n SUCCÈS ! Ta base de données contient exactement {total_lignes} réponses de formulaires.")
print("\n Voici un extrait des 5 premières lignes dans SQLite :")
print(df_extrait[['ID de la réponse', 'Question_Formulation', 'Valeur_Brute', 'Score']])