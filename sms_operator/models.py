from __future__ import unicode_literals

from django.db import models
from django.utils.translation import ugettext_lazy as _

from chamber.utils.datastructures import ChoicesNumEnum


class SMSMessage(models.Model):

    STATE = ChoicesNumEnum(
        ('DELIVERED', _('Delivered'), 0),
        ('NOT_DELIVERED', _('Not delivered'), 1),
        ('NUMBER_NOT_EXIST', _('Number not exist'), 2),
        ('TIMEOUT', _('Timeout'), 3),
        ('WRONG_NUMBER_FORMAT', _('Wrong number format'), 4),
        ('ERROR', _('Error'), 5),
        ('ERROR_NOT_SENT', _('Error not sent'), 6),
        ('TOO_LONG_TEXT', _('Too long text'), 7),
        ('PARTIALLY_DELIVERED_ERROR', _('Only partially delivered'), 10),
        ('SENDING', _('Sending'), 11),
        ('PARTIALLY_DELIVERED_SENDING', _('Partly delivered'), 12),
        ('PARTIALLY_NOT_DELIVERED_SENDING', _('Partly not delivered'), 13),
        ('WAITING', _('Waiting'), 99),
    )

    created_at = models.DateTimeField(verbose_name=_('created at'), null=False, blank=False, auto_now_add=True)
    submited_at = models.DateTimeField(verbose_name=_('submited at'), null=True, blank=True)
    state = models.PositiveIntegerField(verbose_name=_('state'), null=False, blank=False, choices=STATE.choices,
                                        default=STATE.WAITING)
    # TODO custom field
    phone = models.CharField(verbose_name=_('phone'), null=False, blank=False, max_length=20)
    text = models.models.TextField(verbose_name=_('description'), null=True, blank=False)

    def __unicode__(self):
        return self.phone

    class Meta:
        verbose_name = _('add-on')
        verbose_name_plural = _('add-ons')
