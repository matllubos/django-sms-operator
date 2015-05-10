from __future__ import unicode_literals

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.datastructures import SortedDict

from easymode.i18n.decorators import I18n

from chamber.utils.datastructures import ChoicesNumEnum
from chamber.models.fields import SouthMixin


class SMSChoicesNumEnum(ChoicesNumEnum):

    def __init__(self, *items):
        """
        Receives item with four values key, label, i and send state choices
        """

        super(SMSChoicesNumEnum, self).__init__(*((key, label, i) for key, label, i, _ in items))
        self.sender_enum = SortedDict()
        for (key, label, i, sender_choices) in items:
            for j, choice_label in sender_choices:
                self.sender_enum[j] = (choice_label, i)

    @property
    def sender_choices(self):
        return [(val, choice[0]) for val, choice in self.sender_enum.items()]

    def get_value_from_sender_value(self, sender_val):
        """
        Return value according to sender_val
        """

        return self.sender_enum.get(sender_val)[1] if sender_val in self.sender_enum else self.ERROR


class SMSState(SouthMixin, models.PositiveIntegerField):

    def __init__(self, *args, **kwargs):
        self.enum = kwargs.pop('enum', None)
        if self.enum:
            kwargs['choices'] = self.enum.choices
        super(SMSState, self).__init__(*args, **kwargs)

    def pre_save(self, model_instance, add):
        """
        This model field is not editable value is set according to sender_state value
        """
        if self.enum:
            value = self.enum.get_value_from_sender_value(getattr(model_instance, 'sender_state'))
            setattr(model_instance, self.attname, value)
        return value


class SMSMessage(models.Model):

    STATE = SMSChoicesNumEnum(
        ('NEW', _('New'), 0, (
            (17, _('Not send')),
        )),
        ('WAITING', _('Waiting'), 1, (
            (11, _('Unknown state')),
            (12, _('Only partly delivered')),
            (13, _('Only partly delivered')),
            (14, _('Only partly delivered')),
        )),
        ('DELIVERED', _('Delivered'), 2, (
            (0, _('Delivered')),
        )),
        ('ERROR', _('Error'), 3, (
            (1, _('Failed')),
            (2, _('Number does not exist')),
            (3, _('Timeout')),
            (4, _('Number has wrong format')),
            (5, _('GSM operator error')),
            (6, _('GSM operator error')),
            (7, _('SMS text too long')),
            (10, _('Only partly delivered')),
            (15, _('Message not found')),
            (16, _('Connection error')),
        )),
        ('DEBUG', _('Debug'), 4, (
            (18, _('Debug')),
        )),
    )

    created_at = models.DateTimeField(verbose_name=_('created at'), null=False, blank=False, auto_now_add=True)
    state = SMSState(verbose_name=_('state'), null=False, blank=False, enum=STATE, editable=False)
    sender_state = models.PositiveIntegerField(verbose_name=_('sender state'), null=False, blank=False,
                                               choices=STATE.sender_choices, default=17)
    phone = models.CharField(verbose_name=_('phone'), null=False, blank=False, max_length=20)
    text = models.TextField(verbose_name=_('text'), null=False, blank=False)

    @property
    def failed(self):
        return self.state == self.STATE.ERROR

    def __unicode__(self):
        return self.phone

    class Meta:
        verbose_name = _('Log SMS message')
        verbose_name_plural = _('Log SMS messages')
        ordering = ('-created_at',)


@I18n('body')
class SMSTemplate(models.Model):
    slug = models.SlugField(max_length=100, null=False, blank=False, unique=True, verbose_name=_('slug'))
    body = models.TextField(null=True, blank=False, verbose_name=_('message body'))

    def __unicode__(self):
        return self.slug

    class Meta:
        verbose_name = _('SMS template')
        verbose_name_plural = _('SMS templates')
