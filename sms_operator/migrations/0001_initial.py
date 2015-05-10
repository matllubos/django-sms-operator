# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'SMSMessage'
        db.create_table(u'sms_operator_smsmessage', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('state', self.gf(u'sms_operator.models.SMSState')()),
            ('sender_state', self.gf('django.db.models.fields.PositiveIntegerField')(default=17)),
            ('phone', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('text', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal(u'sms_operator', ['SMSMessage'])

        # Adding model 'SMSTemplate'
        db.create_table(u'sms_operator_smstemplate', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('slug', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=100)),
            ('body_cs', self.gf('django.db.models.fields.TextField')(null=True)),
        ))
        db.send_create_signal(u'sms_operator', ['SMSTemplate'])


    def backwards(self, orm):
        # Deleting model 'SMSMessage'
        db.delete_table(u'sms_operator_smsmessage')

        # Deleting model 'SMSTemplate'
        db.delete_table(u'sms_operator_smstemplate')


    models = {
        u'sms_operator.smsmessage': {
            'Meta': {'ordering': "(u'-created_at',)", 'object_name': 'SMSMessage'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'sender_state': ('django.db.models.fields.PositiveIntegerField', [], {'default': '17'}),
            'state': (u'sms_operator.models.SMSState', [], {}),
            'text': ('django.db.models.fields.TextField', [], {})
        },
        u'sms_operator.smstemplate': {
            'Meta': {'object_name': 'SMSTemplate'},
            'body_cs': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '100'})
        }
    }

    complete_apps = ['sms_operator']