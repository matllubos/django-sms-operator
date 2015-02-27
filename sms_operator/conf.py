from django.conf import settings


SMS_URL = 'https://www.sms-operator.cz/webservices/webservice.aspx'
SMS_USER = getattr(settings, 'SMS_USER')
SMS_USER = getattr(settings, 'SMS_PASSWORD')