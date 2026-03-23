import sqlite3

# 1. Créer le fichier de la base de données 
connexion = sqlite3.connect('label_vivre.sqlite')
curseur = connexion.cursor()

# 2. Lire le fichier SQL
with open('SCRIPT_CREATION_BDD_V1.sql', 'r', encoding='utf-8') as fichier_sql:
    script_sql = fichier_sql.read()

# 3. Exécuter le code SQL pour créer toutes les tables
curseur.executescript(script_sql)

# 4. Valider et fermer
connexion.commit()
connexion.close()

print("Succès ! La base de données label_vivre.sqlite a été créée avec toutes tes tables.")