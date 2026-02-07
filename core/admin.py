from django.contrib import admin

from .models import Cadet, LifeLog, Project

admin.site.register(Cadet)
admin.site.register(Project)
admin.site.register(LifeLog)
