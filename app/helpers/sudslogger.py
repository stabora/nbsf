# -*- coding: utf-8 -*-

from suds.plugin import MessagePlugin


class SudsLogger(MessagePlugin):

    def __init__(self):
        self.last_sent_message = None
        self.last_received_reply = None

    def sending(self, context):
        if context.envelope:
            self.last_sent_message = context.envelope

    def parsed(self, context):
        if context.reply:
            self.last_received_reply = context.reply

    def last_sent(self):
        return self.last_sent_message

    def last_received(self):
        return self.last_received_reply
