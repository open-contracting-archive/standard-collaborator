# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'CachedStandard.record_schema'
        db.add_column(u'main_cachedstandard', 'record_schema',
                      self.gf('django.db.models.fields.TextField')(default='', blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'CachedStandard.record_schema'
        db.delete_column(u'main_cachedstandard', 'record_schema')


    models = {
        u'main.cachedstandard': {
            'Meta': {'object_name': 'CachedStandard'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'record_schema': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'release_schema': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'standard': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'tag_name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'vocabulary': ('django.db.models.fields.TextField', [], {'blank': 'True'})
        },
        u'main.latestversion': {
            'Meta': {'object_name': 'LatestVersion'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'tag_name': ('django.db.models.fields.CharField', [], {'max_length': '30'})
        }
    }

    complete_apps = ['main']