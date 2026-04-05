import pandas as pd
import os
import sqlite3 # La bibliothèque intégrée pour parler à la base de données

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

# 3. NOTRE ANCRE POUR LE DÉPIVOTAGE
# Ces 7 colonnes communes ne bougeront pas pendant la transformation
colonnes_fixes = [
    'ID de la réponse', 'Date de soumission', 'Dernière page', 
    'Langue de départ', 'Tête de série', 'Date de lancement', 'Date de la dernière action'
]

# 4. LA BOUCLE  (Extraction + Transformation+ Chargement)
print(" DÉMARRAGE DE LA TRANSFORMATION DES 9 FICHIERS...\n")

for nom_fichier in liste_fichiers:
    chemin_complet = os.path.join(dossier_donnees, nom_fichier)
    print(f"---TRAITEMENT : {nom_fichier} ---")
    
    try:
        # A. LECTURE (Format Large)
        df = pd.read_excel(chemin_complet, engine='openpyxl') 
        print(f"  > AVANT : {df.shape[0]} répondants pour {df.shape[1]} colonnes")
        
        # B. DÉPIVOTAGE (Passage au Format Long)
        df_long = pd.melt(
            df, 
            id_vars=colonnes_fixes,          
            var_name='Question_Formulation', # Les colonnes de questions deviennent des lignes
            value_name='Valeur_Brute'        # Les réponses
        )
        
        # C. NETTOYAGE (On enlève les questions auxquelles la personne n'a pas répondu)
        df_long = df_long.dropna(subset=['Valeur_Brute'])
        
        # --- D. MAPPING (Traduction Texte -> Chiffre) ---
        # On apprend à Python à noter les réponses pour les futurs calculs
        dictionnaire_scores = {
            "Tout à fait d'accord": 4,
            "Plutôt d'accord": 3,
            "Plutôt pas d'accord": 2,
            "Pas du tout d'accord": 1,
            "Oui": 1,
            "Non": 0
        }
        # Création de la colonne 'Score' : si c'est du texte connu, on met le chiffre, sinon on garde la valeur
        df_long['Score'] = df_long['Valeur_Brute'].map(dictionnaire_scores).fillna(df_long['Valeur_Brute'])
        
        print(f"  > TRANSFORMATION : {df_long.shape[0]} lignes générées avec succès.")

        # --- E. CHARGEMENT EN BASE (Load) ---
        # On se connecte à ton fichier de base de données
        connexion = sqlite3.connect('label_vivre.sqlite')
        
        # On injecte nos données dans une table de consolidation.
        # if_exists='append' permet de coller les fichiers les uns à la suite des autres
        df_long.to_sql('DONNEES_LIMESURVEY_NETTOYEES', connexion, if_exists='append', index=False)
        
        # On ferme la porte de la BDD proprement
        connexion.close()
        print("  INJECTION SQL : Données sauvegardées dans la base de données !")

        print("-" * 50) # Petite ligne de séparation visuelle
        
        # Sauvegarde d'un fichier de vérification pour le premier fichier traité
        if nom_fichier == "EHPAD - Proches.xlsx":
            df_long.to_csv("VERIFICATION_RESULTAT.csv", index=False, encoding='utf-8')
            print("   Fichier de vérification créé : VERIFICATION_RESULTAT.csv")
            
    except Exception as e:
        print(f" Erreur sur ce fichier : {e}")

print("\n TOUS LES FICHIERS ONT ÉTÉ TRAITÉS ET INJECTÉS DANS SQLITE !")