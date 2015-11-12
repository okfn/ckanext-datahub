-- Check table size
SELECT nspname || '.' || relname AS "relation",
    pg_size_pretty(pg_table_size(C.oid)) AS "size"
  FROM pg_class C                                                             
  LEFT JOIN pg_namespace N ON (N.oid = C.relnamespace)
  WHERE nspname NOT IN ('pg_catalog', 'information_schema')
  ORDER BY pg_relation_size(C.oid) DESC
  LIMIT 20;

-- Delete update user activities
DELETE FROM activity 
WHERE activity_type = 'changed user';

-- Delete activities from datasets no longer in the db
DELETE FROM activity_detail d 
WHERE d.activity_id IN (
    SELECT a.id 
    FROM activity a 
    WHERE NOT EXISTS (
        SELECT 1 
        FROM package p 
        WHERE a.object_id = p.id
    ) 
    AND a.activity_type IN (
        'new package', 'changed package', 'deleted package', 'follow dataset'
    )
);
DELETE FROM activity a 
WHERE NOT EXISTS (
    SELECT 1 
    FROM package p 
    WHERE a.object_id = p.id
) 
AND a.activity_type IN (
    'new package', 'changed package', 'deleted package', 'follow dataset'
);

-- Empty old unused queue tables
DELETE FROM celery_taskmeta;
DELETE FROM kombu_message;
DELETE FROM kombu_queue;


-- Delete drafts older than 6 months (mostly spam)
DELETE FROM package_role WHERE package_id IN (SELECT p.id FROM package p JOIN package_revision r ON p.id = r.id WHERE p.state = 'draft' AND r.revision_timestamp < '2015-03-01');
DELETE FROM resource_revision r WHERE r.resource_group_id IN (SELECT rg.id FROM resource_group rg WHERE rg.package_id IN (SELECT p.id FROM package p JOIN package_revision r ON p.id = r.id WHERE p.state = 'draft' AND r.revision_timestamp < '2015-03-01'));
DELETE FROM resource r WHERE r.resource_group_id IN (SELECT rg.id FROM resource_group rg WHERE rg.package_id IN (SELECT p.id FROM package p JOIN package_revision r ON p.id = r.id WHERE p.state = 'draft' AND r.revision_timestamp < '2015-03-01'));
DELETE FROM resource_group_revision rg WHERE rg.package_id IN (SELECT p.id FROM package p JOIN package_revision r ON p.id = r.id WHERE p.state = 'draft' AND r.revision_timestamp < '2015-03-01');
DELETE FROM resource_group rg WHERE rg.package_id IN (SELECT p.id FROM package p JOIN package_revision r ON p.id = r.id WHERE p.state = 'draft' AND r.revision_timestamp < '2015-03-01');
DELETE FROM package_tag_revision pt WHERE pt.package_id IN (SELECT p.id FROM package p JOIN package_revision r ON p.id = r.id WHERE p.state = 'draft' AND r.revision_timestamp < '2015-03-01');
DELETE FROM package_tag pt WHERE pt.package_id IN (SELECT p.id FROM package p JOIN package_revision r ON p.id = r.id WHERE p.state = 'draft' AND r.revision_timestamp < '2015-03-01');

DELETE FROM package_revision WHERE id IN (SELECT p.id FROM package p JOIN package_revision r ON p.id = r.id WHERE p.state = 'draft' AND r.revision_timestamp < '2015-03-01');
DELETE FROM package p WHERE NOT EXISTS (SELECT 1 FROM package_revision r WHERE r.id = p.id) AND p.state = 'draft';


-- Delete spam datatsets
-- 1. Draft datasets where name == title
DELETE FROM package_revision WHERE id IN (SELECT id FROM package WHERE name = title AND state = 'draft');
DELETE FROM package_role WHERE package_id IN (SELECT id FROM package WHERE name = title AND state = 'draft');
DELETE FROM resource_revision r WHERE r.resource_group_id IN (SELECT rg.id FROM resource_group rg WHERE rg.package_id IN (SELECT id FROM package WHERE name = title AND state = 'draft'));
DELETE FROM resource r WHERE r.resource_group_id IN (SELECT rg.id FROM resource_group rg WHERE rg.package_id IN (SELECT id FROM package WHERE name = title AND state = 'draft'));
DELETE FROM resource_group_revision rg WHERE rg.package_id IN (SELECT id FROM package WHERE name = title AND state = 'draft');
DELETE FROM resource_group rg WHERE rg.package_id IN (SELECT id FROM package WHERE name = title AND state = 'draft');
DELETE FROM package_tag_revision pt WHERE pt.package_id IN (SELECT id FROM package WHERE name = title AND state = 'draft');
DELETE FROM package_tag pt WHERE pt.package_id IN (SELECT id FROM package WHERE name = title AND state = 'draft');
DELETE FROM package WHERE name = title AND state = 'draft';

-- 1. Draft datasets with duplicated titles
DELETE FROM package_revision WHERE id IN (SELECT id FROM package WHERE title in (SELECT title FROM package WHERE state = 'draft' GROUP BY title HAVING COUNT(title) > 1 ORDER BY title));
DELETE FROM package_role WHERE package_id IN (SELECT id FROM package WHERE title in (SELECT title FROM package WHERE state = 'draft' GROUP BY title HAVING COUNT(title) > 1 ORDER BY title));
DELETE FROM resource_revision r WHERE r.resource_group_id IN (SELECT rg.id FROM resource_group rg WHERE rg.package_id IN (SELECT id FROM package WHERE title in (SELECT title FROM package WHERE state = 'draft' GROUP BY title HAVING COUNT(title) > 1 ORDER BY title)));
DELETE FROM resource r WHERE r.resource_group_id IN (SELECT rg.id FROM resource_group rg WHERE rg.package_id IN (SELECT id FROM package WHERE title in (SELECT title FROM package WHERE state = 'draft' GROUP BY title HAVING COUNT(title) > 1 ORDER BY title)));
DELETE FROM resource_group_revision rg WHERE rg.package_id IN (SELECT id FROM package WHERE title in (SELECT title FROM package WHERE state = 'draft' GROUP BY title HAVING COUNT(title) > 1 ORDER BY title));
DELETE FROM resource_group rg WHERE rg.package_id IN (SELECT id FROM package WHERE title in (SELECT title FROM package WHERE state = 'draft' GROUP BY title HAVING COUNT(title) > 1 ORDER BY title));
DELETE FROM package_tag_revision pt WHERE pt.package_id IN (SELECT id FROM package WHERE title in (SELECT title FROM package WHERE state = 'draft' GROUP BY title HAVING COUNT(title) > 1 ORDER BY title));
DELETE FROM package_tag pt WHERE pt.package_id IN (SELECT id FROM package WHERE title in (SELECT title FROM package WHERE state = 'draft' GROUP BY title HAVING COUNT(title) > 1 ORDER BY title));
DELETE FROM package_extra_revision pt WHERE pt.package_id IN (SELECT id FROM package WHERE title in (SELECT title FROM package WHERE state = 'draft' GROUP BY title HAVING COUNT(title) > 1 ORDER BY title));
DELETE FROM package_extra pt WHERE pt.package_id IN (SELECT id FROM package WHERE title in (SELECT title FROM package WHERE state = 'draft' GROUP BY title HAVING COUNT(title) > 1 ORDER BY title));

DELETE FROM package WHERE title IN (SELECT title FROM package WHERE state = 'draft' GROUP BY title HAVING COUNT(title) > 1 ORDER BY title);

-- Delete deleted datasets
DELETE FROM package_revision WHERE id IN (SELECT id FROM package WHERE state = 'deleted');
DELETE FROM package_role WHERE package_id IN (SELECT id FROM package WHERE state = 'deleted');
DELETE FROM resource_revision r WHERE r.resource_group_id IN (SELECT rg.id FROM resource_group rg WHERE rg.package_id IN (SELECT id FROM package WHERE state = 'deleted'));
DELETE FROM resource r WHERE r.resource_group_id IN (SELECT rg.id FROM resource_group rg WHERE rg.package_id IN (SELECT id FROM package WHERE state = 'deleted'));
DELETE FROM resource_group_revision rg WHERE rg.package_id IN (SELECT id FROM package WHERE state = 'deleted');
DELETE FROM resource_group rg WHERE rg.package_id IN (SELECT id FROM package WHERE state = 'deleted');
DELETE FROM package_tag_revision pt WHERE pt.package_id IN (SELECT id FROM package WHERE state = 'deleted');
DELETE FROM package_tag pt WHERE pt.package_id IN (SELECT id FROM package WHERE state = 'deleted');

DELETE FROM rating r WHERE r.package_id IN (SELECT id FROM package WHERE state = 'deleted');

DELETE FROM package_extra_revision e WHERE e.package_id IN (SELECT id FROM package WHERE state = 'deleted');
DELETE FROM package_extra e WHERE e.package_id IN (SELECT id FROM package WHERE state = 'deleted');

DELETE FROM package_relationship_revision r WHERE r.subject_package_id IN (SELECT id FROM package WHERE state = 'deleted');
DELETE FROM package_relationship_revision r WHERE r.object_package_id IN (SELECT id FROM package WHERE state = 'deleted');
DELETE FROM package_relationship r WHERE r.subject_package_id IN (SELECT id FROM package WHERE state = 'deleted');
DELETE FROM package_relationship r WHERE r.object_package_id IN (SELECT id FROM package WHERE state = 'deleted');

DELETE FROM related_dataset r WHERE r.dataset_id IN (SELECT id FROM package WHERE state = 'deleted');
DELETE FROM package WHERE state = 'deleted';




-- Vacuum to empty disk space
VACUUM FULL;

