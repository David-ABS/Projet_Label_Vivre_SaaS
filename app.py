import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
from werkzeug.security import check_password_hash



# CONFIGURATION PAGE ET CSS (AVEC L'ASTUCE PDF)

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
    justify-content: flex-start;   /* 👈 IMPORTANT */
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


# COMPTES AUTORISÉS (AVEC TOUS TES 31 ETABLISSEMENTS)

COMPTES_AUTORISES = {
    "stephane_dardelet": {
        "hash": "scrypt:32768:8:1$hKj4IHdUQMNBMYez$c6341c4be133c7b35f6cf656d99b758417de3a9576ee91b8ae332f0bc5d35b5f0daa09da94820500ba1832e3c57768c89b803cdea7376c3ecc1b69cfead068b0",
        "profil": "admin",
        "Id_structure": None,
        "nom_affiche": "Stéphane Dardelet"
    },
    "saint_dominique": {
        "hash": "scrypt:32768:8:1$AmgaTumzt7aghmq6$dda37b91037302dcaa7fc662461f98fe742874649857443f53e206d0dac73f361cad88e0ece825341c46cc3f89b6d11f2c6f031beaab7caf065225aea8f98750",
        "profil": "etablissement",
        "Id_structure": 1,
        "nom_affiche": "Saint-Dominique"
    },
    "manon_cormier": {
        "hash": "scrypt:32768:8:1$tZ2lnMnf39RfGwYw$e50a3d09402349034bdc06bbdc60ca3abaae93e659ca7184ce197b3b0518d93b181d41d7a30a7587534b208eab174e3bcd54198ae1f665cc14ea86a21b1786ce",
        "profil": "etablissement",
        "Id_structure": 2,
        "nom_affiche": "Manon Cormier"
    },
    "marie_durand": {
        "hash": "scrypt:32768:8:1$GcO2GiLn42JivSfy$e11f53f7462fa212d47126bbb8f01cb03f4a4f4b76413f7853718ae6a7a015570820eb81baa699b72fc5389d0d8069170989eb9470f89435b427c8ef7143f358",
        "profil": "etablissement",
        "Id_structure": 3,
        "nom_affiche": "Marie Durand"
    },
    "villa_bontemps": {
        "hash": "scrypt:32768:8:1$ROpSo0fyM3xajhFG$cf14f938ed960d41d77040399ca1c3ea456d0a939ebd21bf6bbae4ed57d27d969ccc0da866741573eeb04be3765afcf15602523ce47895e030371ed65ab9d35a",
        "profil": "etablissement",
        "Id_structure": 4,
        "nom_affiche": "Villa Bontemps"
    },
    "ehpad_belves": {
        "hash": "scrypt:32768:8:1$0ORJ28OKliIq9EDP$e7df6a0d6879857bf5642d4244cd7c95df14c0f53548077b6c3e935acaf322130811fe2f55dd9c6ad84d67acc2953b880c6e25dd16a30f17f8251f77df8501dc",
        "profil": "etablissement",
        "Id_structure": 5,
        "nom_affiche": "EHPAD Belvès"
    },
    "richelot_lasse": {
        "hash": "scrypt:32768:8:1$xmluxFwU6IMmfo2A$c6b9a8b8d49b84e64c0f007a0776cd0c391f09c0f16d7b267c6876581a111da4022b12e3443949ae0f4c3732c79b4c40248f422c5b74d7232423325d620d2c1a",
        "profil": "etablissement",
        "Id_structure": 6,
        "nom_affiche": "Richelot-Lassé"
    },
    "korian_le_chalet": {
        "hash": "scrypt:32768:8:1$nYvspGGsB27vZ0Zp$f8252dcd2f14235008b2fe4191fa84bcc64123b45a0ef088e17f6f73785bdb18673650d845b77eff25a0df4713fccf034cab288a958886ddda9bd7e7b788aa88",
        "profil": "etablissement",
        "Id_structure": 7,
        "nom_affiche": "Korian Le Chalet"
    },
    "la_nougeraie": {
        "hash": "scrypt:32768:8:1$dZkDYCwpT4msyRpe$440a515308d8d2d7c2202700fde504e0bb18f9fb8877fac919e0749b2ad441b76ad8cf59cb8ca34e67e96179433bc24ddb74c7ae52a489799cf948b1d28e1b2d",
        "profil": "etablissement",
        "Id_structure": 8,
        "nom_affiche": "La Nougeraie"
    },
    "les_terrasses_de_beausejour": {
        "hash": "scrypt:32768:8:1$H5jhPBObpdHN5ZvL$142e9ba71e60921d36769d83ad6dfa890d3b96d210af9bbba5b5dc9ab76c6b7d5581f378e17a5ba1ddefc8921d5cfe4796c23439f12aea05336178106c7a3ec7",
        "profil": "etablissement",
        "Id_structure": 9,
        "nom_affiche": "Les Terrasses de Beauséjour"
    },
    "sherpa": {
        "hash": "scrypt:32768:8:1$eWa6aduwg5fSLMMA$2d242ace9db7d53ea2372536136c35faefb5450c82c3107baa5f46ec883058de27838496c3fb66e99a495300798166de3ad2316b5d5fcf0756a7c2c2ef290842",
        "profil": "etablissement",
        "Id_structure": 10,
        "nom_affiche": "Sherpa"
    },
    "champdeniers": {
        "hash": "scrypt:32768:8:1$lJ9ChgTtTpHMG3wm$11dc607f3a6ae46a70260536766e142def0c03cc7dbeb6bf617b33ef414a0915f761f004752c0d52a6fc38accba13b9980a38548dc6cea5453d7051da2ee8a54",
        "profil": "etablissement",
        "Id_structure": 11,
        "nom_affiche": "Champdeniers"
    },
    "saint_jacques": {
        "hash": "scrypt:32768:8:1$1VHNx72IIhc5Kl1q$2b96b81bc7fbd4559b41dee07bffa5e6c8d2216478e2eaffc2a50c6fdfbfa3212ccdfb946dc8e7d5aaf2152ad234a0e7c8f23467a8b062b560a325484ba9ec4b",
        "profil": "etablissement",
        "Id_structure": 12,
        "nom_affiche": "Saint-Jacques"
    },
    "la_favorite": {
        "hash": "scrypt:32768:8:1$BQC0D7ug80jx55bI$b6bc3cfb1defce4efd944a7c5c453ef05cfbfcfc1ac5cab334c4be30d01c9426d9e50f3f1cf6614f8cf7121b6b08b7d1b54973535e67af9b07252a7b03ecce7a",
        "profil": "etablissement",
        "Id_structure": 13,
        "nom_affiche": "La Favorite"
    },
    "mfa_les_clarines": {
        "hash": "scrypt:32768:8:1$rB4R6XXTX2So6gQC$91d5cfe46d93041aea2c30daa4f14b4e35109e3ae04070b6bf5e0428b4c1ed18553dc75b3e849fc93807e115c6b9e6440d6dda1149e459abb9103fb3a5701301",
        "profil": "etablissement",
        "Id_structure": 14,
        "nom_affiche": "MFA les Clarines"
    },
    "mfa_clos_saint_francois": {
        "hash": "scrypt:32768:8:1$CX9aHlwLOlIFKfPU$86b7def42699bb6b215e3cdea8f3c9db3a1a9f790a3bf3a955528575de5054d597f6f4cc8e8ebb3b723fb040331cd6d09b630fef4e14314b211e0faa619e84a3",
        "profil": "etablissement",
        "Id_structure": 15,
        "nom_affiche": "MFA Clos Saint-François"
    },
    "mfa_cheveux_d_ange": {
        "hash": "scrypt:32768:8:1$BjQ7j9OTXNgu12Qz$61e05bef2e7041313e06aa304ac6af5c3831fcdee43c62879dec947f68d406368adb9fec7a8f190b07b65d9bf113c31226ac90a7ede54f90ff028aeb701a5bc6",
        "profil": "etablissement",
        "Id_structure": 16,
        "nom_affiche": "MFA Cheveux d'Ange"
    },
    "l_isle_aux_fleurs": {
        "hash": "scrypt:32768:8:1$yKWBBQSrdBkXpdBy$801a2c9514fb7c46c88bdb2d7a67fcea9498675a103311ef9eb486d5751ff5d1f7479f265cdb4874931eead52fa17e2a5838b925d831917cfc613fa84b5693cb",
        "profil": "etablissement",
        "Id_structure": 17,
        "nom_affiche": "L'Isle-aux-Fleurs"
    },
    "le_parc_du_bequet": {
        "hash": "scrypt:32768:8:1$sj3dPjpoacIctdlN$10dc6126ce8eeaacdc5c4a6edcb636495c62337bb34dc3636c8bc5c6131896bc41b617be3d8cb393f766b35e7878f1c753c8eba56ff389640914f78f7ad922a4",
        "profil": "etablissement",
        "Id_structure": 18,
        "nom_affiche": "Le Parc du Béquet"
    },
    "notre_dame_des_anges": {
        "hash": "scrypt:32768:8:1$JPN4NAWrpbsYaqsw$1b74c4386b869bf3d526ef58fdc54e06a8061a513dee83a05894a0d17b08da26ef76936b3248756710fc7a80a538b6c97ef063e2bd586b53b734afeeb14560fe",
        "profil": "etablissement",
        "Id_structure": 19,
        "nom_affiche": "Notre-Dame Des Anges"
    },
    "pont_saint_jean": {
        "hash": "scrypt:32768:8:1$SHXeg8Eq6IJK2BN9$4d3fdce5206abb8e73064a094d20430c373b78fb89ad7aa5a9dc47e8d72c58853b29068fb0778dd0498be40e533f62244f7da3d6cd079621e59af2a0c3300ca8",
        "profil": "etablissement",
        "Id_structure": 20,
        "nom_affiche": "Pont-Saint-Jean"
    },
    "blanche_de_caastille": {
        "hash": "scrypt:32768:8:1$fIMSw7p4Y7VfIRcm$abbe27050e34635750d0213a4efad0cd0bf5d00a38f4aeec607d6234c25cea77effb869acb84f32410fe1f3dec604f61942f99727a74a3cec9bc61507ac401e6",
        "profil": "etablissement",
        "Id_structure": 21,
        "nom_affiche": "Blanche de Caastille"
    },
    "clos_de_rochegude": {
        "hash": "scrypt:32768:8:1$3RfhklgOTQb60rcb$1c9936008bff973c60aade9221f119fc77d62794fbd8a6e59af421617043d257daaa752f1d99f97faeb55729df2c5cc4abe688a09ceda7105f74b09fa241d091",
        "profil": "etablissement",
        "Id_structure": 22,
        "nom_affiche": "Clos de Rochegude"
    },
    "les_cedres_belves": {
        "hash": "scrypt:32768:8:1$UQtLeHo8VwEZP8WI$a2e115bc39eb2eea37e47cedf4c5e57e0ba38dd5fc6a5f3dea1a1314ef1b17c77bb3f89bb984188788bb885ea4b95dabeb1be9513f096226f71800ea7c4d2786",
        "profil": "etablissement",
        "Id_structure": 23,
        "nom_affiche": "Les Cèdres Belvès"
    },
    "maison_de_blandine_limonest": {
        "hash": "scrypt:32768:8:1$U2h99KS8fyGzcsPM$d2db7fe1303ef61a1736abeff6ccfdddd65a94c31f02e97cf918cab39d7eb33fb9181074887ac4f0241a9960c4aaa7a531f39e41a0b2fc1e6f345b228a6788b6",
        "profil": "etablissement",
        "Id_structure": 24,
        "nom_affiche": "Maison de Blandine Limonest"
    },
    "maison_de_blandine_blace": {
        "hash": "scrypt:32768:8:1$NlQyhVXtQgojF78X$0785759fd6ebef55d4809ffdfddd417be6b7e34957195f3c86e51474121e109d387a78cab61d2908769ab7e012ccca49ecb5197c4397c6bbdc1ff6073a97f806",
        "profil": "etablissement",
        "Id_structure": 25,
        "nom_affiche": "Maison de Blandine Blacé"
    },
    "maison_de_blandine_sassenage": {
        "hash": "scrypt:32768:8:1$qJNYmtPL9YTpLL0q$550d246e32f493a335b1404e9234fe954b7f5f5d38d166878970cdefbda23c0cd3769a62d351210e1d63b1fdce13507da9ab9afc7e359adbb9b6441ab47feb08",
        "profil": "etablissement",
        "Id_structure": 26,
        "nom_affiche": "Maison de Blandine Sassenage"
    },
    "maison_de_blandine_amberieux": {
        "hash": "scrypt:32768:8:1$PP2hH61cS7rwaVFu$a48708b1f1658cc3d1142e67be467eade19f8e7db61325f11affed719b20d091c09e5c08d3dc76e8145c515254343675f4bbc018bd0577d3ceb9599a67818129",
        "profil": "etablissement",
        "Id_structure": 27,
        "nom_affiche": "Maison de Blandine Ambérieux"
    },
    "flora_tristan": {
        "hash": "scrypt:32768:8:1$vgcW0F9a4AprwGFX$93042c606b8fdeda51fa65a117516a17fe2932f41229184868c69f840c8a32821f022fc41e51d725aaada286b7b54f292b2d06c28c0b4edaf85e161cb227f841",
        "profil": "etablissement",
        "Id_structure": 28,
        "nom_affiche": "Flora Tristan"
    },
    "maison_de_blandine_ampuis": {
        "hash": "scrypt:32768:8:1$FTwAahShgLvgshQj$e4846ebe89c5a35eeac838184a2e266380de44fef978cd0d662831c1ca7fe04a20cd1e822d9c2426248dfe4d0d5fe4edc07554eea78587b3d3525263a202cab6",
        "profil": "etablissement",
        "Id_structure": 29,
        "nom_affiche": "Maison de Blandine Ampuis"
    },
    "maison_de_blandine_rives": {
        "hash": "scrypt:32768:8:1$ZZ484cjIS1bye1vB$c1824dcb3cd99d116462d8d2eb723721bfe5a19784db51291c8cab10b4ac277e6f6ad7f3a5460d6f5fd7f657b63983dbe724411dc315c50237ff3b46a85de64b",
        "profil": "etablissement",
        "Id_structure": 30,
        "nom_affiche": "Maison de Blandine Rives"
    },
    "louis_jouannin": {
        "hash": "scrypt:32768:8:1$DwqBqnajE0HZ4BZd$b517c93ead03fbae0b3769fc66f66bf8873ef83f98450745d84b7706a29a7425e8dc59a4514fd82b514072a27457ce3ea310b924aba864a7be87918842a38fa1",
        "profil": "etablissement",
        "Id_structure": 31,
        "nom_affiche": "Louis Jouannin"
    },
}

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


# PAGE LOGIN

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

# ============================================================
# CONNEXION BASE DE DONNÉES
# ============================================================
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
            ROUND(100.0 * SUM(CASE WHEN CAST("Score" AS FLOAT) = 4 THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_promoteurs,
            ROUND(100.0 * SUM(CASE WHEN CAST("Score" AS FLOAT) = 3 THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_passifs,
            ROUND(100.0 * SUM(CASE WHEN CAST("Score" AS FLOAT) IN (1,2) THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_detracteurs,
            ROUND(
                100.0 * SUM(CASE WHEN CAST("Score" AS FLOAT) = 4 THEN 1 ELSE 0 END) / COUNT(*) -
                100.0 * SUM(CASE WHEN CAST("Score" AS FLOAT) IN (1,2) THEN 1 ELSE 0 END) / COUNT(*),
            1) AS NPS
        FROM DONNEES_LIMESURVEY_NETTOYEES
        WHERE {where}
        AND "Question_Formulation" NOT LIKE 'Durée%'
        AND "Question_Formulation" NOT LIKE 'Commentaire%'
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
        SELECT
            "Question_Formulation" AS question,
            ROUND(AVG(CAST("Score" AS FLOAT)), 2) AS score_moyen,
            COUNT(*) AS nb_reponses
        FROM DONNEES_LIMESURVEY_NETTOYEES
        WHERE {where}
        AND "Question_Formulation" NOT LIKE 'Durée%'
        AND "Question_Formulation" NOT LIKE 'Commentaire%'
        GROUP BY "Question_Formulation"
        ORDER BY score_moyen DESC
        LIMIT 10
    """
    return pd.read_sql_query(query, conn, params=params)

def get_flop_questions(id_structure, annee):
    conn = get_connexion()
    where, params = build_filtre(id_structure, annee)
    query = f"""
        SELECT
            "Question_Formulation" AS question,
            ROUND(AVG(CAST("Score" AS FLOAT)), 2) AS score_moyen,
            COUNT(*) AS nb_reponses
        FROM DONNEES_LIMESURVEY_NETTOYEES
        WHERE {where}
        AND "Question_Formulation" NOT LIKE 'Durée%'
        AND "Question_Formulation" NOT LIKE 'Commentaire%'
        GROUP BY "Question_Formulation"
        ORDER BY score_moyen ASC
        LIMIT 10
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



# ALGORITHME LABEL VIVRE (TÂCHE 20)

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

col_nav1, col_nav2, col_nav3, col_nav4, col_nav5, col_nav6 = st.columns([2, 2, 2, 2, 2, 1])
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
    if st.button(" Déconnexion", use_container_width=True):
        logout()
with col_nav6:
    badge = "badge-admin" if st.session_state.profil == "admin" else "badge-etab"
    label = " Admin" if st.session_state.profil == "admin" else " Établissement"
    st.markdown(f"<p style='text-align:right; padding-top:6px;'><span class='{badge}'>{label}</span></p>", unsafe_allow_html=True)

st.markdown("---")

# ============================================================
# BARRE DE FILTRES — TÂCHE 18
# ============================================================
df_structures = get_structures()
annees_dispo = get_annees()

with st.container():
    st.markdown("<div class='filtre-bar'>", unsafe_allow_html=True)
    if st.session_state.profil == "admin":
        col_f1, col_f2, col_f3 = st.columns([3, 2, 1])
        with col_f1:
            options_etab = [" Tous les établissements"] + [f"{row['Structure']} ({row['Type']})" for _, row in df_structures.iterrows()]
            choix_etab = st.selectbox(" Établissement", options=options_etab, index=0, key="select_etab")
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
                if not row_info.empty: st.caption(f"📍 {row_info.iloc[0]['Département']} · {row_info.iloc[0]['Région']}")
    else:
        id_s = st.session_state.filtre_structure
        if id_s:
            row_etab = df_structures[df_structures['Id_structure'] == id_s]
            if not row_etab.empty:
                col_e1, col_e2 = st.columns([3, 2])
                with col_e1: st.markdown(f"** {row_etab.iloc[0]['Structure']}** &nbsp;|&nbsp; {row_etab.iloc[0]['Type']} &nbsp;|&nbsp; 📍 {row_etab.iloc[0]['Département']}, {row_etab.iloc[0]['Région']}")
                with col_e2:
                    options_annee = ["Toutes les années"] + [str(a) for a in annees_dispo]
                    choix_annee = st.selectbox(" Année", options=options_annee, index=0, key="select_annee_etab")
                    st.session_state.filtre_annee = None if choix_annee == "Toutes les années" else int(choix_annee)
    st.markdown("</div>", unsafe_allow_html=True)



id_structure_actif = st.session_state.filtre_structure
annee_active = st.session_state.filtre_annee


# ============================================================
# PAGE DASHBOARD (DESIGN PDF VIA ONGLETS)
# ============================================================
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

    # CRÉATION DES ONGLETS
    tab_synthese, tab_thematique, tab_verbatim, tab_methodo = st.tabs([
        " Résultats synthétiques", 
        " Résultats thématiques", 
        " Verbatim", 
        " Méthodologie"
    ])

    # ONGLET 1 : SYNTHÈSE
    with tab_synthese:
        col1, col2, col3, col4, col5 = st.columns(5)
        couleur_nps = "#6BBFB5" if nps['NPS'] >= 30 else "#E8706A"

        with col1:
            st.markdown(f"""<div class='kpi-card'><div class='kpi-label'>NPS Global</div><div class='kpi-value' style='color:{couleur_nps};'>{nps['NPS']}</div><div class='kpi-label'>/ 100</div></div>""", unsafe_allow_html=True)
        with col2:
            st.markdown(f"""<div class='kpi-card'><div class='kpi-label'>Promoteurs</div><div class='kpi-value' style='color:#6BBFB5;'>{nps['pct_promoteurs']}%</div><div class='kpi-label'>Score 4/4</div></div>""", unsafe_allow_html=True)
        with col3:
            st.markdown(f"""<div class='kpi-card'><div class='kpi-label'>Passifs</div><div class='kpi-value' style='color:#F5A623;'>{nps['pct_passifs']}%</div><div class='kpi-label'>Score 3/4</div></div>""", unsafe_allow_html=True)
        with col4:
            st.markdown(f"""<div class='kpi-card'><div class='kpi-label'>Détracteurs</div><div class='kpi-value' style='color:#E8706A;'>{nps['pct_detracteurs']}%</div><div class='kpi-label'>Score 1-2/4</div></div>""", unsafe_allow_html=True)
        with col5:
            st.markdown(f"""<div class='kpi-card'><div class='kpi-label'>Réponses</div><div class='kpi-value' style='color:#5C5C5C;'>{int(nps['total']):,}</div><div class='kpi-label'>analysées</div></div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        col_left, col_right = st.columns(2)

        with col_left:
            st.markdown("<div class='section-title'> Score moyen par public</div>", unsafe_allow_html=True)
            df_pub = scores_public[scores_public['public'] != 'Autre'].copy()
            couleurs = {'Proches': '#6BBFB5', 'Équipe': '#F5A623', 'Résidents': '#E8706A'}
            fig_bar = px.bar(df_pub, x='public', y='score_moyen', color='public', color_discrete_map=couleurs, text='score_moyen', title='Score moyen / 4')
            fig_bar.update_traces(texttemplate='%{text}', textposition='outside')
            fig_bar.update_layout(showlegend=False, plot_bgcolor='white', paper_bgcolor='white', yaxis=dict(range=[0, 4.5], title='Score /4'), xaxis_title='', title_font_family='Georgia', height=350)
            st.plotly_chart(fig_bar, use_container_width=True)

        with col_right:
            st.markdown("<div class='section-title'> Répartition NPS</div>", unsafe_allow_html=True)
            fig_pie = go.Figure(data=[go.Pie(labels=['Promoteurs', 'Passifs', 'Détracteurs'], values=[nps['pct_promoteurs'], nps['pct_passifs'], nps['pct_detracteurs']], hole=0.4, marker_colors=['#6BBFB5', '#F5A623', '#E8706A'])])
            fig_pie.update_layout(title='Répartition des répondants', title_font_family='Georgia', paper_bgcolor='white', height=350, annotations=[dict(text=f'NPS<br>{nps["NPS"]}', x=0.5, y=0.5, font_size=18, showarrow=False)])
            st.plotly_chart(fig_pie, use_container_width=True)

    # ONGLET 2 : THÉMATIQUES
    with tab_thematique:
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

    # ONGLET 3 : VERBATIM
    with tab_verbatim:
        st.markdown("<div class='section-title'> Ce qu'ils nous ont dit</div>", unsafe_allow_html=True)
        st.markdown("#### Retours des Résidents")
        st.info("« C'est une bonne chose de faire cette enquête régulièrement. »")
        st.info("« Cela me semble important de connaître les impressions de chacun. »")
        st.markdown("#### Retours de l'Équipe")
        st.warning("« Il manque toujours des questions précises sur l'inclusion, le fonctionnement du service... »")

    # ONGLET 4 : MÉTHODOLOGIE
    with tab_methodo:
        st.markdown("<div class='section-title'>Méthodologie - Échantillons</div>", unsafe_allow_html=True)
        col_m1, col_m2, col_m3 = st.columns(3)
        with col_m1:
            st.markdown("<div class='kpi-card' style='border-top: 5px solid #E8706A;'><h3 style='color:#E8706A;'>Résidents</h3><p>Présentiel (Entretiens)</p><h2 style='color:#5C5C5C;'>44%</h2><p style='color:#888;'>Taux de réponse</p></div>", unsafe_allow_html=True)
        with col_m2:
            st.markdown("<div class='kpi-card' style='border-top: 5px solid #6BBFB5;'><h3 style='color:#6BBFB5;'>Proches</h3><p>Distanciel (Email)</p><h2 style='color:#5C5C5C;'>53%</h2><p style='color:#888;'>Taux de réponse</p></div>", unsafe_allow_html=True)
        with col_m3:
            st.markdown("<div class='kpi-card' style='border-top: 5px solid #F5A623;'><h3 style='color:#F5A623;'>Équipe</h3><p>Distanciel (En ligne)</p><h2 style='color:#5C5C5C;'>99%</h2><p style='color:#888;'>Taux de réponse</p></div>", unsafe_allow_html=True)

# ============================================================
# PAGE DONNÉES BRUTES
# ============================================================
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

# ============================================================
# PAGE EXPORT
# ============================================================
elif st.session_state.page == 'export':
    st.markdown("<div class='section-title'> Export des données</div>", unsafe_allow_html=True)

    # --- L'astuce pour le PDF ---
    st.info("💡 **Astuce PDF (Rapport) :** Pour générer un rapport PDF parfait, allez dans l'onglet **'Tableau de bord'** et appuyez sur **`Ctrl + P`** (ou `Cmd + P` sur Mac), puis choisissez la destination **'Enregistrer au format PDF'**. Le design a été spécialement codé pour ça !")
    st.markdown("---")

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
        st.download_button(label="⬇️ Télécharger NPS (CSV)", data=csv_nps, file_name=f"nps_{nom_export}_{annee_export}.csv", mime="text/csv", use_container_width=True)

    with col2:
        st.markdown("###  Exporter les scores par public")
        scores_public = get_scores_public(id_structure_actif, annee_active)
        csv_public = scores_public.to_csv(index=False, encoding='utf-8')
        st.download_button(label="⬇️ Télécharger scores par public (CSV)", data=csv_public, file_name=f"scores_public_{nom_export}_{annee_export}.csv", mime="text/csv", use_container_width=True)

    st.markdown("###  Exporter les données brutes")
    df_brut = get_donnees_brutes(id_structure_actif, annee_active, 500)
    csv_brut = df_brut.to_csv(index=False, encoding='utf-8')
    st.download_button(label="⬇️ Télécharger données brutes (CSV)", data=csv_brut, file_name=f"donnees_brutes_{nom_export}_{annee_export}.csv", mime="text/csv", use_container_width=True)

# ============================================================
# PAGE LABEL VIVRE 
# ============================================================
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
    st.markdown("<div class='section-title'> Critère 2 — Expérience positive (score ≥ 7/10)</div>", unsafe_allow_html=True)

    if not scores_public.empty:
        cols = st.columns(len(scores_public))
        for i, (_, row) in enumerate(scores_public.iterrows()):
            with cols[i]:
                couleur = "#6BBFB5" if row['valide'] else "#E8706A"
                icone = "✅" if row['valide'] else "❌"
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
    st.markdown("<div class='section-title'>📝 Récapitulatif</div>", unsafe_allow_html=True)
    col_r1, col_r2 = st.columns(2)
    with col_r1:
        icone_c1 = "✅" if verdict['c1_ok'] else "❌"
        st.markdown(f"""<div class='kpi-card'><div class='kpi-label'>Critère 1 — Critères essentiels</div><div class='kpi-value'>{icone_c1}</div><div class='kpi-label'>{verdict['nb_bloquants']} bloquant(s) · {verdict['nb_avertissements']} avertissement(s)</div></div>""", unsafe_allow_html=True)
    with col_r2:
        icone_c2 = "✅" if verdict['c2_ok'] else "❌"
        publics_ok = scores_public[scores_public['valide']]['public'].tolist() if not scores_public.empty else []
        st.markdown(f"""<div class='kpi-card'><div class='kpi-label'>Critère 2 — Expérience positive</div><div class='kpi-value'>{icone_c2}</div><div class='kpi-label'>{len(publics_ok)}/3 publics ≥ 7/10</div></div>""", unsafe_allow_html=True)