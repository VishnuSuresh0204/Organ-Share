from django.contrib import admin
from .models import Login, Recipient, Donor, Doctor

admin.site.register(Login)
admin.site.register(Recipient)
admin.site.register(Donor)
admin.site.register(Doctor)
