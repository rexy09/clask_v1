from django.contrib import admin
from .models import *


admin.site.site_header = 'Clask'


@admin.register(Employee)
class EmployeeModelAdmin(admin.ModelAdmin):
	list_display = ['pk', 'full_name', 'birth_date', 'gender', 'id_no', 'department','branch','position', 'salary', 'starting_date', 'contract_period', 'performance']
	list_display_links = ['pk', 'full_name']
