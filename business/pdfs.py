from weasyprint import HTML
from django.template.loader import render_to_string
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse, JsonResponse
from administration.models import *
from .models import *
from django.contrib.auth.decorators import login_required


@login_required
def purchase_order_export_pdf(request, **kwargs):
	id = kwargs.get('id')
	purchase_order = PurchaseOrder.objects.filter(id=id).first() 
	html_string = render_to_string('purchase_order_pdf.html', {'purchase_order':purchase_order,})
	html = HTML(string=html_string, base_url=request.build_absolute_uri())
	html.write_pdf(target='/tmp/purchase_order.pdf');

	fs = FileSystemStorage('/tmp')
	with fs.open('purchase_order.pdf') as pdf:
		response = HttpResponse(pdf, content_type='application/pdf')
		return response


@login_required
def local_purchase_order_export_pdf(request, **kwargs):
	id = kwargs.get('id')
	local_purchase_order = LocalPurchaseOrder.objects.filter(id=id).first()
	html_string = render_to_string('local_purchase_order_pdf.html', {'purchase_order':local_purchase_order,})
	html = HTML(string=html_string, base_url=request.build_absolute_uri())
	html.write_pdf(target='/tmp/local_purchase_order.pdf');

	fs = FileSystemStorage('/tmp')
	with fs.open('local_purchase_order.pdf') as pdf:
		response = HttpResponse(pdf, content_type='application/pdf')
		return response


@login_required
def sales_report_export_pdf(request, **kwargs):
	context = {
		'business':kwargs.get('business'),
		'sales':kwargs.get('sales'),
		'summary':kwargs.get('summary'),
		'products':kwargs.get('products'),
	}
	html_string = render_to_string('sales_report_pdf.html', context)
	html = HTML(string=html_string, base_url=request.build_absolute_uri())
	html.write_pdf(target='/tmp/sales_report.pdf');

	fs = FileSystemStorage('/tmp')
	with fs.open('sales_report.pdf') as pdf:
		response = HttpResponse(pdf, content_type='application/pdf')
		return response


@login_required
def inventory_report_export_pdf(request, **kwargs):
	context = {
		'business':kwargs.get('business'),
		'inventories':kwargs.get('inventories'),
		'summary':kwargs.get('summary'),
		'products':kwargs.get('products'),
	}
	html_string = render_to_string('inventory_report_pdf.html', context)
	html = HTML(string=html_string, base_url=request.build_absolute_uri())
	html.write_pdf(target='/tmp/inventory_report.pdf');

	fs = FileSystemStorage('/tmp')
	with fs.open('inventory_report.pdf') as pdf:
		response = HttpResponse(pdf, content_type='application/pdf')
		return response


@login_required
def procurement_report_export_pdf(request, **kwargs):
	context = {
		'business':kwargs.get('business'),
		'local_purchases':kwargs.get('local_purchases'),
		'purchases':kwargs.get('purchases'),
		'summary':kwargs.get('summary'),
	}
	html_string = render_to_string('procurement_report_pdf.html', context)
	html = HTML(string=html_string, base_url=request.build_absolute_uri())
	html.write_pdf(target='/tmp/procurement_report.pdf');

	fs = FileSystemStorage('/tmp')
	with fs.open('procurement_report.pdf') as pdf:
		response = HttpResponse(pdf, content_type='application/pdf')
		return response


@login_required
def opex_report_export_pdf(request, **kwargs):
	context = {
		'business':kwargs.get('business'),
		'expenses':kwargs.get('expense_objects'),
		'cost':kwargs.get('total_cost'),
		'expenses_total':kwargs.get('expenses_total'),
		'exps':kwargs.get('exps'),
	}
	html_string = render_to_string('opex-report-pdf.html', context)
	html = HTML(string=html_string, base_url=request.build_absolute_uri())
	html.write_pdf(target='/tmp/opex_report.pdf');

	fs = FileSystemStorage('/tmp')
	with fs.open('opex_report.pdf') as pdf:
		response = HttpResponse(pdf, content_type='application/pdf')
		return response


@login_required
def customer_report_export_pdf(request, **kwargs):
	context = {
		'business':kwargs.get('business'),
		'customers':kwargs.get('customers'),
		'normal':kwargs.get('normal'),
		'loyal':kwargs.get('loyal'),
		'other':kwargs.get('other'),
	}
	html_string = render_to_string('customer-report-pdf.html', context)
	html = HTML(string=html_string, base_url=request.build_absolute_uri())
	html.write_pdf(target='/tmp/customer_report.pdf');

	fs = FileSystemStorage('/tmp')
	with fs.open('customer_report.pdf') as pdf:
		response = HttpResponse(pdf, content_type='application/pdf')
		return response	


@login_required
def payroll_report_export_pdf(request, **kwargs):
	context = {
		'business':kwargs.get('business'),
		'takehome_total':kwargs.get('takehome_total'),
		'takehome':kwargs.get('takehome'),
		'wcf':kwargs.get('wcf'),
		'nssf':kwargs.get('nssf'),
		'loan_board':kwargs.get('loan_board'),
		'paye':kwargs.get('paye'),
		'bonus':kwargs.get('bonus'),
		'overtime':kwargs.get('overtime'),
		'salaries_total':kwargs.get('salaries_total'),
		'total_expenses':kwargs.get('total_expenses'),
		'employees':kwargs.get('employees'),
		'deduction':kwargs.get('deduction'),
		'sdl': kwargs.get('sdl')
	}
	html_string = render_to_string('payroll-report-pdf.html', context)
	html = HTML(string=html_string, base_url=request.build_absolute_uri())
	html.write_pdf(target='/tmp/payroll_report.pdf');

	fs = FileSystemStorage('/tmp')
	with fs.open('payroll_report.pdf') as pdf:
		response = HttpResponse(pdf, content_type='application/pdf')
		return response				



def trial_balance_export_pdf(request, *args, **kwargs):
	id = kwargs.get('id')
	business = Business.objects.filter(id=id).first()
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



	total_debit = int(nssf_funds) + int(paye_total) + int(loan_board_funds) + int(wcf_funds) + int(takehome_total) + int(sdl) + int(interests) + int(taxes) + int(expenses) + int(cogs) + int(liabilities)
	total_credit = int(sales) + int(assets) 


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

	}
	html_string = render_to_string('trial-balance-pdf.html', context)
	html = HTML(string=html_string, base_url=request.build_absolute_uri())
	html.write_pdf(target='/tmp/trial_balance_report.pdf');

	fs = FileSystemStorage('/tmp')
	with fs.open('trial_balance_report.pdf') as pdf:
		response = HttpResponse(pdf, content_type='application/pdf')
		return response	


def balance_sheet_export_pdf(request, *args, **kwargs):
	context = {
		'business':kwargs.get('business'),
		'assets': kwargs.get('assets'),
		'liabilities': kwargs.get('liabilities'),
		'equity': kwargs.get('equity'),
	}
	html_string = render_to_string('balance_sheet_pdf.html', context)
	html = HTML(string=html_string, base_url=request.build_absolute_uri())
	html.write_pdf(target='/tmp/balance_sheet_report.pdf');

	fs = FileSystemStorage('/tmp')
	with fs.open('balance_sheet_report.pdf') as pdf:
		response = HttpResponse(pdf, content_type='application/pdf')
		return response    	



def income_statement_export_pdf(request, *args, **kwargs):
	context = {
		'business': kwargs.get('business'),
		'summary': kwargs.get('summary'),
	}
	html_string = render_to_string('income-statement-pdf.html', context)
	html = HTML(string=html_string, base_url=request.build_absolute_uri())
	html.write_pdf(target='/tmp/income_statement_report.pdf');

	fs = FileSystemStorage('/tmp')
	with fs.open('income_statement_report.pdf') as pdf:
		response = HttpResponse(pdf, content_type='application/pdf')
		return response  


def cashbook_export_pdf(request, *args, **kwargs):
	context = {
		'business':kwargs.get('business'),
		'cashflow': kwargs.get('cashflow')
	}
	html_string = render_to_string('cashbook-pdf.html', context)
	html = HTML(string=html_string, base_url=request.build_absolute_uri())
	html.write_pdf(target='/tmp/cashbook_report.pdf');

	fs = FileSystemStorage('/tmp')
	with fs.open('cashbook_report.pdf') as pdf:
		response = HttpResponse(pdf, content_type='application/pdf')
		return response  
