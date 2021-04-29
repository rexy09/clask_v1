from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth import get_user_model, authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib import messages	
from .models import *
from .forms import *
from business.forms import PayrollForm
from business.models import Payroll, Sale
from human_resource.models import Employee
from django.http import JsonResponse
from django.core import serializers
from notifications.models import Notification
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from human_resource.decorators import *
from datetime import date, timedelta
from django.db.models import Sum
from .graph import (
	sales_graph_data, 
	expense_graph_data, 
	stock_graph_data)


######### Offline Page #########
def offline(request):
	context = {}
	template_name = 'offline.html'
	return render(request, template_name, context)

######### Index Page #########
@login_required
def index(request):
	# Business list
	business = Business.objects.all().order_by('name')

	context = {
		'sales':sales_graph_data(business=business),
		'expenses':expense_graph_data(business=business),
		'stock':stock_graph_data(business=business),
	}
	template_name = 'index.html'
	return render(request, template_name, context)


######### Administrator Page #########
@staff_required
@login_required
def administrator(request):
	context = {}
	template_name = 'administrator.html'
	return render(request, template_name, context)


########## Business Form ############
@staff_required
@login_required
def business_list(request):
	businesses = Business.objects.all()

	if request.method == 'POST':
		bussiness_form = BusinessModelForm(request.POST)

		if bussiness_form.is_valid():
			bussiness_form.save()
			bussiness_form = BusinessModelForm()
			return redirect('administration:business-list')

	else:
		bussiness_form = BusinessModelForm()
	context = {
		'b_form' : bussiness_form,
		'businesses': businesses,
	}
	template_name = 'business-list.html'
	return render(request, template_name, context)


########## Business Form ############
@staff_required
@login_required
def business_edit(request, *args, **kwargs):
	id = kwargs.get('id')
	business = Business.objects.filter(id=id).first()

	if request.method == 'POST':
		bussiness_form = BusinessModelForm(request.POST or None, instance=business)

		if bussiness_form.is_valid():
			bussiness_form.save()
			return redirect('administration:business-list')

	else:
		bussiness_form = BusinessModelForm(instance=business)
	context = {
		'b_form' : bussiness_form,
	}
	template_name = 'business-edit.html'
	return render(request, template_name, context)



########## Branch List ############
@staff_required
@login_required
def branch_list(request):

	branches = Branch.objects.all()

	if request.method == 'POST':
		branch_form = BranchModelForm(request.POST)

		if branch_form.is_valid():
			branch_form.save()
			return redirect('administration:branch-list')

	else:
		branch_form = BranchModelForm()

	context = {
		'branches' : branches,
		'br_form' : branch_form,
	}
	template_name = 'branch-list.html'
	return render(request, template_name, context)




########## Department List ############
@staff_required
@login_required
def department_list(request):

	departments = Department.objects.all()	

	if request.method == 'POST':
		department_form = DepartmentModelForm(request.POST)

		if department_form.is_valid():
			department_form.save()
			return redirect('administration:department-list')

	else:
		department_form = DepartmentModelForm()

	context = {
		'departments' : departments,
		'dpt_form' : department_form,
	}
	template_name = 'department-list.html'
	return render(request, template_name, context)



########## Department Edit ############
@staff_required
@login_required
def department_edit(request, *args, **kwargs):
	id = kwargs.get('id')
	department = Department.objects.filter(id=id).first()

	if request.method == 'POST':
		# branch_form = BranchModelForm(request.POST)
		department_form = DepartmentModelForm(request.POST or None, instance=department)

		if department_form.is_valid():
			department_form.save()
			return redirect('administration:department-list')



	else:
		branch_form = BranchModelForm()
		department_form = DepartmentModelForm(instance=department)

	context = {
		'dpt_form' : department_form,
	}
	template_name = 'department-edit.html'
	return render(request, template_name, context)



########## Branch Edit ############
@staff_required
@login_required
def branch_edit(request, *args, **kwargs):
	id = kwargs.get('id')
	branch = Branch.objects.filter(id=id).first()

	if request.method == 'POST':
		branch_form = BranchModelForm(request.POST or None, instance=branch)

		if branch_form.is_valid():
			branch_form.save()
			return redirect('administration:branch-list')


	else:
		branch_form = BranchModelForm(instance=branch)

	context = {
		'br_form' : branch_form,
	}
	template_name = 'branch-edit.html'
	return render(request, template_name, context)


# AJAX request
@login_required
def get_business(request):
	if request.is_ajax():
		business =  Business.objects.all().order_by('name')
		data = serializers.serialize('json', business)
		return JsonResponse(data, safe=False)

# Mark notification as READ
@login_required
def mark_notification_read(request, *args, **kwargs):
	notification = Notification.objects.filter(id=kwargs["notification"], recipient=request.user).first()
	notification.mark_as_read()
	try:
		return redirect(notification.action_object.get_absolute_url())
	except:
		pass	
	try:
		return redirect(notification.actor.get_absolute_url())	
	except:
		pass
	try:
		return redirect('index')
	except:
		pass		



@login_required
def load_notification(request, *args, **kwargs):
	pass




################### login view #################
def login_view(request, *args, **kargs):
	if request.method == 'POST':
		form = LoginForm(request.POST or None)
		if form.is_valid():
			# Login Form
			username = form.cleaned_data.get('username')
			password = form.cleaned_data.get('password')

			# authentication
			user = authenticate(request, username=username, password=password)
			if user is not None:
				login(request, user)
				return redirect('index')
			else:
				messages.error(request, "Invalid username or password.")

	else:
		form = LoginForm()

	context = {
		'form': form,
	}
	return render(request, 'login.html', context)


################ logout view ####################
@login_required
def logout_view(request, *args, **kwargs):
	logout(request)
	return redirect('administration:login')



############## User Registration ###################
@staff_required
@login_required
def user_registration(request, *args, **kwargs):
	id = kwargs.get('id')
	employee = Employee.objects.filter(id=id).first()

	if request.method == 'POST':
		form = UserCreationForm(request.POST)

		if form.is_valid():
			user = form.save()
			employee.user = user
			employee.save()
			username = form.cleaned_data.get('username')
			messages.success(request, f'Account created for {username}')
			return redirect('administration:users-list')

	else:
		form = UserCreationForm()

	context = {
		'form': form,
	}
	template_name = 'user-registration.html'	

	return render(request, template_name, context)


############# User List ##################
@staff_required
@login_required
def user_list(request, *args, **kwargs):

	users = User.objects.all()
	employees = Employee.objects.all()

	if request.method == 'POST':

		employee = request.POST.get('dropdown')
		employee = int(employee)

		user = User.objects.filter(user_employee__id=employee)
		
		if user:
			messages.info(request, 'This employee already has an account')
			return redirect('administration:users-list')
		else:	
			return redirect('administration:user-registration', id=employee)

	context = {
		'employees' : employees,
		'users': users,
	}
	template_name = 'users-list.html'	

	return render(request, template_name, context)


############## User Edit ##################	
@staff_required
@login_required
def user_edit(request, *args, **kwargs):
	id = kwargs.get('id')
	user = User.objects.filter(id=id).first()
	print(user)

	if request.method == 'POST':
		user_form = UserCreationForm(request.POST or None, instance=user)

		if user_form.is_valid():
			user_form =  user_form.save(commit=False)
			password1 = request.POST['password1']
			password2 = request.POST['password2']
			if password1 == password2:
				print(password1)
				user_form.set_password(password1)
				user_form.save()
				messages.success(request, f'User {user_form.username} successfully updated')
				return redirect('administration:users-list')


	else:
		user_form = UserCreationForm(instance=user)

	context = {
		'form' : user_form,
	}
	template_name = 'user-edit.html'
	return render(request, template_name, context)


############## User Profile ###################
@login_required
def user_profile(request, *args, **kwargs):
	context = {
	}
	template_name = 'user-profile.html'	

	return render(request, template_name, context)	


############## User Profile Password Change ###################
@login_required
def change_password(request):
	if request.method == 'POST':
		form = PasswordChangeForm(request.user, request.POST)
		if form.is_valid():
			user = form.save()
			# print(user.__dict__)
			update_session_auth_hash(request, user)  # Important!
			messages.success(request, 'Your password was successfully updated!')
			return redirect('administration:user-profile')
		else:
			messages.error(request, 'Please correct the error below.')
	else:
		form = PasswordChangeForm(request.user)
	return render(request, 'change_password.html', {
		'form': form
	})