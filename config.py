# -*- coding: utf-8 -*-

import os

# General
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
HTTP_REQUESTS_TIMEOUT = 40

# Proxy
PROXY_HOST = '172.16.1.107'
PROXY_PORT = 80
PROXY_USER = 'taboras'
PROXY_PASS = 'aXMwMzAzNjYyOQ=='


##################################################
# Databases
##################################################

# App database
SQLALCHEMY_DATABASE_URI = 'mysql://nbsf:nTCWG2ubpRxssD8N@localhost/nbsf'

# Oracle WF6
ORACLE_NBSF_WF6_HOST = '172.16.9.29'
ORACLE_NBSF_WF6_USER = 'dellaquil'
ORACLE_NBSF_WF6_PASSWORD = 'bmJzZjIwMTQ='
ORACLE_NBSF_WF6_SID = 'prod04'


##################################################
# Local web services
##################################################

# Mensajería
# desarrollowf - 172.16.8.165
# mensajeria - 172.16.55.6
NBSF_MENSAJERIA_HOST = 'http://172.16.55.6'
NBSF_MENSAJERIA_RESOURCE = '/asconexweb/asconsultas.asmx/Consultar'

# BrokerWS
# Desarrollo: http://nbsf000des01.nbsf.com.ar/BrokerWSDesa/WebDispatcher.asmx/ExecuteString
# Test: https://nbsfvmwwse01.nbsf.com.ar/BrokerWS/WebDispatcher.asmx/ExecuteString
NBSF_BROKERWS_HOST = 'http://nbsf000des01.nbsf.com.ar'
NBSF_BROKERWS_RESOURCE = '/BrokerWSDesa/WebDispatcher.asmx/ExecuteString'

# SOAT
SOAT_HOST = 'http://soatwstest.nbsf.com.ar'
SOAT_WSDL = '/ServicioSoat.svc?wsdl'
SOAT_ENTIDAD = '0071'
SOAT_CANAL = '003'
SOAT_IP = '192.168.0.1'
SOAT_USUARIO = 'NBSF-PY'


##################################################
# External web services
##################################################

# API Prieto & Prieto
PRIETO_HOST = 'https://api.prietoyprieto.com'
PRIETO_RESOURCE = '/dev.php/api/v1/lotes.xml'
PRIETO_APIKEY = 'CJWSBaUXUjVAz6cV'

# Veraz
VERAZ_HOST = 'https://online.org.veraz.com.ar'
VERAZ_RESOURCE = '/pls/consulta817/wserv'
VERAZ_USUARIO = 'XML'
VERAZ_PASSWORD = '110224870051101206368'
VERAZ_MATRIZ = 'VN0330'  # VN0330: NBSF - C19644: SIng - GO0330: Producción
VERAZ_SECTOR = '03'  # VN0330: 03 - C19644: 05
VERAZ_SUCURSAL = '0'
VERAZ_CLIENTE = 'TRA-999845721'
VERAZ_MEDIO = 'HTML'
VERAZ_FORMATOINFORME = 'T'
VERAZ_PRODUCTO = 'RISC:Experto'

# Veraz - Modo debug
VERAZ_DEBUG = True
VERAZ_DEBUG_SCORE_POBLACION = 'th'
VERAZ_DEBUG_SCORE = 810
VERAZ_DEBUG_BUREAU_PRESTAMOS_CUOTA_RES = 0
VERAZ_DEBUG_BUREAU_TARJETAS_PAGO_MINIMO = 0
VERAZ_DEBUG_OBSERVACIONES_CONCURSOS_QUIEBRAS = 'No'
VERAZ_DEBUG_OBSERVACIONES_JUICIOS = 'No'
VERAZ_DEBUG_OBSERVACIONES_MOROSIDAD = 'No'
VERAZ_DEBUG_CONSULTAS_ENTIDADES_GRP_1 = 0
VERAZ_DEBUG_CONSULTAS_ENTIDADES_GRP_2 = 0
VERAZ_DEBUG_CONSULTAS_ENTIDADES_GRP_3 = 0
VERAZ_DEBUG_CONSULTAS_ENTIDADES_GRP_4 = 0  # NBSF
VERAZ_DEBUG_CONSULTAS_ENTIDADES_GRP_5 = 0
