
from django import forms
from .models import CVEEntry, CVESource

class CVEEntryForm(forms.ModelForm):
    class Meta:
        model = CVEEntry
        fields = '__all__'

class CVESourceForm(forms.ModelForm):
    class Meta:
        model = CVESource
        fields = '__all__'
