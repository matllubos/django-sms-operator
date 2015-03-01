from django.conf import settings


SMS_URL = 'https://www.sm-operator.cz/webservices/webservice.aspx'
SMS_USER = getattr(settings, 'SMS_USER', None)
SMS_PASSWORD = getattr(settings, 'SMS_PASSWORD', None)
SMS_DEBUG = getattr(settings, 'SMS_DEBUG', None)