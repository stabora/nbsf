# -*- coding: utf-8 -*-

from base64 import b64decode
import re
from app import app


class Util:

    @staticmethod
    def format_replaceXMLEntities(xml):
        for k, v in [('&lt;', '<'), ('&gt;', '>')]:
            xml = xml.replace(k, v)

        return xml

    @staticmethod
    def format_removeXMLPrefixes(xml):
        return re.sub(r'(</?)[\w]+:', '\\1', xml)

    @staticmethod
    def format_removeXMLNamespaces(value):
        return re.sub(r'\{[a-z.:/]+\}', '', value)

    @staticmethod
    def cursor_to_dict(cursor):
        columns = [i[0] for i in cursor.description]
        return [dict(zip(columns, row)) for row in cursor]

    @staticmethod
    def get_proxies():
        proxies = {}

        if app.config['PROXY_HOST']:
            for protocol in ('http', 'https'):
                proxies.update({
                    protocol: (
                        'http://' +
                        app.config['PROXY_USER'] + ':' +
                        b64decode(app.config['PROXY_PASS']) + '@' +
                        app.config['PROXY_HOST'] + ':' +
                        str(app.config['PROXY_PORT'])
                    )
                })

        return proxies
