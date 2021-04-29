from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from . import reports 



app_name = 'administration'


urlpatterns = [
	path('administrator/', views.administrator, name='administrator'),

	#Offline Page
	path('offline', views.offline, name='offline'),

    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),	
	path('business/registration/', views.business_list, name='business-list'),
	path('business/edit/<int:id>', views.business_edit, name='business-edit'),
	path('department/registration/', views.department_list, name='department-list'),
	path('branch/registration/', views.branch_list, name='branch-list'),
	path('department/edit/<int:id>/', views.department_edit, name='department-edit'),
	path('branch/edit/<int:id>/', views.branch_edit, name='branch-edit'),

	path('users/', views.user_list, name='users-list'),
	path('users/registration/<int:id>/', views.user_registration, name='user-registration'),
	path('users/edit/<int:id>/', views.user_edit, name='user-edit'),
	path('profile/', views.user_profile, name='user-profile'),
	path('profile/password-change/', views.change_password, name='password-change'),
	# AJAX URL
	path("get_business/", views.get_business, name="get_business"),
	path('<int:notification>/notification/read/', views.mark_notification_read, name="mark_notification_read"),
	#General Reports
	path("general/reports/", reports.general_reports, name="general_reports"),
	path("sales/reports/time/", reports.sales_time, name="sales_time"),
	path("<int:d>/sales/reports/", reports.sales_report, name="sales_report"),
	path("inventory/products/", reports.inventory_product, name="inventory_product"),
	path("inventory/products/reports/", reports.inventory_report, name="inventory_report"),
	path("procurement/reports/time/", reports.procurement_time, name="procurement_time"),
	path("<int:d>/procurement/reports/", reports.procurement_report, name="procurement_report"),
	path("opex/reports/time/", reports.opex_time, name="opex_time"),
	path("<int:d>/opex/reports/", reports.opex_report, name="opex-report"),
	path("customers/reports/", reports.customer_report, name="customer_report"),
    path("<int:d>/payroll/report/", reports.payroll_report, name="payroll-report"),
    path("reports/payroll/", reports.payroll_time, name="payroll-time"),

]