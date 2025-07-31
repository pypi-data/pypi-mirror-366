from django.urls import path
from .views import CVEEntryListView, CVESourceListView, CVESourceCreateView, CVESourceUpdateView

urlpatterns = [
    path('entries/', CVEEntryListView.as_view(), name='cveentry_list'),
    path('sources/', CVESourceListView.as_view(), name='cvesource_list'),
    path('sources/add/', CVESourceCreateView.as_view(), name='cvesource_add'),
    path('sources/<int:pk>/edit/', CVESourceUpdateView.as_view(), name='cvesource_edit'),
]