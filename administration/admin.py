from django.contrib import admin
from .models import *


admin.site.site_header = 'Clask'


@admin.register(Business)
class BusinessModelAdmin(admin.ModelAdmin):
	list_display = ['pk', 'name', 'created_at', 'updated_at',]
	list_display_links = ['pk', 'name']



@admin.register(Branch)
class BranchModelAdmin(admin.ModelAdmin):
	list_display = ['pk', 'business', 'location', 'created_at', 'updated_at',]
	list_display_links = ['pk', 'business', 'location']


@admin.register(Department)
class DepartmentModelAdmin(admin.ModelAdmin):
	list_display = ['pk', 'name',  'created_at', 'updated_at',]
	list_display_links = ['pk', 'name']
