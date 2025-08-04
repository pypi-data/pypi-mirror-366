from django.views.generic import ListView
from netbox_cvexplorer.models import CVE
from netbox_cvexplorer.tables import CVETable

class CVEListView(ListView):
    model = CVE
    template_name = 'netbox_cvexplorer/cve_list.html'
    context_object_name = 'cve_list'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        table = CVETable(self.object_list)
        context['table'] = table
        return context
