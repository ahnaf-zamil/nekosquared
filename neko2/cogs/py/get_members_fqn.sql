SELECT * FROM py_cog.members
WHERE concat('%', fq_member_name, '%') LIKE ($1) OR
  fq_member_name LIKE concat('%', ($1), '%');