/*
CREATE three temp TABLE's
    + tmp_recent_snapshot
        (Holds the most recent snapshot taken of all workers)

    + tmp_previous_snapshot
        (Holds the 2nd last snapshot of all workers)

    + tmp_completed_work - holds all workers that have contributed.
        Calculated using inner join with recent & previous;
        R.credits - P.credits
        R.worker_wus - P.worker_wus

    SELECT all workers that have completed work units since the last pay-out

    DROP all temp tables created.
    [
    'tmp_recent_snapshot',
    'tmp_completed_work',
    'tmp_completed_work'
    ]
 */

DROP TABLE IF EXISTS tmp_recent_snapshot;
DROP TABLE IF EXISTS tmp_previous_snapshot;
DROP TABLE IF EXISTS tmp_completed_work;

CREATE TEMP TABLE tmp_recent_snapshot AS
SELECT worker.*
from fath_workers worker
where worker.lastupdate = (
    SELECT DISTINCT ON (recent.lastupdate) recent.lastupdate
    FROM fath_workers recent
    ORDER BY recent.lastupdate DESC
    LIMIT 1
    )
ORDER BY worker.name DESC;

CREATE TEMP TABLE tmp_previous_snapshot AS
SELECT worker.*
from fath_workers worker
where worker.lastupdate = (
    SELECT DISTINCT ON (previous.lastupdate) previous.lastupdate
    FROM fath_workers previous
    ORDER BY previous.lastupdate DESC
    OFFSET 1
    LIMIT 1
    )
ORDER BY worker.name DESC;

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