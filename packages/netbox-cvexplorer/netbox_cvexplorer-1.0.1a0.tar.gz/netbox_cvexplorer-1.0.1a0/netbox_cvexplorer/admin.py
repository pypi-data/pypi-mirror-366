from django.contrib import admin
from .models import CVEEntry, CVESource

admin.site.register(CVEEntry)
admin.site.register(CVESource)