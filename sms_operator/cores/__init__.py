from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from is_core.main import UIRestModelISCore

from sms_operator.models import SMSMessage


class SMSMessageIsCore(UIRestModelISCore):
    model = SMSMessage
    list_display = (
        'created_at', 'state', 'sender_state', 'phone'
    )
    abstract = True
    form_fields = ('created_at', 'state', 'sender_state', 'phone', 'text')

    def has_create_permission(self, request, obj=None):
        return False

    def has_update_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
