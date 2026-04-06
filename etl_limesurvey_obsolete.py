import pandas as pd
import os # Bibliothèque pour gérer les chemins de dossiers

# 1. LE CORRECTIF ANTI-BUG : On calcule le chemin absolu automatiquement !
# __file__ représente ce script. On demande à Python de trouver le dossier exact où il est rangé.
dossier_actuel = os.path.dirname(os.path.abspath(__file__))
# On colle le nom de ton sous-dossier au chemin actuel
dossier_donnees = os.path.join(dossier_actuel, "jeux_de_donnees")

# 1. Préparation de la liste
# On stocke les noms exacts de tous tes fichiers xlsx dans une liste
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

# 2. La boucle d'extraction
# On va passer sur chaque fichier de la liste un par un
for nom_fichier in liste_fichiers:

    # Permet de créer automatiquement "jeux_de_donnees/EHPAD - Proches.xlsx..."
    chemin_complet = os.path.join(dossier_donnees, nom_fichier)

    print(f"\n--- TEST DU FICHIER : {nom_fichier} ---")
    
    try:
        # Lecture du fichier avec Pandas
        # L'encodage utf-8 est géré par défaut. "sep=','" indique que les colonnes sont séparées par des virgules
        # df signifie "DataFrame" (c'est le tableau de données virtuel créé en mémoire)
        df = pd.read_excel(chemin_complet, engine='openpyxl') 
        
        print(f"✅ Fichier chargé depuis '{dossier_donnees}' avec succès !")
        print(f"📊 Nombre de lignes (répondants) : {len(df)}")
        print(f"📊 Nombre de colonnes : {len(df.columns)}\n")
        
        # Affichage des 15 premières colonnes pour vérifier la structure
        print("📋 Liste des 15 premières colonnes détectées :")
        for i, colonne in enumerate(df.columns[:15]):
            print(f"  {i+1}. {colonne}")
            
    except Exception as e:
        # Si un fichier est introuvable ou mal formaté, l'erreur s'affichera ici sans faire planter tout le script
        print(f"❌ Erreur lors de la lecture : {e}")