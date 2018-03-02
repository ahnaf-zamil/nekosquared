INSERT INTO py_cog.modules (module_name, module_hash)
  VALUES (($1), ($2))
  RETURNING pk;