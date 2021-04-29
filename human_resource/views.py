from django.shortcuts import render, redirect
from django.contrib import messages	
import random
from .models import *
from .forms import *
from django.contrib.auth.decorators import login_required
from .decorators import *



############# Employee Home ############
@hr_required
@login_required
def employee_home(request):
	context = {}
	template_name = 'hr-home.html'

	return render(request, template_name, context)	


######### Employee Form ##########
@hr_required
@login_required
def employee_form(request):
	if request.method == 'POST':
		employee_form = EmployeeModelForm(request.POST)

		if employee_form.is_valid():
			employee_form.save()
			employee_form = EmployeeModelForm()
			redirect('human_resource:employee-registration')

	else:
		employee_form = EmployeeModelForm()

	context ={
		'e_form': employee_form,
	}
	template_name = 'employee-registration.html'

	return render(request, template_name, context)


########## Employee Update Form ############
@hr_required
@login_required
def employee_update(request, *args, **kwargs):
	id = kwargs.get('id')
	employee = Employee.objects.filter(id=id).first()
	if request.method == 'POST':
		employee_form = EmployeeModelForm(request.POST or None, request.FILES, instance=employee)
		if employee_form.is_valid():
			employee = employee_form.save()
			department = employee.department.name
			employee_no = employee.id
			employee_number = department.upper()[:2] + employee_id() + str(employee_no)
			employee.id_no = employee_number
			employee.save()		
			return redirect('human_resource:employee-list')
	else:
		employee_form = EmployeeModelForm(instance=employee)
	context = {
		'e_form' : employee_form,
	}
	template_name = 'employee-update.html'
	return render(request, template_name, context)	


########## Employee Delete Form ############
@hr_required
@login_required
def employee_delete(request, *args, **kwargs):
	id = kwargs.get('id')
	employee = Employee.objects.filter(id=id).first()
	employees = Employee.objects.all()

	try:
		employee.delete()
		messages.success(request, f'{employee.full_name} was deleted')
		return redirect('human_resource:employee-list')


	except Exception as err:
		print(err)
		messages.info(request, f'Error : {err}')
		return redirect('human_resource:employee-list')

				
	context = {
		'employees' : employees,
	}				
	template_name = 'employees-list.html'
	return render(request, template_name, context)	


########### Random ID generator ################
def employee_id():
	number = int(random.random() * 10000)
	return str(number)


############### Employees List#######################	
@hr_required
@login_required
def employee_list(request, *args, **kwargs):
	employees = Employee.objects.all()
	if request.method == 'POST':
		employee_form = EmployeeModelForm(request.POST, request.FILES)

		if employee_form.is_valid():
			employee = employee_form.save()
			department = employee.department.name
			employee_no = employee.id
			employee_number = department.upper()[:2] + employee_id() + str(employee_no)
			employee.id_no = employee_number
			employee_form.save() 
			employee_form = EmployeeModelForm()
			return redirect('human_resource:employee-list')

	else:
		employee_form = EmployeeModelForm()

	context = {
		'employees' : employees,
		'e_form': employee_form,
	}
	template_name = 'employees-list.html'
	return render(request, template_name, context)


