from __future__ import unicode_literals

import logging
import requests

from django.template.loader import render_to_string
from django.utils.translation import ugettext as _

from bs4 import BeautifulSoup

from requests.exceptions import ConnectionError

from .models import SMSMessage
from .conf import SMS_URL, SMS_USER, SMS_PASSWORD, SMS_DEBUG


LOGGER = logging.getLogger('django-sms-operator')

class Sender(object):

    TEMPLATES = {
        'SMS':'sms/send.xml',
        'SMS-Status': 'sms/status.xml'
     }

    def _construct_request(self, type, extra_context=None):
        extra_context = extra_context or {}
        context = {
            'type': type,
            'username': SMS_USER,
            'password': SMS_PASSWORD,
            'type_template':self.TEMPLATES.get(type)
        }

        context.update(extra_context)

        return render_to_string('sms/message.xml', context)

    def _send_request(self, type, extra_context=None):
        try:
            return requests.post(SMS_URL, data={'xml': self._construct_request(type, extra_context)})
        except ConnectionError:
            return None

    def _update_status(self, msg_qs, resp):
        if not resp or resp.content and msg_qs.exists():
            LOGGER.warning(_('SMS messages state with numbers: %s can not be updated because service is unavailable.'),
                           ', '.join((phone for msg.phone in msg_qs)))
        else:
            bs = BeautifulSoup(resp.content)
            pk_list = set(msg_qs.values_list('pk', flat=True))

            for data_item in bs.find_all('dataitem'):
                status = int(data_item.status.string)
                id = int(data_item.smsid.string)
                msg = msg_qs.get(pk=id)
                msg.sender_state = status
                msg.save()

                if msg.failed:
                    LOGGER.warning(_('SMS messages with number: %s failed to sent %s reason is %s.'), msg.phone,
                                   msg.get_sender_state_display())

                pk_list.remove(id)

            unknown_msg_qs = SMSMessage.objects.filter(pk__in=pk_list)
            if unknown_msg_qs.exists():
                for id in unknown_msg_qs:
                    msg = msg_qs.get(pk=id)
                    msg.sender_state = 15
                    msg.save()
                LOGGER.warning(_('SMS messages with numbers: %s can not be updated because had neber been sent.'),
                               ', '.join((phone for msg.phone in unknown_msg_qs)))

    def update_status(self):
        msg_qs = SMSMessage.objects.filter(state=SMSMessage.STATE.WAITING)

        if msg_qs.exists():
            self._update_status(msg_qs, self._send_request('SMS-Status', {'items': msg_qs}))

        return msg_qs

    def send(self, phone, text):
        new_message = SMSMessage.objects.create(phone=phone, text=text)
        msg_qs = SMSMessage.objects.filter(pk=new_message.pk)
        resp = self._send_request('SMS', {'items': msg_qs})
        if not resp:
            new_message.sender_state = 16
            new_message.save()
            LOGGER.warning(_('SMS messages with number: %s failed to sent %s reason is %s.'), msg.phone,
                           msg.get_sender_state_display())
        else:
            self._update_status(msg_qs, resp)
        return new_message


class DebugSender(Sender):

    def update_status(self):
        return SMSMessage.objects.none()

    def send(self, phone, text):
        return SMSMessage.objects.create(phone=phone, text=text, sender_state=18)


sender = Sender() if not SMS_DEBUG else DebugSender()