# -*- coding: utf-8 -*-

import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

PROXY_HOST = 'proxy'
PROXY_PORT = 80
PROXY_USER = 'taboras'
PROXY_PASS = 'aXMwMzAzNjYyMg=='

MYSQL_NBSF_USER = 'nbsf'
MYSQL_NBSF_PASSWORD = 'dx8sBt9F3dAnpfrV'
MYSQL_NBSF_DB = 'nbsf'

ORACLE_NBSF_WF6_HOST = '172.16.9.29'
ORACLE_NBSF_WF6_USER = 'dellaquil'
ORACLE_NBSF_WF6_PASSWORD = 'nbsf2014'
ORACLE_NBSF_WF6_SID = 'prod04'

VERAZ_HOST = 'https://online.org.veraz.com.ar'
VERAZ_RESOURCE = '/pls/consulta817/wserv'
VERAZ_MATRIZ = 'VN0330'
VERAZ_USUARIO = 'XML'
VERAZ_PASSWORD = '110224870051101206368'

# desarrollowf - 172.16.8.165
# mensajeria - 172.16.55.6
NBSF_MENSAJERIA_HOST = 'http://mensajeria'
NBSF_MENSAJERIA_RESOURCE = '/asconexweb/asconsultas.asmx/Consultar'

# Desarrollo: http://nbsf000des01.nbsf.com.ar/BrokerWSDesa/WebDispatcher.asmx/ExecuteString
# Test: https://nbsfvmwwse01.nbsf.com.ar/BrokerWS/WebDispatcher.asmx/ExecuteString
NBSF_BROKERWS_HOST = 'http://nbsf000des01.nbsf.com.ar'
NBSF_BROKERWS_RESOURCE = '/BrokerWSDesa/WebDispatcher.asmx/ExecuteString'

SQLALCHEMY_DATABASE_URI = 'mysql://root:sa@localhost/nbsf'

# Consulta Veraz - Modo debug
VERAZ_DEBUG_SCORE_POBLACION = 'th'
VERAZ_DEBUG_SCORE = '1810'
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
