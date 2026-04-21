# Fichier : creer_hash.py
# CONFIDENTIEL - Ne pas mettre sur GitHub (.gitignore)
# Sert a generer les hashs securises a copier dans app.py
# Relancer ce script si tu ajoutes un nouvel etablissement

from werkzeug.security import generate_password_hash

mots_de_passe_en_clair = {
    # Admin Prismatics
    "stephane_dardelet": "Sd2023!",

    # Etablissements
    "saint_dominique": "Vivre01!",
    "manon_cormier": "Vivre02!",
    "marie_durand": "Vivre03!",
    "villa_bontemps": "Vivre04!",
    "ehpad_belves": "Vivre05!",
    "richelot_lasse": "Vivre06!",
    "korian_le_chalet": "Vivre07!",
    "la_nougeraie": "Vivre08!",
    "les_terrasses_de_beausejour": "Vivre09!",
    "sherpa": "Vivre10!",
    "champdeniers": "Vivre11!",
    "saint_jacques": "Vivre12!",
    "la_favorite": "Vivre13!",
    "mfa_les_clarines": "Vivre14!",
    "mfa_clos_saint_francois": "Vivre15!",
    "mfa_cheveux_d_ange": "Vivre16!",
    "l_isle_aux_fleurs": "Vivre17!",
    "le_parc_du_bequet": "Vivre18!",
    "notre_dame_des_anges": "Vivre19!",
    "pont_saint_jean": "Vivre20!",
    "blanche_de_caastille": "Vivre21!",
    "clos_de_rochegude": "Vivre22!",
    "les_cedres_belves": "Vivre23!",
    "maison_de_blandine_limonest": "Vivre24!",
    "maison_de_blandine_blace": "Vivre25!",
    "maison_de_blandine_sassenage": "Vivre26!",
    "maison_de_blandine_amberieux": "Vivre27!",
    "flora_tristan": "Vivre28!",
    "maison_de_blandine_ampuis": "Vivre29!",
    "maison_de_blandine_rives": "Vivre30!",
    "louis_jouannin": "Vivre31!",
}

print("=" * 60)
print("HASHS A COPIER DANS app.py")
print("=" * 60)

for identifiant, mdp in mots_de_passe_en_clair.items():
    hash_genere = generate_password_hash(mdp)
    print(f"\nIdentifiant : {identifiant}")
    print(f"Mot de passe : {mdp}")
    print(f"Hash : \'{hash_genere}\'")