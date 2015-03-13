# -*- coding: utf-8 -*-

from datetime import datetime
from random import randint
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
    def get_xml_consultarCupoCUAD(cuit):
        return (
            '<Request>'
            '<Header>'
            '<ActionCode>NBSF.PrestamosEnComercios.CUAD.ConsultarCupoQuery</ActionCode>'
            '<TraceGuid>00000000-0000-0000-0000-000{traceGuid:09d}</TraceGuid>'
            '<IsBodyEncrypted>false</IsBodyEncrypted>'
            '<EncryptRequest>false</EncryptRequest>'
            '<EncryptResponse>false</EncryptResponse>'
            '</Header>'
            '<Body>'
            '<DSData>'
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
            '<diffgr:diffgram xmlns:diffgr="urn:schemas-microsoft-com:xml-diffgram-v1">'
            '<CUADDS xmlns="http://tempuri.org/CUADDS.xsd">'
            '<ConsultaCupo>'
            '<ClaveEmpleado>{cuit}</ClaveEmpleado>'
            '<CUIL>{cuit}</CUIL>'
            '<IdEmpleador>{idEmpleador}</IdEmpleador>'
            '</ConsultaCupo>'
            '</CUADDS>'
            '</diffgr:diffgram>'
            '</DSData>'
            '</Body>'
            '</Request>'
        ).format(
            traceGuid=randint(1, 999999999),
            cuit=cuit,
            idEmpleador=10
        )

    @staticmethod
    def get_xml_consultarCupoCUAD_E(cuit):
        return tostring(
            E.Request(
                E.Header(
                    E.ActionCode('NBSF.PrestamosEnComercios.CUAD.ConsultarCupoQuery'),
                    E.TraceGuid('00000000-0000-0000-0000-000{0:09d}'.format(randint(1, 999999999))),
                    E.IsBodyEncrypted('false'),
                    E.EncryptRequest('false'),
                    E.EncryptResponse('false')
                ),

                E.Body(
                    E.DSData(
                        E(
                            '{http://tempuri.org/CUADDS.xsd}schema',
                            E.element(
                                E.complexType(
                                    E.choice(
                                        E.element(
                                            E.complexType(
                                                E.sequence(
                                                    E.element(name='ClaveEmpleado', type='xs:string'),
                                                    E.element(minOccurs='0', name='CUIL', type='xs:long'),
                                                    E.element(name='IdEmpleador', type='xs:int')
                                                )
                                            ),
                                            name='ConsultaCupo'
                                        ),
                                        maxOccurs='unbounded',
                                        minOccurs='0'
                                    )
                                ),
                                name='CUADDS'
                            ),
                            attributeFormDefault='qualified',
                            elementFormDefault='qualified',
                            id='CUADDS',
                            targetNamespace='http://tempuri.org/CUADDS.xsd',
                            # xmlns='http://tempuri.org/CUADDS.xsd',
                            # msdata='urn:schemas-microsoft-com:xml-msdata',
                            # mstns='http://tempuri.org/CUADDS.xsd',
                            # xs='http://www.w3.org/2001/XMLSchema'
                        ),

                        E.diffgram(
                            E.CUADDS(
                                E.ConsultaCupo(
                                    E.ClaveEmpleado(cuit),
                                    E.CUIL(cuit),
                                    E.IdEmpleador('10')
                                ),
                                xmlns='http://tempuri.org/CUADDS.xsd'
                            )
                        )
                    )
                )
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
