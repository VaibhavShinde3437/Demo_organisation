from django.db import models
from organizations.models import Organization

class CustomOrganization(Organization):
    parent = models.ForeignKey("self", on_delete=models.CASCADE, null=True, blank=True)
