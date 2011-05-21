ALTER TABLE runs CHANGE brew_task_id brew_build_id INT;

INSERT INTO schema_version (migration_code, description)
       VALUES ('002', 'Store brew BUILD id, not task id');
