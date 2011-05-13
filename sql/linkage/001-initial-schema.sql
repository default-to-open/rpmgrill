DROP DATABASE IF EXISTS linkage;

CREATE DATABASE linkage;
USE linkage;

/*
** Each row here is an N-V-R; the analyzed_by and _when fields may be used
** to identify which version of brewtap ran the analysis and when. This
** may be important to identify builds that need to be re-analyzed.
*/
CREATE TABLE packages (
       analyzed_when    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
       analyzed_by      VARCHAR(256),
       package_id       INT AUTO_INCREMENT PRIMARY KEY,
       package_name     VARCHAR(256) NOT NULL,
       package_version  VARCHAR(256) NOT NULL,
       package_release  VARCHAR(256) NOT NULL,

       INDEX (package_name),
       INDEX (package_name, package_version, package_release)
);

/*
** The table you're interested in. This gets one entry for each library.
*/
CREATE TABLE linkage_xref (
       package_id      INT NOT NULL,
       subpackage      VARCHAR(256) NOT NULL,
       arch            VARCHAR(128) NOT NULL,
       libname         VARCHAR(256) NOT NULL,   /* This is what you want */
       filepath        VARCHAR(256) NOT NULL,

       FOREIGN KEY           (package_id)
         REFERENCES packages (package_id)
         ON DELETE RESTRICT,

       INDEX (libname)
);


/*
** For future maintainability.
*/
CREATE TABLE schema_version (
       applied_ts           TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
       migration_code       VARCHAR(128) PRIMARY KEY,
       description          VARCHAR(256)
);

INSERT INTO schema_version (migration_code, description)
       VALUES ('001', 'Initial database creation');
