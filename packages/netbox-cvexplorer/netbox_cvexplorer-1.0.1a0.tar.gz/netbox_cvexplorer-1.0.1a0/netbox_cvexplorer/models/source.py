from django.db import models
from utilities.models import ChangeLoggedModel

class CVESource(ChangeLoggedModel):
    name = models.CharField(max_length=100)
    url = models.URLField()
    provider = models.CharField(max_length=100)
    interval = models.IntegerField(help_text="Abrufintervall in Stunden")
    timestamp_last = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.name
