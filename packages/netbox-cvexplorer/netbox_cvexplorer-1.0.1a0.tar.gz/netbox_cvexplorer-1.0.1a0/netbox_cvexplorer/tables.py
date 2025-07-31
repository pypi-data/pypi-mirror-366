
# netbox_cvexplorer/tables.py
import django_tables2 as tables
from .models import CVEEntry, CVESource

class CVEEntryTable(tables.Table):
    class Meta:
        model = CVEEntry
        fields = ('cve_id', 'status', 'description', 'cve_score', 'date_updated')

class CVESourceTable(tables.Table):
    class Meta:
        model = CVESource
        fields = ('name', 'url', 'provider', 'interval', 'timestamp_last')