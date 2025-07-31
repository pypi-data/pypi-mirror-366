from django.db import models
from extras.models import JournalEntry, ObjectChange
from utilities.models import ChangeLoggedModel

class CVEEntry(ChangeLoggedModel):
    cve_id = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=50)
    description = models.TextField()
    information = models.TextField(blank=True)
    date_created = models.DateField()
    date_updated = models.DateField()
    cve_score = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return self.cve_id