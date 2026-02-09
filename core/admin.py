from django.contrib import admin

from .models import Cadet, LifeLog, Project, Resource

admin.site.register(Cadet)
admin.site.register(Project)
admin.site.register(LifeLog)
admin.site.register(Resource)
