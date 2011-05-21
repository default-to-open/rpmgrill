DROP DATABASE IF EXISTS rpmgrill;

CREATE DATABASE rpmgrill;
USE rpmgrill;

/*
** Different versions of rpmgrill, brewtap, whatever we want to call it
*/
CREATE TABLE tools (
       tool_id        INT AUTO_INCREMENT PRIMARY KEY,
       tool_name      VARCHAR(256),
       tool_version   VARCHAR(256)
) TYPE InnoDB;

/*
** RHEL5, RHEL6, etc
*/
CREATE TABLE variants (
       variant_id     INT AUTO_INCREMENT PRIMARY KEY,
       variant_name   VARCHAR(256)
) TYPE InnoDB;

INSERT INTO variants (variant_id, variant_name) VALUES (0, 'Unknown');
INSERT INTO variants (variant_id, variant_name) VALUES (3, 'RHEL3');
INSERT INTO variants (variant_id, variant_name) VALUES (4, 'RHEL4');
INSERT INTO variants (variant_id, variant_name) VALUES (5, 'RHEL5');
INSERT INTO variants (variant_id, variant_name) VALUES (6, 'RHEL6');
INSERT INTO variants (variant_id, variant_name) VALUES (7, 'RHEL7');
INSERT INTO variants (variant_id, variant_name) VALUES (8, 'RHEL8');

/* FIXME! Duplication of brew! */
CREATE TABLE brew_tags (
       brew_tag_id   INT AUTO_INCREMENT PRIMARY KEY,
       brew_tag_name VARCHAR(256)
) TYPE InnoDB;

/* FIXME: yet another userid table */
CREATE TABLE users (
       user_id       INT AUTO_INCREMENT PRIMARY KEY,
       user_name     VARCHAR(16)
) TYPE InnoDB;

/*
** Each row here is an N-V-R; the analyzed_by and _when fields may be used
** to identify which version of brewtap ran the analysis and when. This
** may be important to identify builds that need to be re-analyzed.
*/
CREATE TABLE runs (
       run_id           INT AUTO_INCREMENT PRIMARY KEY,
       analyzed_by      INT,          /* will be null during 'pending' */
       analyzed_when    DATETIME,

       package_name     VARCHAR(256) NOT NULL,
       package_version  VARCHAR(256) NOT NULL,
       package_release  VARCHAR(256) NOT NULL,
/*       variant_id       INT NOT NULL,*/       /* FIXME */
       brew_build_id    INT,                    /* FIXME: allow NULL? */
       brew_tag_id      INT NOT NULL,
       owner_id         INT NOT NULL,

       /* FIXME: Do we really need failed? */
       status           ENUM('queued','running','completed','failed') NOT NULL,

       INDEX (package_name),
       INDEX (package_name, package_version, package_release),

       FOREIGN KEY        (analyzed_by)
         REFERENCES tools (tool_id)
         ON DELETE RESTRICT,

/*       FOREIGN KEY           (variant_id)*/
/*         REFERENCES variants (variant_id)*/
/*         ON DELETE RESTRICT,*/

       FOREIGN KEY            (brew_tag_id)
         REFERENCES brew_tags (brew_tag_id)
         ON DELETE RESTRICT,

       FOREIGN KEY        (owner_id)
         REFERENCES users (user_id)
         ON DELETE RESTRICT
) TYPE InnoDB;

CREATE TABLE plugins (
       plugin_id     INT AUTO_INCREMENT PRIMARY KEY,
       plugin_name   VARCHAR(256) NOT NULL
) TYPE InnoDB;

CREATE TABLE codes (
       code_id       INT AUTO_INCREMENT PRIMARY KEY,
       code_name     VARCHAR(256) NOT NULL
) TYPE InnoDB;

CREATE TABLE tests_run (
       tests_run_id    INT AUTO_INCREMENT PRIMARY KEY,
       run_id          INT NOT NULL,
       plugin_id       INT NOT NULL,
       test_order      INT NOT NULL,
       test_status     ENUM ('NOTRUN', 'completed', 'failed'),
       fail_message    VARCHAR(256),

       FOREIGN KEY       (run_id)
         REFERENCES runs (run_id)
         ON DELETE RESTRICT,
       FOREIGN KEY          (plugin_id)
         REFERENCES plugins (plugin_id)
         ON DELETE RESTRICT
) TYPE InnoDB;

CREATE TABLE results (
       result_id     INT AUTO_INCREMENT PRIMARY KEY,
       tests_run_id  INT NOT NULL,
       code_id       INT,

       diagnostic          VARCHAR(256) NOT NULL,     /* FIXME: maybe TEXT? */
       context_path        VARCHAR(256),
       context_lineno      VARCHAR(256),
       context_subcontext  VARCHAR(256),
       context_excerpt     VARCHAR(2048),

       FOREIGN KEY            (tests_run_id)
         REFERENCES tests_run (tests_run_id)
         ON DELETE RESTRICT
) TYPE InnoDB;

CREATE TABLE schema_version (
       applied_ts           TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
       migration_code       VARCHAR(128) PRIMARY KEY,
       description          VARCHAR(256)
) TYPE InnoDB;

INSERT INTO schema_version (migration_code, description)
       VALUES ('001', 'Initial database creation');
