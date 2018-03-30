-- SQL Query
SELECT hash_code FROM python_doc.module_index WHERE module_name = ($1) LIMIT 1;