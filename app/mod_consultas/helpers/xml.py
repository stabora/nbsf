# -*- coding: utf-8 -*-

from datetime import datetime
from random import randint
from lxml import etree
from lxml.builder import E
from lxml.etree import tostring
from app import app


class XML:

    @staticmethod
    def get_xml_consultarPadron(numeroDocumento):
        return tostring(
            E.PedConsPad(
                E.IDPedido('NBSFPY-' + datetime.today().strftime('%Y%m%d%H%M')),
                E.NroDoc(numeroDocumento)
            )
        )

    @staticmethod
    def get_xml_cliConsBlqDesblq(numeroCliente, operacion, usuario):
        return tostring(
            E.PedCliConsBlqDesblq(
                E.IDPed('NBSFPY-' + datetime.today().strftime('%Y%m%d%H%M')),
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
                        E.usuario(app.config['VERAZ_USUARIO']),
                        E.password(app.config['VERAZ_PASSWORD'])
                    ),
                    E.medio('HTML'),
                    E.formatoInforme('T'),
                    E.reenvio(),
                    E.producto('RISC:Experto'),
                    E.lote(
                        E.sectorVeraz('03'),
                        E.sucursalVeraz('0'),
                        E.cliente('TRA-999845721'),
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
    def get_xml_brokerEnvelope(action):
        xml = E.Request(
            E.Header(
                E.ActionCode(action),
                E.TraceGuid('00000000-0000-0000-0000-000{0:09d}'.format(randint(1, 999999999))),
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
            '<xs:schema attributeFormDefault="qualified" elementFormDefault="qualified" id="CUADDS" targetNamespace="http://tempuri.org/CUADDS.xsd" xmlns="http://tempuri.org/CUADDS.xsd" xmlns:msdata="urn:schemas-microsoft-com:xml-msdata" xmlns:mstns="http://tempuri.org/CUADDS.xsd" xmlns:xs="http://www.w3.org/2001/XMLSchema">'
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
            '</xs:schema>'
        ))

        dsdata.append(etree.fromstring(
            (
                '<diffgr:diffgram xmlns:diffgr="urn:schemas-microsoft-com:xml-diffgram-v1">'
                '<CUADDS xmlns="http://tempuri.org/CUADDS.xsd">'
                '<ConsultaCupo>'
                '<ClaveEmpleado>{cuit}</ClaveEmpleado>'
                '<CUIL>{cuit}</CUIL>'
                '<IdEmpleador>{idEmpleador}</IdEmpleador>'
                '</ConsultaCupo>'
                '</CUADDS>'
                '</diffgr:diffgram>'
            ).format(
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
        elif accion == 'BajaEnWF':
            origen = 2 if idSite > 0 else 1
            estado = 806

        xml = etree.fromstring(XML.get_xml_brokerEnvelope('Prestamos.' + accion))
        dsdata = xml.find('.//Body/DSData')

        dsdata.append(etree.fromstring(
            '<xs:schema id="PrestamosEnWFDS" targetNamespace="http://tempuri.org/PrestamosEnWFDS.xsd" xmlns:mstns="http://tempuri.org/PrestamosEnWFDS.xsd" xmlns="http://tempuri.org/PrestamosEnWFDS.xsd" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:msdata="urn:schemas-microsoft-com:xml-msdata" attributeFormDefault="qualified" elementFormDefault="qualified">'
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
            '</xs:schema>'
        ))

        dsdata.append(etree.fromstring(
            (
                '<diffgr:diffgram xmlns:msdata="urn:schemas-microsoft-com:xml-msdata" xmlns:diffgr="urn:schemas-microsoft-com:xml-diffgram-v1">'
                '<PrestamosEnWFDS xmlns="http://tempuri.org/PrestamosEnWFDS.xsd">'
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
                uid=uidPrestamo,
                estado=estado,
                origen=origen,
                tipoDocumento=tipoDocumento,
                numeroDocumento=numeroDocumento,
                idSite=idSite
            )
        ))

        return tostring(xml)
