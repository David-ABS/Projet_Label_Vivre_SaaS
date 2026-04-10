import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
from werkzeug.security import check_password_hash

# ============================================================
# CONFIGURATION DE LA PAGE ET CSS
# ============================================================
st.set_page_config(
    page_title="Label Vivre",
    page_icon="❤️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    :root { --orange: #F5A623; --rose: #E8706A; --vert: #6BBFB5; --beige: #FAF6F1; --gris: #5C5C5C; }
    .stApp { background-color: #FAF6F1; }
    .header-bar { background-color: #F5A623; padding: 20px 40px; border-radius: 0px; margin: -1rem -1rem 2rem -1rem; display: flex; align-items: center; justify-content: center; }
    .header-title { font-family: 'Georgia', serif; font-size: 2.5rem; font-weight: bold; color: #5C5C5C; text-align: center; margin: 0; }
    .header-subtitle { font-family: 'Georgia', serif; font-size: 1rem; color: #5C5C5C; font-style: italic; text-align: center; }
    .kpi-card { background: white; border-radius: 15px; padding: 25px; text-align: center; box-shadow: 0 2px 10px rgba(0,0,0,0.08); margin: 5px; }
    .kpi-value { font-size: 2.5rem; font-weight: bold; margin: 10px 0; }
    .kpi-label { font-size: 0.9rem; color: #888; font-family: 'Georgia', serif; }
    [data-testid="stSidebar"] { display: none; }
    .section-title { font-family: 'Georgia', serif; font-size: 1.3rem; color: #5C5C5C; font-weight: bold; border-left: 4px solid #F5A623; padding-left: 10px; margin: 20px 0 15px 0; }
</style>
""", unsafe_allow_html=True)

# HEADER - Toujours visible
st.markdown("""
<div class="header-bar">
    <div>
        <div class="header-title"> Label Vivre</div>
        <div class="header-subtitle">Engagés pour nos aînés</div>
    </div>
</div>
""", unsafe_allow_html=True)


# ============================================================
# BASE DE DONNÉES DES COMPTES (À remplacer par tes vrais hashs)
# ============================================================
COMPTES_AUTORISES = {
    "admin_prismatics": {
        "hash": "scrypt:32768:8:1$XUzvzmGi5TJWwRQ0$e36dc27f2cc6eb054be09557c84d4a06a3db9d08f2e46c4ff5fdf719166f1f74409290fa22592dcefd10a5e9890e4dda2e22ddb5973ba2990386c21fc5b6f894", 
        "profil": "admin"
    },
    "ehpad_saintes": {
        "hash": "scrypt:32768:8:1$vk0Z6wDd8ne2G3bB$182fc7c031b71677f5ace038e708be5fa0a20bc61874e7466bf072fd221eab8a9359cc6b9420e285f83f39e21ccdde0aa5112234b807d27ebb3411ae5e25573e", 
        "profil": "etablissement"
    },
    "hap_lyon": {
        "hash": "scrypt:32768:8:1$rHZS9u4DLkl4ad6Q$ee608b3239202e0a70cf004ad2d97763e80a023773b4963325b6e4d59698980d900a31d7beb522fd95da0fe43fbb1c59dd931925dca230f9a61398f576f668a2", 
        "profil": "etablissement"
    },
    "ra_bordeaux": {
        "hash": "scrypt:32768:8:1$zfRGX33FZHiZLY14$bb70e9df3604535757f89b3ef97116531223618c391a8af824a928c122772afe48d3b8b6a6f8da1db6eeb1003dec7f8510f98b1e675680cb02fb3da8721fea50", 
        "profil": "etablissement"
    }
}

# ============================================================
# ÉTAT DE LA PAGE (Navigation & Sécurité)
# ============================================================
if 'identifiant' not in st.session_state:
    st.session_state.identifiant = None
if 'page' not in st.session_state:
    st.session_state.page = 'accueil'
if 'profil' not in st.session_state:
    st.session_state.profil = None

def logout():
    st.session_state.identifiant = None
    st.session_state.profil = None
    st.session_state.page = 'accueil'
    st.rerun()

# ============================================================
# PAGE ACCUEIL - MIRE DE CONNEXION SÉCURISÉE
# ============================================================
if st.session_state.identifiant is None:
    st.markdown("<h2 style='text-align: center; color: #F5A623;'>🔐 Accès Restreint</h2>", unsafe_allow_html=True)
    st.info("L'accès à cette plateforme est réservé aux administrateurs et aux directions d'établissements.")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("login_form"):
            username = st.text_input("Identifiant (ex: admin_prismatics ou ehpad_saintes)").strip().lower()
            password = st.text_input("Mot de passe", type="password")
            submit = st.form_submit_button("Se connecter", use_container_width=True)
            
            if submit:
                if username in COMPTES_AUTORISES:
                    vrai_hash = COMPTES_AUTORISES[username]["hash"]
                    if check_password_hash(vrai_hash, password):
                        # Connexion réussie ! On met à jour les variables
                        st.session_state.identifiant = username
                        st.session_state.profil = COMPTES_AUTORISES[username]["profil"]
                        st.session_state.page = 'dashboard' # On l'envoie sur le dashboard
                        st.rerun()
                    else:
                        st.error(" Mot de passe incorrect.")
                else:
                    st.error(" Cet identifiant n'existe pas.")
    
    st.stop() # Bloque l'exécution du reste du code si non connecté


# ============================================================
# CONNEXION SQLITE & FONCTIONS DE DONNÉES
# ============================================================
@st.cache_resource
def get_connexion():
    chemin = os.path.join(os.path.dirname(os.path.abspath(__file__)), "label_vivre.sqlite")
    return sqlite3.connect(chemin, check_same_thread=False)

@st.cache_data
def get_nps():
    conn = get_connexion()
    df = pd.read_sql_query("""
        SELECT COUNT(*) AS total,
            ROUND(100.0 * SUM(CASE WHEN CAST("Score" AS FLOAT) = 4 THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_promoteurs,
            ROUND(100.0 * SUM(CASE WHEN CAST("Score" AS FLOAT) = 3 THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_passifs,
            ROUND(100.0 * SUM(CASE WHEN CAST("Score" AS FLOAT) IN (1,2) THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_detracteurs,
            ROUND(100.0 * SUM(CASE WHEN CAST("Score" AS FLOAT) = 4 THEN 1 ELSE 0 END) / COUNT(*) -
            100.0 * SUM(CASE WHEN CAST("Score" AS FLOAT) IN (1,2) THEN 1 ELSE 0 END) / COUNT(*), 1) AS NPS
        FROM DONNEES_LIMESURVEY_NETTOYEES
        WHERE CAST("Score" AS FLOAT) IN (1.0,2.0,3.0,4.0)
        AND "Question_Formulation" NOT LIKE 'Durée%'
        AND "Question_Formulation" NOT LIKE 'Commentaire%'
    """, conn)
    return df.iloc[0]

@st.cache_data
def get_scores_public():
    conn = get_connexion()
    return pd.read_sql_query("""
        SELECT
            CASE
                WHEN "Question_Formulation" LIKE '%résident%' OR "Question_Formulation" LIKE '%habitant%' THEN 'Résidents'
                WHEN "Question_Formulation" LIKE '%proche%' THEN 'Proches'
                WHEN "Question_Formulation" LIKE '%équipe%' OR "Question_Formulation" LIKE '%salarié%' THEN 'Équipe'
                ELSE 'Autre'
            END AS public,
            ROUND(AVG(CAST("Score" AS FLOAT)), 2) AS score_moyen,
            COUNT(DISTINCT "ID de la réponse") AS nb_repondants
        FROM DONNEES_LIMESURVEY_NETTOYEES
        WHERE CAST("Score" AS FLOAT) IN (1.0,2.0,3.0,4.0)
        AND "Question_Formulation" NOT LIKE 'Durée%'
        GROUP BY public
        ORDER BY score_moyen DESC
    """, conn)

@st.cache_data
def get_scores_genre():
    conn = get_connexion()
    return pd.read_sql_query("""
        SELECT genre."Valeur_Brute" AS genre,
            COUNT(DISTINCT rep."ID de la réponse") AS nb_repondants,
            ROUND(AVG(CAST(rep."Score" AS FLOAT)), 2) AS score_moyen
        FROM DONNEES_LIMESURVEY_NETTOYEES rep
        JOIN DONNEES_LIMESURVEY_NETTOYEES genre
            ON rep."ID de la réponse" = genre."ID de la réponse"
            AND genre."Question_Formulation" = 'Vous êtes ... ?'
        WHERE CAST(rep."Score" AS FLOAT) IN (1.0,2.0,3.0,4.0)
        AND rep."Question_Formulation" NOT LIKE 'Durée%'
        AND rep."Question_Formulation" != 'Vous êtes ... ?'
        GROUP BY genre ORDER BY score_moyen DESC
    """, conn)

@st.cache_data
def get_top_questions():
    conn = get_connexion()
    return pd.read_sql_query("""
        SELECT "Question_Formulation" AS question,
            ROUND(AVG(CAST("Score" AS FLOAT)), 2) AS score_moyen,
            COUNT(*) AS nb_reponses
        FROM DONNEES_LIMESURVEY_NETTOYEES
        WHERE CAST("Score" AS FLOAT) IN (1.0,2.0,3.0,4.0)
        AND "Question_Formulation" NOT LIKE 'Durée%'
        AND "Question_Formulation" NOT LIKE 'Commentaire%'
        GROUP BY "Question_Formulation"
        ORDER BY score_moyen DESC
        LIMIT 10
    """, conn)

@st.cache_data
def get_donnees_brutes(limite=100):
    conn = get_connexion()
    return pd.read_sql_query(f"""
        SELECT "ID de la réponse" AS ID,
               "Date de soumission" AS Date,
               "Question_Formulation" AS Question,
               "Valeur_Brute" AS Réponse,
               "Score" AS Score
        FROM DONNEES_LIMESURVEY_NETTOYEES
        WHERE CAST("Score" AS FLOAT) IN (1.0,2.0,3.0,4.0)
        LIMIT {limite}
    """, conn)


# ============================================================
# MENU DE NAVIGATION (Visible uniquement si connecté)
# ============================================================
col_nav1, col_nav2, col_nav3, col_nav4, col_nav5 = st.columns([2, 2, 2, 2, 1])
with col_nav1:
    if st.button(" Tableau de bord", use_container_width=True):
        st.session_state.page = 'dashboard'
        st.rerun()
with col_nav2:
    if st.button(" Données brutes", use_container_width=True):
        st.session_state.page = 'donnees'
        st.rerun()
with col_nav3:
    if st.button(" Export", use_container_width=True):
        st.session_state.page = 'export'
        st.rerun()
with col_nav4:
    if st.button(" Déconnexion", use_container_width=True):
        logout()
with col_nav5:
    profil_label = {"admin": "Admin", "etablissement": " Établissement"}.get(st.session_state.profil, "")
    st.markdown(f"<p style='text-align:right; color:#888; padding-top:8px;'>{profil_label}</p>", unsafe_allow_html=True)

st.markdown("---")

# ============================================================
# PAGE DASHBOARD
# ============================================================
if st.session_state.page == 'dashboard':

    # Chargement des données
    nps = get_nps()
    scores_public = get_scores_public()

    # --- KPI PRINCIPAUX ---
    st.markdown("<div class='section-title'> Indicateurs clés</div>", unsafe_allow_html=True)

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        couleur_nps = "#6BBFB5" if nps['NPS'] >= 30 else "#E8706A"
        st.markdown(f"""
        <div class='kpi-card'>
            <div class='kpi-label'>NPS Global</div>
            <div class='kpi-value' style='color:{couleur_nps};'>{nps['NPS']}</div>
            <div class='kpi-label'>/ 100</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class='kpi-card'>
            <div class='kpi-label'> Promoteurs</div>
            <div class='kpi-value' style='color:#6BBFB5;'>{nps['pct_promoteurs']}%</div>
            <div class='kpi-label'>Score 4/4</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class='kpi-card'>
            <div class='kpi-label'> Passifs</div>
            <div class='kpi-value' style='color:#F5A623;'>{nps['pct_passifs']}%</div>
            <div class='kpi-label'>Score 3/4</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div class='kpi-card'>
            <div class='kpi-label'> Détracteurs</div>
            <div class='kpi-value' style='color:#E8706A;'>{nps['pct_detracteurs']}%</div>
            <div class='kpi-label'>Score 1-2/4</div>
        </div>
        """, unsafe_allow_html=True)

    with col5:
        st.markdown(f"""
        <div class='kpi-card'>
            <div class='kpi-label'> Réponses</div>
            <div class='kpi-value' style='color:#5C5C5C;'>{nps['total']:,}</div>
            <div class='kpi-label'>analysées</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # --- GRAPHIQUES ---
    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown("<div class='section-title'>👥 Score moyen par public</div>", unsafe_allow_html=True)

        df_pub = scores_public[scores_public['public'] != 'Autre'].copy()
        couleurs = {'Proches': '#6BBFB5', 'Équipe': '#F5A623', 'Résidents': '#E8706A'}
        df_pub['couleur'] = df_pub['public'].map(couleurs)

        fig_bar = px.bar(
            df_pub, x='public', y='score_moyen', color='public',
            color_discrete_map=couleurs, text='score_moyen', title='Score moyen / 4'
        )
        fig_bar.update_traces(texttemplate='%{text}', textposition='outside')
        fig_bar.update_layout(
            showlegend=False, plot_bgcolor='white', paper_bgcolor='white',
            yaxis=dict(range=[0, 4], title='Score /4'), xaxis_title='',
            title_font_family='Georgia', height=350
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    with col_right:
        st.markdown("<div class='section-title'> Répartition NPS</div>", unsafe_allow_html=True)

        fig_pie = go.Figure(data=[go.Pie(
            labels=['Promoteurs', 'Passifs', 'Détracteurs'],
            values=[nps['pct_promoteurs'], nps['pct_passifs'], nps['pct_detracteurs']],
            hole=0.4, marker_colors=['#6BBFB5', '#F5A623', '#E8706A']
        )])
        fig_pie.update_layout(
            title='Répartition des répondants', title_font_family='Georgia',
            paper_bgcolor='white', height=350,
            annotations=[dict(text=f'NPS<br>{nps["NPS"]}', x=0.5, y=0.5, font_size=18, showarrow=False)]
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    # --- SCORES PAR GENRE ---
    st.markdown("<div class='section-title'> Score moyen par genre</div>", unsafe_allow_html=True)
    genre_df = get_scores_genre()

    col_g1, col_g2 = st.columns([2, 3])
    with col_g1:
        fig_genre = px.bar(
            genre_df, x='genre', y='score_moyen', color='genre',
            color_discrete_sequence=['#E8706A', '#6BBFB5'], text='score_moyen', title='Score par genre'
        )
        fig_genre.update_traces(texttemplate='%{text}', textposition='outside')
        fig_genre.update_layout(
            showlegend=False, plot_bgcolor='white', paper_bgcolor='white',
            yaxis=dict(range=[0, 4]), xaxis_title='', height=300
        )
        st.plotly_chart(fig_genre, use_container_width=True)

    with col_g2:
        st.markdown("<div class='section-title'> Top 10 questions les mieux notées</div>", unsafe_allow_html=True)
        top_q = get_top_questions()
        top_q['question_courte'] = top_q['question'].str[:50] + '...'
        fig_top = px.bar(
            top_q, x='score_moyen', y='question_courte', orientation='h',
            color='score_moyen', color_continuous_scale=['#F5A623', '#6BBFB5'], title='Top 10 meilleures questions'
        )
        fig_top.update_layout(
            plot_bgcolor='white', paper_bgcolor='white', height=350,
            showlegend=False, coloraxis_showscale=False, yaxis_title='', xaxis=dict(range=[0, 4])
        )
        st.plotly_chart(fig_top, use_container_width=True)


# ============================================================
# PAGE DONNÉES BRUTES
# ============================================================
elif st.session_state.page == 'donnees':
    st.markdown("<div class='section-title'> Données brutes LimeSurvey</div>", unsafe_allow_html=True)

    limite = st.slider("Nombre de lignes à afficher", 10, 500, 100)
    df_brut = get_donnees_brutes(limite)

    score_filtre = st.multiselect("Filtrer par score", [1.0, 2.0, 3.0, 4.0], default=[1.0, 2.0, 3.0, 4.0])
    if score_filtre:
        df_brut = df_brut[df_brut['Score'].astype(float).isin(score_filtre)]

    st.dataframe(df_brut, use_container_width=True, height=400)
    st.info(f" {len(df_brut)} lignes affichées")


# ============================================================
# PAGE EXPORT
# ============================================================
elif st.session_state.page == 'export':
    st.markdown("<div class='section-title'> Export des données</div>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("###  Exporter les résultats NPS")
        nps = get_nps()
        df_nps = pd.DataFrame([{
            'Indicateur': 'NPS Global', 'Valeur': nps['NPS'],
        }, {
            'Indicateur': '% Promoteurs', 'Valeur': nps['pct_promoteurs'],
        }, {
            'Indicateur': '% Passifs', 'Valeur': nps['pct_passifs'],
        }, {
            'Indicateur': '% Détracteurs', 'Valeur': nps['pct_detracteurs'],
        }])

        csv_nps = df_nps.to_csv(index=False, encoding='utf-8')
        st.download_button(label=" Télécharger NPS (CSV)", data=csv_nps, file_name="resultats_nps.csv", mime="text/csv", use_container_width=True)

    with col2:
        st.markdown("### 👥 Exporter les scores par public")
        scores_public = get_scores_public()
        csv_public = scores_public.to_csv(index=False, encoding='utf-8')
        st.download_button(label=" Télécharger scores par public (CSV)", data=csv_public, file_name="scores_par_public.csv", mime="text/csv", use_container_width=True)

    st.markdown("### 📋 Exporter les données brutes")
    df_brut = get_donnees_brutes(500)
    csv_brut = df_brut.to_csv(index=False, encoding='utf-8')
    st.download_button(label=" Télécharger données brutes (CSV)", data=csv_brut, file_name="donnees_brutes.csv", mime="text/csv", use_container_width=True)