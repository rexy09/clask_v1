from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import user_passes_test


def hr_required(function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url='administration:login'):
	actual_decorator = user_passes_test(
		lambda u: u.is_active and u.is_staff or u.user_employee.position == 'Human Resource Manager' or u.user_employee.position == 'Human Resource Officer' or u.user_employee.position == 'Financial Manager' or u.user_employee.position == 'CEO' or u.user_employee.position == 'Accountant' or u.user_employee.position == 'Human Resource Manager' or u.user_employee.position == 'Human Resource Officer',
		login_url=login_url,
		redirect_field_name=redirect_field_name
		)

	if function:
		return actual_decorator(function)
	return actual_decorator	


def store_required(function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url='administration:login'):
	actual_decorator = user_passes_test(
	lambda u: u.is_active and u.is_staff or u.user_employee.position == 'Store Officer' or u.user_employee.position == 'Assistant Store Officer',
	login_url=login_url,
	redirect_field_name=redirect_field_name
	)

	if function:
		return actual_decorator(function)
	return actual_decorator


def store_report_required(function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url='administration:login'):
	actual_decorator = user_passes_test(
	lambda u: u.is_active and u.is_staff or u.user_employee.position == 'Store Officer' or u.user_employee.position == 'Assistant Store Officer' or u.user_employee.position == 'CEO' or u.user_employee.position == 'Accountant' or u.user_employee.position == 'Financial Manager',
	login_url=login_url,
	redirect_field_name=redirect_field_name
	)

	if function:
		return actual_decorator(function)
	return actual_decorator


def finance_required(function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url='administration:login'):
	actual_decorator = user_passes_test(
	lambda u: u.is_active and u.is_staff or u.user_employee.position == 'Accountant' or u.user_employee.position == 'Financial Manager',
	login_url=login_url,
	redirect_field_name=redirect_field_name
	)

	if function:
		return actual_decorator(function)
	return actual_decorator		


def finance_report_required(function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url='administration:login'):
	actual_decorator = user_passes_test(
	lambda u: u.is_active and u.is_staff or u.user_employee.position == 'Accountant' or u.user_employee.position == 'Financial Manager' or u.user_employee.position == 'CEO',
	login_url=login_url,
	redirect_field_name=redirect_field_name
	)

	if function:
		return actual_decorator(function)
	return actual_decorator	


def staff_required(function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url='administration:login'):
	actual_decorator = user_passes_test(
		lambda u: u.is_active and u.is_staff,
		login_url=login_url,
		redirect_field_name=redirect_field_name
		)

	if function:
		return actual_decorator(function)
	return actual_decorator	


def fm_required(function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url='administration:login'):
	actual_decorator = user_passes_test(
		lambda u: u.is_active and u.is_staff or u.user_employee.position == 'Financial Manager',
		login_url=login_url,
		redirect_field_name=redirect_field_name
		)

	if function:
		return actual_decorator(function)
	return actual_decorator	


def procurement_required(function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url='administration:login'):
	actual_decorator = user_passes_test(
		lambda u: u.is_active and u.is_staff or u.user_employee.position == 'Procurement Manager' or u.user_employee.position == 'Procurement Officer',
		login_url=login_url,
		redirect_field_name=redirect_field_name
		)

	if function:
		return actual_decorator(function)
	return actual_decorator	


def procurement_finance_ceo_required(function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url='administration:login'):
	actual_decorator = user_passes_test(
	lambda u: u.is_active and u.is_staff or u.user_employee.position == 'Procurement Manager' or u.user_employee.position == 'Procurement Officer' or u.user_employee.position == 'Financial Manager' or u.user_employee.position == 'CEO' or u.user_employee.position == 'Accountant',
	login_url=login_url,
	redirect_field_name=redirect_field_name
	)

	if function:
		return actual_decorator(function)
	return actual_decorator


def accountant_required(function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url='administration:login'):
	actual_decorator = user_passes_test(
		lambda u: u.is_active and u.is_staff or u.user_employee.position == 'Accountant',
		login_url=login_url,
		redirect_field_name=redirect_field_name
		)

	if function:
		return actual_decorator(function)
	return actual_decorator		


def ceo_required(function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url='administration:login'):
	actual_decorator = user_passes_test(
	lambda u: u.is_active and u.is_staff or u.user_employee.position == 'CEO',
	login_url=login_url,
	redirect_field_name=redirect_field_name
	)

	if function:
		return actual_decorator(function)
	return actual_decorator		