# -*- coding: utf-8 -*-

from flask import request
import uuid
from datetime import datetime
from lxml import etree
from lxml.builder import E
from lxml.etree import tostring
from app import app


class XML:

    @staticmethod
    def get_xml_error(motivo):
        return tostring(
            E.NBSFConsultas(
                E.error(
                    E.method(str(request.endpoint)),
                    E.cause(motivo)
                )
            )
        )

    @staticmethod
    def get_xml_consultarPadron(numeroDocumento):
        return tostring(
            E.PedConsPad(
                E.IDPedido('NBSFPY-{}'.format(datetime.today().strftime('%Y%m%d%H%M'))),
                E.NroDoc(numeroDocumento)
            )
        )

    @staticmethod
    def get_xml_cliConsBlqDesblq(numeroCliente, operacion, usuario):
        return tostring(
            E.PedCliConsBlqDesblq(
                E.IDPed('NBSFPY-'.format(datetime.today().strftime('%Y%m%d%H%M'))),
                E.Fecha(datetime.today().strftime('%Y%m%d')),
                E.Operacion(str(operacion)),
                E.NroCliente(numeroCliente),
                E.Producto('0'),
                E.User(str(usuario)),
                E.Plataforma('WEB')
            )
        )

    @staticmethod
    def get_xml_consultarVeraz(nombre, sexo, numeroDocumento):
        return tostring(
            E.mensaje(
                E.identificador(
                    E.userlogon(
                        E.matriz(app.config['VERAZ_MATRIZ']),
                        E.usuario(app.config['VERAZ_USER']),
                        E.password(app.config['VERAZ_PASSWORD'])
                    ),
                    E.medio(app.config['VERAZ_MEDIO']),
                    E.formatoInforme(app.config['VERAZ_FORMATOINFORME']),
                    E.reenvio(),
                    E.producto(app.config['VERAZ_PRODUCTO']),
                    E.lote(
                        E.sectorVeraz(app.config['VERAZ_SECTOR']),
                        E.sucursalVeraz(app.config['VERAZ_SUCURSAL']),
                        E.cliente(app.config['VERAZ_CLIENTE']),
                        E.fechaHora(datetime.today().strftime('%Y-%m-%d %H:%M:%S'))
                    )
                ),
                E.consulta(
                    E.integrantes('1'),
                    E.integrante(
                        E.nombre(nombre),
                        E.sexo(sexo),
                        E.documento(numeroDocumento),
                        valor='1'
                    )
                )
            )
        )

    @staticmethod
    def get_xml_respuestaVerazDebug(nombre, sexo, numeroDocumento):
        return (
            '''<?xml version="1.0" encoding="ISO-8859-1"?><mensaje><estado><codigoError>0</codigoError><mensajeError></mensajeError></estado><identificador><fechaRecepcion>2014-10-24 16:10:56</fechaRecepcion><lote>201410246844523</lote><producto>RISC:Experto</producto><cliente>TRA-999845721</cliente></identificador><respuesta><grupo><variables></variables></grupo><integrantes>1</integrantes><integrante valor="1"><nombre>{nombre}</nombre><documento>{numeroDocumento}</documento><sexo>{sexo}</sexo><variables><variable><nombre clase="A"><![CDATA[Documento]]></nombre><valor tipo="N"><![CDATA[{numeroDocumento}]]></valor></variable><variable><nombre clase="A"><![CDATA[Sexo]]></nombre><valor tipo="C"><![CDATA[{sexo}]]></valor></variable><variable><nombre clase="A"><![CDATA[bureau_prestamos_cuota]]></nombre><valor tipo="N"><![CDATA[0]]></valor></variable><variable><nombre clase="A"><![CDATA[bureau_prestamos_cuota_res]]></nombre><valor tipo="N"><![CDATA[{bureau_prestamos_cuota_res}]]></valor></variable><variable><nombre clase="A"><![CDATA[bureau_prestamos_saldo_total]]></nombre><valor tipo="N"><![CDATA[0]]></valor></variable><variable><nombre clase="A"><![CDATA[bureau_tarjetas_limite_compra]]></nombre><valor tipo="N"><![CDATA[4000]]></valor></variable><variable><nombre clase="A"><![CDATA[bureau_tarjetas_pago_minimo]]></nombre><valor tipo="N"><![CDATA[{bureau_tarjetas_pago_minimo}]]></valor></variable><variable><nombre clase="A"><![CDATA[bureau_tarjetas_saldo_total]]></nombre><valor tipo="N"><![CDATA[3554]]></valor></variable><variable><nombre clase="O"><![CDATA[bureau_ultimo_estado_4M]]></nombre><valor tipo="C"><![CDATA[1]]></valor></variable><variable><nombre clase="A"><![CDATA[cantidad_consultas_financieras]]></nombre><valor tipo="N"><![CDATA[0]]></valor></variable><variable><nombre clase="O"><![CDATA[categoria]]></nombre><valor tipo="C"><![CDATA[rechazar]]></valor></variable><variable><nombre clase="A"><![CDATA[consultas_entidades_grp_1]]></nombre><valor tipo="C"><![CDATA[{consultas_entidades_grp_1}]]></valor></variable><variable><nombre clase="A"><![CDATA[consultas_entidades_grp_2]]></nombre><valor tipo="C"><![CDATA[{consultas_entidades_grp_2}]]></valor></variable><variable><nombre clase="A"><![CDATA[consultas_entidades_grp_3]]></nombre><valor tipo="C"><![CDATA[{consultas_entidades_grp_3}]]></valor></variable><variable><nombre clase="A"><![CDATA[consultas_entidades_grp_4]]></nombre><valor tipo="C"><![CDATA[{consultas_entidades_grp_4}]]></valor></variable><variable><nombre clase="A"><![CDATA[consultas_entidades_grp_5]]></nombre><valor tipo="C"><![CDATA[{consultas_entidades_grp_5}]]></valor></variable><variable><nombre clase="O"><![CDATA[cuota]]></nombre><valor tipo="N"><![CDATA[0]]></valor></variable><variable><nombre clase="A"><![CDATA[cuota_maxima_sugerida]]></nombre><valor tipo="N"><![CDATA[0]]></valor></variable><variable><nombre clase="O"><![CDATA[explicacion]]></nombre><valor tipo="C"><![CDATA[Ingreso promedio menor a 5000]]></valor></variable><variable><nombre clase="O"><![CDATA[maximo_limite]]></nombre><valor tipo="N"><![CDATA[4000]]></valor></variable><variable><nombre clase="A"><![CDATA[maximo_limite_ACC]]></nombre><valor tipo="N"><![CDATA[0]]></valor></variable><variable><nombre clase="A"><![CDATA[observaciones_concursos_quiebras]]></nombre><valor tipo="C"><![CDATA[{observaciones_concursos_quiebras}]]></valor></variable><variable><nombre clase="A"><![CDATA[observaciones_juicios]]></nombre><valor tipo="C"><![CDATA[{observaciones_juicios}]]></valor></variable><variable><nombre clase="A"><![CDATA[observaciones_morosidad]]></nombre><valor tipo="C"><![CDATA[{observaciones_morosidad}]]></valor></variable><variable><nombre clase="O"><![CDATA[relacion_compromiso_ingresos]]></nombre><valor tipo="N"><![CDATA[0]]></valor></variable><variable><nombre clase="A"><![CDATA[relacion_cuota_ingresos]]></nombre><valor tipo="N"><![CDATA[0]]></valor></variable><variable><nombre clase="O"><![CDATA[score_poblacion]]></nombre><valor tipo="C"><![CDATA[{score_poblacion}]]></valor></variable><variable><nombre clase="O"><![CDATA[score_veraz]]></nombre><valor tipo="N"><![CDATA[{score_veraz}]]></valor></variable><variable><nombre clase="A"><![CDATA[total_sugerido_limite_ACC]]></nombre><valor tipo="N"><![CDATA[0]]></valor></variable><variable><nombre clase="O"><![CDATA[total_sugerido_limite_tarjeta]]></nombre><valor tipo="N"><![CDATA[0]]></valor></variable><variable><nombre clase="O"><![CDATA[validacion]]></nombre><valor tipo="C"><![CDATA[Validado]]></valor></variable><variable><nombre clase="A"><![CDATA[version_DNI]]></nombre><valor tipo="C"><![CDATA[Duplicado]]></valor></variable></variables></integrante><informe><html/><texto><![CDATA[001T00000100C010000                                    VERAZ RISC 001T00000200C010000             NUEVO BANCO DE SANTA FE              CONSULTA 001T00000300C010000             LOTE:6844523-VN0330000003 EMITIDO EL 24/10/2014 (INFORME 01/01) 001T00000400E040000Este informe que solicitara en su calidad de cliente, es confidencial y 001T00000500E040000solo debera usarse para la evaluacion y celebracion de negocios. 001T00000600E040000Prohibida su reproduccion, divulgacion y entrega a terceros (Deber de 001T00000700E040000confidencialidad y uso permitido - Ley 25.326). No contiene juicios de 001T00000800E040000valor sobre las personas ni sobre su solvencia. Las decisiones a las que 001T00000900E040000arribe el usuario son de su exclusiva responsabilidad. 001T00001010T020000DATOS SEGUN SU CONSULTA EFECTUADA EL: 24/10/2014 001T00001110L010000      {nombre} CLIENTE: TRA-999845721 001T00001210L010000      DNI= {numeroDocumento} 001T00001315T020000DATOS SEGUN BASE DE VALIDACION VERAZ: 001T00001415H010000      DNI {numeroDocumento} VALIDADO (DUPLICADO) 001T00001515L010000      {nombre}                        EDAD=999  FECHA=1/1/1900 001T00001615L010000      PJE SUD AMERICA 1545   (1290) (C1290AMA)   C.FEDERAL 001T00001788L010000      CUIT {cuit} 001T00001820T010000                       DATOS SEGUN BASE DE INFORMACION: 001T00001930T020000                        OBSERVACIONES (ULTIMOS 5 AÑOS) 001T00002030Z010000NO REGISTRA 001T00002140T050000             VERAZ CREDIT BUREAU (FUENTE PROPIA - ULTIMOS 5 AÑOS) 001T00002240Z043T00                              TARJETAS DE CREDITO 001T00002340H033T0**                                   A¿o   |   2014   |    2013    |2012|3|4|5 001T00002440H023T0**CLIENTE                            Mes   |OSAJJMAMFE|DNOSAJJMAMFE|DN  | (*) 001T00002540W013T00DESDE   MR PAGO MIN. LIM.COMPRA SDO.TOTAL LIM.CRED. SDO.CTAS. VENCIDO SDO.MAX. 001T00002640L023T0002/2011 GI0259-BANCO ITAU  ARGENTINA SA(T)|--11111111|111111111111|11  |1|1| 001T00002740L013T00   +    VI       300       4000      3554      3200      184        0     5262 001T00002840*013T00TOTAL:           300       4000      3554                           0 001T00002940E010000 001T00003040E100000Monedas = ARS:Pesos Argentinos,USD:Dolares,EUR:Euros. 001T00003140E090000Situaciones='-':Sin Informacion,0:No utilizado,S:Saldo No Significativo, 001T00003240E0800001:Normal,2:Atraso 31/60 dias,3:Atraso 61/90 dias,4:Atraso 91/120 dias, 001T00003340E0700006:Atraso 121/180 dias,9:Atraso 181/360 dias,G:En Gestion Extrajudicial, 001T00003440E060000J:Juicio Iniciado,I:Incobrable o atraso mayor a 360 dias,R:Refinanciacion, 001T00003540E050000E:Tarjeta extraviada o incluida en Boletin por seguridad,C:Operacion Cerrada, 001T00003640E040000D:Operacion cerrada por decision de la entidad,L:Denuncia de siniestro. 001T00003740E030000Vinculaciones=(T)Titular,(A)Adicional,(C)Conjunta,(G)Garante,(R)Orden Reciproca, 001T00003840E020000(U)Unipersonal. 001T00003940E010000Periodo= (*)Corresponde a ciclos anteriores de 12 meses consecutivos c/u. 001T00004040E040000NOTA:Los importes corresponden a la ultima situacion informada en el 001T00004140E040000cuatrimestre. 001T00004240E040000Esta informacion es exclusiva de Organizacion Veraz SA y confeccionada 001T00004340E040000en funcion de los datos aportados directamente por nuestros clientes. 001T00004440X040000          RESUMEN CONSIDERANDO 1 LINEA/S DE OPERACION/ES (1 ACTIVA/S) 001T00004540W030000            COMPROMISO  MES      ACUERDO TOTAL    DEUDA TOTAL    DEUDA VENCIDA 001T00004640W020000TOTAL:                300             4000           3554                0 001T00004730T08CH00        CHEQUES RECHAZADOS AL: 23/10/2014  (FUENTE BCRA - ULTIMOS 2 AÑOS) 001T00004830Z07CH00NO REGISTRA 001T00004937T050000        DEUDORES DEL SISTEMA FINANCIERO (FUENTE BCRA - ULTIMOS 2 AÑOS) 001T00005037W030000                           EVOLUCION ULTIMOS 2 AÑOS 001T00005137S020000                Año|   2014   |    2013    |2012|ULT.MONTO|DIAS DE|  ULT.OBS.| 001T00005237W010000ENTIDAD         Mes|OSAJJMAMFE|DNOSAJJMAMFE|DN  |INFORMADO| ATRASO| INFORMADA| 001T00005337L010000BANCO ITAU  ARGENTI|--11111111|111111111111|11  |      3800|   N/A|          | 001T00005437*100000 001T00005537E010000Clasificaciones segun Circular A 4738 del BCRA='-':Sin Informacion, 001T00005637E0200000:STD(Standard),1:Situacion Normal,2:Riesgo Bajo,3:Riesgo Medio,4:Riesgo Alto, 001T00005737E0300005:Irrecuperable,6:Irrecuperable por disposicion tecnica. N/D:No Disponible. 001T00005837E040000Observaciones=A:Refinanciaciones,B:Recategorizacion Obligatoria,C:Situacion 001T00005937E050000Juridica (concordatos judiciales o extrajudiciales, concurso preventivo, 001T00006037E060000gestion judicial o quiebra),D:Irrecuperable por Disposicion Tecnica. 001T00006137E070000Dias de atraso=N/A: No aplicable. 001T00006250T020000                          CONSULTAS (ULTIMOS 5 AÑOS) 001T00006350Z010000FECHA   EMPRESA/ENTIDAD 001T00006450S010000SECTOR FINANCIERO 001T00006550L01010006/2014 BANCO ITAU  ARGENTINA SA 001T00006650L01010009/2013 BANCO DE SERVICIOS FINANCIEROS SA 001T00006780T020000DATOS SEGUN BASE DE RELACIONES 001T00006880L010000RIVERA,ALBERTO ALEJANDRO                  CONYUGE           DNI     12.270.527 001T00006999L030000            ========================================================= 001T00007099H020000            FIN DEL INFORME 01/01 REFERENCIA:0208095004#UPALJXJGYTFXI 001T00007199L010000 ]]></texto></informe></respuesta></mensaje>''').format(
                nombre=nombre,
                numeroDocumento=numeroDocumento,
                sexo=sexo,
                cuit='99-99999999-9',
                score_poblacion=app.config['VERAZ_DEBUG_SCORE_POBLACION'],
                score_veraz=app.config['VERAZ_DEBUG_SCORE'],
                bureau_prestamos_cuota_res=app.config['VERAZ_DEBUG_BUREAU_PRESTAMOS_CUOTA_RES'],
                bureau_tarjetas_pago_minimo=app.config['VERAZ_DEBUG_BUREAU_TARJETAS_PAGO_MINIMO'],
                observaciones_concursos_quiebras=app.config['VERAZ_DEBUG_OBSERVACIONES_CONCURSOS_QUIEBRAS'],
                observaciones_juicios=app.config['VERAZ_DEBUG_OBSERVACIONES_JUICIOS'],
                observaciones_morosidad=app.config['VERAZ_DEBUG_OBSERVACIONES_MOROSIDAD'],
                consultas_entidades_grp_1=app.config['VERAZ_DEBUG_CONSULTAS_ENTIDADES_GRP_1'],
                consultas_entidades_grp_2=app.config['VERAZ_DEBUG_CONSULTAS_ENTIDADES_GRP_2'],
                consultas_entidades_grp_3=app.config['VERAZ_DEBUG_CONSULTAS_ENTIDADES_GRP_3'],
                consultas_entidades_grp_4=app.config['VERAZ_DEBUG_CONSULTAS_ENTIDADES_GRP_4'],
                consultas_entidades_grp_5=app.config['VERAZ_DEBUG_CONSULTAS_ENTIDADES_GRP_5']
        )

    @staticmethod
    def get_xml_brokerEnvelope(action):
        xml = E.Request(
            E.Header(
                E.ActionCode(action),
                E.TraceGuid(str(uuid.uuid4())),
                E.IsBodyEncrypted('false'),
                E.EncryptRequest('false'),
                E.EncryptResponse('false')
            ),
            E.Body(
                E.DSData()
            )
        )

        return tostring(xml)

    @staticmethod
    def get_xml_broker_consultarCupoCUAD(cuit):
        xml = etree.fromstring(XML.get_xml_brokerEnvelope('NBSF.PrestamosEnComercios.CUAD.ConsultarCupoQuery'))
        dsdata = xml.find('.//Body/DSData')

        dsdata.append(etree.fromstring(
            '<xs:schema attributeFormDefault="qualified" elementFormDefault="qualified" id="CUADDS" targetNamespace="{ns}" xmlns="{ns}" xmlns:msdata="urn:schemas-microsoft-com:xml-msdata" xmlns:mstns="{ns}" xmlns:xs="http://www.w3.org/2001/XMLSchema">'
            '<xs:element name="CUADDS">'
            '<xs:complexType>'
            '<xs:choice maxOccurs="unbounded" minOccurs="0">'
            '<xs:element name="ConsultaCupo">'
            '<xs:complexType>'
            '<xs:sequence>'
            '<xs:element name="ClaveEmpleado" type="xs:string"/>'
            '<xs:element minOccurs="0" name="CUIL" type="xs:long"/>'
            '<xs:element name="IdEmpleador" type="xs:int"/>'
            '</xs:sequence>'
            '</xs:complexType>'
            '</xs:element>'
            '</xs:choice>'
            '</xs:complexType>'
            '</xs:element>'
            '</xs:schema>'.format(
                ns=app.config['BROKERWS_XMLNS_CUAD']
            )
        ))

        dsdata.append(etree.fromstring(
            (
                '<diffgr:diffgram xmlns:diffgr="urn:schemas-microsoft-com:xml-diffgram-v1">'
                '<CUADDS xmlns="{ns}">'
                '<ConsultaCupo>'
                '<ClaveEmpleado>{cuit}</ClaveEmpleado>'
                '<CUIL>{cuit}</CUIL>'
                '<IdEmpleador>{idEmpleador}</IdEmpleador>'
                '</ConsultaCupo>'
                '</CUADDS>'
                '</diffgr:diffgram>'
            ).format(
                ns=app.config['BROKERWS_XMLNS_CUAD'],
                cuit=cuit,
                idEmpleador=10
            )
        ))

        return tostring(xml)

    @staticmethod
    def get_xml_broker_consultarPrestamos(accion, tipoDocumento, numeroDocumento, uidPrestamo=0, idSite=0):
        estado = 0

        if accion == 'SelectEnWF':
            origen = 1
        elif accion == 'SelectEnSite':
            origen = 2
        elif accion in ['AltaEnWF', 'BajaEnWF']:
            origen = 2 if idSite > 0 else 1
            estado = 806

        xml = etree.fromstring(XML.get_xml_brokerEnvelope('Prestamos.{}'.format(accion)))
        dsdata = xml.find('.//Body/DSData')

        dsdata.append(etree.fromstring(
            '<xs:schema id="PrestamosEnWFDS" targetNamespace="{ns}" xmlns:mstns="{ns}" xmlns="{ns}" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:msdata="urn:schemas-microsoft-com:xml-msdata" attributeFormDefault="qualified" elementFormDefault="qualified">'
            '<xs:element name="PrestamosEnWFDS" msdata:IsDataSet="true" msdata:Locale="en-US">'
            '<xs:complexType>'
            '<xs:choice minOccurs="0" maxOccurs="unbounded">'
            '<xs:element name="NBSF_PrestamosEnWF">'
            '<xs:complexType>'
            '<xs:sequence>'
            '<xs:element name="IDWorkFlow" type="xs:long" />'
            '<xs:element name="Origen_ID" type="xs:int" minOccurs="0" />'
            '<xs:element name="TipoDoc" type="xs:decimal" minOccurs="0" />'
            '<xs:element name="NumeroDoc" type="xs:decimal" minOccurs="0" />'
            '<xs:element name="FechaBajaWF" type="xs:dateTime" minOccurs="0" />'
            '<xs:element name="Estado_ID" type="xs:int" minOccurs="0" />'
            '<xs:element name="Prestamo_ID" type="xs:long" minOccurs="0" />'
            '</xs:sequence>'
            '</xs:complexType>'
            '</xs:element>'
            '</xs:choice>'
            '</xs:complexType>'
            '<xs:unique name="PrestamosEnWFDSKey1" msdata:PrimaryKey="true">'
            '<xs:selector xpath=".//mstns:NBSF_PrestamosEnWF" />'
            '<xs:field xpath="mstns:IDWorkFlow" />'
            '<xs:field xpath="mstns:Origen_ID" />'
            '</xs:unique>'
            '</xs:element>'
            '</xs:schema>'.format(
                ns=app.config['BROKERWS_XMLNS_PRESTAMOS']
            )
        ))

        dsdata.append(etree.fromstring(
            (
                '<diffgr:diffgram xmlns:msdata="urn:schemas-microsoft-com:xml-msdata" xmlns:diffgr="urn:schemas-microsoft-com:xml-diffgram-v1">'
                '<PrestamosEnWFDS xmlns="{ns}">'
                '<NBSF_PrestamosEnWF diffgr:id="NBSF_PrestamosEnWF1" msdata:rowOrder="0" diffgr:hasChanges="inserted">'
                '<IDWorkFlow>{uid}</IDWorkFlow>'
                '<Prestamo_ID>{idSite}</Prestamo_ID>'
                '<Origen_ID>{origen}</Origen_ID>'
                '<Estado_ID>{estado}</Estado_ID>'
                '<TipoDoc>{tipoDocumento}</TipoDoc>'
                '<NumeroDoc>{numeroDocumento}</NumeroDoc>'
                '</NBSF_PrestamosEnWF>'
                '</PrestamosEnWFDS>'
                '</diffgr:diffgram>'
            ).format(
                ns=app.config['BROKERWS_XMLNS_PRESTAMOS'],
                uid=uidPrestamo,
                estado=estado,
                origen=origen,
                tipoDocumento=tipoDocumento,
                numeroDocumento=numeroDocumento,
                idSite=idSite
            )
        ))

        return tostring(xml)
