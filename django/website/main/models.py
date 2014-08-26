from django.db import models


class LatestVersion(models.Model):
    # This should only ever be an actual tag
    tag_name = models.CharField(max_length=30)

    def __unicode__(self):
        return u'%s' % self.tag_name


class CachedStandard(models.Model):
    # This could be a sha
    tag_name = models.CharField(max_length=100)
    standard = models.TextField(blank=True)
    vocabulary = models.TextField(blank=True)
    release_schema = models.TextField(blank=True)
    record_schema = models.TextField(blank=True)

    def __unicode__(self):
        return u'%s' % self.tag_name
