import pandas as pd
import os
import sqlite3
import random

# 1. GESTION DES CHEMINS
dossier_actuel = os.path.dirname(os.path.abspath(__file__))
dossier_donnees = os.path.join(dossier_actuel, "jeux_de_donnees")

# 2. LISTE DES 9 FICHIERS
liste_fichiers = [
    "EHPAD - Proches.xlsx",
    "EHPAD - Résidents.xlsx",
    "EHPAD Equipe.xlsx",
    "HAP - Equipe.xlsx",
    "HAP - Habitants.xlsx",
    "HAP - Proches.xlsx",
    "RA RSS - Equipe.xlsx",
    "RA RSS - Proches.xlsx",
    "RA RSS - Résidents.xlsx"
]

# 3. COLONNES FIXES POUR LE DÉPIVOTAGE
colonnes_fixes = [
    'ID de la réponse', 'Date de soumission', 'Dernière page',
    'Langue de départ', 'Tête de série', 'Date de lancement', 'Date de la dernière action'
]

tous_les_tableaux = []

# 4. BOUCLE EXTRACTION + TRANSFORMATION
print(" DÉMARRAGE DE LA TRANSFORMATION DES FICHIERS...\n")

for nom_fichier in liste_fichiers:
    chemin_complet = os.path.join(dossier_donnees, nom_fichier)
    print(f"--- TRAITEMENT : {nom_fichier} ---")

    try:
        # A. LECTURE
        df = pd.read_excel(chemin_complet, engine='openpyxl')
        print(f"  > AVANT : {df.shape[0]} répondants pour {df.shape[1]} colonnes")

        # B. DÉPIVOTAGE
        df_long = pd.melt(
            df,
            id_vars=colonnes_fixes,
            var_name='Question_Formulation',
            value_name='Valeur_Brute'
        )

        # C. NETTOYAGE
        df_long = df_long.dropna(subset=['Valeur_Brute'])

        # D. MAPPING Texte → Score
        dictionnaire_scores = {
            "Tout à fait d'accord": 4,
            "Plutôt d'accord": 3,
            "Plutôt pas d'accord": 2,
            "Pas du tout d'accord": 1,
            "Oui": 1,
            "Non": 0
        }
        df_long['Score'] = df_long['Valeur_Brute'].map(dictionnaire_scores).fillna(df_long['Valeur_Brute'])

        tous_les_tableaux.append(df_long)
        print(f"  > TRANSFORMATION : {df_long.shape[0]} lignes prêtes.")
        print("-" * 50)

    except Exception as e:
        print(f" Erreur sur ce fichier : {e}")


# 5. FUSION
print("\n FUSION DES 9 FICHIERS EN COURS...")
df_final = pd.concat(tous_les_tableaux, ignore_index=True)

# ================================================================
# TÂCHE 18 — Ajout colonne Annee (extraite de la date de soumission)
# ================================================================
df_final['Annee'] = pd.to_datetime(
    df_final['Date de soumission'], errors='coerce'
).dt.year.astype('Int64')

# ================================================================
# TÂCHE 18 — Ajout colonne Id_structure (simulée en attendant
# la réponse du client sur l'identification LimeSurvey)
# Chaque répondant unique est assigné aléatoirement à un
# établissement EHPAD (Id 1 à 19).
# À METTRE À JOUR quand le client fournit le vrai identifiant.
# ================================================================
random.seed(42)
ids_repondants = df_final['ID de la réponse'].unique()
ehpad_ids = list(range(1, 20))  # 19 EHPAD dans la table STRUCTURE
mapping_structure = {id_rep: random.choice(ehpad_ids) for id_rep in ids_repondants}
df_final['Id_structure'] = df_final['ID de la réponse'].map(mapping_structure)

# 6. INJECTION SQL
print(" INJECTION SQL...")
chemin_bdd = os.path.join(dossier_actuel, 'label_vivre.sqlite')
connexion = sqlite3.connect(chemin_bdd)
df_final.to_sql('DONNEES_LIMESURVEY_NETTOYEES', connexion, if_exists='replace', index=False)
connexion.close()

# 7. VÉRIFICATION
print(f" {len(df_final)} lignes injectées dans DONNEES_LIMESURVEY_NETTOYEES")
print(f"   Colonnes : {list(df_final.columns)}")
print(f"   Années disponibles : {sorted(df_final['Annee'].dropna().unique().tolist())}")
print(f"   Répondants uniques : {df_final['ID de la réponse'].nunique()}")

# Sauvegarde fichier de vérification
df_final.to_csv("VERIFICATION_RESULTAT.csv", index=False, encoding='utf-8')
print(" Fichier de vérification créé : VERIFICATION_RESULTAT.csv")

print("\n TOUS LES FICHIERS ONT ÉTÉ TRAITÉS ET INJECTÉS DANS SQLITE !")