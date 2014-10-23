# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting model 'LatestVersion'
        db.delete_table(u'main_latestversion')


    def backwards(self, orm):
        # Adding model 'LatestVersion'
        db.create_table(u'main_latestversion', (
            ('tag_name', self.gf('django.db.models.fields.CharField')(max_length=30)),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal(u'main', ['LatestVersion'])


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
            'vocabulary': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'worked_example': ('django.db.models.fields.TextField', [], {'blank': 'True'})
        }
    }

    complete_apps = ['main']