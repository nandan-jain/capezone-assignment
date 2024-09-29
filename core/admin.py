from django.contrib import admin
from .models import Project, Deal, DealProject

# Register your models here.
admin.site.register([Project, Deal, DealProject])
