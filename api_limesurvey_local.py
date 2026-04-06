import sqlite3
import json
import os
from datetime import datetime

# ============================================================
# ID 11 - AUTOMATISATION : Connexion BDD + Récupération JSON
# Simule une API LimeSurvey en lisant directement SQLite
# ============================================================

# 1. CHEMIN DE LA BASE DE DONNÉES
# Modifie ce chemin pour pointer vers ton fichier label_vivre.sqlite
chemin_bdd = os.path.join(os.path.dirname(os.path.abspath(__file__)), "label_vivre.sqlite")


def get_connexion():
    """Crée et retourne une connexion à la base SQLite."""
    conn = sqlite3.connect(chemin_bdd)
    conn.row_factory = sqlite3.Row  # Permet d'accéder aux colonnes par nom
    return conn


# ============================================================
# FONCTION 1 : Récupérer TOUTES les réponses (avec pagination)
# ============================================================
def get_toutes_reponses(limite=100, offset=0):
    """
    Récupère toutes les réponses de la base, avec pagination.

    Paramètres :
        limite  : nombre de résultats à retourner (défaut: 100)
        offset  : point de départ dans les résultats (défaut: 0)

    Retourne : dict JSON avec les données et les métadonnées
    """
    conn = get_connexion()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM DONNEES_LIMESURVEY_NETTOYEES")
    total = cursor.fetchone()[0]

    cursor.execute("""
        SELECT 
            "ID de la réponse"      AS id_reponse,
            "Date de soumission"    AS date_soumission,
            "Dernière page"         AS derniere_page,
            "Langue de départ"      AS langue,
            "Tête de série"         AS token_anonyme,
            "Date de lancement"     AS date_lancement,
            "Question_Formulation"  AS question,
            "Valeur_Brute"          AS valeur_brute,
            "Score"                 AS score
        FROM DONNEES_LIMESURVEY_NETTOYEES
        LIMIT ? OFFSET ?
    """, (limite, offset))

    lignes = cursor.fetchall()
    conn.close()

    resultat = {
        "statut": "succès",
        "horodatage": datetime.now().isoformat(),
        "source": "label_vivre.sqlite",
        "pagination": {
            "total": total,
            "limite": limite,
            "offset": offset,
            "page_courante": (offset // limite) + 1,
            "total_pages": (total // limite) + 1
        },
        "donnees": [dict(row) for row in lignes]
    }

    return resultat


# ============================================================
# FONCTION 2 : Filtrer par question
# ============================================================
def get_reponses_par_question(mot_cle):
    """
    Filtre les réponses contenant un mot-clé dans la question.

    Paramètres :
        mot_cle : texte à chercher dans la formulation de la question

    Retourne : dict JSON avec les résultats filtrés
    """
    conn = get_connexion()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 
            "ID de la réponse"      AS id_reponse,
            "Date de soumission"    AS date_soumission,
            "Question_Formulation"  AS question,
            "Valeur_Brute"          AS valeur_brute,
            "Score"                 AS score
        FROM DONNEES_LIMESURVEY_NETTOYEES
        WHERE "Question_Formulation" LIKE ?
        ORDER BY "Date de soumission" DESC
    """, (f"%{mot_cle}%",))

    lignes = cursor.fetchall()
    conn.close()

    resultat = {
        "statut": "succès",
        "filtre_question": mot_cle,
        "nombre_resultats": len(lignes),
        "donnees": [dict(row) for row in lignes]
    }

    return resultat


# ============================================================
# FONCTION 3 : Score moyen par question (pour les analyses NPS)
# ============================================================
def get_scores_moyens():
    """
    Calcule le score moyen pour chaque question.
    Utile pour préparer les analyses SQL (ID 12, 13, 14).

    Retourne : dict JSON avec le score moyen par question
    """
    conn = get_connexion()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 
            "Question_Formulation"                        AS question,
            COUNT(*)                                      AS nb_reponses,
            ROUND(AVG(CAST("Score" AS FLOAT)), 2)         AS score_moyen,
            MIN(CAST("Score" AS FLOAT))                   AS score_min,
            MAX(CAST("Score" AS FLOAT))                   AS score_max
        FROM DONNEES_LIMESURVEY_NETTOYEES
        WHERE CAST("Score" AS FLOAT) IS NOT NULL
        GROUP BY "Question_Formulation"
        ORDER BY score_moyen DESC
    """)

    lignes = cursor.fetchall()
    conn.close()

    resultat = {
        "statut": "succès",
        "horodatage": datetime.now().isoformat(),
        "nombre_questions": len(lignes),
        "scores_par_question": [dict(row) for row in lignes]
    }

    return resultat


# ============================================================
# FONCTION 4 : Résumé général de la base (tableau de bord)
# ============================================================
def get_resume_bdd():
    """
    Retourne un résumé statistique de la base de données.
    Idéal pour le tableau de bord Streamlit (ID 15).

    Retourne : dict JSON avec les stats générales
    """
    conn = get_connexion()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM DONNEES_LIMESURVEY_NETTOYEES")
    total_reponses = cursor.fetchone()[0]

    cursor.execute('SELECT COUNT(DISTINCT "ID de la réponse") FROM DONNEES_LIMESURVEY_NETTOYEES')
    total_repondants = cursor.fetchone()[0]

    cursor.execute('SELECT COUNT(DISTINCT "Question_Formulation") FROM DONNEES_LIMESURVEY_NETTOYEES')
    total_questions = cursor.fetchone()[0]

    cursor.execute('SELECT MIN("Date de soumission"), MAX("Date de soumission") FROM DONNEES_LIMESURVEY_NETTOYEES')
    dates = cursor.fetchone()

    conn.close()

    resultat = {
        "statut": "succès",
        "horodatage": datetime.now().isoformat(),
        "resume": {
            "total_lignes": total_reponses,
            "total_repondants_uniques": total_repondants,
            "total_questions_distinctes": total_questions,
            "date_premiere_reponse": dates[0],
            "date_derniere_reponse": dates[1]
        }
    }

    return resultat


# ============================================================
# PROGRAMME PRINCIPAL - Démonstration des 4 fonctions
# ============================================================
if __name__ == "__main__":

    print("=" * 60)
    print("  ID 11 - API LOCALE LIMESURVEY (SQLite → JSON)")
    print("=" * 60)

    # --- TEST 1 : Résumé général ---
    print("\n[1] RÉSUMÉ DE LA BASE DE DONNÉES")
    print("-" * 40)
    resume = get_resume_bdd()
    print(json.dumps(resume, indent=2, ensure_ascii=False))

    # --- TEST 2 : Premières réponses (pagination) ---
    print("\n[2] RÉCUPÉRATION DES 3 PREMIÈRES RÉPONSES")
    print("-" * 40)
    reponses = get_toutes_reponses(limite=3, offset=0)
    print(json.dumps(reponses, indent=2, ensure_ascii=False))

    # --- TEST 3 : Filtre par mot-clé ---
    print("\n[3] FILTRE PAR QUESTION (mot-clé : 'satisfait')")
    print("-" * 40)
    filtrees = get_reponses_par_question("satisfait")
    print(f"  Nombre de résultats : {filtrees['nombre_resultats']}")
    if filtrees['donnees']:
        print(f"  Exemple : {json.dumps(filtrees['donnees'][0], ensure_ascii=False)}")

    # --- TEST 4 : Scores moyens ---
    print("\n[4] SCORES MOYENS PAR QUESTION (Top 5)")
    print("-" * 40)
    scores = get_scores_moyens()
    for q in scores["scores_par_question"][:5]:
        print(f"  Score {q['score_moyen']} | {q['nb_reponses']} rép. | {q['question'][:60]}...")

    print("\n" + "=" * 60)
    print("  TOUTES LES FONCTIONS API OPÉRATIONNELLES !")
    print("=" * 60)