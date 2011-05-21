ALTER TABLE runs CHANGE status state ENUM ('queued','running','completed','failed') NOT NULL;

INSERT INTO schema_version (migration_code, description)
       VALUES ('003', 'Rename "status" to "state"');
