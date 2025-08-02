from utilities.tables import BaseTable, ToggleColumn
from django_tables2 import Column
from netbox_cvexplorer.models import CVE

class CVETable(BaseTable):
    pk = ToggleColumn()
    cve_number = Column(linkify=True)
    title = Column()
    score = Column()
    status = Column()
    date_imported = Column()
    date_updated = Column()

    class Meta:
        model = CVE
        fields = ('pk', 'cve_number', 'title', 'score', 'status', 'date_imported', 'date_updated')
        default_columns = ('pk', 'cve_number', 'title', 'score')
