from netbox.tables import NetBoxTable
from netbox.tables.columns import ToggleColumn
from django_tables2 import Column
from netbox_cvexplorer.models import CVE

class CVETable(NetBoxTable):
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