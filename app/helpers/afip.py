# -*- coding: utf-8 -*-

from suds.client import Client
from datetime import datetime, timedelta
from M2Crypto import BIO, SMIME
from lxml import etree
from app import app
from app.helpers.util import Util
import email
import os
import requests


##############################
# Request envelopes
##############################

xmlped_login = (
    '<?xml version="1.0" encoding="UTF-8"?>'
    '<loginTicketRequest version="1.0">'
    '<header>'
    '<uniqueId>{}</uniqueId>'
    '<generationTime>{}</generationTime>'
    '<expirationTime>{}</expirationTime>'
    '</header>'
    '<service>{}</service>'
    '</loginTicketRequest>'
).format(
    datetime.now().strftime('%Y%m%d'),
    datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),
    (datetime.now() + timedelta(hours=10)).strftime('%Y-%m-%dT%H:%M:%S'),
    '{}'
)

xmlped_padron = (
    '<?xml version="1.0" encoding="UTF-8"?>'
    '<SOAP-ENV:Envelope xmlns:ns0="http://{}.soap.ws.server.puc.sr/" xmlns:ns1="http://schemas.xmlsoap.org/soap/envelope/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/">'
    '<SOAP-ENV:Header/>'
    '<ns1:Body>'
    '<ns0:getPersona>'
    '<token>{}</token>'
    '<sign>{}</sign>'
    '<cuitRepresentada>{}</cuitRepresentada>'
    '<idPersona>{}</idPersona>'
    '</ns0:getPersona>'
    '</ns1:Body>'
    '</SOAP-ENV:Envelope>'
)


##############################
# Main class
##############################

class AFIP:

    @staticmethod
    def sign_tra(padron, content=xmlped_login, key=app.config['AFIP_FILE_KEY'], cert=app.config['AFIP_FILE_CERT']):
        content = content.format(padron)
        buf = BIO.MemoryBuffer(content)
        key = BIO.MemoryBuffer(open(key).read())
        cert = BIO.MemoryBuffer(open(cert).read())

        s = SMIME.SMIME()
        s.load_key_bio(key, cert)

        p7 = s.sign(buf, 0)
        out = BIO.MemoryBuffer()
        s.write(out, p7)

        msg = email.message_from_string(out.read())

        for part in msg.walk():
            filename = part.get_filename()

            if filename == 'smime.p7m':
                cms = part.get_payload(decode=False)

        return cms

    @staticmethod
    def verify_login(padron):
        token = None
        sign = None
        filename = app.config['AFIP_FILE_TRA'].format(padron)

        if os.path.exists(filename):
            xmlres = etree.fromstring(open(filename).read().encode('utf-8'), parser=etree.XMLParser(ns_clean=True, recover=True, encoding='utf-8'))
            expiration = datetime.strptime(xmlres.find('header/expirationTime').text, '%Y-%m-%dT%H:%M:%S.%f-03:00')
        else:
            expiration = datetime.now()

        if expiration > datetime.now():
            token = xmlres.find('credentials/token').text
            sign = xmlres.find('credentials/sign').text

        return token, sign

    @staticmethod
    def get_login(padron):
        token, sign = AFIP.verify_login(padron)
        filename = app.config['AFIP_FILE_TRA'].format(padron)

        if not token or not sign:
            cms = AFIP.sign_tra(padron)
            ws = Client(app.config['AFIP_URL_LOGIN'], proxy=Util.get_proxies())
            res = ws.service.loginCms(cms)

            tra = open(filename, 'w')
            tra.write(res)

            xmlres = etree.fromstring(res.encode('utf-8'), parser=etree.XMLParser(ns_clean=True, recover=True, encoding='utf-8'))
            token = xmlres.find('credentials/token').text
            sign = xmlres.find('credentials/sign').text

        return token, sign

    @staticmethod
    def get_persona(cuit_consultada, cuit_representada=app.config['AFIP_CUIT_REPRESENTADA'], padron=app.config['AFIP_PADRON']):
        token, sign = AFIP.get_login('ws_sr_padron_' + padron.lower())

        if token and sign:
            res = requests.post(
                app.config['AFIP_URL_PADRON'].format(padron.upper()),
                data=xmlped_padron.format(
                    padron.lower(),
                    token,
                    sign,
                    cuit_representada,
                    cuit_consultada
                ),
                proxies=Util.get_proxies()
            )

            return res.content.decode('iso-8859-1')
        else:
            return '<error>Error de autenticación con el servicio WSAA de AFIP.</error>'
