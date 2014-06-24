from django.db import models


class LatestVersion(models.Model):
    # This should only ever be an actual tag
    tag_name = models.CharField(max_length=30)


class CachedStandard(models.Model):
    # This could be a sha
    tag_name = models.CharField(max_length=100)
    standard = models.TextField(blank=True)
    vocabulary = models.TextField(blank=True)
