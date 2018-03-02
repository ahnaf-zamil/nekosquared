SELECT DISTINCT pk, module_name FROM (
  SELECT *
  FROM py_cog.modules
  WHERE module_name ILIKE ($1)
  UNION DISTINCT
  SELECT *
  FROM py_cog.modules
  WHERE concat('%', module_name, '%') ILIKE concat('%', ($1) :: TEXT, '%')
) AS result LIMIT 1;