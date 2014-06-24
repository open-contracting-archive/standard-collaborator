# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'CachedStandard'
        db.create_table(u'main_cachedstandard', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('tag_name', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('standard', self.gf('django.db.models.fields.TextField')()),
            ('vocabulary', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal(u'main', ['CachedStandard'])


    def backwards(self, orm):
        # Deleting model 'CachedStandard'
        db.delete_table(u'main_cachedstandard')


    models = {
        u'main.cachedstandard': {
            'Meta': {'object_name': 'CachedStandard'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'standard': ('django.db.models.fields.TextField', [], {}),
            'tag_name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'vocabulary': ('django.db.models.fields.TextField', [], {})
        },
        u'main.latestversion': {
            'Meta': {'object_name': 'LatestVersion'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'tag_name': ('django.db.models.fields.CharField', [], {'max_length': '30'})
        }
    }

    complete_apps = ['main']