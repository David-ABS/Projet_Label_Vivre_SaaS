-- ============================================================
-- ID 12 - ANALYSE SQL : Calcul du NPS (Promoteurs - Détracteurs)
-- Projet CHU-01 : Label Vivre
-- Echelle adaptée : 4=Promoteur, 3=Passif, 1-2=Détracteur
-- NPS = % Promoteurs - % Détracteurs
-- ============================================================


-- ============================================================
-- REQUÊTE 1 : NPS GLOBAL (toutes questions de satisfaction)
-- ============================================================
SELECT
    COUNT(*)    AS total_reponses,

    SUM(CASE WHEN CAST("Score" AS FLOAT) = 4      THEN 1 ELSE 0 END) AS nb_promoteurs,
    SUM(CASE WHEN CAST("Score" AS FLOAT) = 3      THEN 1 ELSE 0 END) AS nb_passifs,
    SUM(CASE WHEN CAST("Score" AS FLOAT) IN (1,2) THEN 1 ELSE 0 END) AS nb_detracteurs,

    ROUND(100.0 * SUM(CASE WHEN CAST("Score" AS FLOAT) = 4      THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_promoteurs,
    ROUND(100.0 * SUM(CASE WHEN CAST("Score" AS FLOAT) = 3      THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_passifs,
    ROUND(100.0 * SUM(CASE WHEN CAST("Score" AS FLOAT) IN (1,2) THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_detracteurs,

    -- NPS FINAL
    ROUND(
        100.0 * SUM(CASE WHEN CAST("Score" AS FLOAT) = 4      THEN 1 ELSE 0 END) / COUNT(*) -
        100.0 * SUM(CASE WHEN CAST("Score" AS FLOAT) IN (1,2) THEN 1 ELSE 0 END) / COUNT(*),
    1) AS NPS_GLOBAL

FROM DONNEES_LIMESURVEY_NETTOYEES
WHERE CAST("Score" AS FLOAT) IN (1.0, 2.0, 3.0, 4.0)
  AND "Question_Formulation" NOT LIKE 'Durée%'
  AND "Question_Formulation" NOT LIKE 'Commentaire%'
  AND "Question_Formulation" NOT LIKE 'Temps%';


-- ============================================================
-- REQUÊTE 2 : NPS PAR QUESTION (classé du meilleur au pire)
-- ============================================================
SELECT
    "Question_Formulation"  AS question,
    COUNT(*)                AS total_reponses,

    SUM(CASE WHEN CAST("Score" AS FLOAT) = 4      THEN 1 ELSE 0 END) AS nb_promoteurs,
    SUM(CASE WHEN CAST("Score" AS FLOAT) = 3      THEN 1 ELSE 0 END) AS nb_passifs,
    SUM(CASE WHEN CAST("Score" AS FLOAT) IN (1,2) THEN 1 ELSE 0 END) AS nb_detracteurs,

    ROUND(
        100.0 * SUM(CASE WHEN CAST("Score" AS FLOAT) = 4      THEN 1 ELSE 0 END) / COUNT(*) -
        100.0 * SUM(CASE WHEN CAST("Score" AS FLOAT) IN (1,2) THEN 1 ELSE 0 END) / COUNT(*),
    1) AS NPS

FROM DONNEES_LIMESURVEY_NETTOYEES
WHERE CAST("Score" AS FLOAT) IN (1.0, 2.0, 3.0, 4.0)
  AND "Question_Formulation" NOT LIKE 'Durée%'
  AND "Question_Formulation" NOT LIKE 'Commentaire%'
  AND "Question_Formulation" NOT LIKE 'Temps%'
GROUP BY "Question_Formulation"
ORDER BY NPS DESC;


-- ============================================================
-- REQUÊTE 3 : TOP 5 MEILLEURES QUESTIONS (NPS le plus élevé)
-- ============================================================
SELECT
    "Question_Formulation"  AS question,
    COUNT(*)                AS total_reponses,
    ROUND(
        100.0 * SUM(CASE WHEN CAST("Score" AS FLOAT) = 4      THEN 1 ELSE 0 END) / COUNT(*) -
        100.0 * SUM(CASE WHEN CAST("Score" AS FLOAT) IN (1,2) THEN 1 ELSE 0 END) / COUNT(*),
    1) AS NPS

FROM DONNEES_LIMESURVEY_NETTOYEES
WHERE CAST("Score" AS FLOAT) IN (1.0, 2.0, 3.0, 4.0)
  AND "Question_Formulation" NOT LIKE 'Durée%'
  AND "Question_Formulation" NOT LIKE 'Commentaire%'
  AND "Question_Formulation" NOT LIKE 'Temps%'
GROUP BY "Question_Formulation"
ORDER BY NPS DESC
LIMIT 5;


-- ============================================================
-- REQUÊTE 4 : TOP 5 QUESTIONS PROBLÉMATIQUES (NPS le plus bas)
-- ============================================================
SELECT
    "Question_Formulation"  AS question,
    COUNT(*)                AS total_reponses,
    ROUND(
        100.0 * SUM(CASE WHEN CAST("Score" AS FLOAT) = 4      THEN 1 ELSE 0 END) / COUNT(*) -
        100.0 * SUM(CASE WHEN CAST("Score" AS FLOAT) IN (1,2) THEN 1 ELSE 0 END) / COUNT(*),
    1) AS NPS

FROM DONNEES_LIMESURVEY_NETTOYEES
WHERE CAST("Score" AS FLOAT) IN (1.0, 2.0, 3.0, 4.0)
  AND "Question_Formulation" NOT LIKE 'Durée%'
  AND "Question_Formulation" NOT LIKE 'Commentaire%'
  AND "Question_Formulation" NOT LIKE 'Temps%'
GROUP BY "Question_Formulation"
ORDER BY NPS ASC
LIMIT 5;