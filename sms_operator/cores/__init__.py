from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _
from django.conf import settings

from is_core.main import UIRestModelISCore

from sms_operator.models import SMSMessage, SMSTemplate


class SMSMessageIsCore(UIRestModelISCore):
    model = SMSMessage
    list_display = ('created_at', 'state', 'sender_state', 'phone')
    abstract = True
    form_fields = ('created_at', 'state', 'sender_state', 'phone', 'text')

    def has_create_permission(self, request, obj=None):
        return False

    def has_update_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class SMSTemplateIsCore(UIRestModelISCore):
    model = SMSTemplate
    list_display = ('slug',)
    abstract = True
    form_fields = ('slug', 'body')
    form_readonly_fields = ('slug',)

    def get_form_fields(self, request, obj=None):
        form_fields = ['slug']
        for language_code, _ in settings.LANGUAGES:
            form_fields.append('body_%s' % language_code)
        return form_fields

    def has_create_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
