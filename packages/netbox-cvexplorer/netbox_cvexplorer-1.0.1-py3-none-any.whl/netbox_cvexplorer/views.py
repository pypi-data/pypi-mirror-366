from django.views.generic import CreateView, UpdateView
from utilities.views import ObjectListView
from extras.forms import CustomFieldModelForm
from .models import CVEEntry, CVESource
from .forms import CVEEntryForm, CVESourceForm
from .tables import CVEEntryTable, CVESourceTable

class CVESourceForm(CustomFieldModelForm):
    class Meta:
        model = CVESource
        fields = '__all__'
        
class CVEEntryListView(ObjectListView):
    queryset = CVEEntry.objects.all()
    table = CVEEntryTable
    template_name = 'netbox_cvexplorer/cveentry_list.html'

class CVESourceListView(ObjectListView):
    queryset = CVESource.objects.all()
    table = CVESourceTable
    template_name = 'netbox_cvexplorer/cvesource_list.html'

class CVESourceCreateView(CreateView):
    model = CVESource
    form_class = CVESourceForm
    template_name = 'netbox_cvexplorer/cvesource_form.html'
    success_url = '/plugins/netbox-cvexplorer/sources/'

class CVESourceUpdateView(UpdateView):
    model = CVESource
    form_class = CVESourceForm
    template_name = 'netbox_cvexplorer/cvesource_form.html'
    success_url = '/plugins/netbox-cvexplorer/sources/'
