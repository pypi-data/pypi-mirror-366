from netbox.views import generic
from netbox_cvexplorer.models import CVE
from netbox_cvexplorer.tables import CVETable

class CVEListView(generic.ObjectListView):
    queryset = CVE.objects.all()
    table = CVETable
    template_name = 'netbox_cvexplorer/cve/cve_list.html'
