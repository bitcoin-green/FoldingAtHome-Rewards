/*
CREATE's three temp TABLE's
    + tmp_recent_snapshot
        (Holds the most recent snapshot taken of all workers)

    + tmp_previous_snapshot
        (Holds the 2nd last snapshot of all workers)

    + tmp_completed_work - [Holds all workers that have contributed]
        (Calculated using inner join with recent & previous;
         R.credits - P.credits
         R.worker_wus - P.worker_wus)

SELECT all workers that don't have 0 credit_diff and 0 wus_diff.

drop temp tables at the end
    * tmp_recent_snapshot
    * tmp_completed_work
    * tmp_completed_work
 */

DROP TABLE IF EXISTS tmp_recent_snapshot;
DROP TABLE IF EXISTS tmp_previous_snapshot;
DROP TABLE IF EXISTS tmp_completed_work;

CREATE TEMP TABLE tmp_recent_snapshot AS
SELECT DISTINCT ON (worker_wus) *
FROM fath_workers recent
WHERE recent.lastupdate =
        (SELECT MAX(lastupdate)
         FROM fath_workers)
ORDER BY recent.worker_wus DESC;

CREATE TEMP TABLE tmp_previous_snapshot AS
SELECT DISTINCT ON (worker_wus) *
FROM fath_workers previous
WHERE previous.lastupdate =
        (SELECT MAX(lastupdate)
         FROM fath_workers
         WHERE lastupdate <
                 (SELECT MAX(lastupdate)
                  FROM fath_workers) )
ORDER BY previous.worker_wus DESC;

CREATE TEMP TABLE tmp_completed_work AS
SELECT R.wus,
       R.worker_wus,
       R.credits,
       R.name,
       R.lastupdate,
       R.credits - P.credits AS credit_diff,
       R.worker_wus - P.worker_wus AS wus_diff
FROM tmp_recent_snapshot R
INNER JOIN tmp_previous_snapshot P ON R.folding_id = P.folding_id;

SELECT *
FROM tmp_completed_work
WHERE credit_diff != 0
    AND wus_diff != 0;