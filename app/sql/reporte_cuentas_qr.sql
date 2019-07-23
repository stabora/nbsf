SELECT
	SL."UID",
	SL.FECHA AS "Fecha",
	ES.DESCRIPCION AS "Estado",
	MVABM.DESCRIPCION AS "Resoluci&oacute;n ABM",
	CL.TIPODOC AS "Tipo doc.", 
	CL.NUMERODOC AS "Nro. doc.", 
	CL.NROCUIT AS "CUIT", 
	CL.NOMBRECLIENTE AS "Nombre",
	LPAD(NVL(CL.SUCAGE, 0), 3 ,'0') || LPAD(NVL(CL.SUCCON, 0), 3 ,'0') AS "Actividad AFIP", 
	PC.SUCURSAL AS "CA Suc.",
	PC.CODIGO_TIPO AS "CA Tipo", 
	PC.CODIGO_PRODUCTO AS "CA Prod.", 
	PC.NUMERO AS "CA Nro.", 
	TO_CHAR(PC.CBU) AS CBU,
	EXTRACTVALUE(XMLTYPE.CREATEXML(CIP.XMLRES), '//Producto[CodigoSistema=1][CodigoProducto=47][1]/Descripcion') AS "CC vinculada",
	(SELECT C.DESCRIPCION FROM WF_SOLICITUDESMASIVAS.TBL_CON_X_INST CI
	INNER JOIN WF_SOLICITUDESMASIVAS.TBL_CONSULTAS C ON C.CODIGO = CI.CODIGO_CONSULTA
	WHERE CI."UID" = SL."UID" AND CI.ESTADO = 5 AND ROWNUM = 1
	) AS "Consultas irregulares"
FROM
	WF_SOLICITUDESMASIVAS.TBL_SOLICITUDES SL
INNER JOIN
	WF_SOLICITUDESMASIVAS.POLL_INGRESO_SOLICITUDES PI
	ON PI."UID" = SL."UID"
INNER JOIN
	WF_SOLICITUDESMASIVAS.TBL_ESTADOS ES
	ON ES.CODIGO = SL.CODIGO_ESTADO
LEFT JOIN
	WF_SOLICITUDESMASIVAS.TBL_PERSONAS PE
	ON PE."UID" = SL."UID"
LEFT JOIN
	WF_SOLICITUDESMASIVAS.TBL_CLIENTES CL
	ON CL."UID" = SL."UID"
LEFT JOIN
	WF_SOLICITUDESMASIVAS.TBL_PRODUCTOS_CUENTAS PC
	ON PC."UID" = SL."UID"
LEFT JOIN
	WF_SOLICITUDESMASIVAS.TBL_CON_X_INST CIP
	ON CIP."UID" = SL."UID"
	AND CIP.CODIGO_CONSULTA = 14
LEFT JOIN (
		SELECT DENSE_RANK() OVER (PARTITION BY MVABM."UID" ORDER BY MVABM.FECHA DESC) AS RNK, MVABM.*, ES.DESCRIPCION
		FROM WF_SOLICITUDESMASIVAS.TBL_MOVIMIENTOS MVABM
		INNER JOIN WF_SOLICITUDESMASIVAS.TBL_ESTADOS ES ON ES.CODIGO = MVABM.CODIGO_ESTADO
		WHERE MVABM.DESCRIPCION_ADICIONAL = '1020'
	) MVABM
	ON MVABM."UID" = SL."UID"
	AND MVABM.RNK = 1
WHERE
	PI.ORIGEN_CODIGO_SISTEMA = 10014
	AND MVABM.DESCRIPCION IS NOT NULL
	AND TRUNC(SL.FECHA) BETWEEN TO_DATE(:FECHA_DESDE, 'DD/MM/YYYY') AND TO_DATE(:FECHA_HASTA, 'DD/MM/YYYY')
ORDER BY
	PI.FECHA_PROCESO_WF