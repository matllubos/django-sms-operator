from __future__ import unicode_literals

import logging
import requests

from unidecode import unidecode

from django.template.loader import render_to_string
from django.utils.translation import ugettext as _
from django.template import Context, Template

from bs4 import BeautifulSoup

from requests.exceptions import ConnectionError, RequestException, Timeout

from .models import SMSMessage, SMSTemplate
from .conf import SMS_URL, SMS_USER, SMS_PASSWORD, SMS_DEBUG


LOGGER = logging.getLogger('sms-operator')

class Sender(object):

    class SMSSendingError(Exception):
        pass

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
        except RequestException:
            return None

    def _update_status(self, msg_qs, resp):
        if (not resp or not resp.content) and msg_qs.exists():
            LOGGER.warning(_('SMS messages state with numbers: %s can not be updated because service is unavailable.'),
                           ', '.join((msg.phone for msg in msg_qs)))
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
                    LOGGER.warning(_('SMS messages with number %(phone)s failed to sent the reason is "%(reason)s".') %
                                   {'phone': msg.phone, 'reason': msg.get_sender_state_display()})

                pk_list.remove(id)

            unknown_msg_qs = SMSMessage.objects.filter(pk__in=pk_list)
            if unknown_msg_qs.exists():
                LOGGER.warning(_('SMS messages with numbers %s can not be updated because service does not return '
                                 'right informations.'),
                               ', '.join((msg.phone for msg in unknown_msg_qs)))

    def update_status(self):
        msg_qs = SMSMessage.objects.filter(state=SMSMessage.STATE.WAITING)

        if msg_qs.exists():
            self._update_status(msg_qs, self._send_request('SMS-Status', {'items': msg_qs}))

        return msg_qs

    def send(self, phone, text):
        new_message = SMSMessage.objects.create(phone=phone, text=unidecode(text).strip())
        msg_qs = SMSMessage.objects.filter(pk=new_message.pk)
        resp = self._send_request('SMS', {'items': msg_qs})
        if not resp or not resp.content:
            new_message.sender_state = 16
            new_message.save()
            LOGGER.warning(_('SMS messages with number %(phone)s failed to sent the reason is "%(reason)s".') %
                           {'phone': new_message.phone, 'reason': new_message.get_sender_state_display()})
        else:
            self._update_status(msg_qs, resp)
        return new_message

    def send_template(self, phone, slug, context):
        try:
            sms_template = SMSTemplate.objects.get(slug=slug)
            return self.send(phone, Template(sms_template.body).render(Context(context)).encode('utf-8'))
        except SMSTemplate.DoesNotExist:
            LOGGER.error(_('SMS message template with slug %(slug)s does not exist. '
                           'The message to %(phone)s can not be sent.') %
                         {'phone': phone, 'slug': slug})
            raise self.SMSSendingError('SMS message template with slug %s does not exist' % slug)


class DebugSender(Sender):

    def update_status(self):
        return SMSMessage.objects.none()

    def send(self, phone, text):
        return SMSMessage.objects.create(phone=phone, text=text, sender_state=18)


sender = Sender() if not SMS_DEBUG else DebugSender()