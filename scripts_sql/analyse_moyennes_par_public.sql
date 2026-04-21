-- ============================================================
-- ID 13 - ANALYSE SQL : Moyennes par Public
-- Projet CHU-01 : Label Vivre
-- Publics : Résidents, Proches, Équipe
-- ============================================================


-- ============================================================
-- REQUÊTE 1 : SCORE MOYEN GLOBAL PAR PUBLIC
-- ============================================================
SELECT
    CASE
        WHEN "Question_Formulation" LIKE '%résident%'
          OR "Question_Formulation" LIKE '%habitant%'  THEN 'Résidents'
        WHEN "Question_Formulation" LIKE '%proche%'    THEN 'Proches'
        WHEN "Question_Formulation" LIKE '%équipe%'
          OR "Question_Formulation" LIKE '%salarié%'   THEN 'Équipe'
        ELSE 'Autre'
    END AS public,

    COUNT(*)                                            AS nb_reponses,
    COUNT(DISTINCT "ID de la réponse")                  AS nb_repondants,
    ROUND(AVG(CAST("Score" AS FLOAT)), 2)               AS score_moyen,
    ROUND(MIN(CAST("Score" AS FLOAT)), 2)               AS score_min,
    ROUND(MAX(CAST("Score" AS FLOAT)), 2)               AS score_max

FROM DONNEES_LIMESURVEY_NETTOYEES
WHERE CAST("Score" AS FLOAT) IN (1.0, 2.0, 3.0, 4.0)
  AND "Question_Formulation" NOT LIKE 'Durée%'
  AND "Question_Formulation" NOT LIKE 'Commentaire%'
  AND "Question_Formulation" NOT LIKE 'Temps%'
GROUP BY public
ORDER BY score_moyen DESC;


-- ============================================================
-- REQUÊTE 2 : SCORE MOYEN PAR QUESTION ET PAR PUBLIC
-- ============================================================
SELECT
    CASE
        WHEN "Question_Formulation" LIKE '%résident%'
          OR "Question_Formulation" LIKE '%habitant%'  THEN 'Résidents'
        WHEN "Question_Formulation" LIKE '%proche%'    THEN 'Proches'
        WHEN "Question_Formulation" LIKE '%équipe%'
          OR "Question_Formulation" LIKE '%salarié%'   THEN 'Équipe'
        ELSE 'Autre'
    END AS public,

    "Question_Formulation"                              AS question,
    COUNT(*)                                            AS nb_reponses,
    ROUND(AVG(CAST("Score" AS FLOAT)), 2)               AS score_moyen

FROM DONNEES_LIMESURVEY_NETTOYEES
WHERE CAST("Score" AS FLOAT) IN (1.0, 2.0, 3.0, 4.0)
  AND "Question_Formulation" NOT LIKE 'Durée%'
  AND "Question_Formulation" NOT LIKE 'Commentaire%'
  AND "Question_Formulation" NOT LIKE 'Temps%'
GROUP BY public, "Question_Formulation"
ORDER BY public, score_moyen DESC;


-- ============================================================
-- REQUÊTE 3 : TOP 5 QUESTIONS PAR PUBLIC (les mieux notées)
-- ============================================================

-- Résidents
SELECT 'Résidents' AS public, "Question_Formulation" AS question,
    ROUND(AVG(CAST("Score" AS FLOAT)), 2) AS score_moyen,
    COUNT(*) AS nb_reponses
FROM DONNEES_LIMESURVEY_NETTOYEES
WHERE CAST("Score" AS FLOAT) IN (1.0, 2.0, 3.0, 4.0)
  AND ("Question_Formulation" LIKE '%résident%' OR "Question_Formulation" LIKE '%habitant%')
  AND "Question_Formulation" NOT LIKE 'Durée%'
GROUP BY "Question_Formulation"
ORDER BY score_moyen DESC LIMIT 5;

-- Proches
SELECT 'Proches' AS public, "Question_Formulation" AS question,
    ROUND(AVG(CAST("Score" AS FLOAT)), 2) AS score_moyen,
    COUNT(*) AS nb_reponses
FROM DONNEES_LIMESURVEY_NETTOYEES
WHERE CAST("Score" AS FLOAT) IN (1.0, 2.0, 3.0, 4.0)
  AND "Question_Formulation" LIKE '%proche%'
  AND "Question_Formulation" NOT LIKE 'Durée%'
GROUP BY "Question_Formulation"
ORDER BY score_moyen DESC LIMIT 5;

-- Équipe
SELECT 'Équipe' AS public, "Question_Formulation" AS question,
    ROUND(AVG(CAST("Score" AS FLOAT)), 2) AS score_moyen,
    COUNT(*) AS nb_reponses
FROM DONNEES_LIMESURVEY_NETTOYEES
WHERE CAST("Score" AS FLOAT) IN (1.0, 2.0, 3.0, 4.0)
  AND ("Question_Formulation" LIKE '%équipe%' OR "Question_Formulation" LIKE '%salarié%')
  AND "Question_Formulation" NOT LIKE 'Durée%'
GROUP BY "Question_Formulation"
ORDER BY score_moyen DESC LIMIT 5;


-- ============================================================
-- REQUÊTE 4 : COMPARAISON DES 3 PUBLICS (vue synthétique)
-- ============================================================
SELECT
    ROUND(AVG(CASE WHEN "Question_Formulation" LIKE '%résident%'
                     OR "Question_Formulation" LIKE '%habitant%'
                   THEN CAST("Score" AS FLOAT) END), 2) AS score_moyen_residents,

    ROUND(AVG(CASE WHEN "Question_Formulation" LIKE '%proche%'
                   THEN CAST("Score" AS FLOAT) END), 2) AS score_moyen_proches,

    ROUND(AVG(CASE WHEN "Question_Formulation" LIKE '%équipe%'
                     OR "Question_Formulation" LIKE '%salarié%'
                   THEN CAST("Score" AS FLOAT) END), 2) AS score_moyen_equipe

FROM DONNEES_LIMESURVEY_NETTOYEES
WHERE CAST("Score" AS FLOAT) IN (1.0, 2.0, 3.0, 4.0)
  AND "Question_Formulation" NOT LIKE 'Durée%'
  AND "Question_Formulation" NOT LIKE 'Commentaire%';