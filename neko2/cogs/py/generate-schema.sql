

-- Generates the schema and base table structure. This will remove the existing
-- schema if it exists. This is performed as a single transaction. It will
-- either finish successfully, or just fail completely and not alter anything.
BEGIN TRANSACTION ISOLATION LEVEL READ COMMITTED READ WRITE;
    -- Drop existing data.
    DROP SCHEMA IF EXISTS python_doc CASCADE;
    CREATE SCHEMA python_doc;
    SET search_path TO python_doc;

    -- Create the index table.
    CREATE TABLE module_index (
        PRIMARY KEY (module_num),
        module_num  SMALLSERIAL NOT NULL UNIQUE,

        -- Qualified module name.
        module_name VARCHAR(20) NOT NULL UNIQUE,

        -- Table we refer to.
        tbl_name    VARCHAR(20) NOT NULL UNIQUE,

        -- Hash of the module. Used to detect changes. Assumes BLAKE2B is used,
        -- which produces 512-bit hashes (64 bytes).
        hash_code   BYTEA       NOT NULL
    );

    -- Ensure that the extension for fuzzy string matching is installed.
    CREATE EXTENSION IF NOT EXISTS pg_trgm SCHEMA python_doc;

    /**
     * Generates a random string of length characters, before returning it.
     * We use this as a way to provide unique table names.
     */
    CREATE OR REPLACE FUNCTION random_string(char_count INTEGER)
        RETURNS TEXT
        AS $random_string$
        DECLARE
            valid_chars TEXT[]  := '{0,1,2,3,4,5,6,7,8,9,A,B,C,D,E,F,G,H,I,' ||
                                   'J,K,L,M,N,O,P,Q,R,S,T,U,V,W,X,Y,Z}';
            result      TEXT    := '';
            i           INTEGER := 0;
        BEGIN
            SET search_path TO python_doc;
            IF char_count < 0 THEN
                RAISE EXCEPTION 'Cannot generate less than zero characters.';
            END IF;

            WHILE TRUE LOOP
                -- Generate random identifier.
                FOR i IN 1..char_count LOOP
                    result := result || valid_chars[1 + RANDOM()
                              * (array_length(valid_chars, 1) - 1)];
                END LOOP;

                -- Ensure the table does not already exist.
                PERFORM TRUE FROM module_index WHERE tbl_name = result;
                -- Very unlikely to ever happen, but if it does, it saves
                -- the headache.
                IF found OR result = 'module_index' THEN
                    CONTINUE;
                ELSE
                    RETURN result;
                END IF;
           END LOOP;
           RETURN result;
        END;
        $random_string$
        LANGUAGE plpgsql;

    /**
     * Creates a new table dynamically for the given module.
     * @param module_name - the module name to make a table for.
     * @param hash_code - the module hash code.
     * @returns the table name that was created. This name is
     */
    CREATE OR REPLACE FUNCTION create_tbl(new_mod_name  TEXT,
                                          new_hash_code BYTEA)
        RETURNS TEXT
        AS $create_tbl$
        DECLARE
            new_table_name  TEXT   := python_doc.random_string(10::INTEGER);
        BEGIN
            SET search_path TO python_doc;

            -- Dynamically generate our table.
            EXECUTE
                'CREATE TABLE "' || new_table_name || '" ( '                  ||
                '    PRIMARY KEY(member_num), '                               ||
                '    member_num     SERIAL    NOT NULL UNIQUE, '              ||
                '    member_name    TEXT      NOT NULL, '                     ||
                '    fq_member_name TEXT      NOT NULL '                      ||
                '                             CONSTRAINT member_in_fqn '      ||
                '                             CHECK ( '                       ||
                '                                 fq_member_name LIKE '       ||
                '                                 concat(''%'', member_name) '||
                '                             ), '                            ||
                '    meta           TEXT      NOT NULL '                      ||
                ')';

            INSERT INTO module_index (module_name, tbl_name, hash_code)
                VALUES (new_mod_name, new_table_name, new_hash_code);

            RETURN new_table_name;
        END;
        $create_tbl$
        LANGUAGE plpgsql;


    /**
     * Adds a new attribute record to the given table.
     * @param tbl_name - the table name.
     * @param mbr_name - the member's name.
     * @param fq_mbr_name - the fully qualified member's name.
     * @param meta - the JSON metadata.
     * @returns the primary key of the record added.
     */
    CREATE OR REPLACE FUNCTION add_attr(tbl_name    TEXT,
                                        mbr_name    TEXT,
                                        fq_mbr_name TEXT,
                                        meta        TEXT)
        RETURNS SETOF INTEGER
        AS $add_attr$
        DECLARE
        BEGIN
            SET search_path TO python_doc;
            RETURN QUERY EXECUTE
                    'INSERT INTO "' || tbl_name || '" (member_name, '    ||
                    '        fq_member_name, meta)'                      ||
                    '   VALUES ($1, $2, $3)'                             ||
                    '   RETURNING member_num;'
                USING mbr_name, fq_mbr_name, meta;
        END;
        $add_attr$
        LANGUAGE plpgsql;


    /**
     * Returns the view of a given table name.
     * @param tbl_name - name of the table.
     * @returns a table.
     */
    CREATE OR REPLACE FUNCTION get_table(tbl_name TEXT)
        RETURNS TABLE(
            member_num     INTEGER,
            member_name    TEXT,
            fq_member_name TEXT,
            meta           TEXT
        ) AS $get_table$
        BEGIN
            SET search_path TO python_doc;
            RETURN QUERY EXECUTE 'SELECT * FROM "' || tbl_name || '";';
        END;
        $get_table$
        LANGUAGE plpgsql;

    /*
    https://www.rdegges.com/2013/easy-fuzzy-text-searching-with-postgresql/
    */

    /**
     * Looks up a given module and attribute, returning the matches ordered by
     * the closest string first.
     *
     * @param module - the module to look up the attribute table for.
     * @param attr - the attribute to look up using fuzzy string matching.
     * @returns a table of the top results.
     */
    CREATE OR REPLACE FUNCTION fuzzy_search_for(module   TEXT,
                                                attr     TEXT)
        RETURNS TABLE (
            member_num       INTEGER,
            member_name      TEXT,
            fq_member_name   TEXT,
            meta             TEXT
        )
        AS $fuzzy_search_for$
        DECLARE
            _tbl_name      TEXT;
        BEGIN
            SET search_path TO python_doc;

            -- Practically return anything.
            PERFORM set_limit(0.2);

            -- Get table name
            SELECT tbl_name INTO STRICT _tbl_name
                FROM module_index
                WHERE module_name ILIKE module;

            -- Fuzzy search
            IF TRIM(attr) = '' THEN
                RETURN QUERY SELECT * FROM get_table(_tbl_name) LIMIT 500;
            ELSE
		RETURN QUERY
                    SELECT
                        *
                    FROM get_table(_tbl_name) as tbl
                    WHERE tbl.fq_member_name % attr
                    ORDER BY
                        char_length(tbl.fq_member_name) ASC,
                        (SELECT CASE
                            WHEN tbl.member_name ILIKE '__%' THEN 4
                            WHEN tbl.fq_member_name ILIKE '%.__%' THEN 3
                            WHEN tbl.member_name ILIKE '_%' THEN 2
                            WHEN tbl.fq_member_name ILIKE '%._%' Then 1
                            ELSE 0
			END),
                        similarity(tbl.fq_member_name, attr) DESC,
	    		tbl.fq_member_name ASC;
	    END IF;
        END;
        $fuzzy_search_for$
        LANGUAGE plpgsql;
COMMIT TRANSACTION;
