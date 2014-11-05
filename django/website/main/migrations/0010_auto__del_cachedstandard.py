# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting model 'CachedStandard'
        db.delete_table(u'main_cachedstandard')


    def backwards(self, orm):
        # Adding model 'CachedStandard'
        db.create_table(u'main_cachedstandard', (
            ('versioned_release_schema', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('vocabulary', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('standard', self.gf('django.db.models.fields.TextField')(blank=True)),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('release_package_schema', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('worked_example', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('merging', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('tag_name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('release_schema', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('record_schema', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal(u'main', ['CachedStandard'])


    models = {
        
    }

    complete_apps = ['main']