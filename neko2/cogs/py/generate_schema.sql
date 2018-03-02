-- Generates the schema to hold documentation cache information. This also
-- generates the base tables and indexes. This will always recreate the schema.
BEGIN;
  DROP SCHEMA IF EXISTS py_cog CASCADE;
  CREATE SCHEMA IF NOT EXISTS py_cog;
  SET search_path TO py_cog;

  -- Holds the mappings to the desired records.
  CREATE TABLE IF NOT EXISTS modules (
    -- Primary key.
    pk              SERIAL      PRIMARY KEY NOT NULL UNIQUE,

    -- Python module name that is being indexed.
    module_name     TEXT        NOT NULL UNIQUE,

    -- Calculated hash of the module. This is dependant on the algorithm
    -- currently being used in code.
    module_hash     TEXT        NOT NULL,

    -- Last cached
    last_cached     TIMESTAMP   NOT NULL DEFAULT now()
  );


  -- Holds all members of all cached attributes from all modules. Indexed by the
  -- module primary key.
  CREATE TABLE IF NOT EXISTS members (
    -- Primary key.
    pk              SERIAL      PRIMARY KEY NOT NULL UNIQUE,

    -- Representative module
    module_pk       SERIAL      NOT NULL,

    -- Member name itself
    member_name     TEXT        NOT NULL,

    -- Fully qualified member name. This MUST end with the member name to be
    -- valid.
    fq_member_name  TEXT        NOT NULL CONSTRAINT valid_fq_member_name CHECK (
                                  fq_member_name LIKE concat('%', member_name)
                                ),

    -- Holds a JSON object of any meta data.
    metadata        TEXT        NOT NULL,

    FOREIGN KEY (module_pk) REFERENCES modules ON DELETE CASCADE
  );


  -- Should speed up access.
  CREATE INDEX IF NOT EXISTS module_pk_index ON members(module_pk);
  CREATE INDEX IF NOT EXISTS member_name_index ON members(lower(member_name));
  CREATE INDEX IF NOT EXISTS fq_mn_index ON members(lower(fq_member_name));
COMMIT;