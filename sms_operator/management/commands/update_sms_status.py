from __future__ import unicode_literals

from django.utils import timezone
from django.core.management.base import NoArgsCommand

from sms_operator.sender import sender


class Command(NoArgsCommand):

    def handle_noargs(self, **options):
        checked_messages_qs = sender.update_status()
        self.stdout.write('Update status of %s sms messages' % checked_messages_qs.count())
