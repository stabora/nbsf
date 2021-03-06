SELECT
	N.*,
	P.DESCRIPCION_PRODUCTO,
	O.DESCRIPCION_OPERACION,
	C.COMENTARIO
FROM
	WF_RECLAMOS.CON_GESTION_NOVEDADES N
LEFT JOIN
	WF_RECLAMOS.CON_COM_X_INST C
	ON C."UID" = UID_REFERENCIA
	AND COD_PROCESO = 'TRA'
INNER JOIN
	WF_RECLAMOS.CON_PRODUCTOS P
	ON P.CODIGO_PRODUCTO = N.GESTION
INNER JOIN
	WF_RECLAMOS.CON_OPERACIONES O
	ON O.CODIGO_OPERACION = N.SUBGESTION
	AND O.CODIGO_PRODUCTO = N.GESTION
WHERE
	TRUNC(FECHA) BETWEEN TO_DATE(:FECHA_DESDE, 'DD/MM/YYYY') AND TO_DATE(:FECHA_HASTA, 'DD/MM/YYYY')