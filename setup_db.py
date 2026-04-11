import sqlite3
import os

# 1. Sécurité absolue sur les chemins
dossier_actuel = os.path.dirname(os.path.abspath(__file__))
chemin_bdd = os.path.join(dossier_actuel, "label_vivre.sqlite")
chemin_sql = os.path.join(dossier_actuel, "SCRIPT_CREATION_BDD_V1.sql")

print(f"⏳ Création des tables dans : {chemin_bdd}")

try:
    # 2. Créer le fichier de la base de données 
    connexion = sqlite3.connect(chemin_bdd)
    curseur = connexion.cursor()

    # 3. Lire le fichier SQL
    with open(chemin_sql, 'r', encoding='utf-8') as fichier_sql:
        script_sql = fichier_sql.read()

    # 4. Exécuter le code SQL
    curseur.executescript(script_sql)
    connexion.commit()
    connexion.close()

    print("✅ SUCCÈS ! Toutes les tables de SCRIPT_CREATION_BDD_V1.sql ont été créées.")
except Exception as e:
    print(f"❌ ERREUR : {e}")