from django.urls import path
from .views import CVEListView

urlpatterns = [
    path('cve/', CVEListView.as_view(), name='cve_list'),
]
