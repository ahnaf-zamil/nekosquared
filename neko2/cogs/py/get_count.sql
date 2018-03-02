SELECT
  (SELECT COUNT(*) FROM py_cog.modules),
  (SELECT COUNT(*) FROM py_cog.members);