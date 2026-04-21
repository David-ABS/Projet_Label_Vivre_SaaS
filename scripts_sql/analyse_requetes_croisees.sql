-- ============================================================
-- ID 14 - ANALYSE SQL : Requêtes Croisées
-- Projet CHU-01 : Label Vivre
-- Croisements : Genre x Age x Score
-- ============================================================


-- ============================================================
-- REQUÊTE 1 : SCORE MOYEN PAR GENRE
-- ============================================================
SELECT
    age."Valeur_Brute"                              AS genre,
    COUNT(DISTINCT rep."ID de la réponse")          AS nb_repondants,
    ROUND(AVG(CAST(rep."Score" AS FLOAT)), 2)       AS score_moyen

FROM DONNEES_LIMESURVEY_NETTOYEES rep
JOIN DONNEES_LIMESURVEY_NETTOYEES age
    ON rep."ID de la réponse" = age."ID de la réponse"
    AND age."Question_Formulation" = 'Vous êtes ... ?'

WHERE CAST(rep."Score" AS FLOAT) IN (1.0, 2.0, 3.0, 4.0)
  AND rep."Question_Formulation" NOT LIKE 'Durée%'
  AND rep."Question_Formulation" NOT LIKE 'Commentaire%'
  AND rep."Question_Formulation" NOT LIKE 'Temps%'
  AND rep."Question_Formulation" != 'Vous êtes ... ?'

GROUP BY genre
ORDER BY score_moyen DESC;


-- ============================================================
-- REQUÊTE 2 : SCORE MOYEN PAR TRANCHE D'ÂGE
-- ============================================================
SELECT
    age."Valeur_Brute"                              AS tranche_age,
    COUNT(DISTINCT rep."ID de la réponse")          AS nb_repondants,
    ROUND(AVG(CAST(rep."Score" AS FLOAT)), 2)       AS score_moyen

FROM DONNEES_LIMESURVEY_NETTOYEES rep
JOIN DONNEES_LIMESURVEY_NETTOYEES age
    ON rep."ID de la réponse" = age."ID de la réponse"
    AND age."Question_Formulation" = 'Quel âge avez-vous ?'

WHERE CAST(rep."Score" AS FLOAT) IN (1.0, 2.0, 3.0, 4.0)
  AND rep."Question_Formulation" NOT LIKE 'Durée%'
  AND rep."Question_Formulation" NOT LIKE 'Commentaire%'
  AND rep."Question_Formulation" NOT LIKE 'Temps%'
  AND rep."Question_Formulation" != 'Quel âge avez-vous ?'

GROUP BY tranche_age
ORDER BY score_moyen DESC;


-- ============================================================
-- REQUÊTE 3 : CROISEMENT GENRE x ÂGE (ex: Femmes >80 ans)
-- ============================================================
SELECT
    genre."Valeur_Brute"                            AS genre,
    age."Valeur_Brute"                              AS tranche_age,
    COUNT(DISTINCT rep."ID de la réponse")          AS nb_repondants,
    ROUND(AVG(CAST(rep."Score" AS FLOAT)), 2)       AS score_moyen

FROM DONNEES_LIMESURVEY_NETTOYEES rep
JOIN DONNEES_LIMESURVEY_NETTOYEES genre
    ON rep."ID de la réponse" = genre."ID de la réponse"
    AND genre."Question_Formulation" = 'Vous êtes ... ?'
JOIN DONNEES_LIMESURVEY_NETTOYEES age
    ON rep."ID de la réponse" = age."ID de la réponse"
    AND age."Question_Formulation" = 'Quel âge avez-vous ?'

WHERE CAST(rep."Score" AS FLOAT) IN (1.0, 2.0, 3.0, 4.0)
  AND rep."Question_Formulation" NOT LIKE 'Durée%'
  AND rep."Question_Formulation" NOT LIKE 'Commentaire%'
  AND rep."Question_Formulation" NOT LIKE 'Temps%'
  AND rep."Question_Formulation" != 'Vous êtes ... ?'
  AND rep."Question_Formulation" != 'Quel âge avez-vous ?'

GROUP BY genre, tranche_age
ORDER BY genre, score_moyen DESC;


-- ============================================================
-- REQUÊTE 4 : FOCUS Femmes de 80 ans et plus
-- (exemple cité dans le cahier des charges)
-- ============================================================
SELECT
    genre."Valeur_Brute"                            AS genre,
    age."Valeur_Brute"                              AS tranche_age,
    rep."Question_Formulation"                      AS question,
    COUNT(*)                                        AS nb_reponses,
    ROUND(AVG(CAST(rep."Score" AS FLOAT)), 2)       AS score_moyen

FROM DONNEES_LIMESURVEY_NETTOYEES rep
JOIN DONNEES_LIMESURVEY_NETTOYEES genre
    ON rep."ID de la réponse" = genre."ID de la réponse"
    AND genre."Question_Formulation" = 'Vous êtes ... ?'
    AND genre."Valeur_Brute" = 'Une femme'
JOIN DONNEES_LIMESURVEY_NETTOYEES age
    ON rep."ID de la réponse" = age."ID de la réponse"
    AND age."Question_Formulation" = 'Quel âge avez-vous ?'
    AND age."Valeur_Brute" IN ('De 80 à 84 ans', 'De 85 à 89 ans', '90 ans et plus', 'De 90 à 94 ans', '95 ans ou plus')

WHERE CAST(rep."Score" AS FLOAT) IN (1.0, 2.0, 3.0, 4.0)
  AND rep."Question_Formulation" NOT LIKE 'Durée%'
  AND rep."Question_Formulation" NOT LIKE 'Commentaire%'
  AND rep."Question_Formulation" != 'Vous êtes ... ?'
  AND rep."Question_Formulation" != 'Quel âge avez-vous ?'

GROUP BY rep."Question_Formulation"
ORDER BY score_moyen DESC;