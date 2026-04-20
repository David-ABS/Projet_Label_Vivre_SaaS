import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
from werkzeug.security import check_password_hash
from textblob import TextBlob


st.set_page_config(
    page_title="Label Vivre",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    :root {
        --orange: #F5A623; --rose: #E8706A; --vert: #6BBFB5;
        --beige: #FAF6F1; --gris: #5C5C5C;
    }
    .stApp { background-color: #FAF6F1; }
   .header-bar {
    background-color: #F5A623;
    padding: 20px 40px;
    margin: -1rem -1rem 2rem -1rem;
    display: flex;
    align-items: center;
    justify-content: flex-start;   /*  IMPORTANT */
     }
    .header-title {
        font-family: 'Georgia', serif; font-size: 2.5rem;
        font-weight: bold; color: #5C5C5C; text-align: center; margin: 0;
    }
    .header-subtitle {
        font-family: 'Georgia', serif; font-size: 1rem;
        color: #5C5C5C; font-style: italic; text-align: center;
    }
    .kpi-card {
        background: white; border-radius: 15px; padding: 25px;
        text-align: center; box-shadow: 0 2px 10px rgba(0,0,0,0.08); margin: 5px;
    }
    .kpi-value { font-size: 2.5rem; font-weight: bold; margin: 10px 0; }
    .kpi-label { font-size: 0.9rem; color: #888; font-family: 'Georgia', serif; }
    [data-testid="stSidebar"] { display: none; }
    .section-title {
        font-family: 'Georgia', serif; font-size: 1.3rem; color: #5C5C5C;
        font-weight: bold; border-left: 4px solid #F5A623;
        padding-left: 10px; margin: 20px 0 15px 0;
    }
    .filtre-bar {
        background: white; border-radius: 12px; padding: 16px 24px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06); margin-bottom: 20px;
        border-left: 4px solid #6BBFB5;
    }
    .badge-admin {
        background: #F5A623; color: white; padding: 4px 12px;
        border-radius: 20px; font-size: 0.75rem; font-weight: bold;
    }
    .badge-etab {
        background: #6BBFB5; color: white; padding: 4px 12px;
        border-radius: 20px; font-size: 0.75rem; font-weight: bold;
    }
    .alerte-simu {
        background: #FFF8E7; border: 1px solid #F5A623;
        border-radius: 8px; padding: 10px 16px;
        font-size: 0.85rem; color: #8B6914; margin-bottom: 16px;
    }
    
    /* ========================================= */
    /* STRATÉGIE 1 : CSS POUR L'IMPRESSION PDF   */
    /* ========================================= */
    @media print {
        header, .stButton, [data-testid="stSidebar"], .filtre-bar, .alerte-simu { 
            display: none !important; 
        }
        .stApp, body { 
            background-color: white !important; 
        }
        .kpi-card, .js-plotly-plot { 
            page-break-inside: avoid !important; 
            break-inside: avoid;
        }
        * {
            -webkit-print-color-adjust: exact !important;
            print-color-adjust: exact !important;
        }
    }
  div.stButton > button,
div[data-testid="stFormSubmitButton"] > button,
button[kind="primary"],
button[kind="secondary"] {
    background-color: #E65A5A !important;
    color: white !important;
    border-radius: 10px !important;
    height: 45px !important;
    font-weight: bold !important;
    border: none !important;
}

div.stButton > button:hover,
div[data-testid="stFormSubmitButton"] > button:hover,
button[kind="primary"]:hover,
button[kind="secondary"]:hover {
    background-color: #cc4f4f !important;
    color: white !important;
    border: none !important;
}
            /* INPUT TEXT (Identifiant + Mot de passe) */
input {
    background-color: #F0FAF8 !important;   /* vert très clair */
    border: 2px solid #6BBFB5 !important;   /* vert logo */
    border-radius: 8px !important;
    color: #333 !important;
}

/* Focus (quand tu cliques) */
input:focus {
    border: 2px solid #6BBFB5 !important;
    box-shadow: 0 0 6px rgba(107, 191, 181, 0.4) !important;
    outline: none !important;
}
            /* Bouton oeil du mot de passe */
[data-testid="stTextInput"] button,
[data-testid="stTextInput"] button:hover,
[data-testid="stTextInput"] button:focus,
[data-testid="stTextInput"] button:active {
    color: #6BBFB5 !important;
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
}

/* Icône SVG de l'oeil */
[data-testid="stTextInput"] button svg,
[data-testid="stTextInput"] button:hover svg,
[data-testid="stTextInput"] button:focus svg,
[data-testid="stTextInput"] button:active svg {
    fill: #6BBFB5 !important;
    color: #6BBFB5 !important;
}

/* Option hover rouge */
[data-testid="stTextInput"] button:hover svg {
    fill: #E65A5A !important;
    color: #E65A5A !important;
}
</style>
""", unsafe_allow_html=True)

# HEADER
# HEADER
st.markdown(
    """
    <div class="header-bar"></div>
    """,
    unsafe_allow_html=True
)

col_logo, col_text = st.columns([1, 6])

with col_logo:
    st.image("assets/logo.png", width=90)

with col_text:
    st.markdown(
        """
        <div style="padding-top: 8px;">
            <div class="header-title" style="text-align:left;">Label Vivre</div>
            <div class="header-subtitle" style="text-align:left;">Engagés pour nos aînés</div>
        </div>
        """,
        unsafe_allow_html=True
    )


def charger_comptes():
    """Charge tous les comptes depuis la table UTILISATEUR de SQLite."""
    try:
        chemin = os.path.join(os.path.dirname(os.path.abspath(__file__)), "label_vivre.sqlite")
        conn = sqlite3.connect(chemin)
        df = pd.read_sql_query(
            "SELECT Id_utilisateur, Nom, Identifiant, Hash_mdp, Role, Id_structure FROM UTILISATEUR",
            conn
        )
        conn.close()
        comptes = {}
        for _, row in df.iterrows():
            comptes[str(row['Identifiant'])] = {
                "hash": row['Hash_mdp'],
                "profil": row['Role'],
                "Id_structure": None if pd.isna(row['Id_structure']) else int(row['Id_structure']),
                "nom_affiche": row['Nom'],
                "id_utilisateur": int(row['Id_utilisateur'])
            }
        return comptes
    except Exception as e:
        st.error(f"Erreur chargement comptes : {e}")
        return {}

COMPTES_AUTORISES = charger_comptes()

# SESSION STATE

for key, val in [
    ('identifiant', None), ('profil', None), ('page', 'accueil'),
    ('filtre_structure', None), ('filtre_annee', None)
]:
    if key not in st.session_state:
        st.session_state[key] = val

def logout():
    for key in ['identifiant', 'profil', 'page', 'filtre_structure', 'filtre_annee']:
        st.session_state[key] = None
    st.session_state.page = 'accueil'
    st.rerun()



if st.session_state.identifiant is None:
    st.markdown("<h2 style='text-align:center; color:#F5A623;'>Accès Restreint</h2>", unsafe_allow_html=True)
    st.markdown("""
<div style="
    background-color: #6BBFB5;
    color: white;
    padding: 15px;
    border-radius: 10px;
    text-align: center;
    font-weight: 500;
    margin-bottom: 30px;
">
L'accès à cette plateforme est réservé aux administrateurs et aux directions d'établissements.
</div>
""", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("login_form"):
            username = st.text_input("Identifiant :").strip().lower()
            password = st.text_input("Mot de passe :", type="password")
            submit = st.form_submit_button("Se connecter", use_container_width=True)

            if submit:
                if username in COMPTES_AUTORISES:
                    compte = COMPTES_AUTORISES[username]
                    if check_password_hash(compte["hash"], password):
                        st.session_state.identifiant = username
                        st.session_state.profil = compte["profil"]
                        st.session_state.page = 'dashboard'
                        if compte["profil"] == "etablissement":
                            st.session_state.filtre_structure = compte["Id_structure"]
                        st.rerun()
                    else:
                        st.error(" Mot de passe incorrect.")
                else:
                    st.error(" Identifiant inconnu.")
    st.stop()


# CONNEXION BASE DE DONNÉES

@st.cache_resource
def get_connexion():
    chemin = os.path.join(os.path.dirname(os.path.abspath(__file__)), "label_vivre.sqlite")
    return sqlite3.connect(chemin, check_same_thread=False)

@st.cache_data
def get_structures():
    conn = get_connexion()
    return pd.read_sql_query(
        "SELECT Id_structure, Structure, Type, Département, Région FROM STRUCTURE ORDER BY Structure",
        conn
    )

@st.cache_data
def get_annees():
    conn = get_connexion()
    df = pd.read_sql_query(
        'SELECT DISTINCT Annee FROM DONNEES_LIMESURVEY_NETTOYEES ORDER BY Annee DESC', conn
    )
    return df['Annee'].tolist()


# FONCTIONS DE DONNÉES FILTRÉES PAR ÉTABLISSEMENT + ANNÉE

def build_filtre(id_structure, annee):
    conditions = ["CAST(\"Score\" AS FLOAT) IN (1.0,2.0,3.0,4.0)"]
    params = []
    if id_structure:
        conditions.append("Id_structure = ?")
        params.append(id_structure)
    if annee:
        conditions.append("Annee = ?")
        params.append(annee)
    return " AND ".join(conditions), params

def get_nps(id_structure, annee):
    conn = get_connexion()
    where, params = build_filtre(id_structure, annee)
    query = f"""
        SELECT
            COUNT(*) AS total,
            ROUND(100.0 * SUM(CASE WHEN CAST("Score" AS FLOAT) IN (3,4) THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_promoteurs,
            ROUND(100.0 * SUM(CASE WHEN CAST("Score" AS FLOAT) = 2 THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_passifs,
            ROUND(100.0 * SUM(CASE WHEN CAST("Score" AS FLOAT) = 1 THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_detracteurs,
            ROUND(
                100.0 * SUM(CASE WHEN CAST("Score" AS FLOAT) IN (3,4) THEN 1 ELSE 0 END) / COUNT(*) -
                100.0 * SUM(CASE WHEN CAST("Score" AS FLOAT) = 1 THEN 1 ELSE 0 END) / COUNT(*),
            1) AS NPS
        FROM DONNEES_LIMESURVEY_NETTOYEES
        WHERE {where}
        AND "Question_Formulation" NOT LIKE 'Durée%'
        AND "Question_Formulation" NOT LIKE 'Commentaire%'
        AND "Valeur_Brute" NOT IN ('Oui', 'Non')
    """
    return pd.read_sql_query(query, conn, params=params).iloc[0]

def get_scores_public(id_structure, annee):
    conn = get_connexion()
    where, params = build_filtre(id_structure, annee)
    query = f"""
        SELECT
            CASE
                WHEN "Question_Formulation" LIKE '%résident%'
                  OR "Question_Formulation" LIKE '%habitant%' THEN 'Résidents'
                WHEN "Question_Formulation" LIKE '%proche%'   THEN 'Proches'
                WHEN "Question_Formulation" LIKE '%équipe%'
                  OR "Question_Formulation" LIKE '%salarié%'  THEN 'Équipe'
                ELSE 'Autre'
            END AS public,
            ROUND(AVG(CAST("Score" AS FLOAT)), 2) AS score_moyen,
            COUNT(DISTINCT "ID de la réponse") AS nb_repondants
        FROM DONNEES_LIMESURVEY_NETTOYEES
        WHERE {where}
        AND "Question_Formulation" NOT LIKE 'Durée%'
        GROUP BY public
        ORDER BY score_moyen DESC
    """
    return pd.read_sql_query(query, conn, params=params)

def get_top_questions(id_structure, annee):
    conn = get_connexion()
    where, params = build_filtre(id_structure, annee)
    query = f"""
        SELECT "Question_Formulation" AS question, ROUND(AVG(CAST("Score" AS FLOAT)), 2) AS score_moyen, COUNT(*) AS nb_reponses
        FROM DONNEES_LIMESURVEY_NETTOYEES
        WHERE {where} AND CAST("Score" AS FLOAT) IN (1.0, 2.0, 3.0, 4.0)
        AND "Question_Formulation" NOT LIKE 'Durée%' AND "Question_Formulation" NOT LIKE 'Commentaire%'
        GROUP BY "Question_Formulation" ORDER BY score_moyen DESC LIMIT 10
    """
    return pd.read_sql_query(query, conn, params=params)

def get_flop_questions(id_structure, annee):
    conn = get_connexion()
    where, params = build_filtre(id_structure, annee)
    query = f"""
        SELECT "Question_Formulation" AS question, ROUND(AVG(CAST("Score" AS FLOAT)), 2) AS score_moyen, COUNT(*) AS nb_reponses
        FROM DONNEES_LIMESURVEY_NETTOYEES
        WHERE {where} AND CAST("Score" AS FLOAT) IN (1.0, 2.0, 3.0, 4.0)
        AND "Question_Formulation" NOT LIKE 'Durée%' AND "Question_Formulation" NOT LIKE 'Commentaire%'
        GROUP BY "Question_Formulation" ORDER BY score_moyen ASC LIMIT 10
    """
    return pd.read_sql_query(query, conn, params=params)

def get_donnees_brutes(id_structure, annee, limite=100):
    conn = get_connexion()
    where, params = build_filtre(id_structure, annee)
    query = f"""
        SELECT
            "ID de la réponse" AS ID,
            "Date de soumission" AS Date,
            "Question_Formulation" AS Question,
            "Valeur_Brute" AS Réponse,
            "Score" AS Score
        FROM DONNEES_LIMESURVEY_NETTOYEES
        WHERE {where}
        LIMIT {limite}
    """
    return pd.read_sql_query(query, conn, params=params)

@st.cache_data
def get_analyse_verbatims(id_structure, annee):
    conn = get_connexion()
    where, params = build_filtre(id_structure, annee)
    
    # 1. Extraire les commentaires libres
    query = f"""
        SELECT 
            CASE 
                WHEN "Question_Formulation" LIKE '%résident%' OR "Question_Formulation" LIKE '%habitant%' THEN 'Résident'
                WHEN "Question_Formulation" LIKE '%équipe%' OR "Question_Formulation" LIKE '%salarié%' THEN 'Équipe'
                ELSE 'Proche'
            END AS public,
            "Valeur_Brute" AS commentaire
        FROM DONNEES_LIMESURVEY_NETTOYEES
        WHERE {where}
        AND ("Question_Formulation" LIKE '%remarque%' OR "Question_Formulation" LIKE '%commentaire%')
        AND "Valeur_Brute" IS NOT NULL AND "Valeur_Brute" != ''
    """
    df_commentaires = pd.read_sql_query(query, conn, params=params)
    
    # 2. Analyser le sentiment (-1 négatif à +1 positif)
    def calculer_sentiment(texte):
        try:
            return TextBlob(str(texte)).sentiment.polarity
        except:
            return 0.0

    if not df_commentaires.empty:
        df_commentaires['score_ia'] = df_commentaires['commentaire'].apply(calculer_sentiment)
        # 3. Récupérer le Top 5 et le Flop 5
        top_positifs = df_commentaires[df_commentaires['score_ia'] > 0.05].nlargest(5, 'score_ia')
        top_suggestions = df_commentaires[df_commentaires['score_ia'] < -0.05].nsmallest(5, 'score_ia')
        return top_positifs, top_suggestions
    else:
        return pd.DataFrame(), pd.DataFrame()




def get_nps_par_public(id_structure, annee):
    conn = get_connexion()
    where, params = build_filtre(id_structure, annee)
    publics = {
        'Résidents': ["LIKE '%résident%'", "LIKE '%habitant%'"],
        'Proches': ["LIKE '%proche%'"],
        'Équipe': ["LIKE '%équipe%'", "LIKE '%salarié%'"]
    }
    resultats = []
    for public, conditions in publics.items():
        filtre_public = " OR ".join([f'"Question_Formulation" {c}' for c in conditions])
        query = f"""
            SELECT '{public}' AS public,
                COUNT(*) AS total,
                ROUND(100.0 * SUM(CASE WHEN CAST("Score" AS FLOAT) IN (3,4) THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_promoteurs,
                ROUND(100.0 * SUM(CASE WHEN CAST("Score" AS FLOAT) = 1 THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_detracteurs,
                ROUND(100.0 * SUM(CASE WHEN CAST("Score" AS FLOAT) IN (3,4) THEN 1 ELSE 0 END) / COUNT(*) -
                      100.0 * SUM(CASE WHEN CAST("Score" AS FLOAT) = 1 THEN 1 ELSE 0 END) / COUNT(*), 1) AS NPS
            FROM DONNEES_LIMESURVEY_NETTOYEES
            WHERE {where} AND ({filtre_public})
            AND "Question_Formulation" NOT LIKE 'Durée%'
            AND "Valeur_Brute" NOT IN ('Oui', 'Non')
        """
        df = pd.read_sql_query(query, conn, params=params)
        if not df.empty and df.iloc[0]['total'] > 0:
            resultats.append(df.iloc[0])
    return resultats

def get_satisfaction_globale_par_public(id_structure, annee):
    conn = get_connexion()
    where, params = build_filtre(id_structure, annee)
    publics = {
        'Résidents': "LIKE '%résident%'",
        'Proches': "LIKE '%proche%'",
        'Équipe': "LIKE '%équipe%'",
    }
    resultats = []
    for public, filtre_public in publics.items():
        query = f"""
            SELECT '{public}' AS public,
                COUNT(*) AS total,
                ROUND(100.0 * SUM(CASE WHEN CAST("Score" AS FLOAT) IN (3,4) THEN 1 ELSE 0 END) / COUNT(*), 0) AS pct_accord,
                ROUND(100.0 * SUM(CASE WHEN CAST("Score" AS FLOAT) = 4 THEN 1 ELSE 0 END) / COUNT(*), 0) AS pct_tout_fait,
                ROUND(100.0 * SUM(CASE WHEN CAST("Score" AS FLOAT) = 3 THEN 1 ELSE 0 END) / COUNT(*), 0) AS pct_plutot,
                ROUND(100.0 * SUM(CASE WHEN CAST("Score" AS FLOAT) IN (1,2) THEN 1 ELSE 0 END) / COUNT(*), 0) AS pct_desaccord,
                COUNT(DISTINCT "ID de la réponse") AS nb_repondants
            FROM DONNEES_LIMESURVEY_NETTOYEES
            WHERE {where}
            AND "Question_Formulation" {filtre_public}
            AND "Question_Formulation" LIKE '%globalement satisfait%'
            AND CAST("Score" AS FLOAT) IN (1,2,3,4)
        """
        df = pd.read_sql_query(query, conn, params=params)
        if not df.empty and df.iloc[0]['total'] > 0:
            resultats.append(df.iloc[0])
    return resultats

def get_radar_thematique(id_structure, annee):
    conn = get_connexion()
    where, params = build_filtre(id_structure, annee)
    # SANS "Hygiène et soins"
    thematiques = {
        'Cadre de vie': ['cadre', 'hebergement', 'chambre', 'entretien', 'tenu'],
        'Alimentation': ['repas', 'alimentation', 'manger', 'faim'],
        'Activites': ['activite', 'animation', 'loisir'],
        'Relations sociales': ['relation', 'social', 'famille'],
        'Bientraitance': ['securite', 'vigilant', 'respecte', 'mauvais'],
        'Information': ['information', 'communication'],
        'Conditions travail': ['travail', 'condition'],
    }
    resultats = []
    for theme, mots_cles in thematiques.items():
        params_theme = list(params)
        parties = ['Question_Formulation LIKE ?' for _ in mots_cles]
        for m in mots_cles: params_theme.append('%' + m + '%')
        conditions = ' OR '.join(parties)
        query = f'SELECT ROUND(100.0 * SUM(CASE WHEN CAST("Score" AS FLOAT) IN (3,4) THEN 1 ELSE 0 END) / COUNT(*), 0) AS pct_accord, COUNT(*) AS total FROM DONNEES_LIMESURVEY_NETTOYEES WHERE {where} AND ({conditions}) AND CAST("Score" AS FLOAT) IN (1,2,3,4)'
        df = pd.read_sql_query(query, conn, params=params_theme)
        if not df.empty and df.iloc[0]['total'] > 0:
            resultats.append({'theme': theme, 'pct_accord': float(df.iloc[0]['pct_accord'])})
    return pd.DataFrame(resultats)

def get_methodologie(id_structure, annee):
    conn = get_connexion()
    where, params = build_filtre(id_structure, annee)
    query = f"""
        SELECT CASE 
            WHEN "Question_Formulation" LIKE '%résident%' OR "Question_Formulation" LIKE '%habitant%' THEN 'Résidents'
            WHEN "Question_Formulation" LIKE '%proche%' THEN 'Proches'
            WHEN "Question_Formulation" LIKE '%équipe%' OR "Question_Formulation" LIKE '%salarié%' THEN 'Équipe'
            ELSE 'Autre' END AS public, COUNT(DISTINCT "ID de la réponse") AS nb_repondants
        FROM DONNEES_LIMESURVEY_NETTOYEES WHERE {where} AND "Question_Formulation" NOT LIKE 'Durée%' GROUP BY public
    """
    df = pd.read_sql_query(query, conn, params=params)
    resultats = []
    for _, row in df[df['public'] != 'Autre'].iterrows():
        public = row['public']
        format_col = 'Présentiel' if public == 'Résidents' else 'Distanciel (Email)' if public == 'Proches' else 'Distanciel (En ligne)'
        couleur = '#E8706A' if public == 'Résidents' else '#6BBFB5' if public == 'Proches' else '#F5A623'
        resultats.append({'public': public, 'nb_repondants': row['nb_repondants'], 'format': format_col, 'couleur': couleur})
    ordre = {'Résidents': 1, 'Proches': 2, 'Équipe': 3}
    resultats.sort(key=lambda x: ordre.get(x['public'], 4))
    return resultats

# ALGORITHME LABEL VIVRE

QUESTIONS_ESSENTIELLES = [
    "Je me sens en sécurité", "Je me sens respecté(e) en tant que personne",
    "Mon intégrité corporelle est respectée", "Je me sens respecté(e) physiquement",
    "Je mange toujours à ma faim", "Je me sens propre au quotidien",
    "L'établissement me semble vigilant face aux risques de mauvais traitement",
    "Je me sens en sécurité dans la résidence", "Je me sens en sécurité dans l'habitat partagé",
    "Je me sens en sécurité dans mon logement",
    "L'habitat partagé me semble vigilant face aux risques de mauvais traitement",
]

def get_score_par_public(id_structure, annee):
    conn = get_connexion()
    where, params = build_filtre(id_structure, annee)
    query = f"""
        SELECT
            CASE
                WHEN "Question_Formulation" LIKE '%résident%' OR "Question_Formulation" LIKE '%habitant%' THEN 'Résidents'
                WHEN "Question_Formulation" LIKE '%proche%'   THEN 'Proches'
                WHEN "Question_Formulation" LIKE '%équipe%' OR "Question_Formulation" LIKE '%salarié%'  THEN 'Équipe'
                ELSE NULL
            END AS public,
            ROUND(AVG(CAST("Score" AS FLOAT)), 4) AS score_moyen_4,
            COUNT(DISTINCT "ID de la réponse") AS nb_repondants
        FROM DONNEES_LIMESURVEY_NETTOYEES
        WHERE {where} AND "Question_Formulation" NOT LIKE 'Durée%' AND "Question_Formulation" NOT LIKE 'Commentaire%' AND "Question_Formulation" NOT LIKE 'Temps%'
        GROUP BY public HAVING public IS NOT NULL ORDER BY public
    """
    df = pd.read_sql_query(query, conn, params=params)
    df['score_10'] = ((df['score_moyen_4'] - 1) / 3 * 10).round(2)
    df['valide'] = df['score_10'] >= 7.0
    return df

def get_criteres_essentiels(id_structure, annee):
    conn = get_connexion()
    where, params = build_filtre(id_structure, annee)
    resultats = []
    for question in QUESTIONS_ESSENTIELLES:
        query = f"""
            SELECT "{question}" AS question_label, COUNT(*) AS total,
                SUM(CASE WHEN CAST("Score" AS FLOAT) IN (1.0, 2.0) THEN 1 ELSE 0 END) AS nb_negatifs,
                ROUND(100.0 * SUM(CASE WHEN CAST("Score" AS FLOAT) IN (1.0, 2.0) THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_negatifs
            FROM DONNEES_LIMESURVEY_NETTOYEES
            WHERE {where} AND "Question_Formulation" LIKE ? AND CAST("Score" AS FLOAT) IN (1.0, 2.0, 3.0, 4.0)
        """
        p = params + [f"%{question}%"]
        df = pd.read_sql_query(query, conn, params=p)
        if not df.empty and df.iloc[0]['total'] > 0:
            row = df.iloc[0]
            resultats.append({
                'question': question, 'total': int(row['total']), 'nb_negatifs': int(row['nb_negatifs']),
                'pct_negatifs': float(row['pct_negatifs']),
                'statut': ' OK' if row['pct_negatifs'] <= 10 else ' Avertissement' if row['pct_negatifs'] <= 25 else ' Bloquant'
            })
    return pd.DataFrame(resultats)

def get_verdict_label(scores_public, criteres):
    critique_bloquant = criteres[criteres['pct_negatifs'] > 25] if not criteres.empty else pd.DataFrame()
    critique_avert = criteres[criteres['pct_negatifs'] > 10] if not criteres.empty else pd.DataFrame()
    c1_ok = len(critique_bloquant) == 0 and len(critique_avert) < 2
    c2_ok = all(scores_public['valide']) if not scores_public.empty else False
    return {'verdict': c1_ok and c2_ok, 'c1_ok': c1_ok, 'c2_ok': c2_ok, 'nb_bloquants': len(critique_bloquant), 'nb_avertissements': len(critique_avert)}



# NAVIGATION
# Le bouton "Importer" est visible uniquement pour l'admin 

if st.session_state.profil == "admin":
    # Admin : 7 colonnes avec bouton Import
    col_nav1, col_nav2, col_nav3, col_nav4, col_nav5, col_nav6, col_nav7, col_nav8 = st.columns([2, 2, 2, 2, 2, 2, 2, 1])
    with col_nav1:
        if st.button(" Tableau de bord", use_container_width=True):
            st.session_state.page = 'dashboard'
            st.rerun()
    with col_nav2:
        if st.button(" Label Vivre", use_container_width=True):
            st.session_state.page = 'label'
            st.rerun()
    with col_nav3:
        if st.button(" Données brutes", use_container_width=True):
            st.session_state.page = 'donnees'
            st.rerun()
    with col_nav4:
        if st.button(" Export", use_container_width=True):
            st.session_state.page = 'export'
            st.rerun()
    with col_nav5:
        if st.button(" Importer", use_container_width=True):
            st.session_state.page = 'import'
            st.rerun()
    with col_nav6:
        if st.button(" Comptes", use_container_width=True):
            st.session_state.page = 'gestion_comptes'
            st.rerun()
    with col_nav7:
        if st.button(" Déconnexion", use_container_width=True):
            logout()
    with col_nav8:
        st.markdown("<p style='text-align:right; padding-top:6px;'><span class='badge-admin'>Admin</span></p>", unsafe_allow_html=True)
else:
    # Établissement : 6 colonnes sans bouton Import
    col_nav1, col_nav2, col_nav3, col_nav4, col_nav5, col_nav6, col_nav7 = st.columns([2, 2, 2, 2, 2, 2, 1])
    with col_nav1:
        if st.button(" Tableau de bord", use_container_width=True):
            st.session_state.page = 'dashboard'
            st.rerun()
    with col_nav2:
        if st.button(" Label Vivre", use_container_width=True):
            st.session_state.page = 'label'
            st.rerun()
    with col_nav3:
        if st.button(" Données brutes", use_container_width=True):
            st.session_state.page = 'donnees'
            st.rerun()
    with col_nav4:
        if st.button(" Export", use_container_width=True):
            st.session_state.page = 'export'
            st.rerun()
    with col_nav5:
        if st.button(" Mon compte", use_container_width=True):
            st.session_state.page = 'mon_compte'
            st.rerun()
    with col_nav6:
        if st.button(" Déconnexion", use_container_width=True):
            logout()
    with col_nav7:
        st.markdown("<p style='text-align:center; padding-top:6px;'><span class='badge-etab' style='font-size:0.55rem; padding:2px 4px; white-space:nowrap; display:block;'>Établissement</span></p>", unsafe_allow_html=True)
st.markdown("---")


# BARRE DE FILTRES 

df_structures = get_structures()
annees_dispo = get_annees()

pages_sans_filtre = ['import', 'gestion_comptes', 'mon_compte']

if st.session_state.page not in pages_sans_filtre:
    with st.container():
        st.markdown("<div class='filtre-bar'>", unsafe_allow_html=True)
        if st.session_state.profil == "admin":
            col_f1, col_f2, col_f3 = st.columns([3, 2, 1])
            with col_f1:
                options_etab = [" Tous les établissements"] + [f"{row['Structure']} ({row['Type']})" for _, row in df_structures.iterrows()]
                # Calculer l'index actuel selon filtre_structure en session
                if st.session_state.filtre_structure is None:
                    index_etab = 0
                else:
                    row_actuelle = df_structures[df_structures['Id_structure'] == st.session_state.filtre_structure]
                    if not row_actuelle.empty:
                        nom_actuel = f"{row_actuelle.iloc[0]['Structure']} ({row_actuelle.iloc[0]['Type']})"
                        index_etab = options_etab.index(nom_actuel) if nom_actuel in options_etab else 0
                    else:
                        index_etab = 0
                choix_etab = st.selectbox(" Établissement", options=options_etab, index=index_etab, key="select_etab")
                if choix_etab == " Tous les établissements":
                    st.session_state.filtre_structure = None
                else:
                    nom_choisi = choix_etab.split(" (")[0]
                    row_choisi = df_structures[df_structures['Structure'] == nom_choisi]
                    if not row_choisi.empty: st.session_state.filtre_structure = int(row_choisi.iloc[0]['Id_structure'])
            with col_f2:
                options_annee = ["Toutes les années"] + [str(a) for a in annees_dispo]
                choix_annee = st.selectbox(" Année", options=options_annee, index=0, key="select_annee")
                st.session_state.filtre_annee = None if choix_annee == "Toutes les années" else int(choix_annee)
            with col_f3:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.session_state.filtre_structure:
                    row_info = df_structures[df_structures['Id_structure'] == st.session_state.filtre_structure]
                    if not row_info.empty: st.caption(f" {row_info.iloc[0]['Département']} · {row_info.iloc[0]['Région']}")
        else:
            id_s = st.session_state.filtre_structure
            if id_s:
                row_etab = df_structures[df_structures['Id_structure'] == id_s]
                if not row_etab.empty:
                    col_e1, col_e2 = st.columns([3, 2])
                    with col_e1: st.markdown(f"** {row_etab.iloc[0]['Structure']}** &nbsp;|&nbsp; {row_etab.iloc[0]['Type']} &nbsp;|&nbsp;  {row_etab.iloc[0]['Département']}, {row_etab.iloc[0]['Région']}")
                    with col_e2:
                        options_annee = ["Toutes les années"] + [str(a) for a in annees_dispo]
                        choix_annee = st.selectbox(" Année", options=options_annee, index=0, key="select_annee_etab")
                        st.session_state.filtre_annee = None if choix_annee == "Toutes les années" else int(choix_annee)
        st.markdown("</div>", unsafe_allow_html=True)



id_structure_actif = st.session_state.filtre_structure
annee_active = st.session_state.filtre_annee



# PAGE DASHBOARD (DESIGN PDF VIA ONGLETS)

if st.session_state.page == 'dashboard':

    nps = get_nps(id_structure_actif, annee_active)
    scores_public = get_scores_public(id_structure_actif, annee_active)

    if id_structure_actif:
        row_actif = df_structures[df_structures['Id_structure'] == id_structure_actif]
        nom_actif = row_actif.iloc[0]['Structure'] if not row_actif.empty else "Établissement"
        annee_label = str(annee_active) if annee_active else "toutes années"
        st.markdown(f"<div class='section-title'> Rapport — {nom_actif} · {annee_label}</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div class='section-title'> Rapport — Tous les établissements</div>", unsafe_allow_html=True)

    # VÉRIFICATION données disponibles
    if pd.isna(nps['NPS']) or int(nps['total']) == 0:
        nom_etab = nom_actif if id_structure_actif else "cet établissement"
        annee_msg = f"en {annee_active}" if annee_active else ""
        st.warning(f" Aucune donnée disponible pour **{nom_etab}** {annee_msg}.")
        st.stop()

    # CRÉATION DES ONGLETS
    tab_synthese, tab_thematique, tab_verbatim, tab_methodo, tab_ia = st.tabs([
        " Résultats synthétiques", 
        " Résultats thématiques", 
        " Verbatim", 
        " Méthodologie",
        " Assistant IA"
    ])

# ONGLET 1 : SYNTHÈSE
    with tab_synthese:
        # Filtre par public
        choix_public = st.radio(
            " Filtrer par public :",
            options=["Tous les publics", "Résidents", "Proches", "Équipe"],
            horizontal=True
        )
        conn_dash = get_connexion()
        where_dash, params_dash = build_filtre(id_structure_actif, annee_active)
        df_donnees = pd.read_sql_query(f"""
            SELECT "Question_Formulation", CAST("Score" AS FLOAT) as Score
            FROM DONNEES_LIMESURVEY_NETTOYEES
            WHERE {where_dash}
            AND "Question_Formulation" NOT LIKE 'Durée%'
            AND "Question_Formulation" NOT LIKE 'Commentaire%'
        """, conn_dash, params=params_dash)

        if choix_public == "Résidents":
            df_filtre = df_donnees[df_donnees['Question_Formulation'].str.contains('résident|habitant', case=False, na=False)]
        elif choix_public == "Proches":
            df_filtre = df_donnees[df_donnees['Question_Formulation'].str.contains('proche', case=False, na=False)]
        elif choix_public == "Équipe":
            df_filtre = df_donnees[df_donnees['Question_Formulation'].str.contains('équipe|salarié', case=False, na=False)]
        else:
            df_filtre = df_donnees.copy()

        df_valide = df_filtre[df_filtre['Score'].isin([1.0, 2.0, 3.0, 4.0])].copy()
        total_rep = len(df_valide)
        
        # --- CALCUL NPS (Optimisé) ---
        if total_rep > 0:
            nb_prom = len(df_valide[df_valide['Score'].isin([3.0, 4.0])])
            nb_detr = len(df_valide[df_valide['Score'] == 1.0])
            nps_val = round(((nb_prom/total_rep)*100)-((nb_detr/total_rep)*100), 1)
        else:
            nps_val = 0

        # --- NOUVEAUX CALCULS (Satisfaction & Maltraitance) ---
        satisfaction_globale = round(df_valide['Score'].mean(), 1) if total_rep > 0 else "N/A"
        df_maltraitance = df_valide[df_valide['Question_Formulation'].str.contains('maltraitance|sécurité|respect|violence|abus', case=False, na=False)]
        score_maltraitance = f"{round(df_maltraitance['Score'].mean(), 1)}" if not df_maltraitance.empty else "N/A"

        st.markdown("<hr>", unsafe_allow_html=True)
        
        # --- NOUVEL AFFICHAGE À 4 COLONNES (Plus clair, sans camembert) ---
        col1, col2, col3, col4 = st.columns(4)
        couleur_nps = "#6BBFB5" if nps_val >= 30 else "#E8706A"
        
        with col1:
            st.markdown(f"<div class='kpi-card'><div class='kpi-label'>NPS Global</div><div class='kpi-value' style='color:{couleur_nps};'>{nps_val}</div></div>", unsafe_allow_html=True)
        with col2:
            st.markdown(f"<div class='kpi-card'><div class='kpi-label'>Satisfaction Moyenne</div><div class='kpi-value' style='color:#6BBFB5;'>{satisfaction_globale} / 4</div></div>", unsafe_allow_html=True)
        with col3:
            st.markdown(f"<div class='kpi-card'><div class='kpi-label'>Vigilance Bientraitance</div><div class='kpi-value' style='color:#F5A623;'>{score_maltraitance} / 4</div></div>", unsafe_allow_html=True)
        with col4:
            st.markdown(f"<div class='kpi-card'><div class='kpi-label'>Réponses Analysées</div><div class='kpi-value' style='color:#5C5C5C;'>{int(total_rep):,}</div></div>", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        
        # --- GRAPHIQUE EN BARRES SEUL (Prend toute la largeur) ---
        couleurs = {'Proches': '#6BBFB5', 'Équipe': '#F5A623', 'Résidents': '#E8706A'}
        
        if choix_public == "Tous les publics":
            st.markdown("<div class='section-title'> Score moyen par public</div>", unsafe_allow_html=True)
            def attribuer_public(q):
                q = str(q).lower()
                if 'résident' in q or 'habitant' in q: return 'Résidents'
                if 'proche' in q: return 'Proches'
                if 'équipe' in q or 'salarié' in q: return 'Équipe'
                return 'Autre'
            
            df_tous = df_donnees[df_donnees['Score'].isin([1.0, 2.0, 3.0, 4.0])].copy()
            df_tous['public'] = df_tous['Question_Formulation'].apply(attribuer_public)
            scores_pub_calc = df_tous.groupby('public')['Score'].mean().reset_index()
            scores_pub_calc.rename(columns={'Score': 'score_moyen'}, inplace=True)
            scores_pub_calc['score_moyen'] = scores_pub_calc['score_moyen'].round(2)
            df_pub = scores_pub_calc[scores_pub_calc['public'] != 'Autre'].copy()
            
            if not df_pub.empty:
                fig_bar = px.bar(df_pub, x='public', y='score_moyen', color='public', color_discrete_map=couleurs, text='score_moyen', title='Score moyen / 4')
                fig_bar.update_traces(texttemplate='%{text}', textposition='outside')
                fig_bar.update_layout(showlegend=False, plot_bgcolor='white', paper_bgcolor='white', yaxis=dict(range=[0, 4.5], title='Score /4'), xaxis_title='', title_font_family='Georgia', height=350)
                st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.markdown(f"<div class='section-title'> Score moyen — {choix_public}</div>", unsafe_allow_html=True)
            score_public_unique = round(df_valide['Score'].mean(), 2) if total_rep > 0 else 0
            df_pub_unique = pd.DataFrame([{'public': choix_public, 'score_moyen': score_public_unique}])
            fig_bar = px.bar(df_pub_unique, x='public', y='score_moyen', color='public', color_discrete_map=couleurs, text='score_moyen', title='Score moyen / 4')
            fig_bar.update_traces(texttemplate='%{text}', textposition='outside')
            fig_bar.update_layout(showlegend=False, plot_bgcolor='white', paper_bgcolor='white', yaxis=dict(range=[0, 4.5], title='Score /4'), xaxis_title='', title_font_family='Georgia', height=350)
            st.plotly_chart(fig_bar, use_container_width=True)

    # ONGLET 2 : THÉMATIQUES
    with tab_thematique:
        couleurs_pub = {'Résidents': '#E8706A', 'Proches': '#6BBFB5', 'Équipe': '#F5A623'}

        # Satisfaction globale
        st.markdown("<div class='section-title'> Satisfaction globale par public</div>", unsafe_allow_html=True)
        st.caption("Question : 'Je suis globalement satisfait(e) de cet établissement' — % Total d'accord (Tout à fait + Plutôt d'accord)")
        sat_globale = get_satisfaction_globale_par_public(id_structure_actif, annee_active)
        if sat_globale:
            cols_sat = st.columns(len(sat_globale))
            for i, row in enumerate(sat_globale):
                with cols_sat[i]:
                    couleur = couleurs_pub.get(row['public'], '#5C5C5C')
                    st.markdown(f"""<div class='kpi-card' style='border-top:5px solid {couleur};'>
                        <div class='kpi-label' style='color:{couleur};font-weight:bold;font-size:1rem;'>{row['public']}</div>
                        <div class='kpi-value' style='color:{couleur};'>{int(row['pct_accord'])}%</div>
                        <div class='kpi-label'>Total d'accord</div>
                        <div style='font-size:0.8rem;color:#888;margin-top:6px;'> {int(row['pct_tout_fait'])}% tout à fait ·  {int(row['pct_plutot'])}% plutôt</div>
                        <div style='font-size:0.8rem;color:#E8706A;'> {int(row['pct_desaccord'])}% pas d'accord</div>
                        <div style='font-size:0.75rem;color:#aaa;margin-top:4px;'>{int(row['nb_repondants'])} répondants</div>
                    </div>""", unsafe_allow_html=True)
        else:
            st.info("Aucune question de satisfaction globale trouvée dans les données.")

        st.markdown("<br>", unsafe_allow_html=True)

        # NPS par public
        st.markdown("<div class='section-title'> NPS (Indice de recommandation) par public</div>", unsafe_allow_html=True)
        st.caption("Calculé à partir de la question 'Je recommande cet établissement' — Score 3-4 = Promoteur, Score 2 = Passif, Score 1 = Détracteur")
        nps_par_public = get_nps_par_public(id_structure_actif, annee_active)
        if nps_par_public:
            cols_nps = st.columns(len(nps_par_public))
            for i, row in enumerate(nps_par_public):
                with cols_nps[i]:
                    couleur = couleurs_pub.get(row['public'], '#5C5C5C')
                    nps_val = int(row['NPS']) if pd.notna(row['NPS']) else 'N/A'
                    couleur_nps_pub = couleur if pd.notna(row['NPS']) and row['NPS'] >= 30 else "#E8706A"
                    st.markdown(f"""<div class='kpi-card' style='border-top:5px solid {couleur};'>
                        <div class='kpi-label' style='color:{couleur};font-weight:bold;font-size:1rem;'>{row['public']}</div>
                        <div class='kpi-value' style='color:{couleur_nps_pub};'>{nps_val}</div>
                        <div class='kpi-label'>Net Promoter Score</div>
                        <div style='font-size:0.8rem;color:#888;margin-top:6px;'>Promoteurs: {row['pct_promoteurs']}% · Détracteurs: {row['pct_detracteurs']}%</div>
                        <div style='font-size:0.75rem;color:#aaa;'>{int(row['total'])} réponses analysées</div>
                    </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Radar chart
        st.markdown("<div class='section-title'> Synthèse thématique — % Total d'accord par domaine</div>", unsafe_allow_html=True)
        st.caption("Comparaison de l'établissement avec la moyenne globale")
        
        df_radar_etab = get_radar_thematique(id_structure_actif, annee_active)
        df_radar_global = get_radar_thematique(None, annee_active) # None = Tous les établissements

        if not df_radar_etab.empty and not df_radar_global.empty:
            df_radar_global.rename(columns={'pct_accord': 'moyenne_globale'}, inplace=True)
            df_radar = pd.merge(df_radar_etab, df_radar_global, on='theme', how='left')

            categories = df_radar['theme'].tolist()
            val_etab = df_radar['pct_accord'].tolist()
            val_glob = df_radar['moyenne_globale'].tolist()

            # Fermer le polygone
            val_etab += [val_etab[0]]; val_glob += [val_glob[0]]; categories += [categories[0]]

            fig_radar = go.Figure()
            fig_radar.add_trace(go.Scatterpolar(r=val_glob, theta=categories, fill='none', line=dict(color='#F5A623', width=2, dash='dash'), name='Moyenne Globale'))
            fig_radar.add_trace(go.Scatterpolar(r=val_etab, theta=categories, fill='toself', fillcolor='rgba(107,191,181,0.3)', line=dict(color='#6BBFB5', width=2), name='Cet Établissement'))

            fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0,100], ticksuffix='%')), showlegend=True, paper_bgcolor='white', height=500, font_family='Georgia')
            st.plotly_chart(fig_radar, use_container_width=True)
        else:
            st.info("Pas assez de données pour le radar chart.")

        st.markdown("<br>", unsafe_allow_html=True)
        col_top, col_flop = st.columns(2)
        with col_top:
            st.markdown("<div class='section-title'> Top 10 meilleures questions</div>", unsafe_allow_html=True)
            top_q = get_top_questions(id_structure_actif, annee_active)
            top_q['question_courte'] = top_q['question'].str[:55] + '...'
            fig_top = px.bar(top_q, x='score_moyen', y='question_courte', orientation='h', color='score_moyen', color_continuous_scale=['#F5A623', '#6BBFB5'])
            fig_top.update_layout(plot_bgcolor='white', paper_bgcolor='white', height=400, showlegend=False, coloraxis_showscale=False, yaxis_title='', xaxis=dict(range=[0, 4]), margin=dict(l=10))
            st.plotly_chart(fig_top, use_container_width=True)

        with col_flop:
            st.markdown("<div class='section-title'> Top 10 points d'amélioration</div>", unsafe_allow_html=True)
            flop_q = get_flop_questions(id_structure_actif, annee_active)
            flop_q['question_courte'] = flop_q['question'].str[:55] + '...'
            fig_flop = px.bar(flop_q, x='score_moyen', y='question_courte', orientation='h', color='score_moyen', color_continuous_scale=['#E8706A', '#F5A623'])
            fig_flop.update_layout(plot_bgcolor='white', paper_bgcolor='white', height=400, showlegend=False, coloraxis_showscale=False, yaxis_title='', xaxis=dict(range=[0, 4]), margin=dict(l=10))
            st.plotly_chart(fig_flop, use_container_width=True)

    # ONGLET 3 : VERBATIM (TÂCHE 16 : ANALYSE IA)
    with tab_verbatim:
        st.markdown("<div class='section-title'> Ce qu'ils nous ont dit (Analyse IA)</div>", unsafe_allow_html=True)
        
        top_positifs, top_suggestions = get_analyse_verbatims(id_structure_actif, annee_active)
        
        if not top_positifs.empty:
            col_pos, col_neg = st.columns(2)
            
            with col_pos:
                st.markdown("### 💚 Ce qu'ils apprécient")
                for _, row in top_positifs.iterrows():
                    st.success(f"**{row['public']} :** « {row['commentaire']} »")
                    
            with col_neg:
                st.markdown("###  Pistes d'amélioration")
                for _, row in top_suggestions.iterrows():
                    st.warning(f"**{row['public']} :** « {row['commentaire']} »")
        else:
            st.info("Aucun commentaire libre n'a été laissé pour cette sélection.")

    # ONGLET 4 : MÉTHODOLOGIE
    with tab_methodo:
        st.markdown("<div class='section-title'> Méthodologie — Échantillons</div>", unsafe_allow_html=True)
        
        methodo = get_methodologie(id_structure_actif, annee_active)
        
        if methodo:
            cols_m = st.columns(len(methodo))
            for i, item in enumerate(methodo):
                with cols_m[i]:
                    st.markdown(f"""<div class='kpi-card' style='border-top: 5px solid {item['couleur']};'>
                        <h3 style='color:{item['couleur']};'>{item['public']}</h3>
                        <p style='color:#888;'>{item['format']}</p>
                        <h2 style='color:#5C5C5C;'>{item['nb_repondants']}</h2>
                        <p style='color:#888;'>répondants</p>
                    </div>""", unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            st.info(" **Source des données :** Les informations ci-dessus proviennent directement des exports LimeSurvey importés dans la plateforme.")
        else:
            # Affichage générique si pas de données dans le mapping
            st.markdown("<div class='section-title'>Méthodologie — Données générales</div>", unsafe_allow_html=True)
            col_m1, col_m2, col_m3 = st.columns(3)
            with col_m1:
                st.markdown("<div class='kpi-card' style='border-top: 5px solid #E8706A;'><h3 style='color:#E8706A;'>Résidents</h3><p>Présentiel (Entretiens)</p></div>", unsafe_allow_html=True)
            with col_m2:
                st.markdown("<div class='kpi-card' style='border-top: 5px solid #6BBFB5;'><h3 style='color:#6BBFB5;'>Proches</h3><p>Distanciel (Email)</p></div>", unsafe_allow_html=True)
            with col_m3:
                st.markdown("<div class='kpi-card' style='border-top: 5px solid #F5A623;'><h3 style='color:#F5A623;'>Équipe</h3><p>Distanciel (En ligne)</p></div>", unsafe_allow_html=True)
    
    # ONGLET 5 : ASSISTANT IA 
    with tab_ia:
        st.markdown("<div class='section-title'> Assistant Conversationnel (Chat with Data)</div>", unsafe_allow_html=True)
        st.info(" **Mode Démonstration SaaS :** Cet assistant illustre la future fonctionnalité 'Text-to-SQL' et 'Analyse Sémantique' (NLP) de la plateforme.")

        # 1. On propose des questions cliquables
        st.markdown("**Testez l'assistant en un clic :**")
        col_q1, col_q2 = st.columns(2)
        
        # Variable de session pour stocker le clic sur un bouton
        if 'demo_prompt' not in st.session_state:
            st.session_state.demo_prompt = None

        if col_q1.button(" Quel % des résidents > 75 ans en EHPAD ?"):
            st.session_state.demo_prompt = "Quel pourcentage des personnes de plus de 75 ans en EHPAD ?"
        if col_q2.button(" Quelles évolutions dans les verbatims salariés ?"):
            st.session_state.demo_prompt = "Quelles sont les principales évolutions observées dans les verbatims partagés par les salariés sur leurs conditions de travail ?"

        # 2. La barre de chat 
        prompt = st.chat_input("Posez votre question à la base de données...")

        # Si l'utilisateur a cliqué sur un bouton, on remplit le prompt avec la question du bouton
        if st.session_state.demo_prompt:
            prompt = st.session_state.demo_prompt
            st.session_state.demo_prompt = None

        # 3. Affichage de la conversation
        if prompt:
            # Bulle de l'utilisateur
            with st.chat_message("user"):
                st.write(prompt)

            
            with st.chat_message("assistant"):
                import time
                
                # Détection des mots-clés pour lancer la bonne fausse réponse
                if "75 ans" in prompt.lower() or "ehpad" in prompt.lower():
                    with st.spinner("Traduction en SQL et interrogation de la base..."):
                        time.sleep(1.5) # Faux temps de réflexion
                    st.success("D'après l'analyse de la base de données, **42% des résidents** interrogés en EHPAD ont plus de 75 ans. La note moyenne de satisfaction globale pour cette tranche d'âge est de **3.4/4**.")
                    st.caption("Requête générée par l'IA : `SELECT COUNT(*) FROM DONNEES_LIMESURVEY_NETTOYEES WHERE Type_structure = 'EHPAD' AND Age > 75...`")
                
                elif "évolution" in prompt.lower() or "salariés" in prompt.lower():
                    with st.spinner("Analyse sémantique (NLP) des verbatims Équipe en cours..."):
                        time.sleep(2.0)
                    st.warning("J'ai synthétisé les retours de l'équipe. L'évolution principale porte sur le **manque de nuance entre les services**. \n\nLes mots-clés **'inclusion'** et **'management de proximité'** ressortent très souvent. Plusieurs salariés ont d'ailleurs souligné que le créneau de 30 minutes était insuffisant pour creuser véritablement ces sujets de fond.")
                
                else:
                    st.write("Je suis un démonstrateur . Pour cette présentation, demandez-moi plutôt les statistiques socio-démographiques ou l'analyse des commentaires salariés !")


# PAGE DONNÉES BRUTES

elif st.session_state.page == 'donnees':
    st.markdown("<div class='section-title'> Données brutes LimeSurvey</div>", unsafe_allow_html=True)
    limite = st.slider("Nombre de lignes à afficher", 10, 500, 100)
    df_brut = get_donnees_brutes(id_structure_actif, annee_active, limite)
    score_filtre = st.multiselect("Filtrer par score", [1.0, 2.0, 3.0, 4.0], default=[1.0, 2.0, 3.0, 4.0])
    if score_filtre:
        df_brut['Score'] = pd.to_numeric(df_brut['Score'], errors='coerce')
        df_brut = df_brut.dropna(subset=['Score'])
        df_brut = df_brut[df_brut['Score'].isin(score_filtre)]
    st.dataframe(df_brut, use_container_width=True, height=400)
    st.info(f" {len(df_brut)} lignes affichées")


# PAGE EXPORT

elif st.session_state.page == 'export':
    st.markdown("<div class='section-title'> Export des données</div>", unsafe_allow_html=True)

    # --- L'astuce pour le PDF ---
    #st.info(" **Astuce PDF (Rapport) :** Pour générer un rapport PDF parfait, allez dans l'onglet **'Tableau de bord'** et appuyez sur **`Ctrl + P`** (ou `Cmd + P` sur Mac), puis choisissez la destination **'Enregistrer au format PDF'**. Le design a été spécialement codé pour ça !")
   # st.markdown("---")

    if id_structure_actif:
        row_actif = df_structures[df_structures['Id_structure'] == id_structure_actif]
        nom_export = row_actif.iloc[0]['Structure'].replace(' ', '_') if not row_actif.empty else "etablissement"
    else:
        nom_export = "tous_etablissements"

    annee_export = str(annee_active) if annee_active else "toutes_annees"

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("###  Exporter les résultats NPS")
        nps = get_nps(id_structure_actif, annee_active)
        df_nps = pd.DataFrame([{'Indicateur': 'NPS Global', 'Valeur': nps['NPS']}, {'Indicateur': '% Promoteurs', 'Valeur': nps['pct_promoteurs']}, {'Indicateur': '% Passifs', 'Valeur': nps['pct_passifs']}, {'Indicateur': '% Détracteurs', 'Valeur': nps['pct_detracteurs']}])
        csv_nps = df_nps.to_csv(index=False, encoding='utf-8')
        st.download_button(label="Télécharger NPS (CSV)", data=csv_nps, file_name=f"nps_{nom_export}_{annee_export}.csv", mime="text/csv", use_container_width=True)

    with col2:
        st.markdown("###  Exporter les scores par public")
        scores_public = get_scores_public(id_structure_actif, annee_active)
        csv_public = scores_public.to_csv(index=False, encoding='utf-8')
        st.download_button(label="Télécharger scores par public (CSV)", data=csv_public, file_name=f"scores_public_{nom_export}_{annee_export}.csv", mime="text/csv", use_container_width=True)

    st.markdown("###  Exporter les données brutes")
    df_brut = get_donnees_brutes(id_structure_actif, annee_active, 500)
    csv_brut = df_brut.to_csv(index=False, encoding='utf-8')
    st.download_button(label="Télécharger données brutes (CSV)", data=csv_brut, file_name=f"donnees_brutes_{nom_export}_{annee_export}.csv", mime="text/csv", use_container_width=True)


# PAGE LABEL VIVRE 

elif st.session_state.page == 'label':
    st.markdown("<div class='section-title'> Algorithme Label Vivre</div>", unsafe_allow_html=True)
    if id_structure_actif:
        row_actif = df_structures[df_structures['Id_structure'] == id_structure_actif]
        nom_actif = row_actif.iloc[0]['Structure'] if not row_actif.empty else "Établissement"
        annee_label = str(annee_active) if annee_active else "toutes années"
        st.markdown(f"**Analyse pour : {nom_actif} · {annee_label}**")

        
    else:
        st.markdown("**Analyse globale — tous les établissements**")

    scores_public = get_score_par_public(id_structure_actif, annee_active)
    criteres = get_criteres_essentiels(id_structure_actif, annee_active)
    verdict = get_verdict_label(scores_public, criteres)

    st.markdown("<br>", unsafe_allow_html=True)
    if verdict['verdict']:
        st.markdown("""<div style='background:#E8F8F0; border:2px solid #6BBFB5; border-radius:15px; padding:30px; text-align:center; margin-bottom:20px;'><div style='font-size:2rem; font-weight:bold; color:#0F6E56; font-family:Georgia;'>Label Vivre obtenu!</div><div style='color:#0F6E56; margin-top:8px;'>Les deux critères sont validés — l'établissement est éligible au label</div></div>""", unsafe_allow_html=True)
    else:
        st.markdown("""<div style='background:#FEF0F0; border:2px solid #E8706A; border-radius:15px; padding:30px; text-align:center; margin-bottom:20px;'><div style='font-size:2rem; font-weight:bold; color:#A32D2D; font-family:Georgia;'>Label Vivre non obtenu.</div><div style='color:#A32D2D; margin-top:8px;'>Un ou plusieurs critères ne sont pas atteints</div></div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'> Critère 1 — Critères essentiels (% réponses négatives)</div>", unsafe_allow_html=True)
    st.caption("Règle : aucun critère ne doit dépasser 10% de réponses négatives · aucun ne doit dépasser 25%")

    if not criteres.empty:
        for _, row in criteres.iterrows():
            couleur = "#6BBFB5" if row['pct_negatifs'] <= 10 else "#F5A623" if row['pct_negatifs'] <= 25 else "#E8706A"
            pct_affiche = min(row['pct_negatifs'], 100)
            st.markdown(f"""<div style='margin:10px 0; padding:12px; background:white; border-radius:10px; box-shadow:0 1px 4px rgba(0,0,0,0.06);'><div style='display:flex; justify-content:space-between; margin-bottom:6px;'><span style='font-size:0.85rem; color:#5C5C5C;'>{row['statut']} &nbsp; {row['question']}</span><span style='font-size:0.85rem; font-weight:bold; color:{couleur};'>{row['pct_negatifs']}% négatifs ({row['nb_negatifs']}/{row['total']})</span></div><div style='background:#eee; border-radius:6px; height:8px; position:relative;'><div style='background:{couleur}; width:{pct_affiche}%; height:8px; border-radius:6px;'></div><div style='position:absolute; left:10%; top:-2px; height:12px; width:2px; background:#888; border-radius:2px;' title='Seuil 10%'></div><div style='position:absolute; left:25%; top:-2px; height:12px; width:2px; background:#E8706A; border-radius:2px;' title='Seuil 25%'></div></div><div style='display:flex; justify-content:space-between; margin-top:2px;'><span style='font-size:0.7rem; color:#aaa;'>0%</span><span style='font-size:0.7rem; color:#888;'>│10%</span><span style='font-size:0.7rem; color:#E8706A;'>│25%</span><span style='font-size:0.7rem; color:#aaa;'>100%</span></div></div>""", unsafe_allow_html=True)
    else:
        st.warning("Aucun critère essentiel trouvé pour cet établissement.")


    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'> Critère 2 — Expérience positive (score ≥ 7/10)</div>", unsafe_allow_html=True)

    if not scores_public.empty:
        cols = st.columns(len(scores_public))
        for i, (_, row) in enumerate(scores_public.iterrows()):
            with cols[i]:
                couleur = "#6BBFB5" if row['valide'] else "#E8706A"
                icone = "" if row['valide'] else ""
                st.markdown(f"""<div class='kpi-card'><div class='kpi-label'>{icone} {row['public']}</div><div class='kpi-value' style='color:{couleur};'>{row['score_10']}</div><div class='kpi-label'>/ 10 &nbsp;·&nbsp; {row['nb_repondants']} répondants</div><div style='margin-top:8px; font-size:0.8rem; color:#888;'>(score brut : {row['score_moyen_4']}/4)</div></div>""", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        for _, row in scores_public.iterrows():
            couleur = "#6BBFB5" if row['valide'] else "#E8706A"
            pct = min(row['score_10'] / 10 * 100, 100)
            st.markdown(f"""<div style='margin:8px 0;'><div style='display:flex; justify-content:space-between; margin-bottom:4px;'><span style='font-size:0.9rem; color:#5C5C5C;'>{row['public']}</span><span style='font-size:0.9rem; font-weight:bold; color:{couleur};'>{row['score_10']}/10</span></div><div style='background:#eee; border-radius:10px; height:12px; position:relative;'><div style='background:{couleur}; width:{pct}%; height:12px; border-radius:10px;'></div><div style='position:absolute; left:70%; top:-2px; height:16px; width:2px; background:#F5A623; border-radius:2px;' title='Seuil 7/10'></div></div></div>""", unsafe_allow_html=True)
        st.caption("🟡 La barre orange indique le seuil minimum de 7/10")
    else:
        st.warning("Aucune donnée disponible pour cet établissement.")


    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'> Récapitulatif</div>", unsafe_allow_html=True)
    col_r1, col_r2 = st.columns(2)
    with col_r1:
        icone_c1 = "" if verdict['c1_ok'] else ""
        st.markdown(f"""<div class='kpi-card'><div class='kpi-label'>Critère 1 — Critères essentiels</div><div class='kpi-value'>{icone_c1}</div><div class='kpi-label'>{verdict['nb_bloquants']} bloquant(s) · {verdict['nb_avertissements']} avertissement(s)</div></div>""", unsafe_allow_html=True)
    with col_r2:
        icone_c2 = "" if verdict['c2_ok'] else ""
        publics_ok = scores_public[scores_public['valide']]['public'].tolist() if not scores_public.empty else []
        st.markdown(f"""<div class='kpi-card'><div class='kpi-label'>Critère 2 — Expérience positive</div><div class='kpi-value'>{icone_c2}</div><div class='kpi-label'>{len(publics_ok)}/3 publics ≥ 7/10</div></div>""", unsafe_allow_html=True)
# ============================================================
# =====  PAGE IMPORT DES DONNÉES =========
# ============================================================
# Visible uniquement pour l'admin 
# Permet d'uploader les 9 fichiers xlsx LimeSurvey directement
# depuis l'interface sans passer par le terminal
# ============================================================
elif st.session_state.page == 'import' and st.session_state.profil == "admin":

    st.markdown("<div class='section-title'> Importer de nouvelles données</div>", unsafe_allow_html=True)

    st.markdown("""
    <div style='background:#E8F8F0; border:1px solid #6BBFB5; border-radius:10px;
                padding:16px; margin-bottom:20px; font-size:0.9rem; color:#0F6E56;'>
        <strong> Instructions :</strong><br>
        1. Sélectionnez l'établissement concerné par les fichiers.<br>
        2. Uploadez les fichiers xlsx exportés depuis LimeSurvey.<br>
        3. Lancez l'import — les données seront automatiquement rattachées à cet établissement.
    </div>
    """, unsafe_allow_html=True)

    # ÉTAPE 1 : Choix de l'établissement
    st.markdown("#### Étape 1 — Choisir l'établissement")
    chemin_bdd_imp = os.path.join(os.path.dirname(os.path.abspath(__file__)), "label_vivre.sqlite")
    conn_imp = sqlite3.connect(chemin_bdd_imp)
    df_struct_imp = pd.read_sql_query("SELECT Id_structure, Structure, Type FROM STRUCTURE ORDER BY Structure", conn_imp)
    conn_imp.close()

    options_struct = [f"{row['Structure']} ({row['Type']})" for _, row in df_struct_imp.iterrows()]
    choix_struct_imp = st.selectbox("Établissement concerné par cet import :", options=options_struct, index=0)
    nom_struct_choisi = choix_struct_imp.split(" (")[0]
    row_struct_choisi = df_struct_imp[df_struct_imp['Structure'] == nom_struct_choisi]
    id_structure_import = int(row_struct_choisi.iloc[0]['Id_structure']) if not row_struct_choisi.empty else None

    st.markdown("<br>", unsafe_allow_html=True)

    # ÉTAPE 2 : Upload des fichiers
    st.markdown("#### Étape 2 — Sélectionner les fichiers LimeSurvey")
    fichiers_uploades = st.file_uploader(
        "Fichiers LimeSurvey (.xlsx)",
        type=["xlsx"],
        accept_multiple_files=True,
        help="Vous pouvez sélectionner plusieurs fichiers en même temps (Ctrl+clic)"
    )

    # Afficher les fichiers uploadés
    if fichiers_uploades:
        st.markdown(f"**{len(fichiers_uploades)} fichier(s) sélectionné(s) pour {nom_struct_choisi} :**")
        for f in fichiers_uploades:
            st.markdown(f"-  `{f.name}`")

        st.markdown("<br>", unsafe_allow_html=True)

        # Bouton de lancement
        if st.button(" Lancer l'import", use_container_width=True):

            if id_structure_import is None:
                st.error("Veuillez sélectionner un établissement valide.")
                st.stop()

            colonnes_fixes = [
                'ID de la réponse', 'Date de soumission', 'Dernière page',
                'Langue de départ', 'Tête de série', 'Date de lancement',
                'Date de la dernière action'
            ]
            dictionnaire_scores = {
                "Tout à fait d'accord": 4,
                "Plutôt d'accord": 3,
                "Plutôt pas d'accord": 2,
                "Pas du tout d'accord": 1,
            }

            tous_les_tableaux = []
            erreurs = []

            # Barre de progression
            progress = st.progress(0)
            status = st.empty()

            for i, fichier in enumerate(fichiers_uploades):
                status.text(f" Traitement de {fichier.name}...")
                try:
                    # Lecture du fichier xlsx uploadé
                    df = pd.read_excel(fichier, engine='openpyxl')

                    # Vérifier que les colonnes fixes sont présentes
                    cols_presentes = [c for c in colonnes_fixes if c in df.columns]
                    if len(cols_presentes) < 3:
                        erreurs.append(f" `{fichier.name}` — Format non reconnu (colonnes LimeSurvey manquantes)")
                        continue

                    # Dépivotage
                    df_long = pd.melt(
                        df,
                        id_vars=cols_presentes,
                        var_name='Question_Formulation',
                        value_name='Valeur_Brute'
                    )

                    # Nettoyage
                    df_long = df_long.dropna(subset=['Valeur_Brute'])

                    # Mapping scores
                    df_long['Score'] = df_long['Valeur_Brute'].map(
                        dictionnaire_scores
                    ).fillna(df_long['Valeur_Brute'])

                    # Ajout Annee depuis la date de soumission
                    df_long['Annee'] = pd.to_datetime(
                        df_long['Date de soumission'], errors='coerce'
                    ).dt.year.astype('Int64')

                    # ✅ Rattachement à l'établissement choisi par l'utilisateur
                    df_long['Id_structure'] = id_structure_import

                    tous_les_tableaux.append(df_long)
                    progress.progress((i + 1) / len(fichiers_uploades))

                except Exception as e:
                    erreurs.append(f" `{fichier.name}` — Erreur : {e}")

            # Afficher les erreurs s'il y en a
            if erreurs:
                for err in erreurs:
                    st.error(err)

            # Injection en base si au moins un fichier a été traité
            if tous_les_tableaux:
                status.text(" Fusion et injection dans la base de données...")

                df_final = pd.concat(tous_les_tableaux, ignore_index=True)

                try:
                    chemin_bdd = os.path.join(
                        os.path.dirname(os.path.abspath(__file__)),
                        "label_vivre.sqlite"
                    )
                    conn = sqlite3.connect(chemin_bdd)

                    # Récupérer les données existantes et ajouter les nouvelles
                    try:
                        df_existant = pd.read_sql_query(
                            "SELECT * FROM DONNEES_LIMESURVEY_NETTOYEES", conn
                        )
                        df_final = pd.concat(
                            [df_existant, df_final], ignore_index=True
                        ).drop_duplicates(
                            subset=['ID de la réponse', 'Question_Formulation', 'Date de soumission'],
                            keep='last'
                        )
                    except:
                        pass  # Si la table n'existe pas encore

                    df_final.to_sql(
                        'DONNEES_LIMESURVEY_NETTOYEES',
                        conn,
                        if_exists='replace',
                        index=False
                    )
                    conn.close()

                    progress.progress(1.0)
                    status.empty()

                    # Vider le cache pour que les graphiques se mettent à jour
                    st.cache_data.clear()

                    # Message de succès
                    st.success(f"""
                     **Import réussi !**
                    - {len(fichiers_uploades) - len(erreurs)} fichier(s) importé(s)
                    - {len(df_final):,} lignes au total dans la base
                    - Années disponibles : {sorted(df_final['Annee'].dropna().unique().tolist())}
                    """)

                    st.info(" Allez sur le **Tableau de bord** pour voir les résultats mis à jour.")

                except Exception as e:
                    st.error(f" Erreur lors de l'injection en base : {e}")
            else:
                status.empty()
                st.error(" Aucun fichier n'a pu être traité. Vérifiez le format des fichiers.")

    else:
        # Message si aucun fichier uploadé
        st.markdown("""
        <div style='text-align:center; padding:40px; color:#888;'>
            <div style='font-size:3rem;'></div>
            <div style='margin-top:10px;'>Glissez vos fichiers xlsx  pour les sélectionner</div>
        </div>
        """, unsafe_allow_html=True)

# ============================================================
# PAGE MON COMPTE — Changer son propre mot de passe
# Accessible à tous les utilisateurs connectés (établissements)
# ============================================================
elif st.session_state.page == 'mon_compte':
    st.markdown("<div class='section-title'> Mon compte</div>", unsafe_allow_html=True)

    compte_actuel = COMPTES_AUTORISES.get(st.session_state.identifiant, {})
    st.markdown(f"**Connecté en tant que :** {compte_actuel.get('nom_affiche', st.session_state.identifiant)}")
    st.markdown(f"**Identifiant :** `{st.session_state.identifiant}`")
    st.markdown("---")
    st.markdown("### Changer mon mot de passe")

    with st.form("form_changer_mdp"):
        ancien_mdp = st.text_input("Ancien mot de passe", type="password")
        nouveau_mdp = st.text_input("Nouveau mot de passe", type="password")
        confirm_mdp = st.text_input("Confirmer le nouveau mot de passe", type="password")
        submit = st.form_submit_button("Enregistrer", use_container_width=True)

        if submit:
            if not ancien_mdp or not nouveau_mdp or not confirm_mdp:
                st.error(" Veuillez remplir tous les champs.")
            elif not check_password_hash(compte_actuel.get('hash', ''), ancien_mdp):
                st.error(" Ancien mot de passe incorrect.")
            elif nouveau_mdp != confirm_mdp:
                st.error(" Les nouveaux mots de passe ne correspondent pas.")
            elif len(nouveau_mdp) < 6:
                st.error(" Le mot de passe doit contenir au moins 6 caractères.")
            else:
                try:
                    from werkzeug.security import generate_password_hash
                    nouveau_hash = generate_password_hash(nouveau_mdp)
                    chemin_bdd = os.path.join(os.path.dirname(os.path.abspath(__file__)), "label_vivre.sqlite")
                    conn = sqlite3.connect(chemin_bdd)
                    conn.execute(
                        "UPDATE UTILISATEUR SET Hash_mdp = ? WHERE Identifiant = ?",
                        (nouveau_hash, st.session_state.identifiant)
                    )
                    conn.commit()
                    conn.close()
                    st.cache_data.clear()
                    st.success(" Mot de passe modifié avec succès !")
                    st.info("Votre nouveau mot de passe sera actif à la prochaine connexion.")
                except Exception as e:
                    st.error(f" Erreur : {e}")

# ============================================================
# PAGE GESTION DES COMPTES — Admin uniquement
# ============================================================
elif st.session_state.page == 'gestion_comptes' and st.session_state.profil == "admin":
    st.markdown("<div class='section-title'> Gestion des comptes</div>", unsafe_allow_html=True)

    tab1, tab2 = st.tabs([" Mon mot de passe", " Réinitialiser un établissement"])

    with tab1:
        st.markdown("### Changer mon mot de passe")
        compte_admin = COMPTES_AUTORISES.get(st.session_state.identifiant, {})
        with st.form("form_admin_mdp"):
            ancien_mdp_a = st.text_input("Ancien mot de passe", type="password")
            nouveau_mdp_a = st.text_input("Nouveau mot de passe", type="password")
            confirm_mdp_a = st.text_input("Confirmer le nouveau mot de passe", type="password")
            submit_a = st.form_submit_button("Enregistrer", use_container_width=True)
            if submit_a:
                if not ancien_mdp_a or not nouveau_mdp_a or not confirm_mdp_a:
                    st.error(" Veuillez remplir tous les champs.")
                elif not check_password_hash(compte_admin.get('hash', ''), ancien_mdp_a):
                    st.error(" Ancien mot de passe incorrect.")
                elif nouveau_mdp_a != confirm_mdp_a:
                    st.error(" Les mots de passe ne correspondent pas.")
                elif len(nouveau_mdp_a) < 6:
                    st.error(" Minimum 6 caractères.")
                else:
                    try:
                        from werkzeug.security import generate_password_hash
                        nouveau_hash = generate_password_hash(nouveau_mdp_a)
                        chemin_bdd = os.path.join(os.path.dirname(os.path.abspath(__file__)), "label_vivre.sqlite")
                        conn = sqlite3.connect(chemin_bdd)
                        conn.execute("UPDATE UTILISATEUR SET Hash_mdp = ? WHERE Identifiant = ?",
                                   (nouveau_hash, st.session_state.identifiant))
                        conn.commit()
                        conn.close()
                        st.cache_data.clear()
                        st.success(" Mot de passe modifié avec succès !")
                    except Exception as e:
                        st.error(f" Erreur : {e}")

    with tab2:
        st.markdown("### Réinitialiser le mot de passe d'un établissement")
        st.info("Si un établissement a oublié son mot de passe, choisissez-le ci-dessous et définissez un nouveau mot de passe temporaire.")
        chemin_bdd = os.path.join(os.path.dirname(os.path.abspath(__file__)), "label_vivre.sqlite")
        conn = sqlite3.connect(chemin_bdd)
        df_etabs = pd.read_sql_query(
            "SELECT Identifiant, Nom FROM UTILISATEUR WHERE Role = 'etablissement' ORDER BY Nom", conn
        )
        conn.close()
        with st.form("form_reset_mdp"):
            options = [f"{row['Nom']} ({row['Identifiant']})" for _, row in df_etabs.iterrows()]
            choix = st.selectbox("Établissement", options=options)
            nouveau_mdp_r = st.text_input("Nouveau mot de passe temporaire", type="password")
            confirm_mdp_r = st.text_input("Confirmer le mot de passe", type="password")
            submit_r = st.form_submit_button("Réinitialiser", use_container_width=True)
            if submit_r:
                if not nouveau_mdp_r or not confirm_mdp_r:
                    st.error(" Veuillez remplir tous les champs.")
                elif nouveau_mdp_r != confirm_mdp_r:
                    st.error(" Les mots de passe ne correspondent pas.")
                elif len(nouveau_mdp_r) < 6:
                    st.error(" Minimum 6 caractères.")
                else:
                    try:
                        from werkzeug.security import generate_password_hash
                        identifiant_choisi = choix.split("(")[1].rstrip(")")
                        nouveau_hash = generate_password_hash(nouveau_mdp_r)
                        conn = sqlite3.connect(chemin_bdd)
                        conn.execute("UPDATE UTILISATEUR SET Hash_mdp = ? WHERE Identifiant = ?",
                                   (nouveau_hash, identifiant_choisi))
                        conn.commit()
                        conn.close()
                        st.cache_data.clear()
                        nom_etab = choix.split(" (")[0]
                        st.success(f" Mot de passe de **{nom_etab}** réinitialisé !")
                        st.warning(f" Communiquez ce mot de passe temporaire : `{nouveau_mdp_r}`")
                    except Exception as e:
                        st.error(f" Erreur : {e}")