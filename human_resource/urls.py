from django.urls import path
from . import views

app_name = 'human_resource'

urlpatterns = [
	path('', views.employee_home, name="human-resource-home"),
	path('employees/', views.employee_list, name="employee-list"),
	path('<int:id>/employee/edit/', views.employee_update, name="employee-update"),
	path('<int:id>/employee/delete/', views.employee_delete, name="employee-delete"),
]