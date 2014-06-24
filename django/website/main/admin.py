from django.contrib import admin
from .models import LatestVersion, CachedStandard

admin.site.register(LatestVersion)
admin.site.register(CachedStandard)
