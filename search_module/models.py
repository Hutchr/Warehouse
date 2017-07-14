from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class SearchTerm(models.Model):
    q = models.CharField(max_length=50)
    date = models.DateTimeField(auto_now_add=True)
    ip_address = models.IPAddressField()
    user = models.ForeignKey(User, null=True)

    def __str__(self):
        return self.q