SELECT op.registro_operadora,
       op.cnpj,
       op.razao_social,
       op.nome_fantasia
FROM dim_operadoras op
order by razao_social asc