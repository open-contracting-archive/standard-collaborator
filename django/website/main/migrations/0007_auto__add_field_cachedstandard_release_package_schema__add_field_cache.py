# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'CachedStandard.release_package_schema'
        db.add_column(u'main_cachedstandard', 'release_package_schema',
                      self.gf('django.db.models.fields.TextField')(default='', blank=True),
                      keep_default=False)

        # Adding field 'CachedStandard.versioned_release_schema'
        db.add_column(u'main_cachedstandard', 'versioned_release_schema',
                      self.gf('django.db.models.fields.TextField')(default='', blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'CachedStandard.release_package_schema'
        db.delete_column(u'main_cachedstandard', 'release_package_schema')

        # Deleting field 'CachedStandard.versioned_release_schema'
        db.delete_column(u'main_cachedstandard', 'versioned_release_schema')


    models = {
        u'main.cachedstandard': {
            'Meta': {'object_name': 'CachedStandard'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'merging': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'record_schema': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'release_package_schema': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'release_schema': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'standard': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'tag_name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'versioned_release_schema': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'vocabulary': ('django.db.models.fields.TextField', [], {'blank': 'True'})
        },
        u'main.latestversion': {
            'Meta': {'object_name': 'LatestVersion'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'tag_name': ('django.db.models.fields.CharField', [], {'max_length': '30'})
        }
    }

    complete_apps = ['main']