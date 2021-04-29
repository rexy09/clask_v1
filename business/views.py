from django.shortcuts import render, redirect
from administration.models import *
from django.db.models import F, Q, Avg, Sum	
from .models import *
from .forms import *
from django.http import HttpResponse, JsonResponse
from django.core import serializers
import json
from django.http import JsonResponse
from django.contrib import messages
from decimal import Decimal
from human_resource.models import *
from django.template.loader import render_to_string
from .forms import *
from datetime import date, timedelta, datetime
import string
import secrets
from notifications.signals import notify
from django.utils.html import strip_tags
from django.core.mail import EmailMultiAlternatives
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.decorators import login_required
from decimal import Decimal
from human_resource.decorators import *

# Create your views here.


@login_required
def business_profile(request, *args, **kwargs):
	id = kwargs.get('id')
	business = Business.objects.filter(id=id).first()
	context = {
		'business':business,
	}
	return render(request, "business_profile.html", context)

@store_required
@login_required
def inventory(request, *args, **kwargs):
	id = kwargs.get('id')
	business = Business.objects.filter(id=id).first()
	context = {
		'business':business,
	}
	return render(request, "inventory.html", context)

@store_required
@login_required
def products(request, *args, **kwargs):
	id = kwargs.get('id')
	business = Business.objects.filter(id=id).first()
	products = Product.objects.filter(business=business).all()
	context = {
		'business':business,
		'products':products,
	}
	return render(request, "products.html", context)

@store_required
@login_required
def add_product(request, *args, **kwargs):
	id = kwargs.get('id')
	business = Business.objects.filter(id=id).first()
	if request.method == 'POST':
		form = ProductForm(request.POST or None)

		if form.is_valid():
			product = form.save(commit=False)
			product.business  = business
			product.save()

			return redirect('business:products', id=id)
	else:    
		form = ProductForm()
			
	context = {
		'business':business,
		'form':form,
	}
	return render(request, "add_product.html", context)


@store_required
@login_required
def edit_product(request, *args, **kwargs):
	id = kwargs.get('id')
	product = Product.objects.filter(id=id).first()
	if request.method == 'POST':
		form = ProductForm(request.POST or None, instance=product)

		if form.is_valid():
			product.save()

			return redirect('business:products', id=product.business.id)
	else:    
		form = ProductForm(instance=product)
			
	context = {
		'product':product,
		'form':form,
	}
	return render(request, "edit_product.html", context)    


@store_required
@login_required
def inventory_list(request, *args, **kwargs):
	id = kwargs.get('id')
	business = Business.objects.filter(id=id).first()
	inventory_qs = Inventory.objects.filter(business=business, exist=True).annotate(available=F('remain')-F('damage'))
	if inventory_qs:
		inventory_qs.filter(available=0).update(exist=False)			
	inventories = inventory_qs.filter(available__gt=0).order_by('-pk')

	context = {
		'business':business,
		'inventories':inventories,
	}
	return render(request, "inventory_list.html", context)


@store_required
@login_required
def add_inventory(request, *args, **kwargs):
	id = kwargs.get('id')
	business = Business.objects.filter(id=id).first()
	if request.method == 'POST':
		form = InventoryForm(request.POST or None, business=business)

		if form.is_valid():
			inventory = form.save(commit=False)
			inventory.business = business
			inventory.remain = request.POST['quantity']
			inventory.save()

			return redirect('business:inventory_list', id=id)
	else:    
		form = InventoryForm(business=business,)
			
	context = {
		'business':business,
		'form':form,
	}
	return render(request, "add_inventory.html", context)


@store_required
@login_required
def edit_inventory(request, *args, **kwargs):
	id = kwargs.get('id')
	inventory = Inventory.objects.filter(id=id).first()
	if request.method == 'POST':
		form = InventoryUpdateForm(request.POST or None, business=inventory.business, instance=inventory )

		if form.is_valid():
			form.save()

			return redirect('business:inventory_list', id=inventory.business.id)
	else:    
		form = InventoryUpdateForm(business=inventory.business, instance=inventory)
			
	context = {
		'inventory':inventory,
		'form':form,
	}
	return render(request, "edit_inventory.html", context)    


@login_required
def expenses(request, *args, **kwargs):
	id = kwargs.get('id')
	business = Business.objects.filter(id=id).first()
	context = {
		'business':business,
	}
	return render(request, "expenses.html", context)

@finance_required
@login_required
def sales(request, *args, **kwargs):
	id = kwargs.get('id')
	business = Business.objects.filter(id=id).first()
	context = {
		'business':business,
	}
	return render(request, "sales.html", context)


@store_required
@login_required
def stock_list(request, *args, **kwargs):
	id = kwargs.get('id')
	business = Business.objects.filter(id=id).first()
	products = Product.objects.filter(business=business).all().order_by('name')
	context = {
		'business':business,
		'products':products,
	}
	return render(request, "stock_list.html", context)



@finance_required
@login_required
def sales_list(request, *args, **kwargs):
	id = kwargs.get('id')
	branch = Branch.objects.filter(id=id).first()
	sales = Sale.objects.filter(Q(branch=branch, created_at__date=date.today())|Q(branch=branch, status='Awaiting Payment')).all().order_by('-pk')
	context = {
		'branch':branch,
		'sales':sales,
	}
	return render(request, "sales_list.html", context)



@finance_required
@login_required
def sales_branch(request, *args, **kwargs):
	id = kwargs.get('id')
	business = Business.objects.filter(id=id).first()
	branches = Branch.objects.filter(business=business).all()
	context = {
		'business':business,
		'branches':branches
	}
	return render(request, "sales_branch.html", context)


@finance_required
@login_required
def add_sale(request, *args, **kwargs):
	id = kwargs.get('id')
	branch = Branch.objects.filter(id=id).first()
	if request.method == 'POST':
		form = SaleForm(request.POST or None, business=branch.business)
		
		if form.is_valid():
			inventory = Inventory.objects.filter(id=request.POST['inventory']).first()
			if inventory.get_available != 0:
				if int(request.POST['quantity']) != 0:
					available = inventory.get_available - int(request.POST['quantity'])
					if available >= 0:
						remain = inventory.remain - int(request.POST['quantity'])
						if remain >= 0:
							sale = form.save(commit=False)
							sale.branch = branch
							sale.user = request.user
							sale.save()

							# Updating Iventory
							Inventory.objects.filter(id=inventory.id).update(remain=remain)

							if sale.status == 'Completed':
								# Adding Transaction in Saving Account
								acc = CheckAccount.objects.filter(business=branch.business).last()
								try:
									balance = acc.balance + Decimal(sale.amount_paid)
									CheckAccount.objects.create(business=branch.business, employee=request.user, description="Sale", debit=0, credit=sale.amount_paid, balance=balance)
								except:
									balance = Decimal(sale.amount_paid)
									CheckAccount.objects.create(business=branch.business, employee=request.user, description="Sale", debit=0, credit=sale.amount_paid, balance=balance)
							
							return redirect('business:sales_list', id=branch.id)
						else:
							messages.error(request, "You have exceeded available quantity.")
					else:
						messages.error(request, "You have exceeded available quantity.")		
				else:
					messages.error(request, "Quantity must be 1 and above.")  
			else:
				pass     
		else:
			pass

	else:
		code = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for x in range(10))
		form = SaleForm(business=branch.business, initial={'order_no':code})

	context = {
		'business':branch.business,
		'form':form
	}
	return render(request, "add_sale.html", context)  


@finance_required
@login_required
def edit_sale(request, *args, **kwargs):
	id = kwargs.get('id')
	sale = Sale.objects.filter(id=id).first()
	if request.method == 'POST':
		form = SaleForm(request.POST or None, business=sale.branch.business, instance=sale)
		
		if form.is_valid():
				sale = form.save(commit=False)
				sale.save()
				
				if sale.status == 'Completed':
					# Adding Transaction in Saving Account
					acc = CheckAccount.objects.filter(business=sale.branch.business).last()
					try:
						balance = acc.balance + Decimal(sale.amount_paid)
						CheckAccount.objects.create(business=sale.branch.business, employee=request.user, description="Sale", debit=0, credit=sale.amount_paid, balance=balance)
					except:
						balance = Decimal(sale.amount_paid)
						CheckAccount.objects.create(business=sale.branch.business, employee=request.user, description="Sale", debit=0, credit=sale.amount_paid, balance=balance)

				return redirect('business:sales_list', id=sale.branch.id)
		else:
			pass

	else:
		form = SaleForm(business=sale.branch.business, instance=sale)

	context = {
		'business':sale.branch.business,
		'form':form
	}
	return render(request, "edit_sale.html", context)  


@finance_required
@login_required
def delete_sale(request, *args, **kwargs):
	id = kwargs.get('id')
	sale = Sale.objects.filter(id=id).first()

	inventory = Inventory.objects.filter(id=sale.inventory.id).first()

	remain = inventory.remain + sale.quantity

	Inventory.objects.filter(id=inventory.id).update(remain=remain)

	Sale.objects.filter(id=sale.id).first().delete()

	# Adding Transaction in Saving Account
	acc = CheckAccount.objects.filter(business=sale.branch.business).last()
	try:
		balance = acc.balance - Decimal(sale.amount_paid)
		CheckAccount.objects.create(business=sale.branch.business, employee=request.user, description="Sale Return", debit=sale.amount_paid, credit=0, balance=balance)
	except:
		balance = Decimal(sale.amount_paid)
		CheckAccount.objects.create(business=sale.branch.business,  employee=request.user, description="Sale Return", debit=sale.amount_paid, credit=0, balance=balance)	

	return redirect('business:sales_list', id=sale.branch.id)


@finance_required
@login_required
def customer_list(request, *args, **kwargs):
	id = kwargs.get('id')
	business = Business.objects.filter(id=id).first()
	customers = Customer.objects.filter(business=business).all()
	context = {
		'business':business,
		'customers':customers
	}
	return render(request, "customer_list.html", context)


@finance_required
@login_required
def add_customer(request, *args, **kwargs):
	id = kwargs.get('id')
	business = Business.objects.filter(id=id).first()
	if request.method == 'POST':
		form = CustomerForm(request.POST or None,)
		
		if form.is_valid():
			customer = form.save(commit=False)
			customer.business = business
			customer.save()
			return redirect('business:customer_list', id=business.id)
		else:
			pass
	else:
		form = CustomerForm()

	context = {
		'business':business,
		'form':form
	}
	return render(request, "add_customer.html", context)    


@finance_required
@login_required
def edit_customer(request, *args, **kwargs):
	id = kwargs.get('id')
	customer = Customer.objects.filter(id=id).first()
	if request.method == 'POST':
		form = CustomerForm(request.POST or None, instance=customer)
		
		if form.is_valid():
			form.save()
			return redirect('business:customer_list', id=customer.business.id)

	else:
		form = CustomerForm(instance=customer)

	context = {
		'business':customer.business,
		'form':form
	}
	return render(request, "edit_customer.html", context)   


@finance_required
@login_required
def get_inventory(request):
	if request.is_ajax():
		id = request.GET.get('inventory')
		if id !='':
			inventory = Inventory.objects.filter(id=id).first()

			data_dict = {
				'name':inventory.product.name,
				'sell_price':float(inventory.product.sell_price),
				'product_cost':float(inventory.product_cost),
			}

			data = json.dumps(data_dict)
			return JsonResponse(data, safe=False)
		else:
			data = json.dumps([{}])
			return JsonResponse(data, safe=False)


############ Payroll Form Update################
@finance_required
@login_required
def payroll_update(request, *args, **kwargs):

	pk = kwargs.get('pk')
	id = kwargs.get('id')
	business = Business.objects.filter(id=id).first()
	employee = Payroll.objects.filter(employee=pk, business=business).first()


	if request.method == 'POST':
		payroll_form = PayrollForm(request.POST or None, instance=employee, business=business)

		if payroll_form.is_valid():
			paryoll = payroll_form.save()
			worker = Payroll.objects.filter(id=paryoll.id).first()
			social_rates = worker.tax_rate  
			paye_rate = worker.paye
			income = worker.employee.salary
			bonus = worker.bonus
			overtime = worker.overtime
			deduction = worker.deduction

			#### When PAYE Tax is selected only

			if paye_rate and not social_rates:

				if income <= 270000:

					if bonus or overtime or deduction:
						income = income + bonus + overtime - deduction                   

					Takehome.objects.filter(payroll=worker, business=business).update(salary=income)

				elif 270000 < income <= 520000:
					
					tax_payment = (income - 270000) * 0.09 
					income = income - tax_payment

					if bonus or overtime or deduction:
						income = income + bonus + overtime - deduction

					Takehome.objects.filter(payroll=worker, business=business).update(salary=income)

				elif 520000 < income <= 760000:
					
					tax_payment = (income - 520000) * 0.2 + 22500
					income = income - tax_payment

					if bonus or overtime or deduction:
						income = income + bonus + overtime - deduction

					Takehome.objects.filter(payroll=worker, business=business).update(salary=income)

				elif 760000 < income <= 1000000:
					
					tax_payment = (income - 760000) * 0.25 + 70500
					income = income - tax_payment

					if bonus or overtime or deduction:
						income = income + bonus + overtime - deduction

					Takehome.objects.filter(payroll=worker, business=business).update(salary=income)

				elif 1000000 < income:
					
					tax_payment = (income - 1000000) * 0.3 + 130500 
					income = income - tax_payment

					if bonus or overtime or deduction:
						income = income + bonus + overtime - deduction

					Takehome.objects.filter(payroll=worker, business=business).update(salary=income)


			### When Tax from social funds are selected only
			###HINT: 0.1 -> NSSF, 0.01 -> WCF, HELSB -> 0.15

			elif social_rates and not paye_rate:

				if len(social_rates) == 3:
					tax_payment = income * 0.26
					income = income - tax_payment

					if bonus or overtime or deduction:
						income = income + bonus + overtime - deduction

					Takehome.objects.filter(payroll=worker, business=business).update(salary=income)

				elif len(social_rates) == 2:
					if 'nssf' and 'wcf' in social_rates and not 'loan board' in social_rates:
						tax_payment = income * 0.11
						income = income - tax_payment

						if bonus or overtime or deduction:
							income = income + bonus + overtime - deduction

						Takehome.objects.filter(payroll=worker, business=business).update(salary=income)

					elif 'nssf' and 'loan board' in social_rates and not 'wcf' in social_rates:
						tax_payment = income * 0.25
						income = income - tax_payment

						if bonus or overtime or deduction:
							income = income + bonus + overtime - deduction

						Takehome.objects.filter(payroll=worker, business=business).update(salary=income)

					elif 'wcf' and 'loan board' in social_rates and not 'nssf' in social_rates: 
						tax_payment = income * 0.16
						income = income - tax_payment

						if bonus or overtime or deduction:
							income = income + bonus + overtime - deduction                      
							  
						Takehome.objects.filter(payroll=worker, business=business).update(salary=income)

				elif len(social_rates) == 1:

					for rate in social_rates:
						if rate == 'nssf':
							rate = 0.1
						elif rate == 'wcf':
							rate = 0.01
						elif rate == 'loan board':
							rate = 0.15		
					tax_payment = income * rate
					income = income - tax_payment

					if bonus or overtime or deduction:
						income = income + bonus + overtime - deduction
					
					Takehome.objects.filter(payroll=worker, business=business).update(salary=income)
					

			#### When Social funds and PAYE Tax are selected

			if paye_rate and social_rates:


				### When PAYE and all Social Tax are selected


				if income <= 270000 and len(social_rates) == 3:

					social_payment = income * 0.26
					income = income - social_payment

					if bonus or overtime or deduction:
						income = income + bonus + overtime - deduction                     

					Takehome.objects.filter(payroll=worker, business=business).update(salary=income)


				elif 270000 < income <= 520000 and len(social_rates) == 3: 

					social_payment = income * 0.26
					paye_payment = (income - 270000) * 0.09
					total_payment = social_payment + paye_payment  
					income = income - total_payment

					if bonus or overtime or deduction:
						income = income + bonus + overtime - deduction

					Takehome.objects.filter(payroll=worker, business=business).update(salary=income)

				elif 520000 < income <= 760000 and len(social_rates) == 3:  

					social_payment = income * 0.26
					paye_payment = (income - 520000) * 0.2 + 22500
					total_payment = social_payment + paye_payment  
					income = income - total_payment

					if bonus or overtime or deduction:
						income = income + bonus + overtime - deduction

					Takehome.objects.filter(payroll=worker, business=business).update(salary=income)

				elif 760000 < income <= 1000000 and len(social_rates) == 3:

					social_payment = income * 0.26
					paye_payment = (income - 760000) * 0.25 + 70500
					total_payment = social_payment + paye_payment  
					income = income - total_payment

					if bonus or overtime or deduction:
						income = income + bonus + overtime - deduction

					Takehome.objects.filter(payroll=worker, business=business).update(salary=income)
			
				elif 1000000 < income and len(social_rates) == 3:  

					social_payment = income * 0.26
					paye_payment = (income - 1000000) * 0.3 + 130500
					total_payment = social_payment + paye_payment  
					income = income - total_payment

					if bonus or overtime or deduction:
						income = income + bonus + overtime - deduction

					Takehome.objects.filter(payroll=worker, business=business).update(salary=income)



				#### When PAYE Tax and both Social Tax is selected    


				elif income <= 270000 and len(social_rates) == 2:

					if 'nssf' and 'wcf' in social_rates and not 'loan board' in social_rates:
						tax_payment = income * 0.11
						income = income - tax_payment

						if bonus or overtime or deduction:
							income = income + bonus + overtime - deduction                       
							 
						Takehome.objects.filter(payroll=worker, business=business).update(salary=income)

					elif 'nssf' and 'loan board' in social_rates and not 'wcf' in social_rates:
						tax_payment = income * 0.25
						income = income - tax_payment

						if bonus or overtime or deduction:
							income = income + bonus + overtime - deduction                       

						Takehome.objects.filter(payroll=worker, business=business).update(salary=income)


					elif 'wcf' and 'loan board' in social_rates and not 'nssf' in social_rates: 
						tax_payment = income * 0.16
						income = income - tax_payment

						if bonus or overtime or deduction:
							income = income + bonus + overtime - deduction                      

						Takehome.objects.filter(payroll=worker, business=business).update(salary=income)


				elif 270000 < income <= 520000 and len(social_rates) == 2: 

					if 'nssf' and 'wcf' in social_rates and not 'loan board' in social_rates:
						social_payment = income * 0.11

					elif 'nssf' and 'loan board' in social_rates and not 'wcf' in social_rates:
						social_payment = income * 0.25

					elif 'wcf' and 'loan board' in social_rates and not 'nssf' in social_rates: 
						social_payment = income * 0.16

					paye_payment = (income - 270000) * 0.09
					total_payment = social_payment + paye_payment  
					income = income - total_payment

					if bonus or overtime or deduction:
						income = income + bonus + overtime - deduction

					Takehome.objects.filter(payroll=worker, business=business).update(salary=income)

				elif 520000 < income <= 760000 and len(social_rates) == 2:  

					if 'nssf' and 'wcf' in social_rates and not 'loan board' in social_rates:
						social_payment = income * 0.11

					elif 'nssf' and 'loan board' in social_rates and not 'wcf' in social_rates:
						social_payment = income * 0.25

					elif 'wcf' and 'loan board' in social_rates and not 'nssf' in social_rates: 
						social_payment = income * 0.16

					paye_payment = (income - 520000) * 0.2 + 22500
					total_payment = social_payment + paye_payment  
					income = income - total_payment

					if bonus or overtime or deduction:
						income = income + bonus + overtime - deduction

					Takehome.objects.filter(payroll=worker, business=business).update(salary=income)

				elif 760000 < income <= 1000000 and len(social_rates) == 2:

					if 'nssf' and 'wcf' in social_rates and not 'loan board' in social_rates:
						social_payment = income * 0.11

					elif 'nssf' and 'loan board' in social_rates and not 'wcf' in social_rates:
						social_payment = income * 0.25

					elif 'wcf' and 'loan board' in social_rates and not 'nssf' in social_rates: 
						social_payment = income * 0.16

					paye_payment = (income - 760000) * 0.25 + 70500
					total_payment = social_payment + paye_payment  
					income = income - total_payment

					if bonus or overtime or deduction:
						income = income + bonus + overtime - deduction

					Takehome.objects.filter(payroll=worker, business=business).update(salary=income)
			
				elif 1000000 < income and len(social_rates) == 2:  

					if 'nssf' and 'wcf' in social_rates and not 'loan board' in social_rates:
						social_payment = income * 0.11

					elif 'nssf' and 'loan board' in social_rates and not 'wcf' in social_rates:
						social_payment = income * 0.25

					elif 'wcf' and 'loan board' in social_rates and not 'nssf' in social_rates: 
						social_payment = income * 0.16

					paye_payment = (income - 1000000) * 0.3 + 130500
					total_payment = social_payment + paye_payment  
					income = income - total_payment

					if bonus or overtime or deduction:
						income = income + bonus + overtime - deduction

					Takehome.objects.filter(payroll=worker, business=business).update(salary=income)

				 
				#### When PAYE Tax and one Social Tax is selected    


				elif income <= 270000 and len(social_rates) == 1:
					for rate in social_rates:
						if rate == 'nssf':
							rate = 0.1

						elif rate == 'wcf':
							rate = 0.01

						elif rate == 'loan board':
							rate = 0.15		
							   
					tax_payment = income * rate
					income = income - tax_payment

					if bonus or overtime or deduction:
						income = income + bonus + overtime - deduction
					
					Takehome.objects.filter(payroll=worker, business=business).update(salary=income)

				elif 270000 < income <= 520000 and len(social_rates) == 1:
						
					for rate in social_rates:
						if rate == 'nssf':
							rate = 0.1

						elif rate == 'wcf':
							rate = 0.01
							
						elif rate == 'loan board':
							rate = 0.15

					social_payment = income * rate
					paye_payment = (income - 270000) * 0.09
					total_payment = social_payment + paye_payment  
					income = income - total_payment

					if bonus or overtime or deduction:
						income = income + bonus + overtime - deduction

					Takehome.objects.filter(payroll=worker, business=business).update(salary=income)

				elif 520000 < income <= 760000 and len(social_rates) == 1:

					for rate in social_rates:
						if rate == 'nssf':
							rate = 0.1

						elif rate == 'wcf':
							rate = 0.01
							
						elif rate == 'loan board':
							rate = 0.15

					social_payment = income * rate
					paye_payment = (income - 520000) * 0.2 + 22500
					total_payment = social_payment + paye_payment  
					income = income - total_payment

					if bonus or overtime or deduction:
						income = income + bonus + overtime - deduction

					Takehome.objects.filter(payroll=worker, business=business).update(salary=income)

				elif 760000 < income <= 1000000 and len(social_rates) == 1:
	
					for rate in social_rates:
						if rate == 'nssf':
							rate = 0.1

						elif rate == 'wcf':
							rate = 0.01
							
						elif rate == 'loan board':
							rate = 0.15

					social_payment = income * rate
					paye_payment = (income - 760000) * 0.25 + 70500
					total_payment = social_payment + paye_payment  
					income = income - total_payment

					if bonus or overtime or deduction:
						income = income + bonus + overtime - deduction

					Takehome.objects.filter(payroll=worker, business=business).update(salary=income)
			
				elif 1000000 < income and len(social_rates) == 1:

					for rate in social_rates:
						if rate == 'nssf':
							rate = 0.1

						elif rate == 'wcf':
							rate = 0.01
							
						elif rate == 'loan board':
							rate = 0.15

					social_payment = income * rate
					paye_payment = (income - 1000000) * 0.3 + 130500                                                                                                                                                                                                                                                
					total_payment = social_payment + paye_payment  
					income = income - total_payment

					if bonus or overtime or deduction:
						income = income + bonus + overtime - deduction

					Takehome.objects.filter(payroll=worker, business=business).update(salary=income)


			### When Pay rate and Social rates are not selected        

			if not paye_rate and not social_rates:

				if bonus or overtime or deduction:
					income = income + bonus + overtime - deduction               
			
				Takehome.objects.filter(payroll=worker, business=business).update(salary=income)        

			###HINT: 0.1 -> NSSF, 0.01 -> WCF, HELSB -> 0.15
			"""
				Total for each individual cut in Payroll i.e
				Paye, Bonuses, Overtime and Social funds
			"""	
			bonuses = Payroll.objects.aggregate(Sum('bonus'))['bonus__sum']   		
			overtime = Payroll.objects.aggregate(Sum('overtime'))['overtime__sum']    		
			nssf = Payroll.objects.filter(tax_rate__icontains='nssf')
			wcf = Payroll.objects.filter(tax_rate__icontains='wcf')
			loan_board = Payroll.objects.filter(tax_rate__icontains='loan board')
			salaries = Payroll.objects.aggregate(Sum('employee__salary'))['employee__salary__sum']
			paye_objs = Payroll.objects.all().filter(paye=True)

			paye_total = 0

			if paye_objs:     	

				for worker in paye_objs:

					salary = worker.employee.salary

					if salary <= 270000:

						paye_total += 0

					elif 270000 < salary <= 520000:

						tax_payment = (salary - 270000) * 0.09 
						paye_total += tax_payment


					elif 520000 < salary <= 760000:

						tax_payment = (salary - 520000) * 0.2 + 22500 
						paye_total += tax_payment

					elif 760000 < salary <= 1000000:

						tax_payment = (salary - 760000) * 0.25 + 70500 
						paye_total += tax_payment


					elif 1000000 < salary:

						tax_payment = (salary - 1000000) * 0.3 + 130500 
						paye_total += tax_payment                  

			nssf_funds = 0
			wcf_funds = 0
			loan_board_funds = 0			

			total_funds = 0
			if nssf:
				for worker in nssf:
					total_funds += worker.employee.salary
				nssf_funds = total_funds * 0.1 
				total_funds = 0

			if wcf:
				for worker in wcf:
					total_funds += worker.employee.salary            	
				wcf_funds = total_funds * 0.01 
				total_funds = 0

			if loan_board:
				for worker in loan_board:
					total_funds += worker.employee.salary
				loan_board_funds = total_funds * 0.15 

			#### Saving Sum to the database
			Total.objects.filter(business=business).update(nssf=nssf_funds, wcf=wcf_funds, loan_board=loan_board_funds, paye=int(paye_total), bonus=bonuses, overtime=overtime, deduction=deduction)	

			takehome_salary = Takehome.objects.aggregate(Sum('salary'))['salary__sum']

			total = Total.objects.filter(business=business).first()

			NSSF = total.nssf
			PAYE = total.paye
			LOAN = total.loan_board
			WCF = total.wcf
			BONUS = total.bonus
			OVERTIME = total.overtime

			### Total payroll expenses
			total_expenses = NSSF + PAYE + LOAN + WCF + BONUS + OVERTIME + takehome_salary

			### Get check acount object
			check_account = CheckAccount.objects.filter(id=1).first()

			### Initial check account balance
			check_account_balance = 0

			return redirect('business:takehome', id=id)  

	else:
		payroll_form = PayrollForm(instance=employee, business=business)

	context = {
		'business' : business,
		'payroll_form': payroll_form,
	}
	template_name = 'payroll.html'

	return render(request, template_name, context)

@login_required
def check_account_debit(**kwargs):

	business = kwargs.get('business')
	amount = kwargs.get('amount')
	user = kwargs.get('user')
	description = kwargs.get('description')

	### Get check acount object
	check_account = CheckAccount.objects.filter(business=business).last()

	if check_account:
		check_account_balance = check_account.balance 
		new_balance = check_account_balance - Decimal(amount)
		CheckAccount.objects.create(business=business, employee=user, balance=new_balance, debit=amount, credit=0.00, description=description)

@login_required
def check_account_credit(**kwargs):

	business = kwargs.get('business')
	amount = kwargs.get('amount')
	user = kwargs.get('user')
	description = kwargs.get('description')

	### Get check acount object
	check_account = CheckAccount.objects.filter(business=business).last()
	
	if check_account:
		check_account_balance = check_account.balance 
		new_balance = check_account_balance + Decimal(amount)
		CheckAccount.objects.create(business=business, employee=user, balance=new_balance, debit=0.00, credit=amount, description=description)

@login_required
def saving_account_debit(**kwargs):

	business = kwargs.get('business')
	amount = kwargs.get('amount')
	user = kwargs.get('user')
	description = kwargs.get('description')

	### Get saving acount object
	saving_account = SavingAccount.objects.filter(business=business).last()

	if saving_account:
		saving_account_balance = saving_account.balance 
		new_balance = saving_account_balance - Decimal(amount)
		SavingAccount.objects.create(business=business, employee=user, balance=new_balance, debit=amount, credit=0.00, description=description)

@login_required
def saving_account_credit(**kwargs):

	business = kwargs.get('business')
	amount = kwargs.get('amount')
	user = kwargs.get('user')
	description = kwargs.get('description')

	### Get saving acount object
	saving_account = SavingAccount.objects.filter(business=business).last()
	
	if saving_account:
		saving_account_balance = saving_account.balance 
		new_balance = saving_account_balance + Decimal(amount)
		SavingAccount.objects.create(business=business, employee=user, balance=new_balance, debit=0.00, credit=amount, description=description)



############ Takehome Form ################
@finance_required
@login_required
def takehome(request, *args, **kwargs):

	id = kwargs.get('id')
	business = Business.objects.filter(id=id).first()
	takehome = Takehome.objects.filter(business=business) 


	if request.method == 'POST':
		payroll_form = PayrollForm(request.POST or None, business=business)

		if payroll_form.is_valid():
			payroll = payroll_form.save(commit=False)
			payroll.business = business
			payroll.save()
			worker = Payroll.objects.filter(id=payroll.id, business=business).first()
			loan = Loan.objects.filter(employee=worker.employee, business=business).first()
			social_rates = worker.tax_rate  
			paye_rate = worker.paye
			income = worker.employee.salary
			bonus = worker.bonus
			deduction = worker.deduction
			overtime = worker.overtime
			sdl = worker.sdl

			####### Get Employee Loan
			if loan :
				if loan.debt:
					worker.loan_debt = loan.remaining_debt

			#### When PAYE Tax is selected only

			if paye_rate and not social_rates:

				if income <= 270000:

					if bonus or overtime or deduction:
						income = income + bonus + overtime - deduction                    

					Takehome.objects.create(payroll=worker, salary=income, business=business)
					employee = Takehome.objects.filter(business=business, payroll=worker).first()

					if sdl:
						employee_salary = employee.salary 
						sdl = employee_salary * 0.04
						worker.sdl_amount = int(sdl)
						employee_salary = employee_salary - sdl
						employee.salary = employee_salary
						employee.save()
						worker.save()

					#### Deduct loan return from employee
					if loan:
						if loan.debt == True :
							takehome_salary = employee.salary
							employee.salary = takehome_salary - loan.amount_paid
							loan.remaining_debt = loan.remaining_debt - loan.amount_paid
							worker.loan_debt = loan.remaining_debt
							loan.save()
							employee.save()
							worker.save()



					check_account_debit(business=business, amount=income, user=request.user, description="Payroll")


				elif 270000 < income <= 520000:
					
					tax_payment = (income - 270000) * 0.09 
					income = income - tax_payment

					if bonus or overtime or deduction:
						income = income + bonus + overtime - deduction

					worker.paye_amount = tax_payment
					worker.save()

					Takehome.objects.create(payroll=worker, salary=income, business=business)
					employee = Takehome.objects.filter(business=business, payroll=worker).first()

					if sdl:
						employee_salary = employee.salary 
						sdl = employee_salary * 0.04
						worker.sdl_amount = int(sdl)
						employee_salary = employee_salary - sdl
						employee.salary = employee_salary
						employee.save()
						worker.save()					

					#### Deduct loan return from employee
					if loan:
						if loan.debt == True :
							takehome_salary = employee.salary
							employee.salary = takehome_salary - loan.amount_paid
							loan.remaining_debt = loan.remaining_debt - loan.amount_paid
							worker.loan_debt = loan.remaining_debt
							loan.save()
							employee.save()
							worker.save()

					check_account_debit(business=business, amount=tax_payment, user=request.user, description="Paye")
					check_account_debit(business=business, amount=income, user=request.user, description="Payroll")



				elif 520000 < income <= 760000:
					
					tax_payment = (income - 520000) * 0.2 + 22500
					income = income - tax_payment 

					if bonus or overtime or deduction:
						income = income + bonus + overtime - deduction

					worker.paye_amount = tax_payment
					worker.save()

					Takehome.objects.create(payroll=worker, salary=income, business=business)
					employee = Takehome.objects.filter(business=business, payroll=worker).first()

					if sdl:
						employee_salary = employee.salary 
						sdl = employee_salary * 0.04
						worker.sdl_amount = int(sdl)
						employee_salary = employee_salary - sdl
						employee.salary = employee_salary
						employee.save()
						worker.save()					

					#### Deduct loan return from employee
					if loan:
						if loan.debt == True :
							takehome_salary = employee.salary
							employee.salary = takehome_salary - loan.amount_paid
							loan.remaining_debt = loan.remaining_debt - loan.amount_paid
							worker.loan_debt = loan.remaining_debt
							loan.save()
							employee.save()
							worker.save()

					check_account_debit(business=business, amount=tax_payment, user=request.user, description="Paye")
					check_account_debit(business=business, amount=income, user=request.user, description="Payroll")

				elif 760000 < income <= 1000000:
					
					tax_payment = (income - 760000) * 0.25 + 70500
					income = income - tax_payment

					if bonus or overtime or deduction:
						income = income + bonus + overtime - deduction

					worker.paye_amount = tax_payment
					worker.save()

					Takehome.objects.create(payroll=worker, salary=income, business=business)
					employee = Takehome.objects.filter(business=business, payroll=worker).first()

					if sdl:
						employee_salary = employee.salary 
						sdl = employee_salary * 0.04
						worker.sdl_amount = int(sdl)
						employee_salary = employee_salary - sdl
						employee.salary = employee_salary
						employee.save()
						worker.save()					

					#### Deduct loan return from employee
					if loan:
						if loan.debt == True :
							takehome_salary = employee.salary
							employee.salary = takehome_salary - loan.amount_paid
							loan.remaining_debt = loan.remaining_debt - loan.amount_paid
							worker.loan_debt = loan.remaining_debt
							loan.save()
							employee.save()
							worker.save()

					check_account_debit(business=business, amount=tax_payment, user=request.user, description="Paye")
					check_account_debit(business=business, amount=income, user=request.user, description="Payroll")

				elif 1000000 < income:
					
					tax_payment = (income - 1000000) * 0.3 + 130500 
					income = income - tax_payment

					if bonus or overtime or deduction:
						income = income + bonus + overtime - deduction

					worker.paye_amount = tax_payment
					worker.save()

					Takehome.objects.create(payroll=worker, salary=income, business=business)
					employee = Takehome.objects.filter(business=business, payroll=worker).first()

					if sdl:
						employee_salary = employee.salary 
						sdl = employee_salary * 0.04
						worker.sdl_amount = int(sdl)
						employee_salary = employee_salary - sdl
						employee.salary = employee_salary
						employee.save()
						worker.save()					

					#### Deduct loan return from employee
					if loan:
						if loan.debt == True :
							takehome_salary = employee.salary
							employee.salary = takehome_salary - loan.amount_paid
							loan.remaining_debt = loan.remaining_debt - loan.amount_paid
							worker.loan_debt = loan.remaining_debt
							loan.save()
							employee.save()
							worker.save()

					check_account_debit(business=business, amount=tax_payment, user=request.user, description="Paye")
					check_account_debit(business=business, amount=income, user=request.user, description="Payroll")


			### When Tax from social funds are selected only
			###HINT: 0.1 -> NSSF, 0.01 -> WCF, HELSB -> 0.15

			elif social_rates and not paye_rate:

				if len(social_rates) == 3:
					tax_payment = income * 0.26
					income = income - tax_payment

					if bonus or overtime or deduction:
						income = income + bonus + overtime - deduction

					worker.tax_amount = tax_payment
					worker.save()
						
					Takehome.objects.create(payroll=worker, salary=income, business=business)
					employee = Takehome.objects.filter(business=business, payroll=worker).first()

					if sdl:
						employee_salary = employee.salary 
						sdl = employee_salary * 0.04
						worker.sdl_amount = int(sdl)
						employee_salary = employee_salary - sdl
						employee.salary = employee_salary
						employee.save()
						worker.save()					

					#### Deduct loan return from employee
					if loan:
						if loan.debt == True :
							takehome_salary = employee.salary
							employee.salary = takehome_salary - loan.amount_paid
							loan.remaining_debt = loan.remaining_debt - loan.amount_paid
							worker.loan_debt = loan.remaining_debt
							loan.save()
							employee.save()
							worker.save()

					check_account_debit(business=business, amount=tax_payment, user=request.user, description="Payroll Tax")
					check_account_debit(business=business, amount=income, user=request.user, description="Payroll")

				elif len(social_rates) == 2:

					if 'nssf' and 'wcf' in social_rates and not 'loan board' in social_rates:
						tax_payment = income * 0.11
						income = income - tax_payment

						if bonus or overtime or deduction:
							income = income + bonus + overtime -deduction

						worker.tax_amount = tax_payment
						worker.save()

						Takehome.objects.create(payroll=worker, salary=income, business=business)
						employee = Takehome.objects.filter(business=business, payroll=worker).first()

						if sdl:
							employee_salary = employee.salary 
							sdl = employee_salary * 0.04
							worker.sdl_amount = int(sdl)
							employee_salary = employee_salary - sdl
							employee.salary = employee_salary
							employee.save()
							worker.save()					

						#### Deduct loan return from employee
						if loan:
							if loan.debt == True :
								takehome_salary = employee.salary
								employee.salary = takehome_salary - loan.amount_paid
								loan.remaining_debt = loan.remaining_debt - loan.amount_paid
								worker.loan_debt = loan.remaining_debt
								loan.save()
								employee.save()
								worker.save()

						check_account_debit(business=business, amount=tax_payment, user=request.user, description="Payroll Tax")
						check_account_debit(business=business, amount=income, user=request.user, description="Payroll")


					elif 'nssf' and 'loan board' in social_rates and not 'wcf' in social_rates:
						tax_payment = income * 0.25
						income = income - tax_payment

						if bonus or overtime or deduction:
							income = income + bonus + overtime - deduction

						worker.tax_amount = tax_payment
						worker.save()

						Takehome.objects.create(payroll=worker, salary=income, business=business)
						employee = Takehome.objects.filter(business=business, payroll=worker).first()

						if sdl:
							employee_salary = employee.salary 
							sdl = employee_salary * 0.04
							worker.sdl_amount = int(sdl)
							employee_salary = employee_salary - sdl
							employee.salary = employee_salary
							employee.save()
							worker.save()					

						#### Deduct loan return from employee
						if loan:
							if loan.debt == True :
								takehome_salary = employee.salary
								employee.salary = takehome_salary - loan.amount_paid
								loan.remaining_debt = loan.remaining_debt - loan.amount_paid
								worker.loan_debt = loan.remaining_debt
								loan.save()
								employee.save()
								worker.save()

						check_account_debit(business=business, amount=tax_payment, user=request.user, description="Payroll Tax")
						check_account_debit(business=business, amount=income, user=request.user, description="Payroll")

					elif 'wcf' and 'loan board' in social_rates and not 'nssf' in social_rates:
						tax_payment = income * 0.16
						income = income - tax_payment

						if bonus or overtime or deduction:
							income = income + bonus + overtime - deduction

						worker.tax_amount = tax_payment
						worker.save()

						Takehome.objects.create(payroll=worker, salary=income, business=business)
						employee = Takehome.objects.filter(business=business, payroll=worker).first()

						if sdl:
							employee_salary = employee.salary 
							sdl = employee_salary * 0.04
							worker.sdl_amount = int(sdl)
							employee_salary = employee_salary - sdl
							employee.salary = employee_salary
							employee.save()
							worker.save()					

						#### Deduct loan return from employee
						if loan:
							if loan.debt == True :
								takehome_salary = employee.salary
								employee.salary = takehome_salary - loan.amount_paid
								loan.remaining_debt = loan.remaining_debt - loan.amount_paid
								worker.loan_debt = loan.remaining_debt
								loan.save()
								employee.save()
								worker.save()

						check_account_debit(business=business, amount=tax_payment, user=request.user, description="Payroll Tax")
						check_account_debit(business=business, amount=income, user=request.user, description="Payroll")

				elif len(social_rates) == 1:

					for rate in social_rates:
						if rate == 'nssf':
							rate = 0.1
						elif rate == 'wcf':
							rate = 0.01
						elif rate == 'loan board':
							rate = 0.15		
					tax_payment = income * rate
					income = income - tax_payment

					worker.tax_amount = tax_payment
					worker.save()

					if bonus or overtime or deduction:
						income = income + bonus + overtime - deduction

					Takehome.objects.create(payroll=worker, salary=income, business=business)
					employee = Takehome.objects.filter(business=business, payroll=worker).first()

					if sdl:
						employee_salary = employee.salary 
						sdl = employee_salary * 0.04
						worker.sdl_amount = int(sdl)
						employee_salary = employee_salary - sdl
						employee.salary = employee_salary
						employee.save()
						worker.save()					

					#### Deduct loan return from employee
					if loan:
						if loan.debt == True :
							takehome_salary = employee.salary
							employee.salary = takehome_salary - loan.amount_paid
							loan.remaining_debt = loan.remaining_debt - loan.amount_paid
							worker.loan_debt = loan.remaining_debt
							loan.save()
							employee.save()
							worker.save()

					check_account_debit(business=business, amount=tax_payment, user=request.user, description="Payroll Tax")
					check_account_debit(business=business, amount=income, user=request.user, description="Payroll")

			#### When Social funds and PAYE Tax are selected

			if paye_rate and social_rates:


				### When PAYE Tax and all Social Tax are selected

				if income <= 270000 and len(social_rates) == 3:

					social_payment = income * 0.26
					income = income - social_payment

					if bonus or overtime or deduction:
						income = income + bonus + overtime - deduction

					worker.tax_amount = social_payment
					worker.save()


					Takehome.objects.create(payroll=worker, salary=income, business=business)
					employee = Takehome.objects.filter(business=business, payroll=worker).first()

					if sdl:
						employee_salary = employee.salary 
						sdl = employee_salary * 0.04
						worker.sdl_amount = int(sdl)
						employee_salary = employee_salary - sdl
						employee.salary = employee_salary
						employee.save()
						worker.save()					

					#### Deduct loan return from employee
					if loan:
						if loan.debt == True :
							takehome_salary = employee.salary
							employee.salary = takehome_salary - loan.amount_paid
							loan.remaining_debt = loan.remaining_debt - loan.amount_paid
							worker.loan_debt = loan.remaining_debt
							loan.save()
							employee.save()
							worker.save()

					check_account_debit(business=business, amount=social_payment, user=request.user, description="Payroll Tax")
					check_account_debit(business=business, amount=income, user=request.user, description="Payroll")					

				elif 270000 < income <= 520000 and len(social_rates) == 3: 

					social_payment = income * 0.26
					paye_payment = (income - 270000) * 0.09
					total_payment = social_payment + paye_payment  
					income = income - total_payment

					if bonus or overtime or deduction:
						income = income + bonus + overtime - deduction

					worker.tax_amount = social_payment
					worker.paye_amount = paye_payment
					worker.save()

					Takehome.objects.create(payroll=worker, salary=income, business=business)
					employee = Takehome.objects.filter(business=business, payroll=worker).first()

					if sdl:
						employee_salary = employee.salary 
						sdl = employee_salary * 0.04
						worker.sdl_amount = int(sdl)
						employee_salary = employee_salary - sdl
						employee.salary = employee_salary
						employee.save()
						worker.save()					

					#### Deduct loan return from employee
					if loan:
						if loan.debt == True :
							takehome_salary = employee.salary
							employee.salary = takehome_salary - loan.amount_paid
							loan.remaining_debt = loan.remaining_debt - loan.amount_paid
							worker.loan_debt = loan.remaining_debt
							loan.save()
							employee.save()
							worker.save()
	
					check_account_debit(business=business, amount=social_payment, user=request.user, description="Payroll Tax")
					check_account_debit(business=business, amount=paye_payment, user=request.user, description="Paye")
					check_account_debit(business=business, amount=income, user=request.user, description="Payroll")

				elif 520000 < income <= 760000 and len(social_rates) == 3:  

					social_payment = income * 0.26
					paye_payment = (income - 520000) * 0.2 + 22500
					total_payment = social_payment + paye_payment  
					income = income - total_payment

					if bonus or overtime or deduction:
						income = income + bonus + overtime - deduction

					worker.tax_amount = social_payment
					worker.paye_amount = paye_payment
					worker.save()


					Takehome.objects.create(payroll=worker, salary=income, business=business)
					employee = Takehome.objects.filter(business=business, payroll=worker).first()

					if sdl:
						employee_salary = employee.salary 
						sdl = employee_salary * 0.04
						worker.sdl_amount = int(sdl)
						employee_salary = employee_salary - sdl
						employee.salary = employee_salary
						employee.save()
						worker.save()					

					#### Deduct loan return from employee
					if loan:
						if loan.debt == True :
							takehome_salary = employee.salary
							employee.salary = takehome_salary - loan.amount_paid
							loan.remaining_debt = loan.remaining_debt - loan.amount_paid
							worker.loan_debt = loan.remaining_debt
							loan.save()
							employee.save()
							worker.save()

					check_account_debit(business=business, amount=social_payment, user=request.user, description="Payroll Tax")
					check_account_debit(business=business, amount=paye_payment, user=request.user, description="Paye")
					check_account_debit(business=business, amount=income, user=request.user, description="Payroll")

				elif 760000 < income <= 1000000 and len(social_rates) == 3:

					social_payment = income * 0.26
					paye_payment = (income - 760000) * 0.25 + 70500
					total_payment = social_payment + paye_payment  
					income = income - total_payment

					if bonus or overtime or deduction:
						income = income + bonus + overtime - deduction

					worker.tax_amount = social_payment
					worker.paye_amount = paye_payment
					worker.save()


					Takehome.objects.create(payroll=worker, salary=income, business=business)
					employee = Takehome.objects.filter(business=business, payroll=worker).first()

					if sdl:
						employee_salary = employee.salary 
						sdl = employee_salary * 0.04
						worker.sdl_amount = int(sdl)
						employee_salary = employee_salary - sdl
						employee.salary = employee_salary
						employee.save()
						worker.save()					

					#### Deduct loan return from employee
					if loan:
						if loan.debt == True :
							takehome_salary = employee.salary
							employee.salary = takehome_salary - loan.amount_paid
							loan.remaining_debt = loan.remaining_debt - loan.amount_paid
							worker.loan_debt = loan.remaining_debt
							loan.save()
							employee.save()
							worker.save()

					check_account_debit(business=business, amount=social_payment, user=request.user, description="Payroll Tax")
					check_account_debit(business=business, amount=paye_payment, user=request.user, description="Paye")
					check_account_debit(business=business, amount=income, user=request.user, description="Payroll")
			
				elif 1000000 < income and len(social_rates) == 3:  

					social_payment = income * 0.26
					paye_payment = (income - 1000000) * 0.3 + 130500
					total_payment = social_payment + paye_payment  
					income = income - total_payment

					if bonus or overtime or deduction:
						income = income + bonus + overtime - deduction

					worker.tax_amount = social_payment
					worker.paye_amount = paye_payment
					worker.save()

					Takehome.objects.create(payroll=worker, salary=income, business=business)
					employee = Takehome.objects.filter(business=business, payroll=worker).first()

					if sdl:
						employee_salary = employee.salary 
						sdl = employee_salary * 0.04
						worker.sdl_amount = int(sdl)
						employee_salary = employee_salary - sdl
						employee.salary = employee_salary
						employee.save()
						worker.save()					

					#### Deduct loan return from employee
					if loan:
						if loan.debt == True :
							takehome_salary = employee.salary
							employee.salary = takehome_salary - loan.amount_paid
							loan.remaining_debt = loan.remaining_debt - loan.amount_paid
							worker.loan_debt = loan.remaining_debt
							loan.save()
							employee.save()
							worker.save()

					check_account_debit(business=business, amount=social_payment, user=request.user, description="Payroll Tax")
					check_account_debit(business=business, amount=paye_payment, user=request.user, description="Paye")
					check_account_debit(business=business, amount=income, user=request.user, description="Payroll")

				#### When PAYE Tax and both Social Tax is selected    

				if income <= 270000 and len(social_rates) == 2:

					if 'nssf' and 'wcf' in social_rates and not 'loan board' in social_rates:
						tax_payment = income * 0.11
						income = income - tax_payment

						if bonus or overtime or deduction:
							income = income + bonus + overtime - deduction

						worker.tax_amount = tax_payment
						worker.save()

						Takehome.objects.create(payroll=worker, salary=income, business=business)
						employee = Takehome.objects.filter(business=business, payroll=worker).first()

						if sdl:
							employee_salary = employee.salary 
							sdl = employee_salary * 0.04
							worker.sdl_amount = int(sdl)
							employee_salary = employee_salary - sdl
							employee.salary = employee_salary
							employee.save()
							worker.save()					

						#### Deduct loan return from employee
						if loan:
							if loan.debt == True :
								takehome_salary = employee.salary
								employee.salary = takehome_salary - loan.amount_paid
								loan.remaining_debt = loan.remaining_debt - loan.amount_paid
								worker.loan_debt = loan.remaining_debt
								loan.save()
								employee.save()
								worker.save()

						check_account_debit(business=business, amount=tax_payment, user=request.user, description="Payroll Tax")
						check_account_debit(business=business, amount=income, user=request.user, description="Payroll")

					elif 'nssf' and 'loan board' in social_rates and not 'wcf' in social_rates:
						tax_payment = income * 0.25
						income = income - tax_payment

						if bonus or overtime or deduction:
							income = income + bonus + overtime - deduction

						worker.tax_amount = tax_payment
						worker.save()

						Takehome.objects.create(payroll=worker, salary=income, business=business)
						employee = Takehome.objects.filter(business=business, payroll=worker).first()

						if sdl:
							employee_salary = employee.salary 
							sdl = employee_salary * 0.04
							worker.sdl_amount = int(sdl)
							employee_salary = employee_salary - sdl
							employee.salary = employee_salary
							employee.save()
							worker.save()					

						#### Deduct loan return from employee
						if loan:
							if loan.debt == True :
								takehome_salary = employee.salary
								employee.salary = takehome_salary - loan.amount_paid
								loan.remaining_debt = loan.remaining_debt - loan.amount_paid
								worker.loan_debt = loan.remaining_debt
								loan.save()
								employee.save()
								worker.save()

						check_account_debit(business=business, amount=tax_payment, user=request.user, description="Payroll Tax")
						check_account_debit(business=business, amount=income, user=request.user, description="Payroll")

					elif 'wcf' and 'loan board' in social_rates and not 'nssf' in social_rates:
						tax_payment = income * 0.16
						income = income - tax_payment

						if bonus or overtime or deduction:
							income = income + bonus + overtime - deduction

						worker.tax_amount = tax_payment
						worker.save()

						Takehome.objects.create(payroll=worker, salary=income, business=business)
						employee = Takehome.objects.filter(business=business, payroll=worker).first()

						if sdl:
							employee_salary = employee.salary 
							sdl = employee_salary * 0.04
							worker.sdl_amount = int(sdl)
							employee_salary = employee_salary - sdl
							employee.salary = employee_salary
							employee.save()
							worker.save()					

						#### Deduct loan return from employee
						if loan:
							if loan.debt == True :
								takehome_salary = employee.salary
								employee.salary = takehome_salary - loan.amount_paid
								loan.remaining_debt = loan.remaining_debt - loan.amount_paid
								worker.loan_debt = loan.remaining_debt
								loan.save()
								employee.save()
								worker.save()

						check_account_debit(business=business, amount=tax_payment, user=request.user, description="Payroll Tax")
						check_account_debit(business=business, amount=income, user=request.user, description="Payroll")

				elif 270000 < income <= 520000 and len(social_rates) == 2: 

					if 'nssf' and 'wcf' in social_rates and not 'loan board' in social_rates:
						social_payment = income * 0.11

					elif 'nssf' and 'loan board' in social_rates and not 'wcf' in social_rates:
						social_payment = income * 0.25

					elif 'wcf' and 'loan board' in social_rates and not 'nssf' in social_rates:
						social_payment = income * 0.16

					paye_payment = (income - 270000) * 0.09
					total_payment = social_payment + paye_payment  
					income = income - total_payment

					if bonus or overtime or deduction:
						income = income + bonus + overtime - deduction

					worker.tax_amount = social_payment
					worker.paye_amount = paye_payment
					worker.save()

					Takehome.objects.create(payroll=worker, salary=income, business=business)
					employee = Takehome.objects.filter(business=business, payroll=worker).first()

					if sdl:
						employee_salary = employee.salary 
						sdl = employee_salary * 0.04
						worker.sdl_amount = int(sdl)
						employee_salary = employee_salary - sdl
						employee.salary = employee_salary
						employee.save()
						worker.save()					

					#### Deduct loan return from employee
					if loan:
						if loan.debt == True :
							takehome_salary = employee.salary
							employee.salary = takehome_salary - loan.amount_paid
							loan.remaining_debt = loan.remaining_debt - loan.amount_paid
							worker.loan_debt = loan.remaining_debt
							loan.save()
							employee.save()
							worker.save()

					check_account_debit(business=business, amount=social_payment, user=request.user, description="Payroll Tax")
					check_account_debit(business=business, amount=paye_payment, user=request.user, description="Paye")
					check_account_debit(business=business, amount=income, user=request.user, description="Payroll")

				elif 520000 < income <= 760000 and len(social_rates) == 2:  

					if 'nssf' and 'wcf' in social_rates and not 'loan board' in social_rates:
						social_payment = income * 0.11

					elif 'nssf' and 'loan board' in social_rates and not 'wcf' in social_rates:
						social_payment = income * 0.25

					elif 'wcf' and 'loan board' in social_rates and not 'nssf' in social_rates:
						social_payment = income * 0.16

					paye_payment = (income - 520000) * 0.2 + 22500
					total_payment = social_payment + paye_payment  
					income = income - total_payment

					if bonus or overtime or deduction:
						income = income + bonus + overtime - deduction

					worker.tax_amount = social_payment
					worker.paye_amount = paye_payment
					worker.save()

					Takehome.objects.create(payroll=worker, salary=income, business=business)
					employee = Takehome.objects.filter(business=business, payroll=worker).first()

					if sdl:
						employee_salary = employee.salary 
						sdl = employee_salary * 0.04
						worker.sdl_amount = int(sdl)
						employee_salary = employee_salary - sdl
						employee.salary = employee_salary
						employee.save()
						worker.save()					

					#### Deduct loan return from employee
					if loan:
						if loan.debt == True :
							takehome_salary = employee.salary
							employee.salary = takehome_salary - loan.amount_paid
							loan.remaining_debt = loan.remaining_debt - loan.amount_paid
							worker.loan_debt = loan.remaining_debt
							loan.save()
							employee.save()
							worker.save()

					check_account_debit(business=business, amount=social_payment, user=request.user, description="Payroll Tax")
					check_account_debit(business=business, amount=paye_payment, user=request.user, description="Paye")
					check_account_debit(business=business, amount=income, user=request.user, description="Payroll")

				elif 760000 < income <= 1000000 and len(social_rates) == 2:

					if 'nssf' and 'wcf' in social_rates and not 'loan board' in social_rates:
						social_payment = income * 0.11

					elif 'nssf' and 'loan board' in social_rates and not 'wcf' in social_rates:
						social_payment = income * 0.25

					elif 'wcf' and 'loan board' in social_rates and not 'nssf' in social_rates:
						social_payment = income * 0.16

					paye_payment = (income - 760000) * 0.25 + 70500
					total_payment = social_payment + paye_payment  
					income = income - total_payment

					if bonus or overtime or deduction:
						income = income + bonus + overtime - deduction

					worker.tax_amount = social_payment
					worker.paye_amount = paye_payment
					worker.save()


					Takehome.objects.create(payroll=worker, salary=income, business=business)
					employee = Takehome.objects.filter(business=business, payroll=worker).first()

					if sdl:
						employee_salary = employee.salary 
						sdl = employee_salary * 0.04
						worker.sdl_amount = int(sdl)
						employee_salary = employee_salary - sdl
						employee.salary = employee_salary
						employee.save()
						worker.save()					

					#### Deduct loan return from employee
					if loan:
						if loan.debt == True :
							takehome_salary = employee.salary
							employee.salary = takehome_salary - loan.amount_paid
							loan.remaining_debt = loan.remaining_debt - loan.amount_paid
							worker.loan_debt = loan.remaining_debt
							loan.save()
							employee.save()
							worker.save()

					check_account_debit(business=business, amount=social_payment, user=request.user, description="Payroll Tax")
					check_account_debit(business=business, amount=paye_payment, user=request.user, description="Paye")
					check_account_debit(business=business, amount=income, user=request.user, description="Payroll")
			
				elif 1000000 < income and len(social_rates) == 2:  

					if 'nssf' and 'wcf' in social_rates and not 'loan board' in social_rates:
						social_payment = income * 0.11

					elif 'nssf' and 'loan board' in social_rates and not 'wcf' in social_rates:
						social_payment = income * 0.25

					elif 'wcf' and 'loan board' in social_rates and not 'nssf' in social_rates:
						social_payment = income * 0.16

					paye_payment = (income - 1000000) * 0.3 + 130500
					total_payment = social_payment + paye_payment  
					income = income - total_payment

					if bonus or overtime or deduction:
						income = income + bonus + overtime - deduction

					worker.tax_amount = social_payment
					worker.paye_amount = paye_payment
					worker.save()

					Takehome.objects.create(payroll=worker, salary=income, business=business)
					employee = Takehome.objects.filter(business=business, payroll=worker).first()

					if sdl:
						employee_salary = employee.salary 
						sdl = employee_salary * 0.04
						worker.sdl_amount = int(sdl)
						employee_salary = employee_salary - sdl
						employee.salary = employee_salary
						employee.save()
						worker.save()					

					#### Deduct loan return from employee
					if loan:
						if loan.debt == True :
							takehome_salary = employee.salary
							employee.salary = takehome_salary - loan.amount_paid
							loan.remaining_debt = loan.remaining_debt - loan.amount_paid
							worker.loan_debt = loan.remaining_debt
							loan.save()
							employee.save()
							worker.save()

					check_account_debit(business=business, amount=social_payment, user=request.user, description="Payroll Tax")
					check_account_debit(business=business, amount=paye_payment, user=request.user, description="Paye")
					check_account_debit(business=business, amount=income, user=request.user, description="Payroll")
				 
				#### When PAYE Tax and one Social Tax is selected    


				elif income <= 270000 and len(social_rates) == 1:

					for rate in social_rates:
						if rate == 'nssf':
							rate = 0.1

						elif rate == 'wcf':
							rate = 0.01

						elif rate == 'loan board':
							rate = 0.15	
							   
					tax_payment = income * rate
					income = income - tax_payment

					if bonus or overtime or deduction:
						income = income + bonus + overtime - deduction

					worker.tax_amount = tax_payment
					worker.save()

					Takehome.objects.create(payroll=worker, salary=income, business=business)
					employee = Takehome.objects.filter(business=business, payroll=worker).first()

					if sdl:
						employee_salary = employee.salary 
						sdl = employee_salary * 0.04
						worker.sdl_amount = int(sdl)
						employee_salary = employee_salary - sdl
						employee.salary = employee_salary
						employee.save()
						worker.save()					

					#### Deduct loan return from employee
					if loan:
						if loan.debt == True :
							takehome_salary = employee.salary
							employee.salary = takehome_salary - loan.amount_paid
							loan.remaining_debt = loan.remaining_debt - loan.amount_paid
							worker.loan_debt = loan.remaining_debt
							loan.save()
							employee.save()
							worker.save()

					check_account_debit(business=business, amount=tax_payment, user=request.user, description="Payroll Tax")
					check_account_debit(business=business, amount=income, user=request.user, description="Payroll")

				elif 270000 < income <= 520000 and len(social_rates) == 1:

					for rate in social_rates:
						if rate == 'nssf':
							rate = 0.1

						elif rate == 'wcf':
							rate = 0.01

						elif rate == 'loan board':
							rate = 0.15	

					social_payment = income * rate
					paye_payment = (income - 270000) * 0.09
					total_payment = social_payment + paye_payment  
					income = income - total_payment

					if bonus or overtime or deduction:
						income = income + bonus + overtime - deduction

					worker.tax_amount = social_payment
					worker.paye_amount = paye_payment
					worker.save()

					Takehome.objects.create(payroll=worker, salary=income, business=business)
					employee = Takehome.objects.filter(business=business, payroll=worker).first()

					if sdl:
						employee_salary = employee.salary 
						sdl = employee_salary * 0.04
						worker.sdl_amount = int(sdl)
						employee_salary = employee_salary - sdl
						employee.salary = employee_salary
						employee.save()
						worker.save()					

					#### Deduct loan return from employee
					if loan:
						if loan.debt == True :
							takehome_salary = employee.salary
							employee.salary = takehome_salary - loan.amount_paid
							loan.remaining_debt = loan.remaining_debt - loan.amount_paid
							worker.loan_debt = loan.remaining_debt
							loan.save()
							employee.save()
							worker.save()

					check_account_debit(business=business, amount=social_payment, user=request.user, description="Payroll Tax")
					check_account_debit(business=business, amount=paye_payment, user=request.user, description="Paye")
					check_account_debit(business=business, amount=income, user=request.user, description="Payroll")

				elif 520000 < income <= 760000 and len(social_rates) == 1:

					for rate in social_rates:
						if rate == 'nssf':
							rate = 0.1

						elif rate == 'wcf':
							rate = 0.01

						elif rate == 'loan board':
							rate = 0.15	

					social_payment = income * rate
					paye_payment = (income - 520000) * 0.2 + 22500
					total_payment = social_payment + paye_payment  
					income = income - total_payment

					if bonus or overtime or deduction:
						income = income + bonus + overtime - deduction

					worker.tax_amount = social_payment
					worker.paye_amount = paye_payment
					worker.save()

					Takehome.objects.create(payroll=worker, salary=income, business=business)
					employee = Takehome.objects.filter(business=business, payroll=worker).first()

					if sdl:
						employee_salary = employee.salary 
						sdl = employee_salary * 0.04
						worker.sdl_amount = int(sdl)
						employee_salary = employee_salary - sdl
						employee.salary = employee_salary
						employee.save()
						worker.save()					

					#### Deduct loan return from employee
					if loan:
						if loan.debt == True :
							takehome_salary = employee.salary
							employee.salary = takehome_salary - loan.amount_paid
							loan.remaining_debt = loan.remaining_debt - loan.amount_paid
							worker.loan_debt = loan.remaining_debt
							loan.save()
							employee.save()
							worker.save()

					check_account_debit(business=business, amount=social_payment, user=request.user, description="Payroll Tax")
					check_account_debit(business=business, amount=paye_payment, user=request.user, description="Paye")
					check_account_debit(business=business, amount=income, user=request.user, description="Payroll")

				elif 760000 < income <= 1000000 and len(social_rates) == 1:

					for rate in social_rates:
						if rate == 'nssf':
							rate = 0.1

						elif rate == 'wcf':
							rate = 0.01

						elif rate == 'loan board':
							rate = 0.15	

					social_payment = income * rate
					paye_payment = (income - 760000) * 0.25 + 70500
					total_payment = social_payment + paye_payment  
					income = income - total_payment

					if bonus or overtime or deduction:
						income = income + bonus + overtime - deduction

					worker.tax_amount = social_payment
					worker.paye_amount = paye_payment
					worker.save()						

					Takehome.objects.create(payroll=worker, salary=income, business=business)
					employee = Takehome.objects.filter(business=business, payroll=worker).first()

					if sdl:
						employee_salary = employee.salary 
						sdl = employee_salary * 0.04
						worker.sdl_amount = int(sdl)
						employee_salary = employee_salary - sdl
						employee.salary = employee_salary
						employee.save()
						worker.save()					

					#### Deduct loan return from employee
					if loan:
						if loan.debt == True :
							takehome_salary = employee.salary
							employee.salary = takehome_salary - loan.amount_paid
							loan.remaining_debt = loan.remaining_debt - loan.amount_paid
							worker.loan_debt = loan.remaining_debt
							loan.save()
							employee.save()
							worker.save()

					check_account_debit(business=business, amount=social_payment, user=request.user, description="Payroll Tax")
					check_account_debit(business=business, amount=paye_payment, user=request.user, description="Paye")
					check_account_debit(business=business, amount=income, user=request.user, description="Payroll")
			
				elif 1000000 < income and len(social_rates) == 1:

					for rate in social_rates:
						if rate == 'nssf':
							rate = 0.1

						elif rate == 'wcf':
							rate = 0.01

						elif rate == 'loan board':
							rate = 0.15	

					social_payment = income * rate
					paye_payment = (income - 1000000) * 0.3 + 130500
					total_payment = social_payment + paye_payment  
					income = income - total_payment

					if bonus or overtime or deduction:
						income = income + bonus + overtime - deduction

					worker.tax_amount = social_payment
					worker.paye_amount = paye_payment
					worker.save()						

					Takehome.objects.create(payroll=worker, salary=income, business=business)
					employee = Takehome.objects.filter(business=business, payroll=worker).first()

					if sdl:
						employee_salary = employee.salary 
						sdl = employee_salary * 0.04
						worker.sdl_amount = int(sdl)
						employee_salary = employee_salary - sdl
						employee.salary = employee_salary
						employee.save()
						worker.save()	

					#### Deduct loan return from employee
					if loan:
						if loan.debt == True :
							takehome_salary = employee.salary
							employee.salary = takehome_salary - loan.amount_paid
							loan.remaining_debt = loan.remaining_debt - loan.amount_paid
							worker.loan_debt = loan.remaining_debt
							loan.save()
							employee.save()
							worker.save()

					check_account_debit(business=business, amount=social_payment, user=request.user, description="Payroll Tax")
					check_account_debit(business=business, amount=paye_payment, user=request.user, description="Paye")
					check_account_debit(business=business, amount=income, user=request.user, description="Payroll")

			### When Pay rate and Social rates are not selected        

			if not paye_rate and not social_rates:

				if bonus or overtime or deduction:
					income = income + bonus + overtime - deduction               
			
				Takehome.objects.create(payroll=worker, salary=income, business=business)
				employee = Takehome.objects.filter(business=business, payroll=worker).first()

				if sdl:
					employee_salary = employee.salary 
					sdl = employee_salary * 0.04
					worker.sdl_amount = int(sdl)
					employee_salary = employee_salary - sdl
					employee.salary = employee_salary
					employee.save()
					worker.save()					

				#### Deduct loan return from employee
				if loan:
					if loan.debt == True :
						takehome_salary = employee.salary
						employee.salary = takehome_salary - loan.amount_paid
						loan.remaining_debt = loan.remaining_debt - loan.amount_paid
						worker.loan_debt = loan.remaining_debt
						loan.save()
						employee.save()
						worker.save()

				check_account_debit(business=business, amount=income, user=request.user, description="Payroll")			


			###HINT: 0.1 -> NSSF, 0.01 -> WCF, HELSB -> 0.15
			"""
				Total for each individual cut in Payroll i.e
				Paye, Bonuses, Overtime and Social funds
			"""	

			deduction = Payroll.objects.filter(business=business).aggregate(Sum('deduction'))['deduction__sum']   		
			bonuses = Payroll.objects.filter(business=business).aggregate(Sum('bonus'))['bonus__sum']   		
			overtime = Payroll.objects.filter(business=business).aggregate(Sum('overtime'))['overtime__sum']    		
			nssf = Payroll.objects.filter(tax_rate__icontains='nssf', business=business)
			wcf = Payroll.objects.filter(tax_rate__icontains='wcf', business=business)
			loan_board = Payroll.objects.filter(tax_rate__icontains='loan board', business=business)
			salaries = Payroll.objects.filter(business=business).aggregate(Sum('employee__salary'))['employee__salary__sum']
			paye_objs = Payroll.objects.filter(paye=True, business=business)

			### Total paye
			paye_total = 0

			if paye_objs:     	

				for worker in paye_objs:

					salary = worker.employee.salary

					if salary <= 270000:

						paye_total += 0

					elif 270000 < salary <= 520000:

						tax_payment = (salary - 270000) * 0.09 
						paye_total += tax_payment


					elif 520000 < salary <= 760000:

						tax_payment = (salary - 520000) * 0.2 + 22500 
						paye_total += tax_payment

					elif 760000 < salary <= 1000000:

						tax_payment = (salary - 760000) * 0.25 + 70500 
						paye_total += tax_payment


					elif 1000000 < salary:

						tax_payment = (salary - 1000000) * 0.3 + 130500 
						paye_total += tax_payment                  

			nssf_funds = 0
			wcf_funds = 0
			loan_board_funds = 0


			### Total Taxes in individuality
			total_funds = 0
			if nssf:
				for worker in nssf:
					total_funds += worker.employee.salary
				nssf_funds = total_funds * 0.1 
				total_funds = 0

			if wcf:
				for worker in wcf:
					total_funds += worker.employee.salary            	
				wcf_funds = total_funds * 0.01 
				total_funds = 0

			if loan_board:
				for worker in loan_board:
					total_funds += worker.employee.salary
				loan_board_funds = total_funds * 0.15 


			#### Saving Sum to the database
			total_id = Total.objects.filter(business=business).first()

			if total_id:

				Total.objects.filter(business=business).update(nssf=nssf_funds, wcf=wcf_funds, loan_board=loan_board_funds, paye=int(paye_total), bonus=bonuses, overtime=overtime, deduction=deduction)	
			
			else:
				Total.objects.create(nssf=nssf_funds, wcf=wcf_funds, loan_board=loan_board_funds, paye=int(paye_total), bonus=bonuses, overtime=overtime, deduction=deduction ,business=business)	

			takehome_salary = Takehome.objects.filter(business=business).aggregate(Sum('salary'))['salary__sum']


			total = Total.objects.filter(id=1, business=business).first()

			NSSF = total.nssf
			PAYE = total.paye
			LOAN = total.loan_board
			WCF = total.wcf
			BONUS = total.bonus
			OVERTIME = total.overtime
			DEDUCTION = total.deduction

			### Total payroll expenses
			total_expenses = NSSF + PAYE + LOAN + WCF + takehome_salary + sdl

			return redirect('business:takehome', id=id)  

		else:
			print(payroll_form.errors	)
			messages.warning(request, f'This employee is already on payroll')
			return redirect('business:takehome', id=id)  

	else:
		payroll_form = PayrollForm(business=business)

	context = {
		'business' : business,
		'payroll_form' : payroll_form,
		'takehome': takehome,
	}
	template_name = 'payroll-list.html'

	return render(request, template_name, context)


########## Payroll Delete ############
@finance_required
@login_required
def payroll_delete(request, *args, **kwargs):

	pk = kwargs.get('pk')
	id = kwargs.get('id')
	business = Business.objects.filter(id=id).first()   	
	payroll = Payroll.objects.filter(id=pk, business=business).first()
	takehome = Takehome.objects.filter(business=business)

	try:
		tax_payment = payroll.tax_amount
		paye_payment = payroll.paye_amount
		employee = Takehome.objects.filter(payroll=payroll, business=business).first()
		salary = employee.salary
		check_account_credit(business=business, amount=tax_payment, user=request.user, description="Payroll Tax")
		check_account_credit(business=business, amount=paye_payment, user=request.user, description="Paye")
		check_account_credit(business=business, amount=salary, user=request.user, description="Payroll")
		payroll.delete()
		messages.success(request, f'{payroll.employee.full_name} was deleted')
		return redirect('business:takehome', id=id)  


	except Exception as err:
		messages.info(request, f'Error : {err}')
		return redirect('business:takehome', id=id)  

				
	context = {
		'takehome': takehome,
	}

	template_name = 'payroll-list.html'
	return render(request, template_name, context)
	

############ Expense Form ################
@finance_required
@login_required
def expense(request, *args, **kwargs):

	id = kwargs.get('id')
	business = Business.objects.filter(id=id).first()    

	if request.method == 'POST':
		expense_form = ExpenseForm(request.POST)

		if expense_form.is_valid():
			expense_form.save(commit=False)

	else:
		expense_form = ExpenseForm() 

	context = {
		'business' : business,
		'exp_form': expense_form,
	}
	template_name = 'expense.html'

	return render(request, template_name, context)


############ Expense Update Form ################
@finance_required
@login_required
def expense_update(request, *args, **kwargs):

	id = kwargs.get('id')
	pk = kwargs.get('pk')
	business = Business.objects.filter(id=id).first()    
	expense_obj = Expense.objects.filter(id=pk, business=business).first()

	if request.method == 'POST':
		expense_form = ExpenseForm(request.POST or None, instance=expense_obj)

		if expense_form.is_valid():
			expense_form.save()
			expense_total = Expense.objects.aggregate(Sum('cost'))['cost__sum']

			Total.objects.filter(id=1, business=business).update(opex=expense_total)

			return redirect('business:expense-list', id=id)
		else:
			pass
	else:
		expense_form = ExpenseForm(instance=expense_obj) 

	context = {
		'business' : business,
		'exp_form': expense_form,
	}
	template_name = 'expense.html'

	return render(request, template_name, context)



########## Expense Delete ############
@finance_required
@login_required
def expense_delete(request, *args, **kwargs):

	pk = kwargs.get('pk')
	id = kwargs.get('id')
	business = Business.objects.filter(id=id).first()   	
	expense = Expense.objects.filter(id=pk, business=business).first()
	expenses = Expense.objects.filter(business=business)  

	try:

		cost = expense.cost
		name = expense.name
		check_account_credit(business=business, amount=cost, user=request.user, description=name)			
		expense.delete()
		messages.success(request, f'{expense.name} was deleted')
		return redirect('business:expense-list', id=id)


	except Exception as err:
		messages.info(request, f'Error : {err}')
		return redirect('business:expense-list', id=id)

				
	context = {
		'expenses' : expenses,
	}

	template_name = 'expense-list.html'
	return render(request, template_name, context)	


############ Expenses List ################
@finance_required
@login_required
def expense_list(request, *args, **kwargs):
	id = kwargs.get('id')
	business = Business.objects.filter(id=id).first()
	expenses = Expense.objects.filter(business=business)  

	if request.method == 'POST':
		expense_form = ExpenseForm(request.POST)

		if expense_form.is_valid():
			expense = expense_form.save(commit=False)
			expense.business = business
			expense.save()
			cost = expense.cost
			name = expense.name
			check_account_debit(business=business, amount=cost, user=request.user, description=name)			
			expense_total = Expense.objects.filter(business=business).aggregate(Sum('cost'))['cost__sum']

			Total.objects.filter(id=1, business=business).update(opex=expense_total)
			return redirect('business:expense-list', id=id)

	else:
		expense_form = ExpenseForm() 


	context = {
		'business' : business,
		'expenses' : expenses,
		'exp_form': expense_form,
	}
	template_name = 'expense-list.html'

	return render(request, template_name, context)


######### Fixed Assets Home ##############
@finance_required
@login_required
def fixed_assets(request, *args, **kwargs):
	id = kwargs.get('id')
	business = Business.objects.filter(id=id).first()
	context = {
		'business':business,
	}
	return render(request, "fixed-assets.html", context)  


 
############ FixedAsset Form ############### 
@finance_required
@login_required
def fixed_asset_list(request, *args, **kwargs):
	id = kwargs.get('id')
	business = Business.objects.filter(id=id).first()
	assets = FixedAsset.objects.filter(business=business)    

	if request.method == 'POST':
		fixed_asset_form = FixedAssetForm(request.POST)
		if fixed_asset_form.is_valid():
			asset = fixed_asset_form.save(commit=False)
			asset.business = business
			asset.save()
			buying_price_total = FixedAsset.objects.aggregate(Sum('buying_price'))['buying_price__sum']
			maintanance_fee_total = FixedAsset.objects.aggregate(Sum('maintanance_fee'))['maintanance_fee__sum']

			"""
				Depreciation / Amortizaion calculations
			"""


			"""
				If maintanance schedule in weeks
			"""

			if asset.maintanance_schedule_period == 'weeks':

				### Changing schedule to months

				maintanance_schedule = asset.maintanance_schedule * 0.23
	
			#### If maintanance schedule in years
			
			elif asset.maintanance_schedule_period == 'years':

				### Changing schedule to months

				maintanance_schedule = asset.maintanance_schedule * 12

			elif asset.maintanance_schedule_period == 'months':
				### Maintanance schedule in months

				maintanance_schedule = asset.maintanance_schedule 	

			
			"""
				Number of times in maintanance throughout usage of asset

			"""	

			"""
				If maintanance schedule in years
			"""

			if asset.usage_period_intervals== 'years':

				### Changing schedule to months

				usage_period = asset.usage_period_estimation * 12

			else:
				usage_period = asset.usage_period_estimation	


			#### Number of maintanace through usage period

			maintanance_times_though_usage = usage_period / maintanance_schedule


			##### Total maintanace estimated fee thoughout usage

			estimated_maintanance_fee = asset.maintanance_fee * maintanance_times_though_usage


			if asset.asset_type == 'tangible':

				###### For depreciation Value ######

				asset_cost = asset.buying_price + estimated_maintanance_fee

				depreciation_value = asset_cost / usage_period

				float_value = depreciation_value / asset_cost

				depreciation_percent = float_value * 100

				asset.depreciation_value = depreciation_value

				asset.depreciation_percent = round(depreciation_percent,1)

				### Saving asset object

				asset.save()

				return redirect('business:fixed-asset-list', id=id)


			elif asset.asset_type == 'intangible':

				###### For amortization Value ######

				asset_cost = asset.buying_price + estimated_maintanance_fee

				amortization_value = asset_cost / usage_period

				float_value = amortization_value / asset_cost

				amortization_percent = float_value * 100

				asset.amortization_value = amortization_value

				asset.amortization_percent = round(amortization_percent,1)

				### Saving asset object

				asset.save()

				return redirect('business:fixed-asset-list', id=id)

	else:
		fixed_asset_form = FixedAssetForm() 



	fixed_assets = FixedAsset.objects.filter(business=business)

	for asset in fixed_assets:

		date_bought = asset.date_bought
		today = date.today()

		time_period = today - date_bought
		time_period = time_period.days
		time_period = round(time_period/30)

		if asset.asset_type == 'intangible':

			amortization_amount = asset.amortization_value * time_period
			buying_price = asset.buying_price
			current_cost = buying_price - amortization_amount

			asset.value = current_cost
			asset.save()

		elif asset.asset_type == 'tangible':

			depreciation_amount = asset.depreciation_value * time_period
			buying_price = asset.buying_price
			current_cost = buying_price - depreciation_amount

			asset.value = current_cost
			asset.save()			


	context = {
		'business' : business,
		'fixed_asset_form' : fixed_asset_form,
		'assets': assets,
	}
	template_name = 'fixed-asset-list.html'

	return render(request, template_name, context) 


############### FixedAsset Update Form ################
@finance_required
@login_required
def fixed_asset_update(request, *args, **kwargs):

	id = kwargs.get('id')
	pk = kwargs.get('pk')
	business = Business.objects.filter(id=id).first()    
	fixed_asset = FixedAsset.objects.filter(id=pk, business=business).first()

	if request.method == 'POST':
		fixed_asset_form = FixedAssetForm(request.POST or None, instance=fixed_asset)

		if fixed_asset_form.is_valid():
			asset = fixed_asset_form.save()

			"""
				Depreciation / Amortizaion calculations
			"""


			"""
				If maintanance schedule in weeks
			"""

			if asset.maintanance_schedule_period == 'weeks':

				### Changing schedule to months

				maintanance_schedule = asset.maintanance_schedule * 0.23

	
			###### If maintanance schedule in years

			elif asset.maintanance_schedule_period == 'years':

				### Changing schedule to months

				maintanance_schedule = asset.maintanance_schedule * 12

			elif asset.maintanance_schedule_period == 'months':
				### Maintanance schedule in months

				maintanance_schedule = asset.maintanance_schedule 	

			
			"""
				Number of times in maintanance throughout usage of asset

			"""	

			"""
				If maintanance schedule in years
			"""

			if asset.usage_period_intervals== 'years':

				### Changing schedule to months

				usage_period = asset.usage_period_estimation * 12

			else:
				usage_period = asset.usage_period_estimation	


			#### Number of maintanace through usage period

			maintanance_times_though_usage = usage_period / maintanance_schedule


			##### Total maintanace estimated fee thoughout usage

			estimated_maintanance_fee = asset.maintanance_fee * maintanance_times_though_usage


			if asset.asset_type == 'tangible':

				###### For depreciation Value ######

				asset_cost = asset.buying_price + estimated_maintanance_fee

				depreciation_value = asset_cost / usage_period

				float_value = depreciation_value / asset_cost

				depreciation_percent = float_value * 100

				asset.depreciation_value = depreciation_value

				asset.depreciation_percent = round(depreciation_percent,1)

				### Saving asset object

				asset.save()

				return redirect('business:fixed-asset-list', id=id)


			elif asset.asset_type == 'intangible':

				###### For amortization Value ######

				asset_cost = asset.buying_price + estimated_maintanance_fee

				amortization_value = asset_cost / usage_period

				float_value = amortization_value / asset_cost

				amortization_percent = float_value * 100

				asset.amortization_value = amortization_value


				asset.amortization_percent = round(amortization_percent,1)

				### Saving asset object

				asset.save()

				return redirect('business:fixed-asset-list', id=id)

	else:
		fixed_asset_form =  FixedAssetForm(instance=fixed_asset) 

	context = {
		'business' : business,
		'fixed_asset_form': fixed_asset_form,
	}
	template_name = 'fixed-asset-form.html'

	return render(request, template_name, context)          

@login_required
def procurement_management(request, *args, **kwargs):
	id = kwargs.get('id')
	business = Business.objects.filter(id=id).first()
	context = {
		'business':business,
	}
	return render(request, 'procurement_management.html', context)


@procurement_required
@login_required
def suppliers(request, *args, **kwargs):
	id = kwargs.get('id')
	business = Business.objects.filter(id=id).first()
	suppliers = Supplier.objects.filter(business=business).all()
	context = {
		'business':business,
		'suppliers':suppliers,
	}
	return render(request, 'suppliers.html', context)


@procurement_required
@login_required
def add_supplier(request, *args, **kwargs):
	id = kwargs.get('id')
	business = Business.objects.filter(id=id).first()
	if request.method == "POST":
		form = SupplierForm(request.POST or None)
		if form.is_valid():
			supplier = form.save(commit=False)
			supplier.business = business
			supplier.save()
			return redirect('business:suppliers', id=id)
	else:
		form = SupplierForm()
		
	context = {
		'business':business,
		'form':form
	}
	return render(request, 'add_supplier.html', context)


@procurement_required
@login_required
def edit_supplier(request, *args, **kwargs):
	id = kwargs.get('id')
	supplier = Supplier.objects.filter(id=id).first()
	if request.method == "POST":
		form = SupplierForm(request.POST or None, instance=supplier)
		if form.is_valid():
			form.save()
			return redirect('business:suppliers', id=supplier.business.id)
	else:
		form = SupplierForm(instance=supplier)
		
	context = {
		'business':supplier.business,
		'form':form
	}
	return render(request, 'edit_supplier.html', context)


@procurement_finance_ceo_required
@login_required
def purchase_order(request, *args, **kwargs):
	id = kwargs.get('id')
	business = Business.objects.filter(id=id).first()
	purchases = PurchaseOrder.objects.filter(Q(business=business, created_at__date=date.today())|Q(business=business, authorized=False)).all()
	context = {
		'business':business,
		'purchases':purchases,
	}
	return render(request, 'purchase_order.html', context)


@procurement_finance_ceo_required
@login_required
def view_purchase_order(request, *args, **kwargs):
	id = kwargs.get('id')
	purchase_order = PurchaseOrder.objects.filter(id=id).first()
	context = {
		'business':purchase_order.business,
		'purchase_order':purchase_order,
	}
	return render(request, 'view_purchase_order.html', context)


@procurement_required
@login_required
def add_purchase_order(request, *args, **kwargs):
	id = kwargs.get('id')
	business = Business.objects.filter(id=id).first()
	data = datetime.now()
	if request.method == "POST":
		purchase_order_form = PurchaseOrderForm(request.POST or None, business=business)
		purchase_order_list_form = PurchaseOrderListFormSet(request.POST or None,)
		if purchase_order_form.is_valid() and purchase_order_list_form.is_valid():
			purchase_order = purchase_order_form.save(commit=False)
			purchase_order.business = business
			purchase_order.employee = request.user
			purchase_order.save()

			purchase_order_list_form.instance = purchase_order
			purchase_order_list_form.save()

			if purchase_order.published:
				users = User.objects.filter(Q(user_employee__position='Accountant')|Q(user_employee__position='Financial Manager')|Q(user_employee__position='CEO'))
				try:
					notify.send(sender=request.user, recipient=users, action_object=purchase_order, level="info", verb="{0} created Purchase Order No. {1}".format(request.user.user_employee.full_name, purchase_order.po_no))
				except:
					pass				

				current_site = get_current_site(request)
				subject = "Purchase No. {0} Created.".format(purchase_order.po_no)
				html_message = render_to_string("purchase_order_email.html",{'purchase_order':purchase_order,'domain': current_site.domain,})
				message = strip_tags(html_message)
				from_email = 'cscu.fredrick@gmail.com'
				recipient_list=[]
				for user in users:
					recipient_list.append(user.user_employee.email)
				email = EmailMultiAlternatives(subject, message, from_email, recipient_list)
				email.attach_alternative(html_message, "text/html")
				email.send()

			return redirect('business:purchase_order', id=business.id)
	else:
		purchase_order_form = PurchaseOrderForm(initial={'po_no':data.strftime("%Y%m%d/%H%M%S")}, business=business)
		purchase_order_list_form = PurchaseOrderListFormSet()
	context = {
		'business':business,
		'purchase_order_form':purchase_order_form,
		'purchase_order_list_form':purchase_order_list_form,
	}
	return render(request, 'add_purchase_order.html', context)


@procurement_required
@login_required
def edit_purchase_order(request, *args, **kwargs):
	id = kwargs.get('id')
	purchase_order = PurchaseOrder.objects.filter(id=id).first()
	if request.method == "POST":
		purchase_order_form = PurchaseOrderForm(request.POST or None, business=purchase_order.business, instance=purchase_order)
		purchase_order_list_form = PurchaseOrderListUpdateFormSet(request.POST or None, instance=purchase_order)
		if purchase_order_form.is_valid() and purchase_order_list_form.is_valid():
			purchase_order = purchase_order_form.save()
			purchase_order_list_form.save()

			if purchase_order.published:
				users = User.objects.filter(Q(user_employee__position='Accountant')|Q(user_employee__position='Financial Manager')|Q(user_employee__position='CEO'))
				try:
					notify.send(sender=request.user, recipient=users, action_object=purchase_order, level="info", verb="{0} updated Purchase Order No. {1}".format(request.user.user_employee.full_name, purchase_order.po_no))
				except:
					pass				

				current_site = get_current_site(request)
				subject = "Purchase No. {0} Updated.".format(purchase_order.po_no)
				html_message = render_to_string("purchase_order_email.html",{'purchase_order':purchase_order,'domain': current_site.domain,})
				message = strip_tags(html_message)
				from_email = 'cscu.fredrick@gmail.com'
				recipient_list=[]
				for user in users:
					recipient_list.append(user.user_employee.email)
				email = EmailMultiAlternatives(subject, message, from_email, recipient_list)
				email.attach_alternative(html_message, "text/html")
				email.send()

			return redirect('business:purchase_order', id=purchase_order.business.id)
		else:
			pass
	else:
		purchase_order_form = PurchaseOrderForm(instance=purchase_order, business=purchase_order.business)
		purchase_order_list_form = PurchaseOrderListUpdateFormSet(instance=purchase_order)
	context = {
		'business':purchase_order.business,
		'purchase_order_form':purchase_order_form,
		'purchase_order_list_form':purchase_order_list_form,
	}
	return render(request, 'edit_purchase_order.html', context)


@procurement_finance_ceo_required
@login_required
def local_purchase_order(request, *args, **kwargs):
	id = kwargs.get('id')
	business = Business.objects.filter(id=id).first()
	local_purchases = LocalPurchaseOrder.objects.filter(Q(business=business,created_at__date=date.today())|Q(business=business, authorized=False)).all()
	context = {
		'business':business,
		'purchases':local_purchases,
	}
	return render(request, 'local_purchase_order.html', context)


@procurement_finance_ceo_required
@login_required
def view_local_purchase_order(request, *args, **kwargs):
	id = kwargs.get('id')
	local_purchase_order = LocalPurchaseOrder.objects.filter(id=id).first()
	context = {
		'business':local_purchase_order.business,
		'local_purchase_order':local_purchase_order,
	}
	return render(request, 'view_local_purchase_order.html', context)


@procurement_required
@login_required
def add_local_purchase_order(request, *args, **kwargs):
	id = kwargs.get('id')
	business = Business.objects.filter(id=id).first()
	data = datetime.now()
	if request.method == "POST":
		local_purchase_order_form = LocalPurchaseOrderForm(request.POST or None, business=business)
		local_purchase_order_list_form = LocalPurchaseOrderListFormSet(request.POST or None,)
		if local_purchase_order_form.is_valid() and local_purchase_order_list_form.is_valid():
			local_purchase_order = local_purchase_order_form.save(commit=False)
			local_purchase_order.business = business
			local_purchase_order.employee = request.user
			local_purchase_order.save()

			local_purchase_order_list_form.instance = local_purchase_order
			local_purchase_order_list_form.save()

			if local_purchase_order.published:
				users = User.objects.filter(Q(user_employee__position='Accountant')|Q(user_employee__position='Financial Manager')|Q(user_employee__position='CEO'))
				try:
					notify.send(sender=request.user, recipient=users, action_object=local_purchase_order, level="info",	verb="{0} created Local Purchase Order No. {1}".format(request.user.user_employee.full_name, local_purchase_order.lpo_no))
				except:
					pass

				current_site = get_current_site(request)
				subject = "Local Purchase No. {0} Created.".format(local_purchase_order.lpo_no)
				html_message = render_to_string("local_purchase_order_email.html",{'purchase_order':local_purchase_order,'domain': current_site.domain,})
				message = strip_tags(html_message)
				from_email = 'cscu.fredrick@gmail.com'
				recipient_list=[]
				for user in users:
					recipient_list.append(user.user_employee.email)
				email = EmailMultiAlternatives(subject, message, from_email, recipient_list)
				email.attach_alternative(html_message, "text/html")
				email.send()

			return redirect('business:local_purchase_order', id=business.id)
	else:
		local_purchase_order_form = LocalPurchaseOrderForm(initial={'lpo_no':data.strftime("%Y%m%d/%H%M%S")}, business=business)
		local_purchase_order_list_form = LocalPurchaseOrderListFormSet()
	context = {
		'business':business,
		'purchase_order_form':local_purchase_order_form,
		'purchase_order_list_form':local_purchase_order_list_form,
	}
	return render(request, 'add_local_purchase_order.html', context)


@procurement_required
@login_required
def edit_local_purchase_order(request, *args, **kwargs):
	id = kwargs.get('id')
	local_purchase_order = LocalPurchaseOrder.objects.filter(id=id).first()
	if request.method == "POST":
		local_purchase_order_form = LocalPurchaseOrderForm(request.POST or None, business=local_purchase_order.business, instance=local_purchase_order)
		local_purchase_order_list_form = LocalPurchaseOrderListUpdateFormSet(request.POST or None, instance=local_purchase_order)
		if local_purchase_order_form.is_valid() and local_purchase_order_list_form.is_valid():
			local_purchase_order = local_purchase_order_form.save()
			local_purchase_order_list_form.save()

			if local_purchase_order.published:
				users = User.objects.filter(Q(user_employee__position='Accountant')|Q(user_employee__position='Financial Manager')|Q(user_employee__position='CEO'))

				try:
					notify.send(sender=request.user, recipient=users, action_object=local_purchase_order, level="info", verb="{0} updated Local Purchase Order No. {1}".format(request.user.user_employee.full_name, local_purchase_order.lpo_no))
				except:
					pass
				
				current_site = get_current_site(request)
				subject = "Local Purchase No. {0} Updated.".format(local_purchase_order.lpo_no)
				html_message = render_to_string("local_purchase_order_email.html",{'purchase_order':local_purchase_order,'domain': current_site.domain,})
				message = strip_tags(html_message)
				from_email = 'cscu.fredrick@gmail.com'
				recipient_list=[]
				for user in users:
					recipient_list.append(user.user_employee.email)
				email = EmailMultiAlternatives(subject, message, from_email, recipient_list)
				email.attach_alternative(html_message, "text/html")
				email.send()

			return redirect('business:local_purchase_order', id=local_purchase_order.business.id)
		else:
			pass
	else:
		local_purchase_order_form = LocalPurchaseOrderForm(instance=local_purchase_order, business=local_purchase_order.business)
		local_purchase_order_list_form = LocalPurchaseOrderListUpdateFormSet(instance=local_purchase_order)
	context = {
		'business':local_purchase_order.business,
		'purchase_order_form':local_purchase_order_form,
		'purchase_order_list_form':local_purchase_order_list_form,
	}
	return render(request, 'edit_local_purchase_order.html', context)      


################ Accounts ################
@finance_required
@login_required
def accounts(request, *args, **kwargs):
	id = kwargs.get('id')
	pk = kwargs.get('pk')	
	business = Business.objects.filter(id=id).first() 
	context = {
		'business': business,
	}
	template_name = 'accounts.html'
	return render(request, template_name, context)


################ Bank Accounts################
@finance_required
@login_required
def bank_accounts(request, *args, **kwargs):
	id = kwargs.get('id')
	pk = kwargs.get('pk')	
	business = Business.objects.filter(id=id).first() 
	context = {
		'business': business,
	}
	template_name = 'bank-accounts.html'
	return render(request, template_name, context)

################ Assets (Accounts) ################
@finance_required
@login_required
def assets(request, *args, **kwargs):
	id = kwargs.get('id')
	pk = kwargs.get('pk')	
	business = Business.objects.filter(id=id).first() 

	context = {
		'business': business,
	}
	template_name = 'assets.html'

	return render(request, template_name, context) 

################ Fixed Assets (Accounts) ################
@finance_required
@login_required
def fixed_assets(request, *args, **kwargs):
	id = kwargs.get('id')
	pk = kwargs.get('pk')	
	business = Business.objects.filter(id=id).first() 
	assets = AccountsFixedAsset.objects.filter(business=business, created_at__date=date.today())    

	if request.method == 'POST':
		fixed_asset_form = AccountsFixedAssetForm(request.POST)

		if fixed_asset_form.is_valid():
			asset = fixed_asset_form.save(commit=False)
			asset.business = business
			asset.save()

			"""
				Depreciation / Amortizaion calculations
			"""


			"""
				If maintanance schedule in weeks
			"""

			if asset.maintanance_schedule_period == 'weeks':

				### Changing schedule to months

				maintanance_schedule = asset.maintanance_schedule * 0.23

			##### If maintanance schedule in years

			elif asset.maintanance_schedule_period == 'years':

				### Changing schedule to months

				maintanance_schedule = asset.maintanance_schedule * 12

			elif asset.maintanance_schedule_period == 'months':
				### Maintanance schedule in months

				maintanance_schedule = asset.maintanance_schedule 	

			
			"""
				Number of times in maintanance throughout usage of asset

			"""	

			"""
				If maintanance schedule in years
			"""

			if asset.usage_period_intervals== 'years':

				### Changing schedule to months

				usage_period = asset.usage_period_estimation * 12

			else:
				usage_period = asset.usage_period_estimation	


			#### Number of maintanace through usage period

			maintanance_times_though_usage = usage_period / maintanance_schedule


			##### Total maintanace estimated fee thoughout usage

			estimated_maintanance_fee = asset.maintanance_fee * maintanance_times_though_usage


			if asset.asset_type == 'tangible':

				###### For depreciation Value ######

				asset_cost = asset.cost + estimated_maintanance_fee

				depreciation_value = asset_cost / usage_period

				float_value = depreciation_value / asset_cost

				depreciation_percent = float_value * 100

				asset.depreciation_value = depreciation_value

				asset.depreciation_percent = round(depreciation_percent,1)

				### Saving asset object

				asset.save()

				return redirect('business:fixed_assets-list', id=id)


			elif asset.asset_type == 'intangible':

				###### For amortization Value ######

				asset_cost = asset.cost + estimated_maintanance_fee

				amortization_value = asset_cost / usage_period

				float_value = amortization_value / asset_cost

				amortization_percent = float_value * 100

				asset.amortization_value = amortization_value

				asset.amortization_percent = round(amortization_percent,1)

				### Saving asset object

				asset.save()

				return redirect('business:fixed_assets-list', id=id)
			
	else:
		fixed_asset_form = AccountsFixedAssetForm()


	fixed_assets = AccountsFixedAsset.objects.filter(business=business)

	for asset in fixed_assets:

		date_bought = asset.date_bought
		today = date.today()

		time_period = today - date_bought
		time_period = time_period.days
		time_period = round(time_period/30)

		if asset.asset_type == 'intangible':

			amortization_amount = asset.amortization_value * time_period
			buying_price = asset.cost
			current_cost = buying_price - amortization_amount

			asset.value = current_cost
			asset.save()

		elif asset.asset_type == 'tangible':

			depreciation_amount = asset.depreciation_value * time_period
			buying_price = asset.cost
			current_cost = buying_price - depreciation_amount

			asset.value = current_cost
			asset.save()			



	context = {
		'business': business,
		'assets': assets, 
		'asset_form': fixed_asset_form,
	}
	template_name = 'fixed_assets-list.html'

	return render(request, template_name, context) 


################ Fixed Assets Update(Accounts) ################
@finance_required
@login_required
def fixed_assets_update(request, *args, **kwargs):
	id = kwargs.get('id')
	pk = kwargs.get('pk')	
	business = Business.objects.filter(id=id).first() 
	asset = AccountsFixedAsset.objects.filter(id=pk, business=business).first()    

	if request.method == 'POST':
		fixed_asset_form = AccountsFixedAssetForm(request.POST or None, instance=asset)

		if fixed_asset_form.is_valid():
			asset = fixed_asset_form.save()

			"""
				Depreciation / Amortizaion calculations
			"""


			"""
				If maintanance schedule in weeks
			"""

			if asset.maintanance_schedule_period == 'weeks':

				### Changing schedule to months

				maintanance_schedule = asset.maintanance_schedule * 0.23

			###### If maintanance schedule in years

			elif asset.maintanance_schedule_period == 'years':

				### Changing schedule to months

				maintanance_schedule = asset.maintanance_schedule * 12

			elif asset.maintanance_schedule_period == 'months':
				### Maintanance schedule in months

				maintanance_schedule = asset.maintanance_schedule 	

			
			"""
				Number of times in maintanance throughout usage of asset

			"""	

			"""
				If maintanance schedule in years
			"""

			if asset.usage_period_intervals== 'years':

				### Changing schedule to months

				usage_period = asset.usage_period_estimation * 12

			else:
				usage_period = asset.usage_period_estimation	


			#### Number of maintanace through usage period

			maintanance_times_though_usage = usage_period / maintanance_schedule


			##### Total maintanace estimated fee thoughout usage

			estimated_maintanance_fee = asset.maintanance_fee * maintanance_times_though_usage


			if asset.asset_type == 'tangible':

				###### For depreciation Value ######

				asset_cost = asset.cost + estimated_maintanance_fee

				depreciation_value = asset_cost / usage_period

				float_value = depreciation_value / asset_cost

				depreciation_percent = float_value * 100

				asset.depreciation_value = depreciation_value

				asset.depreciation_percent = round(depreciation_percent,1)

				### Saving asset object

				asset.save()

				return redirect('business:fixed_assets-list', id=id)


			elif asset.asset_type == 'intangible':

				###### For amortization Value ######

				asset_cost = asset.cost + estimated_maintanance_fee

				amortization_value = asset_cost / usage_period

				float_value = amortization_value / asset_cost

				amortization_percent = float_value * 100

				asset.amortization_value = amortization_value

				asset.amortization_percent = round(amortization_percent,1)

				### Saving asset object

				asset.save()

				return redirect('business:fixed_assets-list', id=id)

	else:
		fixed_asset_form = AccountsFixedAssetForm(instance=asset)

	context = {
		'business': business, 
		'asset_form': fixed_asset_form,
	}
	template_name = 'fixed_assets-update.html'

	return render(request, template_name, context) 


################ Current Assets (Accounts) ################
@finance_required
@login_required
def current_assets(request, *args, **kwargs):
	id = kwargs.get('id')
	pk = kwargs.get('pk')	
	business = Business.objects.filter(id=id).first() 
	assets = AccountsCurrentAsset.objects.filter(business=business, created_at__date=date.today())  
	inventory_qs = Inventory.objects.filter(business=business).annotate(available=F('remain')-F('damage'))			
	inventories = inventory_qs.filter(available__gt=0).order_by('-pk')
	total_worth = inventory_qs.aggregate(total_worth=Sum(F('available')*F('product__sell_price'),output_field=FloatField()))['total_worth']  

	if request.method == 'POST':
		current_asset_form = AccountsCurrentAssetForm(request.POST)

		if current_asset_form.is_valid():
			current = current_asset_form.save(commit=False)
			current.business = business
			current.save()
			return redirect('business:current_assets-list', id=id)

	else:
		current_asset_form = AccountsCurrentAssetForm()

	context = {
		'business': business,
		'assets': assets,
		'asset_form': current_asset_form,
		'total_worth':total_worth,
	}
	template_name = 'current_assets-list.html'

	return render(request, template_name, context)


################ Current Assets Update(Accounts) ################
@finance_required
@login_required
def current_assets_update(request, *args, **kwargs):
	id = kwargs.get('id')
	pk = kwargs.get('pk')	
	business = Business.objects.filter(id=id).first() 
	asset = AccountsCurrentAsset.objects.filter(id=pk, business=business).first()    

	if request.method == 'POST':
		current_asset_form = AccountsCurrentAssetForm(request.POST or None, instance=asset)

		if current_asset_form.is_valid():
			current_asset_form.save()
			return redirect('business:current_assets-list', id=id)

	else:
		current_asset_form = AccountsCurrentAssetForm(instance=asset)

	context = {
		'business': business,
		'asset_form': current_asset_form,
	}
	template_name = 'current_assets-update.html'

	return render(request, template_name, context)


################ Liabilities ################
@finance_required
@login_required
def liabilities_list(request, *args, **kwargs):
	id = kwargs.get('id')
	pk = kwargs.get('pk')	
	business = Business.objects.filter(id=id).first() 
	liabilities = Liability.objects.filter(business=business) 
	interest_total = Interest.objects.filter(business=business).aggregate(Sum('remaining'))['remaining__sum']
	tax_total = Tax.objects.filter(business=business,).aggregate(total=Sum('remain'))['total']

	if request.method == 'POST':
		liability_form = LiabilityForm(request.POST)

		if liability_form.is_valid():
			liability = liability_form.save(commit=False)
			liability.business = business
			liability.save()
			return redirect('business:liabilities-list', id=id)

	else:
		liability_form = LiabilityForm()

	context = {
		'business': business,
		'liabilities': liabilities,
		'liability_form': liability_form,
		'interest_total': interest_total,
		'tax_total':tax_total,
		
	}
	template_name = 'liabilities-list.html'

	return render(request, template_name, context)     


################ Liabilities Update ################
@finance_required
@login_required
def liabilities_update(request, *args, **kwargs):
	id = kwargs.get('id')
	pk = kwargs.get('pk')	
	business = Business.objects.filter(id=id).first() 
	liability = Liability.objects.filter(id=pk, business=business).first()

	if request.method == 'POST':
		liability_form = LiabilityForm(request.POST or None, instance=liability)

		if liability_form.is_valid():
			liability_form.save()
			return redirect('business:liabilities-list', id=id)

	else:
		liability_form = LiabilityForm(instance=liability)

	context = {
		'business': business,
		'liability_form': liability_form,

	}
	template_name = 'liabilities-update.html'

	return render(request, template_name, context)     


############# Check Account ###################
@finance_required
@login_required
def check_account(request, *args, **kwargs):

	transfer = kwargs.get('trans')
	id = kwargs.get('id')
	business = Business.objects.filter(id=id).first()
	check_account = CheckAccount.objects.filter(business=business).last()
	first_account = CheckAccount.objects.filter(business=business).first()
	if first_account:	
		opening_balance = first_account.balance
	else:
		opening_balance = 0

	### Get Saving acount object
	saving_account = SavingAccount.objects.filter(business=business).last()

	if check_account:
		#### Updating Check Account Balance after expenses
		check_account_balance = check_account.balance

	if request.method == 'POST':

		if transfer == 'True':

			"""
				Money transfer from Check to Saving Account
			"""
			transaction_form = TransactionForm(request.POST)

			if transaction_form.is_valid():

				transfer_from = request.POST['transaction_from']
				transfer_to = request.POST['transaction_to']
				transfer_amount = request.POST['amount']

				transfer_amount = int(transfer_amount)
				check_account_balance = int(check_account_balance)

				if transfer_from == transfer_to:

					messages.warning(request, "You can't make transfer to the same account")
					return redirect('business:check-account', id=business.id, trans=False)

				if transfer_from == 'Saving Account' and transfer_to == 'Check Account':

					messages.warning(request, "This operation should be done from Saving Account")
					return redirect('business:check-account', id=business.id, trans=False)

				if transfer_amount > check_account_balance:

					messages.warning(request, "You do not have enough amount to make this transaction")
					return redirect('business:check-account', id=business.id, trans=False)
					
				else:

					if saving_account is None:
						messages.info(request, "Saving account has not been created")
						return redirect('business:check-account', id=business.id, trans=False)						

					else:
						transaction = transaction_form.save()
						amount = transaction.amount
						check_account_debit(business=business, amount=amount, user=request.user, description="Transfer to Saving Account")			
						saving_account_credit(business=business, amount=amount, user=request.user, description="Recieved from Check Account")			
						messages.success(request, f"Successfully transfered {transaction.amount}")
						return redirect('business:check-account', id=business.id, trans=False)


			else:
				transaction_form = TransactionForm()				

		else:
			"""
				Creating Check Account
			"""
			account_form = CheckAccountForm(request.POST)

			if account_form.is_valid():

				amount = request.POST['balance']
				user = request.user

				account_form = account_form.save(commit=False)
				account_form.description = 'Opening Balance'
				account_form.business = business
				account_form.employee = user
				account_form.credit = amount
				account_form.debit = 0.00
				account_form.balance = amount
				account_form.save()
				return redirect('business:check-account', id=business.id, trans=False)

			else:
				transaction_form = TransactionForm()	

	else:
		transaction_form = TransactionForm()
		account_form = CheckAccountForm()				



	context = {
		'business': business,
		'account_form': account_form,
		'check_account': check_account,
		# 'balance': check_account_balance,
		'transaction_form': transaction_form,
		'opening_balance' : opening_balance,

	}
	template_name = 'check-account.html'
	return render(request, template_name, context)


############# Saving Account ###################
@finance_required
@login_required
def saving_account(request, *args, **kwargs):

	transfer = kwargs.get('trans')
	id = kwargs.get('id')
	business = Business.objects.filter(id=id).first()
	first_account = SavingAccount.objects.filter(business=business).first()
	if first_account:
		opening_balance = first_account.balance
	else:
		opening_balance = 0

	### Get check acount object
	check_account = CheckAccount.objects.filter(business=business).last()

	### Get Saving acount object
	saving_account = SavingAccount.objects.filter(business=business).last()


	if request.method == 'POST':

		if transfer == 'True':

			"""
				Money transfer from Saving to Check Account
			"""
			transaction_form = TransactionForm(request.POST)

			if transaction_form.is_valid():

				transfer_from = request.POST['transaction_from']
				transfer_to = request.POST['transaction_to']
				transfer_amount = request.POST['amount']

				transfer_amount = int(transfer_amount)

				if transfer_from == transfer_to:

					messages.warning(request, "You can't make transfer to the same account")
					return redirect('business:saving-account', id=business.id, trans=False)

				if transfer_from == 'Check Account' and transfer_to == 'Saving Account':

					messages.warning(request, "This operation should be done from Check Account")
					return redirect('business:saving-account', id=business.id, trans=False)

				if transfer_amount > saving_account.balance:

					messages.warning(request, "You do not have enough amount to make this transaction")
					return redirect('business:saving-account', id=business.id, trans=False)
					
				else:

					if check_account is None:
						messages.info(request, "Check account has not been created")
						return redirect('business:saving-account', id=business.id, trans=False)						

					else:
						transaction = transaction_form.save()
						amount = transaction.amount
						saving_account_debit(business=business, amount=amount, user=request.user, description="Transfer to Check Account")			
						check_account_credit(business=business, amount=amount, user=request.user, description="Recieved From Saving Account")			
						messages.success(request, f"Successfully transfered {transaction.amount}")
						return redirect('business:saving-account', id=business.id, trans=False)

			else:
				transaction_form = TransactionForm()


		else:
			"""
				Creating Saving Account
			"""

			account_form = SavingAccountForm(request.POST)

			if account_form.is_valid():

				amount = request.POST['balance']
				user = request.user

				account_form = account_form.save(commit=False)
				account_form.description = 'Opening Balance'
				account_form.business = business
				account_form.employee = user
				account_form.credit = amount
				account_form.debit = 0.00
				account_form.balance = amount
				account_form.save()
				return redirect('business:saving-account', id=business.id, trans=False)

	else:
		transaction_form = TransactionForm()
		account_form = SavingAccountForm()

	context = {
		'business': business,
		'account_form': account_form,
		'saving_account': saving_account,
		'transaction_form': transaction_form,
		'opening_balance': opening_balance,
	}

	template_name = 'saving-account.html'
	return render(request, template_name, context)	

@accountant_required
@login_required
def purchase_order_check_approve(request, *args, **kwargs):
	id = kwargs.get('id')
	purchase_order = PurchaseOrder.objects.filter(id=id).first()
	PurchaseOrderCheck.objects.create(purchase_order=purchase_order, supervisor=request.user, checked=True)
	if purchase_order.published:
		users = User.objects.filter(Q(user_employee__position='Financial Manager'))
		try:
			notify.send(sender=request.user, recipient=users, action_object=purchase_order, level="info", verb="Purchase Order No. {1} checked by {0}".format(request.user.user_employee.full_name, purchase_order.po_no))		
		except:
			pass
		return redirect('business:purchase_order', id=purchase_order.business.id)
	

@accountant_required
@login_required
def purchase_order_check_decline(request, *args, **kwargs):
	id = kwargs.get('id')
	purchase_order = PurchaseOrder.objects.filter(id=id).first()
	if purchase_order.published:
		try:
			notify.send(sender=request.user, recipient=purchase_order.employee, action_object=purchase_order, level="warning", verb="Purchase Order No. {1} declined by {0}".format(request.user.user_employee.full_name, purchase_order.po_no))		
		except:
			pass
		PurchaseOrder.objects.filter(id=id).update(published=False)
		return redirect('business:purchase_order', id=purchase_order.business.id)


@fm_required
@login_required
def purchase_order_approve(request, *args, **kwargs):
	id = kwargs.get('id')
	purchase_order = PurchaseOrder.objects.filter(id=id).first()
	PurchaseOrderApprove.objects.create(purchase_order=purchase_order, supervisor=request.user, approved=True)
	if purchase_order.published:
		users = User.objects.filter(Q(user_employee__position='CEO'))
		try:
			notify.send(sender=request.user, recipient=users, action_object=purchase_order, level="info", verb="Purchase Order No. {1} approved by {0}".format(request.user.user_employee.full_name, purchase_order.po_no))	
		except:
			pass
		return redirect('business:purchase_order', id=purchase_order.business.id)
	

@fm_required
@login_required
def purchase_order_decline(request, *args, **kwargs):
	id = kwargs.get('id')
	purchase_order = PurchaseOrder.objects.filter(id=id).first()
	if purchase_order.published:
		try:
			notify.send(sender=request.user, recipient=purchase_order.employee, action_object=purchase_order, level="warning", verb="Purchase Order No. {1} declined by {0}".format(request.user.user_employee.full_name, purchase_order.po_no))
		except:
			pass
		PurchaseOrder.objects.filter(id=id).update(published=False)
		for check in purchase_order.positive_check_list.all():
			check.checked = False
			check.save()
			try:
				notify.send(sender=request.user, recipient=check.supervisor, action_object=purchase_order, level="warning", verb="Purchase Order No. {1} declined by {0}".format(request.user.user_employee.full_name, purchase_order.po_no))
			except:
				pass
		return redirect('business:purchase_order', id=purchase_order.business.id)


@ceo_required
@login_required
def purchase_order_authorize_approve(request, *args, **kwargs):
	id = kwargs.get('id')
	purchase_order = PurchaseOrder.objects.filter(id=id).first()	
	if purchase_order.published:
		PurchaseOrderAuthorize.objects.create(purchase_order=purchase_order, supervisor=request.user, authorized=True)
		PurchaseOrder.objects.filter(id=id).update(authorized=True)
		# Adding Transaction in Saving Account
		acc = CheckAccount.objects.filter(business=purchase_order.business).last()
		try:
			balance = acc.balance - Decimal(purchase_order.total)
			CheckAccount.objects.create(business=purchase_order.business, employee=request.user, description="Purchase Order", debit=purchase_order.total, credit=0, balance=balance)
		except:
			balance = Decimal(purchase_order.total)
			CheckAccount.objects.create(business=purchase_order.business, employee=request.user, description="Purchase Order", debit=purchase_order.tota, credit=0, balance=balance)
		try:
			notify.send(sender=request.user, recipient=purchase_order.employee, action_object=purchase_order, level="info", verb="Purchase Order No. {1} authorized by {0}".format(request.user.user_employee.full_name, purchase_order.po_no))			
		except:
			pass
		return redirect('business:purchase_order', id=purchase_order.business.id)
	

@ceo_required
@login_required
def purchase_order_authorize_decline(request, *args, **kwargs):
	id = kwargs.get('id')
	purchase_order = PurchaseOrder.objects.filter(id=id).first()
	if purchase_order.published:
		try:
			notify.send(sender=request.user, recipient=purchase_order.employee, action_object=purchase_order, level="warning", verb="Purchase Order No. {1} declined by {0}".format(request.user.user_employee.full_name, purchase_order.po_no))
		except:
			pass
		PurchaseOrder.objects.filter(id=id).update(published=False)
		for check in purchase_order.positive_check_list.all():
			check.checked = False
			check.save()
			try:
				notify.send(sender=request.user, recipient=check.supervisor, action_object=purchase_order, level="warning", verb="Purchase Order No. {1} declined by {0}".format(request.user.user_employee.full_name, purchase_order.po_no))
			except:
				pass
		for approve in purchase_order.positive_approve_list.all():
			approve.approved = False
			approve.save()
			try:
				notify.send(sender=request.user, recipient=approve.supervisor, action_object=purchase_order, level="warning", verb="Purchase Order No. {1} declined by {0}".format(request.user.user_employee.full_name, purchase_order.po_no))
			except:
				pass
			
		return redirect('business:purchase_order', id=purchase_order.business.id)


@accountant_required
@login_required
def local_purchase_order_check_approve(request, *args, **kwargs):
	id = kwargs.get('id')
	local_purchase_order = LocalPurchaseOrder.objects.filter(id=id).first()
	LocalPurchaseOrderCheck.objects.create(local_purchase_order=local_purchase_order, supervisor=request.user, checked=True)
	if local_purchase_order.published:
		users = User.objects.filter(Q(user_employee__position='Financial Manager'))
		try:
			notify.send(sender=request.user, recipient=users, action_object=local_purchase_order, level="info", verb="Local Purchase Order No. {1} checked by {0}".format(request.user.user_employee.full_name, local_purchase_order.lpo_no))
		except:
			pass
		return redirect('business:local_purchase_order', id=local_purchase_order.business.id)
	

@accountant_required
@login_required
def local_purchase_order_check_decline(request, *args, **kwargs):
	id = kwargs.get('id')
	local_purchase_order = LocalPurchaseOrder.objects.filter(id=id).first()
	if local_purchase_order.published:
		try:
			notify.send(sender=request.user, recipient=local_purchase_order.employee, action_object=local_purchase_order, level="warning", verb="Local Purchase Order No. {1} declined by {0}".format(request.user.user_employee.full_name, local_purchase_order.lpo_no))
		except:
			pass
		LocalPurchaseOrder.objects.filter(id=id).update(published=False)
		return redirect('business:local_purchase_order', id=local_purchase_order.business.id)


@fm_required
@login_required
def local_purchase_order_approve(request, *args, **kwargs):
	id = kwargs.get('id')
	local_purchase_order = LocalPurchaseOrder.objects.filter(id=id).first()
	LocalPurchaseOrderApprove.objects.create(local_purchase_order=local_purchase_order, supervisor=request.user, approved=True)
	if local_purchase_order.published:
		users = User.objects.filter(Q(user_employee__position='CEO'))
		try:
			notify.send(sender=request.user, recipient=users, action_object=local_purchase_order, level="info", verb="Local Purchase Order No. {1} approved by {0}".format(request.user.user_employee.full_name, local_purchase_order.lpo_no))
		except:
			pass
		return redirect('business:local_purchase_order', id=local_purchase_order.business.id)
	

@fm_required
@login_required
def local_purchase_order_decline(request, *args, **kwargs):
	id = kwargs.get('id')
	local_purchase_order = LocalPurchaseOrder.objects.filter(id=id).first()
	if local_purchase_order.published:
		try:
			notify.send(sender=request.user, recipient=local_purchase_order.employee, action_object=local_purchase_order, level="warning", verb="Local Purchase Order No. {1} declined by {0}".format(request.user.user_employee.full_name, local_purchase_order.lpo_no))
		except:
			pass
		LocalPurchaseOrder.objects.filter(id=id).update(published=False)
		for check in local_purchase_order.positive_check_list.all():
			check.checked = False
			check.save()
			try:
				notify.send(sender=request.user, recipient=check.supervisor, action_object=local_purchase_order, level="warning", verb="Local Purchase Order No. {1} declined by {0}".format(request.user.user_employee.full_name, local_purchase_order.lpo_no))
			except:
				pass
		return redirect('business:local_purchase_order', id=local_purchase_order.business.id)


@ceo_required
@login_required
def local_purchase_order_authorize_approve(request, *args, **kwargs):
	id = kwargs.get('id')
	local_purchase_order = LocalPurchaseOrder.objects.filter(id=id).first()
	if local_purchase_order.published:    	
		LocalPurchaseOrderAuthorize.objects.create(local_purchase_order=local_purchase_order, supervisor=request.user, authorized=True)
		# Adding Transaction in Saving Account
		LocalPurchaseOrder.objects.filter(id=id).update(authorized=True)
		acc = CheckAccount.objects.filter(business=local_purchase_order.business).last()
		try:
			balance = acc.balance - Decimal(local_purchase_order.total)
			CheckAccount.objects.create(business=local_purchase_order.business, employee=request.user, description="Local Purchase Order", debit=local_purchase_order.total, credit=0, balance=balance)
		except:
			balance = Decimal(local_purchase_order.total)
			CheckAccount.objects.create(business=local_purchase_order.business, employee=request.user, description="Local Purchase Order", debit=local_purchase_order.tota, credit=0, balance=balance)
		try:
			notify.send(sender=request.user, recipient=local_purchase_order.employee, action_object=local_purchase_order, level="info", verb="Purchase Order No. {1} authorized by {0}".format(request.user.user_employee.full_name, local_purchase_order.lpo_no))
		except:
			pass
		return redirect('business:local_purchase_order', id=local_purchase_order.business.id)
	

@ceo_required
@login_required
def local_purchase_order_authorize_decline(request, *args, **kwargs):
	id = kwargs.get('id')
	local_purchase_order = LocalPurchaseOrder.objects.filter(id=id).first()
	if local_purchase_order.published:
		try:
			notify.send(sender=request.user, recipient=local_purchase_order.employee, action_object=local_purchase_order, level="warning", verb="Purchase Order No. {1} declined by {0}".format(request.user.user_employee.full_name, local_purchase_order.lpo_no))
		except:
			pass
		LocalPurchaseOrder.objects.filter(id=id).update(published=False)
		for check in local_purchase_order.positive_check_list.all():
			check.checked = False
			check.save()
			try:
				notify.send(sender=request.user, recipient=check.supervisor, action_object=local_purchase_order, level="warning", verb="Purchase Order No. {1} declined by {0}".format(request.user.user_employee.full_name, local_purchase_order.lpo_no))
			except:
				pass
		for approve in local_purchase_order.positive_approve_list.all():
			approve.approved = False
			approve.save()				
			try:
				notify.send(sender=request.user, recipient=approve.supervisor, action_object=local_purchase_order, level="warning", verb="Purchase Order No. {1} declined by {0}".format(request.user.user_employee.full_name, local_purchase_order.lpo_no))
			except:
				pass
		return redirect('business:local_purchase_order', id=local_purchase_order.business.id)


@finance_required
@login_required
def taxes(request, *args, **kwargs):
	id = kwargs.get('id')
	business = Business.objects.filter(id=id).first()
	taxes = Tax.objects.filter(business=business, remain__gt=0).all()

	if request.method == 'POST':
		form = TaxForm(request.POST or None )

		if form.is_valid():			
			tax = form.save(commit=False)
			tax.business = business
			tax. remain = tax.amount
			tax.save()

			return redirect('business:taxes', id=business.id)
	else:
		form = TaxForm()
	
		
	context = {
		'business':business,
		'taxes':taxes,
		'form':form,
	}
	return render(request, 'taxes.html', context)

@finance_required
@login_required
def pay_tax(request, *args, **kwargs):
	id = kwargs.get('id')
	business = Business.objects.filter(id=id).first()
	if request.method == 'POST':
		tax = int(request.POST['tax'])
		amount = request.POST['amount']
		taxes = Tax.objects.filter(id=tax).first()

		remain = taxes.remain - Decimal(amount)
		if remain >= 0:
			Tax.objects.filter(id=taxes.id).update(remain=remain)

			# Adding Transaction in Saving Account
			acc = CheckAccount.objects.filter(business=business).last()
			try:
				balance = acc.balance - Decimal(amount)
				CheckAccount.objects.create(business=business, employee=request.user, description="Tax Payment", debit=amount, credit=0, balance=balance)
			except:
				balance = Decimal(amount)
				CheckAccount.objects.create(business=business, employee=request.user, description="Tax Payment", debit=amount, credit=0, balance=balance)

			return redirect('business:taxes', id=business.id)
		else:
			return redirect('business:taxes', id=business.id)    				
	else:
		return redirect('business:taxes', id=business.id)
	

############# Interest ###############		
@finance_required
@login_required
def interest_list(request, *args, **kwargs):
	id = kwargs.get('id')
	business = Business.objects.filter(id=id).first()
	interests = Interest.objects.filter(business=business, debt=True)

	if request.method == 'POST':

		"""	
			Add interest
		"""		
		form = InterestForm(request.POST)

		if form.is_valid():
			form = form.save(commit=False)
			loan = form.principal
			form.business = business
			form.debt = True
			principal = form.principal
			rate = form.rate
			time = form.time / 12
			top = principal * Decimal(rate) * Decimal(time)
			interest = top / 100
			repayment =  loan + interest
			form.repayment = repayment
			form.remaining = repayment
			form.save()
			return redirect('business:interest-list', id=business.id)


	else:
		form = InterestForm()


	context = {
		'business' : business,
		'interests' : interests,
		'form': form,
	}
	template_name = 'interest.html'
	return render(request, template_name, context)



############# Interest Payment ###############		
@finance_required
@login_required
def interest_payment(request, *args, **kwargs):
	id = kwargs.get('id')
	pk = kwargs.get('pk')
	business = Business.objects.filter(id=id).first()
	interests = Interest.objects.filter(business=business, debt=True)

	if request.method == 'POST':

			
		"""
			Loan Payment
		"""
		pk = kwargs.get('pk')
		payment_form = PaymentForm(request.POST)
		interest = Interest.objects.filter(business=business, id=pk).first()
		loan_amount = interest.remaining

		if payment_form.is_valid():
			payment = request.POST['payment']
			check_account_debit(business=business, amount=payment, user=request.user, description="Interest Payment")
			interest.remaining = loan_amount - Decimal(payment) 
			interest.save()

			if interest.remaining == 0:

				##### Remove from debt list
				interest.debt = False
				interest.save()

				return redirect('business:interest-list', id=business.id)

			else:
				return redirect('business:interest-list', id=business.id)

	else:
		payment_form = PaymentForm()

	context = {
		'business' : business,
		'interests' : interests,
		'payment_form': payment_form,
	}
	template_name = 'payment.html'
	return render(request, template_name, context)	


############## Employee Loan #################
@finance_required
@login_required
def loan_list(request, *args, **kwargs):
	id = kwargs.get('id')
	business = Business.objects.filter(id=id).first()
	loans = Loan.objects.filter(business=business, debt=True)

	if loans:
		for loan in loans:
			if loan.remaining_debt == 0:
				loan.debt = False
				loan.save()

	if request.method == 'POST':
		loan_form = LoanForm(request.POST)
		
		if loan_form.is_valid():

			loan_form = loan_form.save(commit=False)
			employee = loan_form.employee
			employee = Loan.objects.filter(business=business, debt=True, employee=employee).first()

			if employee:
				messages.info(request, f"{employee} still has a debt")
				return redirect('business:loan-list', id=id)
			else:
				loan_form.business = business
				loan = loan_form.loan_amount
				loan_form.remaining_debt = loan
				loan_form.debt = True
				loan_form.save()
				check_account_debit(business=business, amount=loan, user=request.user, description="Employee Loan")			
				return redirect('business:loan-list', id=id)

		else:
			print(loan_form.errors)
	else:
		loan_form = LoanForm()		

	context = {
		'business': business,
		'loan_form': loan_form,
		'loans': loans,
	}
	template_name = 'loan-list.html'
	return render(request, template_name, context)


################ Trial Balance #####################
@finance_report_required
@finance_required
def trial_balance(request, *args, **kwargs):
	id = kwargs.get('id')
	fr = request.GET.get('fr')
	to = request.GET.get('to')	
	business = Business.objects.filter(id=id).first()
	nssf = Payroll.objects.filter(tax_rate__icontains='nssf', business=business, created_at__date__gte=fr, created_at__date__lte=to)
	wcf = Payroll.objects.filter(tax_rate__icontains='wcf', business=business, created_at__date__gte=fr, created_at__date__lte=to)
	loan_board = Payroll.objects.filter(tax_rate__icontains='loan board', business=business, created_at__date__gte=fr, created_at__date__lte=to)
	paye_objs = Payroll.objects.filter(paye=True, business=business, created_at__date__gte=fr, created_at__date__lte=to)
	takehome_total = Takehome.objects.filter(business=business).aggregate(Sum('salary'))['salary__sum']
	sdl = Payroll.objects.filter(business=business, created_at__date__gte=fr, created_at__date__lte=to).aggregate(Sum('sdl_amount'))['sdl_amount__sum']   		
	taxes = Tax.objects.filter(business=business, created_at__date__gte=fr, created_at__date__lte=to).aggregate(Sum('remain'))['remain__sum']
	interest_remaining = Interest.objects.filter(business=business, created_at__date__gte=fr, created_at__date__lte=to).aggregate(Sum('remaining'))['remaining__sum']
	interest_repayment = Interest.objects.filter(business=business, created_at__date__gte=fr, created_at__date__lte=to).aggregate(Sum('repayment'))['repayment__sum']
	sales = Sale.objects.filter(branch__business=business, status='Completed', created_at__date__gte=fr, created_at__date__lte=to).all().aggregate(total_paid=Sum('amount_paid'))
	inventory_qs = Inventory.objects.filter(business=business, created_at__date__gte=fr, created_at__date__lte=to).annotate(available=F('remain')-F('damage'))			
	inventories = inventory_qs.filter(available__gt=0, ).order_by('-pk')
	expenses = Expense.objects.filter(business=business, created_at__date__gte=fr, created_at__date__lte=to).aggregate(Sum('cost'))['cost__sum']
	liabilities = Liability.objects.filter(business=business, created_at__date__gte=fr, created_at__date__lte=to).aggregate(Sum('cost'))['cost__sum']
	fixed_assets = AccountsFixedAsset.objects.filter(business=business, created_at__date__gte=fr, created_at__date__lte=to).aggregate(Sum('value'))['value__sum']
	current_assets = AccountsCurrentAsset.objects.filter(business=business, created_at__date__gte=fr, created_at__date__lte=to).aggregate(Sum('cost'))['cost__sum']

	sales = sales['total_paid']



	cogs = 0
	for i in inventories:
		cogs = cogs + i.cogs

	if fixed_assets is None:
		fixed_assets = 0
	if current_assets is None:
		current_assets = 0
	if interest_remaining is None:
		interest_remaining = 0	
	if interest_repayment is None:
		interest_repayment = 0		
	
	interests = interest_repayment - interest_remaining		

	assets = fixed_assets + current_assets		


	paye_total = 0

	if paye_objs:     	

		for worker in paye_objs:

			salary = worker.employee.salary

			if salary <= 270000:

				paye_total += 0

			elif 270000 < salary <= 520000:

				tax_payment = (salary - 270000) * 0.09 
				paye_total += tax_payment


			elif 520000 < salary <= 760000:

				tax_payment = (salary - 520000) * 0.2 + 22500 
				paye_total += tax_payment

			elif 760000 < salary <= 1000000:

				tax_payment = (salary - 760000) * 0.25 + 70500 
				paye_total += tax_payment


			elif 1000000 < salary:

				tax_payment = (salary - 1000000) * 0.3 + 130500 
				paye_total += tax_payment          


	nssf_funds = 0
	wcf_funds = 0
	loan_board_funds = 0				

	total_funds = 0
	if nssf:
		# print(nssf)
		for worker in nssf:
			total_funds += worker.employee.salary
		nssf_funds = total_funds * 0.1 
		# print(f"NSSF : {int(nssf_funds)}")
		total_funds = 0

	if wcf:
		# print(wcf)
		for worker in wcf:
			total_funds += worker.employee.salary            	
		wcf_funds = total_funds * 0.01 
		# print(f"WCF : {int(wcf_funds)}")
		total_funds = 0

	if loan_board:
		# print(loan_board)
		for worker in loan_board:
			total_funds += worker.employee.salary
		loan_board_funds = total_funds * 0.15 
		# print(f"LOAN BOARD : {int(loan_board_funds)}")


	if takehome_total is None:
		takehome_total = 0
	if sdl is None:
		sdl = 0	
	if taxes is None:
		taxes = 0
	if interests is None:
		interests = 0					
	if liabilities is None:
		liabilities = 0
	if assets is None:
		assets = 0
	if cogs is None:
		cogs = 0
	if paye_total is None:
		paye_total = 0	
	if expenses is None:
		expenses = 0
	if sales is None:
		sales = 0



	total_debit = int(nssf_funds) + int(paye_total) + int(loan_board_funds) + int(wcf_funds) + int(takehome_total) + int(sdl) + int(interests) + int(taxes) + int(expenses) + int(cogs) 
	total_credit = int(sales) + int(assets) + int(liabilities)


	context = {
		'business' : business,
		'wcf': int(wcf_funds),
		'nssf': int(nssf_funds),
		'heslb': int(loan_board_funds),
		'sdl': int(sdl),
		'salaries': int(takehome_total),
		'paye': int(paye_total),
		'sales': sales,
		'taxes': taxes,
		'interests': interests,
		'expenses': expenses,
		'cogs': int(cogs),
		'liabilities': liabilities,
		'assets': assets,
		'credit': total_credit,
		'debit': total_debit,
		'fr': fr,
		'to': to,

	}
	template_name = 'trial-balance.html'
	return render(request, template_name, context)	