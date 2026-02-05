from django.db import models

# Create your models here.

class SiteVisit(models.Model):
    session_key = models.CharField(max_length=40, db_index=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)
    first_seen = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.session_key} @ {self.first_seen}"

class PageView(models.Model):
    session_key = models.CharField(max_length=40, db_index=True)
    path = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.session_key} - {self.path} @ {self.timestamp}"
