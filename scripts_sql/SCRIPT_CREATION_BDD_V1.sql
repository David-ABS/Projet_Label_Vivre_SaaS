-- Création des tables de référence (sans clés étrangères)
CREATE TABLE UTILISATEUR (
    Id_utilisateur INT PRIMARY KEY,
    Nom VARCHAR(100) NOT NULL,
    Email VARCHAR(150) NOT NULL,
    Role VARCHAR(50) NOT NULL
);

CREATE TABLE GROUPE (
    Id_groupe INT PRIMARY KEY,
    Nom_groupe VARCHAR(100) NOT NULL
);

CREATE TABLE TYPE_STRUCTURE (
    Id_type_struct INT PRIMARY KEY,
    Libelle_type VARCHAR(50) NOT NULL
);

CREATE TABLE TYPE_REPONDANT (
    Id_type_rep INT PRIMARY KEY,
    Libelle_public VARCHAR(50) NOT NULL
);

CREATE TABLE QUESTIONNAIRE (
    Id_questionnaire INT PRIMARY KEY,
    Version VARCHAR(10) NOT NULL,
    Periode_validite VARCHAR(50)
);

CREATE TABLE QUESTION (
    Code_question VARCHAR(50) PRIMARY KEY,
    Code_question_precedente VARCHAR(50),
    FOREIGN KEY (Code_question_precedente) REFERENCES QUESTION(Code_question)
);

-- Création des tables avec clés étrangères
CREATE TABLE STRUCTURE (
    Id_structure INT PRIMARY KEY,
    Nom VARCHAR(150) NOT NULL,
    Departement VARCHAR(3),
    Region VARCHAR(50),
    Statut VARCHAR(50) NOT NULL,
    Nb_places INT,
    FINESS VARCHAR(9),
    Id_type_struct INT NOT NULL,
    Id_groupe INT,
    Id_utilisateur INT,
    FOREIGN KEY (Id_type_struct) REFERENCES TYPE_STRUCTURE(Id_type_struct),
    FOREIGN KEY (Id_groupe) REFERENCES GROUPE(Id_groupe),
    FOREIGN KEY (Id_utilisateur) REFERENCES UTILISATEUR(Id_utilisateur)
);

CREATE TABLE CAMPAGNE (
    Id_campagne INT PRIMARY KEY,
    Annee INT NOT NULL,
    Mois INT NOT NULL,
    Date_debut DATE NOT NULL,
    Date_fin DATE,
    Statut VARCHAR(20) NOT NULL,
    Nb_Resident INT,
    Nb_proches INT,
    Nb_Salarie INT,
    GMP DECIMAL(5,2),
    PMP DECIMAL(5,2),
    Taux_OCCUP DECIMAL(5,2),
    Taux_ENCAD DECIMAL(5,2),
    TURNOVER DECIMAL(5,2),
    Id_structure INT NOT NULL,
    FOREIGN KEY (Id_structure) REFERENCES STRUCTURE(Id_structure)
);

CREATE TABLE LABELLISATION (
    Id_label INT PRIMARY KEY,
    Date_obtention DATE NOT NULL,
    Score_residents DECIMAL(4,2),
    Score_proches DECIMAL(4,2),
    Score_salaries DECIMAL(4,2),
    Id_campagne INT NOT NULL UNIQUE,
    FOREIGN KEY (Id_campagne) REFERENCES CAMPAGNE(Id_campagne)
);

CREATE TABLE VERSION_QUESTION (
    Id_version_q INT PRIMARY KEY,
    Formulation TEXT NOT NULL,
    Date_validite DATE,
    Indicateur_principal BOOLEAN NOT NULL,
    Critere_essentiel BOOLEAN NOT NULL,
    Active_Restitution BOOLEAN NOT NULL,
    Code_question VARCHAR(50) NOT NULL,
    FOREIGN KEY (Code_question) REFERENCES QUESTION(Code_question)
);

-- Création des tables d'associations (Les Ternaires et liaisons N-M)
CREATE TABLE Cible (
    Id_type_struct INT NOT NULL,
    Id_type_rep INT NOT NULL,
    Id_questionnaire INT NOT NULL,
    PRIMARY KEY (Id_type_struct, Id_type_rep, Id_questionnaire),
    FOREIGN KEY (Id_type_struct) REFERENCES TYPE_STRUCTURE(Id_type_struct),
    FOREIGN KEY (Id_type_rep) REFERENCES TYPE_REPONDANT(Id_type_rep),
    FOREIGN KEY (Id_questionnaire) REFERENCES QUESTIONNAIRE(Id_questionnaire)
);

CREATE TABLE Contient (
    Id_questionnaire INT NOT NULL,
    Id_version_q INT NOT NULL,
    PRIMARY KEY (Id_questionnaire, Id_version_q),
    FOREIGN KEY (Id_questionnaire) REFERENCES QUESTIONNAIRE(Id_questionnaire),
    FOREIGN KEY (Id_version_q) REFERENCES VERSION_QUESTION(Id_version_q)
);

CREATE TABLE Mobilise (
    Id_campagne INT NOT NULL,
    Id_questionnaire INT NOT NULL,
    PRIMARY KEY (Id_campagne, Id_questionnaire),
    FOREIGN KEY (Id_campagne) REFERENCES CAMPAGNE(Id_campagne),
    FOREIGN KEY (Id_questionnaire) REFERENCES QUESTIONNAIRE(Id_questionnaire)
);

-- Création des tables de réponses (Les données LimeSurvey)
CREATE TABLE REPONDANT (
    Id_repondant_tech VARCHAR(50) PRIMARY KEY,
    Id_questionnaire INT NOT NULL,
    Id_campagne INT NOT NULL,
    FOREIGN KEY (Id_questionnaire) REFERENCES QUESTIONNAIRE(Id_questionnaire),
    FOREIGN KEY (Id_campagne) REFERENCES CAMPAGNE(Id_campagne)
);

CREATE TABLE REPONSE (
    Id_reponse INT PRIMARY KEY,
    Valeur_brute TEXT,
    Horodatage DATETIME NOT NULL,
    Id_version_q INT NOT NULL,
    Id_repondant_tech VARCHAR(50) NOT NULL,
    Id_reponse_liee INT, 
    FOREIGN KEY (Id_version_q) REFERENCES VERSION_QUESTION(Id_version_q),
    FOREIGN KEY (Id_repondant_tech) REFERENCES REPONDANT(Id_repondant_tech),
    FOREIGN KEY (Id_reponse_liee) REFERENCES REPONSE(Id_reponse)
);