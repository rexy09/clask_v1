from django.shortcuts import render, redirect
from administration.models import *
from .models import *
from django.db.models import Avg, CharField, F, FloatField, Q, Sum, Value
from datetime import date, timedelta, datetime
from decimal import Decimal
from .pdfs import *
from .excels import *
from django.contrib.auth.decorators import login_required
from human_resource.decorators import *


@login_required
def reports(request, *args, **kwargs):
	id = kwargs.get('id')
	business = Business.objects.filter(id=id).first() 
	context = {
		'business':business,
	}
	return render(request, 'reports.html', context)


# """""""""" PROCUREMENT REPORT """""""""""
@procurement_finance_ceo_required
@login_required
def procurement_time(request, *args, **kwargs):
	id = kwargs.get('id')
	business = Business.objects.filter(id=id).first()
	context = {
		'business':business,
	}
	return render(request, 'procurement_time.html', context)

@procurement_finance_ceo_required
@login_required
def procurement_report(request, *args, **kwargs):
	id = kwargs.get('id')
	d = kwargs.get('d')
	pdf = request.GET.get('pdf')
	xl = request.GET.get('xl')
	fr = request.GET.get('fr')
	to = request.GET.get('to')
	business = Business.objects.filter(id=id).first() 
	if d == 1:
		local_purchases = LocalPurchaseOrder.objects.filter(business=business, created_at__date=date.today(), published=True,local_purchase_order_authorize__authorized=True).all().order_by('-pk')
		purchases = PurchaseOrder.objects.filter(business=business, created_at__date=date.today(), published=True, purchase_order_authorize__authorized=True).all().order_by('-pk')

		summary = LocalPurchaseOrder.objects.filter(business=business, created_at__date=date.today(), published=True, local_purchase_order_authorize__authorized=True).all().aggregate(total_local_purchase=Sum('local_purchase_order_list__total'),)
		summary['total_purchase'] = PurchaseOrder.objects.filter(business=business, created_at__date=date.today(), published=True, purchase_order_authorize__authorized=True).all().aggregate(total_purchase=Sum('purchase_order_list__total'),)['total_purchase']

		if pdf == '1':
			return procurement_report_export_pdf(request,business=business, local_purchases=local_purchases, purchases=purchases, summary=summary,)

		if xl == '2':
			return procurement_report_export_excel(request,business=business, local_purchases=local_purchases, purchases=purchases)	

	elif d == 2:	
		dt = date.today() - timedelta(days=1)

		local_purchases = LocalPurchaseOrder.objects.filter(business=business, created_at__date=dt, published=True,local_purchase_order_authorize__authorized=True).all().order_by('-pk')
		purchases = PurchaseOrder.objects.filter(business=business, created_at__date=dt, published=True, purchase_order_authorize__authorized=True).all().order_by('-pk')
		
		summary = LocalPurchaseOrder.objects.filter(business=business, created_at__date=dt, published=True, local_purchase_order_authorize__authorized=True).all().aggregate(total_local_purchase=Sum('local_purchase_order_list__total'),)
		summary['total_purchase'] = PurchaseOrder.objects.filter(business=business, created_at__date=dt, published=True, purchase_order_authorize__authorized=True).all().aggregate(total_purchase=Sum('purchase_order_list__total'),)['total_purchase']

		if pdf == '1':
			return procurement_report_export_pdf(request,business=business, local_purchases=local_purchases, purchases=purchases, summary=summary,)

		if xl == '2':
			return procurement_report_export_excel(request,business=business, local_purchases=local_purchases, purchases=purchases)	
		
	elif d == 3:	
		dt = date.today() - timedelta(days=7)

		local_purchases = LocalPurchaseOrder.objects.filter(business=business, created_at__date__gte=dt, created_at__date__lte=date.today(), published=True,local_purchase_order_authorize__authorized=True).all().order_by('-pk')
		purchases = PurchaseOrder.objects.filter(business=business, created_at__date__gte=dt, created_at__date__lte=date.today(), published=True, purchase_order_authorize__authorized=True).all().order_by('-pk')
		
		summary = LocalPurchaseOrder.objects.filter(business=business, created_at__date__gte=dt, created_at__date__lte=date.today(), published=True, local_purchase_order_authorize__authorized=True).all().aggregate(total_local_purchase=Sum('local_purchase_order_list__total'),)
		summary['total_purchase'] = PurchaseOrder.objects.filter(business=business, created_at__date__gte=dt, created_at__date__lte=date.today(), published=True, purchase_order_authorize__authorized=True).all().aggregate(total_purchase=Sum('purchase_order_list__total'),)['total_purchase']

		if pdf == '1':
			return procurement_report_export_pdf(request,business=business, local_purchases=local_purchases, purchases=purchases, summary=summary,)

		if xl == '2':
			return procurement_report_export_excel(request,business=business, local_purchases=local_purchases, purchases=purchases)	

	elif d == 4:	
		dt = date.today() - timedelta(days=30)

		local_purchases = LocalPurchaseOrder.objects.filter(business=business, created_at__date__gte=dt, created_at__date__lte=date.today(), published=True,local_purchase_order_authorize__authorized=True).all().order_by('-pk')
		purchases = PurchaseOrder.objects.filter(business=business, created_at__date__gte=dt, created_at__date__lte=date.today(), published=True, purchase_order_authorize__authorized=True).all().order_by('-pk')
		
		summary = LocalPurchaseOrder.objects.filter(business=business, created_at__date__gte=dt, created_at__date__lte=date.today(), published=True, local_purchase_order_authorize__authorized=True).all().aggregate(total_local_purchase=Sum('local_purchase_order_list__total'),)
		summary['total_purchase'] = PurchaseOrder.objects.filter(business=business, created_at__date__gte=dt, created_at__date__lte=date.today(), published=True, purchase_order_authorize__authorized=True).all().aggregate(total_purchase=Sum('purchase_order_list__total'),)['total_purchase']

		if pdf == '1':
			return procurement_report_export_pdf(request,business=business, local_purchases=local_purchases, purchases=purchases, summary=summary,)

		if xl == '2':
			return procurement_report_export_excel(request,business=business, local_purchases=local_purchases, purchases=purchases)		
		
	elif d == 5:	
		dt = date.today()
		local_purchases = LocalPurchaseOrder.objects.filter(business=business, created_at__month=dt.month, created_at__year=dt.year, published=True,local_purchase_order_authorize__authorized=True).all().order_by('-pk')
		purchases = PurchaseOrder.objects.filter(business=business, created_at__month=dt.month, created_at__year=dt.year, published=True, purchase_order_authorize__authorized=True).all().order_by('-pk')
		
		summary = LocalPurchaseOrder.objects.filter(business=business, created_at__month=dt.month, created_at__year=dt.year, published=True, local_purchase_order_authorize__authorized=True).all().aggregate(total_local_purchase=Sum('local_purchase_order_list__total'),)
		summary['total_purchase'] = PurchaseOrder.objects.filter(business=business, created_at__month=dt.month, created_at__year=dt.year, published=True, purchase_order_authorize__authorized=True).all().aggregate(total_purchase=Sum('purchase_order_list__total'),)['total_purchase']

		if pdf == '1':
			return procurement_report_export_pdf(request,business=business, local_purchases=local_purchases, purchases=purchases, summary=summary,)

		if xl == '2':
			return procurement_report_export_excel(request,business=business, local_purchases=local_purchases, purchases=purchases)	
	
	elif d == 6:	
		dt = date.today()
		month = dt.month - 1
		local_purchases = LocalPurchaseOrder.objects.filter(business=business, created_at__month=month, created_at__year=dt.year, published=True,local_purchase_order_authorize__authorized=True).all().order_by('-pk')
		purchases = PurchaseOrder.objects.filter(business=business, created_at__month=month, created_at__year=dt.year, published=True, purchase_order_authorize__authorized=True).all().order_by('-pk')
		
		summary = LocalPurchaseOrder.objects.filter(business=business, created_at__month=month, created_at__year=dt.year, published=True, local_purchase_order_authorize__authorized=True).all().aggregate(total_local_purchase=Sum('local_purchase_order_list__total'),)
		summary['total_purchase'] = PurchaseOrder.objects.filter(business=business, created_at__month=month, created_at__year=dt.year, published=True, purchase_order_authorize__authorized=True).all().aggregate(total_purchase=Sum('purchase_order_list__total'),)['total_purchase']

		if pdf == '1':
			return procurement_report_export_pdf(request,business=business, local_purchases=local_purchases, purchases=purchases, summary=summary,)

		if xl == '2':
			return procurement_report_export_excel(request,business=business, local_purchases=local_purchases, purchases=purchases)	

	elif d == 7:	
		local_purchases = LocalPurchaseOrder.objects.filter(business=business, published=True,local_purchase_order_authorize__authorized=True).all().order_by('-pk')
		purchases = PurchaseOrder.objects.filter(business=business, published=True, purchase_order_authorize__authorized=True).all().order_by('-pk')
		
		summary = LocalPurchaseOrder.objects.filter(business=business, published=True, local_purchase_order_authorize__authorized=True).all().aggregate(total_local_purchase=Sum('local_purchase_order_list__total'),)
		summary['total_purchase'] = PurchaseOrder.objects.filter(business=business, published=True, purchase_order_authorize__authorized=True).all().aggregate(total_purchase=Sum('purchase_order_list__total'),)['total_purchase']

		if pdf == '1':
			return procurement_report_export_pdf(request,business=business, local_purchases=local_purchases, purchases=purchases, summary=summary,)

		if xl == '2':
			return procurement_report_export_excel(request,business=business, local_purchases=local_purchases, purchases=purchases)	
	
	elif d == 8:
		if request.method == 'GET':	
			local_purchases = LocalPurchaseOrder.objects.filter(business=business, created_at__date__gte=fr, created_at__date__lte=to, published=True,local_purchase_order_authorize__authorized=True).all().order_by('-pk')
			purchases = PurchaseOrder.objects.filter(business=business, created_at__date__gte=fr, created_at__date__lte=to, published=True, purchase_order_authorize__authorized=True).all().order_by('-pk')
			
			summary = LocalPurchaseOrder.objects.filter(business=business, created_at__date__gte=fr, created_at__date__lte=to, published=True, local_purchase_order_authorize__authorized=True).all().aggregate(total_local_purchase=Sum('local_purchase_order_list__total'),)
			summary['total_purchase'] = PurchaseOrder.objects.filter(business=business, created_at__date__gte=fr, created_at__date__lte=to, published=True, purchase_order_authorize__authorized=True).all().aggregate(total_purchase=Sum('purchase_order_list__total'),)['total_purchase']

			if pdf == '1':
				return procurement_report_export_pdf(request,business=business, local_purchases=local_purchases, purchases=purchases, summary=summary,)

			if xl == '2':
				return procurement_report_export_excel(request,business=business, local_purchases=local_purchases, purchases=purchases)		

	context = {
		'business':business,
		'local_purchases':local_purchases,
		'purchases':purchases,
		'summary':summary,
		'd':d,
		'fr':fr,
		'to':to,
	}
	return render(request, 'procurement_report.html', context)


# """""""""" SALES REPORT """""""""""
@finance_report_required
@login_required
def sales_time(request, *args, **kwargs):
	id = kwargs.get('id')
	business = Business.objects.filter(id=id).first()
	context = {
		'business':business,
	}
	return render(request, 'sale_time.html', context)

@finance_report_required
@login_required
def sales_report(request, *args, **kwargs):
	id = kwargs.get('id')
	day = kwargs.get('d')
	pdf = request.GET.get('pdf')
	xl = request.GET.get('xl')
	fr = request.GET.get('fr')
	to = request.GET.get('to')
	business = Business.objects.filter(id=id).first() 
	if day == 1:
		sales = Sale.objects.filter(branch__business=business, created_at__date=date.today(), status='Completed').all().order_by('-pk')
		summary = Sale.objects.filter(branch__business=business, created_at__date=date.today(), status='Completed').all().aggregate(total_paid=Sum('amount_paid'), total_quantity=Sum('quantity'), total_profit=Sum('profit'))

		discount = 0
		tax = 0
		for sale in sales:
			if sale.discount_unit == 'flat':
				discount = discount + sale.discount
			elif sale.discount_unit == '%':
				disc = (Decimal(sale.discount)/100) * Decimal(sale.total)
				discount = discount + disc

			if sale.tax_unit == '%':
				t = ( Decimal(sale.tax)/100) * Decimal(sale.total)
				tax = tax + t
						
		summary['total_discount'] = discount
		summary['total_tax'] = tax

		data = Product.objects.filter(business=business, inventory_product__sale_inventory__status='Completed', inventory_product__sale_inventory__created_at__date=date.today()).all().annotate(quantity_sold=Sum('inventory_product__sale_inventory__quantity'),profit_sold=Sum('inventory_product__sale_inventory__profit'),revenue_sold=Sum('inventory_product__sale_inventory__amount_paid'))
		products = []
		for d in data:
			dic = {'name': d.name, 'quantity_sold': d.quantity_sold, 'profit_sold': d.profit_sold, 'revenue_sold': d.revenue_sold}
			products.append(dic)

		if pdf == '1':
			return sales_report_export_pdf(request,business=business, products=products, summary=summary,sales=sales)

		if xl == '2':
			return sales_report_export_excel(request,business=business,sales=sales)	

	elif day == 2:	
		dt = date.today() - timedelta(days=1)
		sales = Sale.objects.filter(branch__business=business, created_at__date=dt, status='Completed').all().order_by('-pk')	
		summary = Sale.objects.filter(branch__business=business, created_at__date=dt, status='Completed').all().aggregate(total_paid=Sum('amount_paid'), total_quantity=Sum('quantity'), total_profit=Sum('profit'))

		discount = 0
		tax = 0
		for sale in sales:
			if sale.discount_unit == 'flat':
				discount = discount + sale.discount
			elif sale.discount_unit == '%':
				disc = (Decimal(sale.discount)/100) * Decimal(sale.total)
				discount = discount + disc

			if sale.tax_unit == '%':
				t = ( Decimal(sale.tax)/100) * Decimal(sale.total)
				tax = tax + t				

		summary['total_discount'] = discount
		summary['total_tax'] = tax

		data = Product.objects.filter(business=business, inventory_product__sale_inventory__status='Completed', inventory_product__sale_inventory__created_at__date=dt).all().annotate(quantity_sold=Sum('inventory_product__sale_inventory__quantity'),profit_sold=Sum('inventory_product__sale_inventory__profit'),revenue_sold=Sum('inventory_product__sale_inventory__amount_paid'))
		products = []
		for d in data:
			dic = {'name': d.name, 'quantity_sold': d.quantity_sold, 'profit_sold': d.profit_sold, 'revenue_sold': d.revenue_sold}
			products.append(dic)

		if pdf == '1':
			return sales_report_export_pdf(request,business=business, products=products, summary=summary,sales=sales)

		if xl == '2':
			return sales_report_export_excel(request,business=business,sales=sales)	

	elif day == 3:	
		dt = date.today() - timedelta(days=7)
		sales = Sale.objects.filter(branch__business=business, created_at__date__gte=dt, created_at__date__lte=date.today(), status='Completed').all().order_by('-pk')
		summary = Sale.objects.filter(branch__business=business, created_at__date__gte=dt, created_at__date__lte=date.today(), status='Completed').all().aggregate(total_paid=Sum('amount_paid'), total_quantity=Sum('quantity'), total_profit=Sum('profit'))

		discount = 0
		tax = 0
		for sale in sales:
			if sale.discount_unit == 'flat':
				discount = discount + sale.discount
			elif sale.discount_unit == '%':
				disc = (Decimal(sale.discount)/100) * Decimal(sale.total)
				discount = discount + disc

			if sale.tax_unit == '%':
				t = ( Decimal(sale.tax)/100) * Decimal(sale.total)
				tax = tax + t				

		summary['total_discount'] = discount
		summary['total_tax'] = tax

		data = Product.objects.filter(business=business, inventory_product__sale_inventory__status='Completed', inventory_product__sale_inventory__created_at__date__gte=dt, inventory_product__sale_inventory__created_at__date__lte=date.today()).all().annotate(quantity_sold=Sum('inventory_product__sale_inventory__quantity'),profit_sold=Sum('inventory_product__sale_inventory__profit'),revenue_sold=Sum('inventory_product__sale_inventory__amount_paid'))
		products = []
		for d in data:
			dic = {'name': d.name, 'quantity_sold': d.quantity_sold, 'profit_sold': d.profit_sold, 'revenue_sold': d.revenue_sold}
			products.append(dic)

		if pdf == '1':
			return sales_report_export_pdf(request,business=business, products=products, summary=summary,sales=sales)

		if xl == '2':
			return sales_report_export_excel(request,business=business,sales=sales)

	elif day == 4:	
		dt = date.today() - timedelta(days=30)
		sales = Sale.objects.filter(branch__business=business, created_at__date__gte=dt, created_at__date__lte=date.today(), status='Completed').all().order_by('-pk')	
		summary = Sale.objects.filter(branch__business=business, created_at__date__gte=dt, created_at__date__lte=date.today(), status='Completed').all().aggregate(total_paid=Sum('amount_paid'), total_quantity=Sum('quantity'), total_profit=Sum('profit'))

		discount = 0
		tax = 0
		for sale in sales:
			if sale.discount_unit == 'flat':
				discount = discount + sale.discount
			elif sale.discount_unit == '%':
				disc = (Decimal(sale.discount)/100) * Decimal(sale.total)
				discount = discount + disc

			if sale.tax_unit == '%':
				t = ( Decimal(sale.tax)/100) * Decimal(sale.total)
				tax = tax + t				

		summary['total_discount'] = discount
		summary['total_tax'] = tax	

		data = Product.objects.filter(business=business, inventory_product__sale_inventory__status='Completed', inventory_product__sale_inventory__created_at__date__gte=dt, inventory_product__sale_inventory__created_at__date__lte=date.today()).all().annotate(quantity_sold=Sum('inventory_product__sale_inventory__quantity'),profit_sold=Sum('inventory_product__sale_inventory__profit'),revenue_sold=Sum('inventory_product__sale_inventory__amount_paid'))
		products = []
		for d in data:
			dic = {'name': d.name, 'quantity_sold': d.quantity_sold, 'profit_sold': d.profit_sold, 'revenue_sold': d.revenue_sold}
			products.append(dic)

		if pdf == '1':
			return sales_report_export_pdf(request,business=business, products=products, summary=summary,sales=sales)	

		if xl == '2':
			return sales_report_export_excel(request,business=business,sales=sales)	

	elif day == 5:	
		dt = date.today()
		sales = Sale.objects.filter(branch__business=business, created_at__month=dt.month, created_at__year=dt.year, status='Completed').all().order_by('-pk')
		summary = Sale.objects.filter(branch__business=business, created_at__month=dt.month, created_at__year=dt.year, status='Completed').all().aggregate(total_paid=Sum('amount_paid'), total_quantity=Sum('quantity'), total_profit=Sum('profit'))

		discount = 0
		tax = 0
		for sale in sales:
			if sale.discount_unit == 'flat':
				discount = discount + sale.discount
			elif sale.discount_unit == '%':
				disc = (Decimal(sale.discount)/100) * Decimal(sale.total)
				discount = discount + disc

			if sale.tax_unit == '%':
				t = ( Decimal(sale.tax)/100) * Decimal(sale.total)
				tax = tax + t				

		summary['total_discount'] = discount
		summary['total_tax'] = tax	

		data = Product.objects.filter(business=business, inventory_product__sale_inventory__status='Completed', inventory_product__sale_inventory__created_at__month=dt.month, inventory_product__sale_inventory__created_at__year=dt.year).all().annotate(quantity_sold=Sum('inventory_product__sale_inventory__quantity'),profit_sold=Sum('inventory_product__sale_inventory__profit'),revenue_sold=Sum('inventory_product__sale_inventory__amount_paid'))
		products = []
		for d in data:
			dic = {'name': d.name, 'quantity_sold': d.quantity_sold, 'profit_sold': d.profit_sold, 'revenue_sold': d.revenue_sold}
			products.append(dic)

		if pdf == '1':
			return sales_report_export_pdf(request,business=business, products=products, summary=summary,sales=sales)

		if xl == '2':
			return sales_report_export_excel(request,business=business,sales=sales)
				
	elif day == 6:	
		dt = date.today()
		month = dt.month - 1
		sales = Sale.objects.filter(branch__business=business, created_at__month=month, created_at__year=dt.year, status='Completed').all().order_by('-pk')	
		summary = Sale.objects.filter(branch__business=business, created_at__month=month, created_at__year=dt.year, status='Completed').all().aggregate(total_paid=Sum('amount_paid'), total_quantity=Sum('quantity'), total_profit=Sum('profit'))

		discount = 0
		tax = 0
		for sale in sales:
			if sale.discount_unit == 'flat':
				discount = discount + sale.discount
			elif sale.discount_unit == '%':
				disc = (Decimal(sale.discount)/100) * Decimal(sale.total)
				discount = discount + disc

			if sale.tax_unit == '%':
				t = ( Decimal(sale.tax)/100) * Decimal(sale.total)
				tax = tax + t				

		summary['total_discount'] = discount
		summary['total_tax'] = tax	

		data = Product.objects.filter(business=business, inventory_product__sale_inventory__status='Completed', inventory_product__sale_inventory__created_at__month=month, inventory_product__sale_inventory__created_at__year=dt.year).all().annotate(quantity_sold=Sum('inventory_product__sale_inventory__quantity'),profit_sold=Sum('inventory_product__sale_inventory__profit'),revenue_sold=Sum('inventory_product__sale_inventory__amount_paid'))
		products = []
		for d in data:
			dic = {'name': d.name, 'quantity_sold': d.quantity_sold, 'profit_sold': d.profit_sold, 'revenue_sold': d.revenue_sold}
			products.append(dic)

		if pdf == '1':
			return sales_report_export_pdf(request,business=business, products=products, summary=summary,sales=sales)
		
		if xl == '2':
			return sales_report_export_excel(request,business=business,sales=sales)

	elif day == 7:	
		sales = Sale.objects.filter(branch__business=business, status='Completed').all().order_by('-pk')	
		summary = Sale.objects.filter(branch__business=business, status='Completed').all().aggregate(total_paid=Sum('amount_paid'), total_quantity=Sum('quantity'), total_profit=Sum('profit'))

		discount = 0
		tax = 0
		for sale in sales:
			if sale.discount_unit == 'flat':
				discount = discount + sale.discount
			elif sale.discount_unit == '%':
				disc = (Decimal(sale.discount)/100) * Decimal(sale.total)
				discount = discount + disc

			if sale.tax_unit == '%':
				t = ( Decimal(sale.tax)/100) * Decimal(sale.total)
				tax = tax + t				

		summary['total_discount'] = discount
		summary['total_tax'] = tax	

		data = Product.objects.filter(business=business, inventory_product__sale_inventory__status='Completed').all().annotate(quantity_sold=Sum('inventory_product__sale_inventory__quantity'),profit_sold=Sum('inventory_product__sale_inventory__profit'),revenue_sold=Sum('inventory_product__sale_inventory__amount_paid'))
		products = []
		for d in data:
			dic = {'name': d.name, 'quantity_sold': d.quantity_sold, 'profit_sold': d.profit_sold, 'revenue_sold': d.revenue_sold}
			products.append(dic)	

		if pdf == '1':
			return sales_report_export_pdf(request,business=business, products=products, summary=summary,sales=sales)

		if xl == '2':
			return sales_report_export_excel(request,business=business,sales=sales)

	elif day == 8:
		if request.method == 'GET':	
			sales = Sale.objects.filter(branch__business=business, created_at__date__gte=fr, created_at__date__lte=to, status='Completed').all().order_by('-pk')	
			summary = Sale.objects.filter(branch__business=business, created_at__date__gte=fr, created_at__date__lte=to, status='Completed').all().aggregate(total_paid=Sum('amount_paid'), total_quantity=Sum('quantity'), total_profit=Sum('profit'))

			discount = 0
			tax = 0
			for sale in sales:
				if sale.discount_unit == 'flat':
					discount = discount + sale.discount
				elif sale.discount_unit == '%':
					disc = (Decimal(sale.discount)/100) * Decimal(sale.total)
					discount = discount + disc

				if sale.tax_unit == '%':
					t = ( Decimal(sale.tax)/100) * Decimal(sale.total)
					tax = tax + t				

			summary['total_discount'] = discount
			summary['total_tax'] = tax	
			data = Product.objects.filter(business=business, inventory_product__sale_inventory__status='Completed', inventory_product__sale_inventory__created_at__date__gte=fr, inventory_product__sale_inventory__created_at__date__lte=to).all().annotate(quantity_sold=Sum('inventory_product__sale_inventory__quantity'),profit_sold=Sum('inventory_product__sale_inventory__profit'),revenue_sold=Sum('inventory_product__sale_inventory__amount_paid'))
			products = []
			for d in data:
				dic = {'name': d.name, 'quantity_sold': d.quantity_sold, 'profit_sold': d.profit_sold, 'revenue_sold': d.revenue_sold}
				products.append(dic)

			if pdf == '1':
				return sales_report_export_pdf(request,business=business, products=products, summary=summary,sales=sales)

			if xl == '2':
				return sales_report_export_excel(request,business=business,sales=sales)
				
	context = {
		'business':business,
		'sales':sales,
		'summary':summary,
		'products':products,
		'day':day,
		'fr':fr,
		'to':to,
	}
	return render(request, 'sales_report.html', context)


# """""""""" INVENTORY REPORT """""""""""
@store_report_required
@login_required
def inventory_product(request, *args, **kwargs):
	id = kwargs.get('id')
	business = Business.objects.filter(id=id).first()
	products = Product.objects.filter(business=business)
	context = {
		'business':business,
		'products':products,
	}
	return render(request, 'inventory_product.html', context)

@store_report_required
@login_required
def inventory_report(request, *args, **kwargs):
	id = kwargs.get('id')
	business = Business.objects.filter(id=id).first() 
	pdf = request.GET.get('pdf')
	xl = request.GET.get('xl')

	if request.method == 'GET':
		p = request.GET['p']

		if p == '0':
			inventory_qs = Inventory.objects.filter(business=business, exist=True).annotate(available=F('remain')-F('damage'))	
			if inventory_qs:
				inventory_qs.filter(available=0).update(exist=False)		
			inventories = inventory_qs.filter(available__gt=0).order_by('-pk')
			summary = inventory_qs.aggregate(total_cost=Sum(F('available')*F('product_cost'),output_field=FloatField()),total_worth=Sum(F('available')*F('product__sell_price'),output_field=FloatField()))

			data = Product.objects.filter(business=business).all()
			products = []
			for d in data:
				dic = {'name': d.name, 'quantity': d.quantity, 'worth':d.worth}
				products.append(dic)

			if pdf == '1':				
				return inventory_report_export_pdf(request, business=business, inventories=inventories, summary=summary, products=products,)

			if xl == '2':				
				return inventory_report_export_excel(request, business=business, inventories=inventories)

		else:
			inventory_qs = Inventory.objects.filter(business=business, product__id=p, exist=True).annotate(available=F('remain')-F('damage'))	
			if inventory_qs:
				inventory_qs.filter(available=0).update(exist=False)			
			inventories = inventory_qs.filter(available__gt=0).order_by('-pk')
			summary = inventory_qs.aggregate(total_cost=Sum(F('available')*F('product_cost'),output_field=FloatField()),total_worth=Sum(F('available')*F('product__sell_price'),output_field=FloatField()))

			data = Product.objects.filter(id=p,business=business).all()
			products = []
			for d in data:
				dic = {'name': d.name, 'quantity': d.quantity, 'worth':d.worth}
				products.append(dic)

			if pdf == '1':				
				return inventory_report_export_pdf(request, business=business, inventories=inventories, summary=summary, products=products,)

			if xl == '2':				
				return inventory_report_export_excel(request, business=business, inventories=inventories)	
			
	context = {
		'business':business,
		'inventories':inventories,
		'summary':summary,
		'products':products,
		'p':p,
	}
	return render(request, 'inventory_report.html', context)


############ Payroll Report ###########    
@finance_report_required
@login_required
def payroll_report(request, *args, **kwargs):

	id = kwargs.get('id')
	day = kwargs.get('d')
	fr = request.GET.get('fr')
	to = request.GET.get('to')
	pdf = request.GET.get('pdf')
	xl = request.GET.get('xl')

	business = Business.objects.filter(id=id).first()

	if day == 1:
		takehome = Takehome.objects.filter(created_at__date=date.today(), business=business)
		employees = Payroll.objects.filter(created_at__date=date.today(), business=business).count()           
		deduction = Payroll.objects.filter(created_at__date=date.today(), business=business).aggregate(Sum('deduction'))['deduction__sum']   		
		bonuses = Payroll.objects.filter(created_at__date=date.today(), business=business).aggregate(Sum('bonus'))['bonus__sum']   		
		overtime = Payroll.objects.filter(created_at__date=date.today(), business=business).aggregate(Sum('overtime'))['overtime__sum']    		
		nssf = Payroll.objects.filter(tax_rate__icontains='nssf', created_at__date=date.today(), business=business)
		wcf = Payroll.objects.filter(tax_rate__icontains='wcf', created_at__date=date.today(), business=business)
		loan_board = Payroll.objects.filter(tax_rate__icontains='loan board', created_at__date=date.today(), business=business)
		salaries = Payroll.objects.filter(created_at__date=date.today(), business=business).aggregate(Sum('employee__salary'))['employee__salary__sum']
		paye_objs = Payroll.objects.filter(paye=True, created_at__date=date.today(), business=business)
		takehome_total = Takehome.objects.filter(created_at__date=date.today(), business=business).aggregate(Sum('salary'))['salary__sum']
		sdl = Payroll.objects.filter(created_at__date=date.today(), business=business).aggregate(Sum('sdl_amount'))['sdl_amount__sum']   		


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

		if bonuses is None:
			bonuses = 0
		if overtime is None:
			overtime = 0
		if takehome_total is None:
			takehome_total = 0
		if deduction is None:
			deduction = 0
		if sdl is None:
			sdl = 0				

		total = int(nssf_funds) + int(paye_total) + int(loan_board_funds) + int(wcf_funds) + takehome_total + int(sdl)

		if pdf == '1':
			return payroll_report_export_pdf(request, takehome=takehome, takehome_total=takehome_total, wcf=int(wcf_funds), nssf=int(nssf_funds), loan_board=int(loan_board_funds), paye=int(paye_total), employees=employees, bonus=bonuses, overtime=overtime, total_expenses=total, salaries_total=salaries, deduction=deduction, sdl=sdl)
		if xl == '1':
			return payroll_report_export_excel(request, takehome=takehome, business=business)	

	elif day == 2:	
		dt = date.today() - timedelta(days=1)
		takehome = Takehome.objects.filter(created_at__date=dt, business=business)
		employees = Payroll.objects.filter(created_at__date=dt, business=business).count()           
		sdl = Payroll.objects.filter(created_at__date=dt, business=business).aggregate(Sum('sdl_amount'))['sdl_amount__sum']   		
		deduction = Payroll.objects.filter(created_at__date=dt, business=business).aggregate(Sum('deduction'))['deduction__sum']   		
		bonuses = Payroll.objects.filter(created_at__date=dt, business=business).aggregate(Sum('bonus'))['bonus__sum']   		
		overtime = Payroll.objects.filter(created_at__date=dt, business=business).aggregate(Sum('overtime'))['overtime__sum']    		
		nssf = Payroll.objects.filter(tax_rate__icontains='nssf', created_at__date=dt, business=business)
		wcf = Payroll.objects.filter(tax_rate__icontains='wcf', created_at__date=dt, business=business)
		loan_board = Payroll.objects.filter(tax_rate__icontains='loan board', created_at__date=dt, business=business)
		salaries = Payroll.objects.filter(created_at__date=dt, business=business).aggregate(Sum('employee__salary'))['employee__salary__sum']
		paye_objs = Payroll.objects.filter(paye=True, created_at__date=dt, business=business)
		takehome_total = Takehome.objects.filter(created_at__date=dt, business=business).aggregate(Sum('salary'))['salary__sum']

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

		if bonuses is None:
			bonuses = 0
		if overtime is None:
			overtime = 0
		if takehome_total is None:
			takehome_total = 0		
		if deduction is None:
			deduction = 0
		if sdl is None:
			sdl = 0	

		total = int(nssf_funds) + int(paye_total) + int(loan_board_funds) + int(wcf_funds) + takehome_total + int(sdl)

		if pdf == '1':
			return payroll_report_export_pdf(request, takehome=takehome, takehome_total=takehome_total, wcf=int(wcf_funds), nssf=int(nssf_funds), loan_board=int(loan_board_funds), paye=int(paye_total), employees=employees, bonus=bonuses, overtime=overtime, total_expenses=total, salaries_total=salaries,deduction=deduction, sdl=sdl)
		if xl == '1':
    			return payroll_report_export_excel(request, takehome=takehome, business=business)

	elif day == 3:	
		dt = date.today() - timedelta(days=7)
		takehome = Takehome.objects.filter(created_at__date__gte=dt, created_at__date__lte=date.today(), business=business)
		employees = Payroll.objects.filter(created_at__date__gte=dt, created_at__date__lte=date.today(), business=business).count()           
		sdl = Payroll.objects.filter(created_at__date__gte=dt, created_at__date__lte=date.today(), business=business).aggregate(Sum('sdl_amount'))['sdl_amount__sum']   		
		deduction = Payroll.objects.filter(created_at__date__gte=dt, created_at__date__lte=date.today(), business=business).aggregate(Sum('deduction'))['deduction__sum']   		
		bonuses = Payroll.objects.filter(created_at__date__gte=dt, created_at__date__lte=date.today(), business=business).aggregate(Sum('bonus'))['bonus__sum']   		
		overtime = Payroll.objects.filter(created_at__date__gte=dt, created_at__date__lte=date.today(), business=business).aggregate(Sum('overtime'))['overtime__sum']    		
		nssf = Payroll.objects.filter(tax_rate__icontains='nssf', created_at__date__gte=dt, created_at__date__lte=date.today(), business=business)
		wcf = Payroll.objects.filter(tax_rate__icontains='wcf', created_at__date__gte=dt, created_at__date__lte=date.today(), business=business)
		loan_board = Payroll.objects.filter(tax_rate__icontains='loan board', created_at__date__gte=dt, created_at__date__lte=date.today(), business=business)
		salaries = Payroll.objects.filter(created_at__date__gte=dt, created_at__date__lte=date.today(), business=business).aggregate(Sum('employee__salary'))['employee__salary__sum']
		paye_objs = Payroll.objects.filter(paye=True, created_at__date__gte=dt, created_at__date__lte=date.today(), business=business)
		takehome_total = Takehome.objects.filter(created_at__date__gte=dt, created_at__date__lte=date.today(), business=business).aggregate(Sum('salary'))['salary__sum']

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

		if bonuses is None:
			bonuses = 0
		if overtime is None:
			overtime = 0
		if takehome_total is None:
			takehome_total = 0	
		if deduction is None:
			deduction = 0
		if sdl is None:
			sdl = 0			

		total = int(nssf_funds) + int(paye_total) + int(loan_board_funds) + int(wcf_funds) + takehome_total + int(sdl)

		if pdf == '1':
			return payroll_report_export_pdf(request, takehome=takehome, takehome_total=takehome_total, wcf=int(wcf_funds), nssf=int(nssf_funds), loan_board=int(loan_board_funds), paye=int(paye_total), employees=employees, bonus=bonuses, overtime=overtime, total_expenses=total, salaries_total=salaries, deduction=deduction, sdl=sdl)
		if xl == '1':
    			return payroll_report_export_excel(request, takehome=takehome, business=business)

	elif day == 4:	
		dt = date.today() - timedelta(days=30)
		takehome = Takehome.objects.filter(created_at__date__gte=dt, created_at__date__lte=date.today(), business=business)
		employees = Payroll.objects.filter(created_at__date__gte=dt, created_at__date__lte=date.today(), business=business).count()           
		sdl = Payroll.objects.filter(created_at__date__gte=dt, created_at__date__lte=date.today(), business=business).aggregate(Sum('sdl_amount'))['sdl_amount__sum']   		
		deduction = Payroll.objects.filter(created_at__date__gte=dt, created_at__date__lte=date.today(), business=business).aggregate(Sum('deduction'))['deduction__sum']   		
		bonuses = Payroll.objects.filter(created_at__date__gte=dt, created_at__date__lte=date.today(), business=business).aggregate(Sum('bonus'))['bonus__sum']   		
		overtime = Payroll.objects.filter(created_at__date__gte=dt, created_at__date__lte=date.today(), business=business).aggregate(Sum('overtime'))['overtime__sum']    		
		nssf = Payroll.objects.filter(tax_rate__icontains='nssf', created_at__date__gte=dt, created_at__date__lte=date.today(), business=business)
		wcf = Payroll.objects.filter(tax_rate__icontains='wcf', created_at__date__gte=dt, created_at__date__lte=date.today(), business=business)
		loan_board = Payroll.objects.filter(tax_rate__icontains='loan board', created_at__date__gte=dt, created_at__date__lte=date.today(), business=business)
		salaries = Payroll.objects.filter(created_at__date__gte=dt, created_at__date__lte=date.today(), business=business).aggregate(Sum('employee__salary'))['employee__salary__sum']
		paye_objs = Payroll.objects.all().filter(paye=True, created_at__date__gte=dt, created_at__date__lte=date.today(), business=business)
		takehome_total = Takehome.objects.filter(created_at__date__gte=dt, created_at__date__lte=date.today(), business=business).aggregate(Sum('salary'))['salary__sum']

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

		if bonuses is None:
			bonuses = 0
		if overtime is None:
			overtime = 0
		if takehome_total is None:
			takehome_total = 0		
		if deduction is None:
			deduction = 0
		if sdl is None:
			sdl = 0	
 
		total = int(nssf_funds) + int(paye_total) + int(loan_board_funds) + int(wcf_funds) + takehome_total + int(sdl)

		if pdf == '1':
			return payroll_report_export_pdf(request, takehome=takehome, takehome_total=takehome_total, wcf=int(wcf_funds), nssf=int(nssf_funds), loan_board=int(loan_board_funds), paye=int(paye_total), employees=employees, bonus=bonuses, overtime=overtime, total_expenses=total, salaries_total=salaries, deduction=deduction, sdl=sdl)
		if xl == '1':
    			return payroll_report_export_excel(request, takehome=takehome, business=business)

	elif day == 5:	
		dt = date.today()
		takehome = Takehome.objects.filter(created_at__month=dt.month, created_at__year=dt.year, business=business)
		employees = Payroll.objects.filter(created_at__month=dt.month, created_at__year=dt.year, business=business).count()           
		sdl = Payroll.objects.filter(created_at__month=dt.month, created_at__year=dt.year, business=business).aggregate(Sum('sdl_amount'))['sdl_amount__sum']   		
		deduction = Payroll.objects.filter(created_at__month=dt.month, created_at__year=dt.year, business=business).aggregate(Sum('deduction'))['deduction__sum']   		
		bonuses = Payroll.objects.filter(created_at__month=dt.month, created_at__year=dt.year, business=business).aggregate(Sum('bonus'))['bonus__sum']   		
		overtime = Payroll.objects.filter(created_at__month=dt.month, created_at__year=dt.year, business=business).aggregate(Sum('overtime'))['overtime__sum']    		
		nssf = Payroll.objects.filter(tax_rate__icontains='nssf', created_at__month=dt.month, created_at__year=dt.year, business=business)
		wcf = Payroll.objects.filter(tax_rate__icontains='wcf', created_at__month=dt.month, created_at__year=dt.year, business=business)
		loan_board = Payroll.objects.filter(tax_rate__icontains='loan board', created_at__month=dt.month, created_at__year=dt.year, business=business)
		salaries = Payroll.objects.filter(created_at__month=dt.month, created_at__year=dt.year, business=business).aggregate(Sum('employee__salary'))['employee__salary__sum']
		paye_objs = Payroll.objects.filter(paye=True, created_at__month=dt.month, created_at__year=dt.year, business=business)
		takehome_total = Takehome.objects.filter(created_at__month=dt.month, created_at__year=dt.year, business=business).aggregate(Sum('salary'))['salary__sum']

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

		if bonuses is None:
			bonuses = 0
		if overtime is None:
			overtime = 0
		if takehome_total is None:
			takehome_total = 0	
		if deduction is None:
			deduction = 0
		if sdl is None:
			sdl = 0			

		total = int(nssf_funds) + int(paye_total) + int(loan_board_funds) + int(wcf_funds) + takehome_total + int(sdl)

		if pdf == '1':
			return payroll_report_export_pdf(request, takehome=takehome, takehome_total=takehome_total, wcf=int(wcf_funds), nssf=int(nssf_funds), loan_board=int(loan_board_funds), paye=int(paye_total), employees=employees, bonus=bonuses, overtime=overtime, total_expenses=total, salaries_total=salaries, deduction=deduction, sdl=sdl)
		if xl == '1':
    			return payroll_report_export_excel(request, takehome=takehome, business=business)

	elif day == 6:	
		dt = date.today()
		month = dt.month - 1
		takehome = Takehome.objects.filter(created_at__month=month, created_at__year=dt.year, business=business)
		employees = Payroll.objects.filter(created_at__month=month, created_at__year=dt.year, business=business).count()           
		sdl = Payroll.objects.filter(created_at__month=month, created_at__year=dt.year, business=business).aggregate(Sum('sdl_amount'))['sdl_amount__sum']   		
		deduction = Payroll.objects.filter(created_at__month=month, created_at__year=dt.year, business=business).aggregate(Sum('deduction'))['deduction__sum']   		
		bonuses = Payroll.objects.filter(created_at__month=month, created_at__year=dt.year, business=business).aggregate(Sum('bonus'))['bonus__sum']   		
		overtime = Payroll.objects.filter(created_at__month=month, created_at__year=dt.year, business=business).aggregate(Sum('overtime'))['overtime__sum']    		
		nssf = Payroll.objects.filter(tax_rate__icontains='nssf', created_at__month=month, created_at__year=dt.year, business=business)
		wcf = Payroll.objects.filter(tax_rate__icontains='wcf', created_at__month=month, created_at__year=dt.year, business=business)
		loan_board = Payroll.objects.filter(tax_rate__icontains='loan board', created_at__month=month, created_at__year=dt.year, business=business)
		salaries = Payroll.objects.filter(created_at__month=month, created_at__year=dt.year, business=business).aggregate(Sum('employee__salary'))['employee__salary__sum']
		paye_objs = Payroll.objects.filter(paye=True, created_at__month=month, created_at__year=dt.year, business=business)
		takehome_total = Takehome.objects.filter(created_at__month=month, created_at__year=dt.year, business=business).aggregate(Sum('salary'))['salary__sum']


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

		if bonuses is None:
			bonuses = 0
		if overtime is None:
			overtime = 0
		if takehome_total is None:
			takehome_total = 0	
		if deduction is None:
			deduction = 0	
		if sdl is None:
			sdl = 0		

		total = int(nssf_funds) + int(paye_total) + int(loan_board_funds) + int(wcf_funds) + takehome_total + int(sdl)

		if pdf == '1':
			return payroll_report_export_pdf(request, takehome=takehome, takehome_total=takehome_total, wcf=int(wcf_funds), nssf=int(nssf_funds), loan_board=int(loan_board_funds), paye=int(paye_total), employees=employees, bonus=bonuses, overtime=overtime, total_expenses=total, salaries_total=salaries, deduction=deduction, sdl=sdl)
		if xl == '1':
    			return payroll_report_export_excel(request, takehome=takehome, business=business)

	elif day == 7:	
		takehome = Takehome.objects.filter(business=business)
		employees = Payroll.objects.filter(business=business).count()           
		sdl = Payroll.objects.filter(business=business).aggregate(Sum('sdl_amount'))['sdl_amount__sum']   		
		deduction = Payroll.objects.filter(business=business).aggregate(Sum('deduction'))['deduction__sum']   		
		bonuses = Payroll.objects.filter(business=business).aggregate(Sum('bonus'))['bonus__sum']   		
		overtime = Payroll.objects.filter(business=business).aggregate(Sum('overtime'))['overtime__sum']    		
		nssf = Payroll.objects.filter(tax_rate__icontains='nssf', business=business)
		wcf = Payroll.objects.filter(tax_rate__icontains='wcf', business=business)
		loan_board = Payroll.objects.filter(tax_rate__icontains='loan board', business=business)
		salaries = Payroll.objects.filter(business=business).aggregate(Sum('employee__salary'))['employee__salary__sum']
		paye_objs = Payroll.objects.filter(paye=True, business=business)
		takehome_total = Takehome.objects.filter(business=business).aggregate(Sum('salary'))['salary__sum']


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

		if bonuses is None:
			bonuses = 0
		if overtime is None:
			overtime = 0
		if takehome_total is None:
			takehome_total = 0
		if deduction is None:
			deduction = 0
		if sdl is None:
			sdl = 0				

		total = int(nssf_funds) + int(paye_total) + int(loan_board_funds) + int(wcf_funds) + takehome_total + int(sdl)

		if pdf == '1':
			return payroll_report_export_pdf(request, takehome=takehome, takehome_total=takehome_total, wcf=int(wcf_funds), nssf=int(nssf_funds), loan_board=int(loan_board_funds), paye=int(paye_total), employees=employees, bonus=bonuses, overtime=overtime, total_expenses=total, salaries_total=salaries, deduction=deduction, sdl=sdl)
		if xl == '1':
    			return payroll_report_export_excel(request, takehome=takehome, business=business)

	elif day == 8:
		if request.method == 'GET':	
			takehome = Takehome.objects.filter(created_at__date__gte=fr, created_at__date__lte=to, business=business)
			employees = Payroll.objects.filter(created_at__date__gte=fr, created_at__date__lte=to, business=business).count()           
			sdl = Payroll.objects.filter(created_at__date__gte=fr, created_at__date__lte=to, business=business).aggregate(Sum('sdl_amount'))['sdl_amount__sum']   		
			deduction = Payroll.objects.filter(created_at__date__gte=fr, created_at__date__lte=to, business=business).aggregate(Sum('deduction'))['deduction__sum']   		
			bonuses = Payroll.objects.filter(created_at__date__gte=fr, created_at__date__lte=to, business=business).aggregate(Sum('bonus'))['bonus__sum']   		
			overtime = Payroll.objects.filter(created_at__date__gte=fr, created_at__date__lte=to, business=business).aggregate(Sum('overtime'))['overtime__sum']    		
			nssf = Payroll.objects.filter(tax_rate__icontains='nssf', created_at__date__gte=fr, created_at__date__lte=to, business=business)
			wcf = Payroll.objects.filter(tax_rate__icontains='wcf', created_at__date__gte=fr, created_at__date__lte=to, business=business)
			loan_board = Payroll.objects.filter(tax_rate__icontains='loan board', created_at__date__gte=fr, created_at__date__lte=to, business=business)
			salaries = Payroll.objects.filter(created_at__date__gte=fr, created_at__date__lte=to, business=business).all().aggregate(Sum('employee__salary'))['employee__salary__sum']
			paye_objs = Payroll.objects.filter(paye=True, created_at__date__gte=fr, created_at__date__lte=to, business=business)
			takehome_total = Takehome.objects.filter(created_at__date__gte=fr, created_at__date__lte=to, business=business).aggregate(Sum('salary'))['salary__sum']

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

			if bonuses is None:
				bonuses = 0
			if overtime is None:
				overtime = 0
			if takehome_total is None:
				takehome_total = 0
			if deduction is None:
				deduction = 0
			if sdl is None:
				sdl = 0				

			total = int(nssf_funds) + int(paye_total) + int(loan_board_funds) + int(wcf_funds) + takehome_total + int(sdl)

			if pdf == '1':
				return payroll_report_export_pdf(request, takehome=takehome, takehome_total=takehome_total, wcf=int(wcf_funds), nssf=int(nssf_funds), loan_board=int(loan_board_funds), paye=int(paye_total), employees=employees, bonus=bonuses, overtime=overtime, total_expenses=total, salaries_total=salaries, deduction=deduction, sdl=sdl)
			if xl == '1':
					return payroll_report_export_excel(request, takehome=takehome, business=business)

	if bonuses is None:
		bonuses = 0
	if overtime is None:
		overtime = 0
	if takehome_total is None:
		takehome_total = 0		

	### Total payroll expenses
	total_expenses = int(nssf_funds) + int(paye_total) + int(loan_board_funds) + int(wcf_funds) + takehome_total + int(sdl)

	funds = [
		{ 'name': 'Paye', 'cost': int(paye_total) },
		{ 'name': 'Helsb', 'cost': int(loan_board_funds) },
		{ 'name': 'Nssf', 'cost': int(nssf_funds) },
		{ 'name': 'Wcf', 'cost': int(wcf_funds) },
	]	

	extras = [

		{ 'name': 'Takehome', 'cost': takehome_total },
		{ 'name': 'Overtime', 'cost': overtime },
		{ 'name': 'Bonus', 'cost': bonuses },

	]

	context = {
		'business' : business,
		# 'payroll' : payroll_objects,
		'takehome': takehome,
		'takehome_total': takehome_total,
		'wcf': int(wcf_funds),
		'nssf': int(nssf_funds),
		'loan_board': int(loan_board_funds),
		'deduction': deduction,
		'bonus': bonuses,
		'sdl': sdl,
		'salaries_total': salaries,
		'overtime': overtime,
		'paye': int(paye_total),
		'employees': employees,
		'funds': funds,
		'extras': extras,
		'total_expenses': total_expenses,
		'day': day,
		'fr': fr,
		'to': to,
	}
	template_name = 'payroll-report.html'

	return render(request, template_name, context)


########## Payroll Report - time ##############
@finance_report_required
@login_required
def payroll_time(request, *args, **kwargs):
	id = kwargs.get('id')
	business = Business.objects.filter(id=id).first()
	context = {
		'business':business,
	}
	return render(request, 'payroll-time.html', context)


############ OPEX Report ###########  
@finance_report_required  
@login_required
def opex_report(request, *args, **kwargs):

	id = kwargs.get('id')
	day = kwargs.get('d')
	fr = request.GET.get('fr')
	to = request.GET.get('to')	
	pdf = request.GET.get('pdf')
	xl = request.GET.get('xl')
	business = Business.objects.filter(id=id).first()

	exps_objects = []

	if day == 1:	
		expense_objects = Expense.objects.filter(created_at__date=date.today(), business=business)
		total_cost = Expense.objects.filter(created_at__date=date.today(), business=business).aggregate(Sum('cost'))['cost__sum'] 
		expenses = Expense.objects.filter(created_at__date=date.today(), business=business).count()          
		exps = Expense.objects.filter(created_at__date=date.today(), business=business)

		if pdf == '1':
			return opex_report_export_pdf(request, expense_objects=expense_objects, total_cost=total_cost, expenses_total=expenses, exps=exps, business=business)

		if xl == '2':
			return opex_report_export_excel(request, expense_objects=expense_objects, business=business)	

	elif day == 2:	
		dt = date.today() - timedelta(days=1)
		expense_objects = Expense.objects.filter(created_at__date=dt, business=business)
		total_cost = Expense.objects.filter(created_at__date=dt, business=business).aggregate(Sum('cost'))['cost__sum'] 
		expenses = Expense.objects.filter(created_at__date=dt, business=business).count()          
		exps = Expense.objects.filter(created_at__date=dt, business=business)

		if pdf == '1':
			return opex_report_export_pdf(request, expense_objects=expense_objects, total_cost=total_cost, expenses_total=expenses, exps=exps)

		if xl == '2':
   			return opex_report_export_excel(request, expense_objects=expense_objects, business=business)	
	

	elif day == 3:	
		dt = date.today() - timedelta(days=7)
		expense_objects = Expense.objects.filter(created_at__date__gte=dt, created_at__date__lte=date.today(), business=business)
		total_cost = Expense.objects.filter(created_at__date__gte=dt, created_at__date__lte=date.today(), business=business).aggregate(Sum('cost'))['cost__sum'] 
		expenses = Expense.objects.filter(created_at__date__gte=dt, created_at__date__lte=date.today(), business=business).count()          
		exps = Expense.objects.filter(created_at__date__gte=dt, created_at__date__lte=date.today(), business=business)

		if pdf == '1':
			return opex_report_export_pdf(request, expense_objects=expense_objects, total_cost=total_cost, expenses_total=expenses, exps=exps)

		if xl == '2':
   			return opex_report_export_excel(request, expense_objects=expense_objects, business=business)	

	elif day == 4:	
		dt = date.today() - timedelta(days=30)
		expense_objects = Expense.objects.filter(created_at__date__gte=dt, created_at__date__lte=date.today(), business=business)
		total_cost = Expense.objects.filter(created_at__date__gte=dt, created_at__date__lte=date.today(), business=business).aggregate(Sum('cost'))['cost__sum'] 
		expenses = Expense.objects.filter(created_at__date__gte=dt, created_at__date__lte=date.today(), business=business).count()          
		exps = Expense.objects.filter(created_at__date__gte=dt, created_at__date__lte=date.today(), business=business)

		if pdf == '1':
			return opex_report_export_pdf(request, expense_objects=expense_objects, total_cost=total_cost, expenses_total=expenses, exps=exps)

		if xl == '2':
   			return opex_report_export_excel(request, expense_objects=expense_objects, business=business)	

	elif day == 5:	
		dt = date.today()
		expense_objects = Expense.objects.filter(created_at__month=dt.month, created_at__year=dt.year, business=business)
		total_cost = Expense.objects.filter(created_at__month=dt.month, created_at__year=dt.year, business=business).aggregate(Sum('cost'))['cost__sum'] 
		expenses = Expense.objects.filter(created_at__month=dt.month, created_at__year=dt.year, business=business).count()          
		exps = Expense.objects.filter(created_at__month=dt.month, created_at__year=dt.year, business=business)

		if pdf == '1':
			return opex_report_export_pdf(request, expense_objects=expense_objects, total_cost=total_cost, expenses_total=expenses, exps=exps)

		if xl == '2':
   			return opex_report_export_excel(request, expense_objects=expense_objects, business=business)	

	elif day == 6:	
		dt = date.today()
		month = dt.month - 1
		expense_objects = Expense.objects.filter(created_at__month=month, created_at__year=dt.year, business=business)
		total_cost = Expense.objects.filter(created_at__month=month, created_at__year=dt.year, business=business).aggregate(Sum('cost'))['cost__sum'] 
		expenses = Expense.objects.filter(created_at__month=month, created_at__year=dt.year, business=business).count()          
		exps = Expense.objects.filter(created_at__month=month, created_at__year=dt.year, business=business)

		if pdf == '1':
			return opex_report_export_pdf(request, expense_objects=expense_objects, total_cost=total_cost, expenses_total=expenses, exps=exps)

		if xl == '2':
			return opex_report_export_excel(request, expense_objects=expense_objects, business=business)	

	elif day == 7:	
		expense_objects = Expense.objects.all()
		total_cost = Expense.objects.aggregate(Sum('cost'))['cost__sum'] 
		expenses = Expense.objects.all().count()          
		exps = Expense.objects.all()

		if pdf == '1':
			return opex_report_export_pdf(request, expense_objects=expense_objects, total_cost=total_cost, expenses_total=expenses, exps=exps)

		if xl == '2':
   			return opex_report_export_excel(request, expense_objects=expense_objects, business=business)	

	elif day == 8:
		if request.method == 'GET':	
			expense_objects = Expense.objects.filter(created_at__date__gte=fr, created_at__date__lte=to, business=business)
			total_cost = Expense.objects.filter(created_at__date__gte=fr, created_at__date__lte=to, business=business).aggregate(Sum('cost'))['cost__sum'] 
			expenses = Expense.objects.filter(created_at__date__gte=fr, created_at__date__lte=to, business=business).count()          
			exps = Expense.objects.filter(created_at__date__gte=fr, created_at__date__lte=to, business=business)

		if pdf == '1':
			return opex_report_export_pdf(request, expense_objects=expense_objects, total_cost=total_cost, expenses_total=expenses, exps=exps)
			
		if xl == '2':
   			return opex_report_export_excel(request, expense_objects=expense_objects, business=business)	

	if total_cost is None:
		total_cost = 0


	for exp in exps:
		exps_objects.append({'name': exp.name, 'cost':exp.cost})

	context = {
		'business' : business,
		'expenses': expense_objects,
		'cost': total_cost,
		'expenses_total': str(expenses),
		'exps' : exps_objects,
		'day': day,
		'fr' : fr,
		'to' : to,
	}
	template_name = 'opex-report.html'

	return render(request, template_name, context)


########## Opex Report - time ##############
@finance_report_required
@login_required
def opex_time(request, *args, **kwargs):
	id = kwargs.get('id')
	business = Business.objects.filter(id=id).first()
	context = {
		'business':business,
	}
	return render(request, 'opex-time.html', context)	


@finance_report_required
@login_required
def customer_report(request, *args, **kwargs):

	id = kwargs.get('id')
	pdf = request.GET.get('pdf')
	business = Business.objects.filter(id=id).first()
	customers = Customer.objects.filter(business=business)
	url_parameter = request.GET.get("q")

	for customer in customers:
		customer_sales = Sale.objects.filter(customer=customer, branch__business=business)
		dates = []

		for sale in customer_sales:

			customer_point = {f'{customer.full_name} : {sale.created_at.date()}'}

			if customer_point in dates:
				pass
			else:
				dates.append({f'{customer.full_name} : {sale.created_at.date()}'})

		points = len(dates)

		Customer.objects.filter(id=customer.id, business=business).update(points=points)

		if customer.points == 30:
			Customer.objects.filter(id=customer.id, business=business).update(category='Loyal')


	# print(url_parameter)

	if url_parameter:
		# print("Executes")
		# customers = []
		customers = Customer.objects.filter(business=business).filter(Q(full_name__icontains=url_parameter) | Q(contact__icontains=url_parameter))
		# customers.append(customer)

	else:
		# print("Runs")
		customers = Customer.objects.filter(business=business)
			

	if request.is_ajax():
		html = render_to_string(
			template_name='customer-results.html',
			context={'customers':customers}
		)

		data_dict = {"html_from_view": html}

		return JsonResponse(data=data_dict, safe=False)

	normal_customers = Customer.objects.filter(category="Normal", business=business).count()	
	loyal_customers = Customer.objects.filter(category="Loyal", business=business).count()	
	other_customers = Sale.objects.filter(customer=None, branch__business=business).count()

	if pdf == '1':
		return customer_report_export_pdf(request, customers=customers, normal=normal_customers, loyal=loyal_customers, other=other_customers,business=business)

	customer_category = [
		{"name": "Loyal customers", "value": loyal_customers},
		{"name": "Normal customers", "value": normal_customers},
		{"name": "Other customers", "value": other_customers},
		]

	# print(customers)
	context = {
		'business': business,
		'customers': customers,
		'categories': customer_category,
		'normal': normal_customers,
		'loyal': loyal_customers,
		'other': other_customers,
	}
	template_name = 'customer-report.html'
	return render(request, template_name, context)


@finance_report_required
@login_required
def financial_statements(request, *args, **kwargs):
	id = kwargs.get('id')
	business = Business.objects.filter(id=id).first()

	context = {
		'business':business,
	}
	return render(request, 'financial_statements.html', context)

@finance_report_required
@login_required
def income_statement_time(request, *args, **kwargs):
	id = kwargs.get('id')
	business = Business.objects.filter(id=id).first()

	context = {
		'business':business,
	}
	return render(request, 'income_statement_time.html', context)


@finance_report_required
@login_required
def income_statement(request, *args, **kwargs):
	id = kwargs.get('id')
	d = kwargs.get('d')
	pdf = request.GET.get('pdf')
	pdf = request.GET.get('pdf')
	xl = request.GET.get('xl')
	year = request.GET.get('year')
	business = Business.objects.filter(id=id).first() 
	if d == 1:
		dt = date.today() - timedelta(days=30)
		summary = Sale.objects.filter(branch__business=business, created_at__date__gte=dt, created_at__date__lte=date.today(), status='Completed').all().aggregate(total_paid=Sum('amount_paid'))
		inventory_qs = Inventory.objects.filter(business=business,).annotate(available=F('remain')-F('damage'))			
		inventories = inventory_qs.filter(available__gt=0).order_by('-pk')
		total_expense = Expense.objects.filter(created_at__date__gte=dt, created_at__date__lte=date.today(), business=business).aggregate(Sum('cost'))['cost__sum']
		depreciation = AccountsFixedAsset.objects.filter(depreciation_value__gt=0, created_at__date__gte=dt, created_at__date__lte=date.today(), business=business).aggregate(Sum('depreciation_value'))['depreciation_value__sum']
		amortization = AccountsFixedAsset.objects.filter(amortization_value__gt=0, created_at__date__gte=dt, created_at__date__lte=date.today(), business=business).aggregate(Sum('amortization_value'))['amortization_value__sum'] 
		takehome = Takehome.objects.filter(created_at__date__gte=dt, created_at__date__lte=date.today(), business=business).aggregate(Sum('salary'))['salary__sum']
		interest_total = Interest.objects.filter(business=business, created_at__date__gte=dt, created_at__date__lte=date.today()).aggregate(Sum('remaining'))['remaining__sum']
		tax_total = Tax.objects.filter(business=business, created_at__date__gte=dt, created_at__date__lte=date.today()).aggregate(total=Sum('remain'))['total']

		if tax_total is None:
				tax_total = 0

		if interest_total is None:
				interest_total = 0
	
		total_revenue = summary['total_paid']

		if total_revenue is None:
				total_revenue = 0

		if takehome is None:
				takehome = 0
		
		if total_expense is None:
				total_expense = 0

		if depreciation is None:
				depreciation = 0

		if amortization is None:
				amortization = 0

		nssf = Payroll.objects.filter(tax_rate__icontains='nssf',created_at__date__gte=dt, created_at__date__lte=date.today(), business=business)
		wcf = Payroll.objects.filter(tax_rate__icontains='wcf', created_at__date__gte=dt, created_at__date__lte=date.today(), business=business)
		loan_board = Payroll.objects.filter(tax_rate__icontains='loan board', created_at__date__gte=dt, created_at__date__lte=date.today(), business=business)
		paye_objs = Payroll.objects.filter(paye=True, created_at__date__gte=dt, created_at__date__lte=date.today(), business=business)

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

		cogs = 0
		for i in inventories:
			cogs = cogs + i.cogs

		summary['cogs'] = cogs

		total_social_funds = int(nssf_funds) + int(paye_total) + int(loan_board_funds) + int(wcf_funds) 

		tax = tax_total 	
		tax_interest = tax + interest_total

		takehome = takehome - total_social_funds

		

		##### Calculating OPEX #####
		opex = total_expense + takehome + depreciation + amortization
		opex_da = total_expense + takehome

		##### Calculating EBIT #####
		ebit = total_revenue - (cogs + opex)

		##### Calculating EBITDA #####
		ebitda = total_revenue - (cogs + opex_da)

		####### Net Income ########
		net_income = ebit - tax_interest

		summary['net_income'] = round(net_income,2)
		summary['social_funds'] = round(total_social_funds,2)
		summary['opex'] = round(opex,2)
		summary['ebit'] = round(ebit,2)
		summary['ebitda'] = round(ebitda,2)
		summary['tax_interest'] = round(tax_interest,2)


		if pdf == '1':
			return income_statement_export_pdf(request, business=business, summary=summary)
		if xl == '1':
				return income_statement_export_excel(request, business=business, summary=summary)

	elif d == 2:	
		dt = date.today() - timedelta(days=90)
		summary = Sale.objects.filter(branch__business=business, created_at__date__gte=dt, created_at__date__lte=date.today(), status='Completed').all().aggregate(total_paid=Sum('amount_paid'))
		inventory_qs = Inventory.objects.filter(business=business,).annotate(available=F('remain')-F('damage'))			
		inventories = inventory_qs.filter(available__gt=0).order_by('-pk')
		total_expense = Expense.objects.filter(created_at__date__gte=dt, created_at__date__lte=date.today(), business=business).aggregate(Sum('cost'))['cost__sum'] 
		depreciation = AccountsFixedAsset.objects.filter(depreciation_value__gt=0, created_at__date__gte=dt, created_at__date__lte=date.today(), business=business).aggregate(Sum('depreciation_value'))['depreciation_value__sum']
		amortization = AccountsFixedAsset.objects.filter(amortization_value__gt=0, created_at__date__gte=dt, created_at__date__lte=date.today(), business=business).aggregate(Sum('amortization_value'))['amortization_value__sum'] 
		takehome = Takehome.objects.filter(created_at__date__gte=dt, created_at__date__lte=date.today(), business=business).aggregate(Sum('salary'))['salary__sum']
		interest_total = Interest.objects.filter(business=business, created_at__date__gte=dt, created_at__date__lte=date.today()).aggregate(Sum('remaining'))['remaining__sum']
		tax_total = Tax.objects.filter(business=business, created_at__date__gte=dt, created_at__date__lte=date.today()).aggregate(total=Sum('remain'))['total']

		if tax_total is None:
				tax_total = 0

		if interest_total is None:
				interest_total = 0


		total_revenue = summary['total_paid']

		if total_revenue is None:
				total_revenue = 0

		if takehome is None:
				takehome = 0
		
		if total_expense is None:
				total_expense = 0

		if depreciation is None:
				depreciation = 0

		if amortization is None:
				amortization = 0		

		nssf = Payroll.objects.filter(tax_rate__icontains='nssf',created_at__date__gte=dt, created_at__date__lte=date.today(), business=business)
		wcf = Payroll.objects.filter(tax_rate__icontains='wcf', created_at__date__gte=dt, created_at__date__lte=date.today(), business=business)
		loan_board = Payroll.objects.filter(tax_rate__icontains='loan board', created_at__date__gte=dt, created_at__date__lte=date.today(), business=business)
		paye_objs = Payroll.objects.all().filter(paye=True, created_at__date__gte=dt, created_at__date__lte=date.today(), business=business)

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

		cogs = 0
		for i in inventories:
			cogs = cogs + i.cogs

		summary['cogs'] = cogs

		total_social_funds = int(nssf_funds) + int(paye_total) + int(loan_board_funds) + int(wcf_funds) 

		tax = tax_total 	
		tax_interest = tax + interest_total

		takehome = takehome - total_social_funds

		print(takehome)

		##### Calculating OPEX #####
		opex = total_expense + takehome + depreciation + amortization
		opex_da = total_expense + takehome 

		##### Calculating EBIT #####
		ebit = total_revenue - (cogs + opex)

		##### Calculating EBITDA #####
		ebitda = total_revenue - (cogs + opex_da)		

		####### Net Income ########
		net_income = ebit - tax_interest

		summary['net_income'] = round(net_income,2)
		summary['social_funds'] = round(total_social_funds,2)
		summary['opex'] = round(opex,2)
		summary['ebit'] = round(ebit,2)
		summary['ebitda'] = round(ebitda,2)
		summary['tax_interest'] = round(tax_interest,2)

		if pdf == '1':
			return income_statement_export_pdf(request, business=business, summary=summary)
		if xl == '1':
				return income_statement_export_excel(request, business=business, summary=summary)			

	elif d == 3:	
		dt = date.today() - timedelta(days=180)
		summary = Sale.objects.filter(branch__business=business, created_at__date__gte=dt, created_at__date__lte=date.today(), status='Completed').all().aggregate(total_paid=Sum('amount_paid'))
		inventory_qs = Inventory.objects.filter(business=business,).annotate(available=F('remain')-F('damage'))			
		inventories = inventory_qs.filter(available__gt=0).order_by('-pk')
		total_expense = Expense.objects.filter(created_at__date__gte=dt, created_at__date__lte=date.today(), business=business).aggregate(Sum('cost'))['cost__sum'] 
		depreciation = AccountsFixedAsset.objects.filter(depreciation_value__gt=0, created_at__date__gte=dt, created_at__date__lte=date.today(), business=business).aggregate(Sum('depreciation_value'))['depreciation_value__sum']
		amortization = AccountsFixedAsset.objects.filter(amortization_value__gt=0, created_at__date__gte=dt, created_at__date__lte=date.today(), business=business).aggregate(Sum('amortization_value'))['amortization_value__sum'] 
		takehome = Takehome.objects.filter(created_at__date__gte=dt, created_at__date__lte=date.today(), business=business).aggregate(Sum('salary'))['salary__sum']
		interest_total = Interest.objects.filter(business=business, created_at__date__gte=dt, created_at__date__lte=date.today()).aggregate(Sum('remaining'))['remaining__sum']
		tax_total = Tax.objects.filter(business=business, created_at__date__gte=dt, created_at__date__lte=date.today()).aggregate(total=Sum('remain'))['total']

		if tax_total is None:
				tax_total = 0

		if interest_total is None:
				interest_total = 0


		total_revenue = summary['total_paid']

		if total_revenue is None:
				total_revenue = 0

		if takehome is None:
				takehome = 0
		
		if total_expense is None:
				total_expense = 0

		if depreciation is None:
				depreciation = 0

		if amortization is None:
				amortization = 0

		nssf = Payroll.objects.filter(tax_rate__icontains='nssf',created_at__date__gte=dt, created_at__date__lte=date.today(), business=business)
		wcf = Payroll.objects.filter(tax_rate__icontains='wcf', created_at__date__gte=dt, created_at__date__lte=date.today(), business=business)
		loan_board = Payroll.objects.filter(tax_rate__icontains='loan board', created_at__date__gte=dt, created_at__date__lte=date.today(), business=business)
		paye_objs = Payroll.objects.all().filter(paye=True, created_at__date__gte=dt, created_at__date__lte=date.today(), business=business)

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

		cogs = 0
		for i in inventories:
			cogs = cogs + i.cogs

		summary['cogs'] = cogs

		total_social_funds = int(nssf_funds) + int(paye_total) + int(loan_board_funds) + int(wcf_funds) 

		tax = tax_total 	
		tax_interest = tax + interest_total

		takehome = takehome - total_social_funds

		print(takehome)

		##### Calculating OPEX #####
		opex = total_expense + takehome + depreciation + amortization
		opex_da = total_expense + takehome 

		##### Calculating EBIT #####
		ebit = total_revenue - (cogs + opex)

		##### Calculating EBITDA #####
		ebitda = total_revenue - (cogs + opex_da)				

		####### Net Income ########
		net_income = ebit - tax_interest

		summary['net_income'] = round(net_income,2)
		summary['social_funds'] = round(total_social_funds,2)
		summary['opex'] = round(opex,2)
		summary['ebit'] = round(ebit,2)
		summary['ebitda'] = round(ebitda,2)
		summary['tax_interest'] = round(tax_interest,2)

		if pdf == '1':
			return income_statement_export_pdf(request, business=business, summary=summary)
		if xl == '1':
				return income_statement_export_excel(request, business=business, summary=summary)			
		
	elif d == 4:	
		dt = date.today() - timedelta(days=365)
		summary = Sale.objects.filter(branch__business=business, created_at__date__gte=dt, created_at__date__lte=date.today(), status='Completed').all().aggregate(total_paid=Sum('amount_paid'))

		inventory_qs = Inventory.objects.filter(business=business,).annotate(available=F('remain')-F('damage'))			
		inventories = inventory_qs.filter(available__gt=0).order_by('-pk')
		total_expense = Expense.objects.filter(created_at__date__gte=dt, created_at__date__lte=date.today(), business=business).aggregate(Sum('cost'))['cost__sum'] 
		depreciation = AccountsFixedAsset.objects.filter(depreciation_value__gt=0, created_at__date__gte=dt, created_at__date__lte=date.today(), business=business).aggregate(Sum('depreciation_value'))['depreciation_value__sum']
		amortization = AccountsFixedAsset.objects.filter(amortization_value__gt=0, created_at__date__gte=dt, created_at__date__lte=date.today(), business=business).aggregate(Sum('amortization_value'))['amortization_value__sum'] 
		takehome = Takehome.objects.filter(created_at__date__gte=dt, created_at__date__lte=date.today(), business=business).aggregate(Sum('salary'))['salary__sum']
		takehome_objs = Takehome.objects.filter(created_at__date__gte=dt, created_at__date__lte=date.today(), business=business)
		interest_total = Interest.objects.filter(business=business, created_at__date__gte=dt, created_at__date__lte=date.today()).aggregate(Sum('remaining'))['remaining__sum']
		tax_total = Tax.objects.filter(business=business, created_at__date__gte=dt, created_at__date__lte=date.today()).aggregate(total=Sum('remain'))['total']

		if tax_total is None:
				tax_total = 0

		if interest_total is None:
				interest_total = 0

		total_revenue = summary['total_paid']

		print(f'Takehome: {takehome}')

		if total_revenue is None:
				total_revenue = 0

		if takehome is None:
				takehome = 0
		
		if total_expense is None:
				total_expense = 0

		if depreciation is None:
				depreciation = 0

		if amortization is None:
				amortization = 0

		nssf = Payroll.objects.filter(tax_rate__icontains='nssf',created_at__date__gte=dt, created_at__date__lte=date.today(), business=business)
		wcf = Payroll.objects.filter(tax_rate__icontains='wcf', created_at__date__gte=dt, created_at__date__lte=date.today(), business=business)
		loan_board = Payroll.objects.filter(tax_rate__icontains='loan board', created_at__date__gte=dt, created_at__date__lte=date.today(), business=business)
		paye_objs = Payroll.objects.filter(paye=True, created_at__date__gte=dt, created_at__date__lte=date.today(), business=business)

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


		cogs = 0
		for i in inventories:
			cogs = cogs + i.cogs

		summary['cogs'] = cogs

		total_social_funds = int(nssf_funds) + int(paye_total) + int(loan_board_funds) + int(wcf_funds) 

		tax = tax_total 	
		tax_interest = tax + interest_total

		takehome = takehome - total_social_funds

		print(takehome)

		##### Calculating OPEX #####
		opex = total_expense + takehome + depreciation + amortization
		opex_da = total_expense + takehome 

		##### Calculating EBIT #####
		ebit = total_revenue - (cogs + opex)

		##### Calculating EBITDA #####
		ebitda = total_revenue - (cogs + opex_da)				

		####### Net Income ########
		net_income = ebit - tax_interest

		summary['net_income'] = round(net_income,2)
		summary['social_funds'] = round(total_social_funds,2)
		summary['opex'] = round(opex,2)
		summary['ebit'] = round(ebit,2)
		summary['ebitda'] = round(ebitda,2)
		summary['tax_interest'] = round(tax_interest,2)

		if pdf == '1':
			return income_statement_export_pdf(request, business=business, summary=summary)
		if xl == '1':
				return income_statement_export_excel(request, business=business, summary=summary)			

	elif d == 5:
		if request.method == 'GET':	
			summary = Sale.objects.filter(branch__business=business, created_at__year=year, status='Completed').all().aggregate(total_paid=Sum('amount_paid'))

			inventory_qs = Inventory.objects.filter(business=business,).annotate(available=F('remain')-F('damage'))			
			inventories = inventory_qs.filter(available__gt=0).order_by('-pk')
			total_expense = Expense.objects.filter(created_at__year=year, business=business).all().aggregate(Sum('cost'))['cost__sum'] 
			depreciation = AccountsFixedAsset.objects.filter(depreciation_value__gt=0, created_at__year=year, business=business).all().aggregate(Sum('depreciation_value'))['depreciation_value__sum']
			amortization = AccountsFixedAsset.objects.filter(amortization_value__gt=0, created_at__year=year, business=business).all().aggregate(Sum('amortization_value'))['amortization_value__sum'] 
			takehome = Takehome.objects.filter(created_at__year=year, business=business).aggregate(Sum('salary'))['salary__sum']
			interest_total = Interest.objects.filter(business=business, created_at__year=year).aggregate(Sum('remaining'))['remaining__sum']
			tax_total = Tax.objects.filter(business=business, created_at__year=year).aggregate(total=Sum('remain'))['total']

			if tax_total is None:
					tax_total = 0

			if interest_total is None:
					interest_total = 0

			total_revenue = summary['total_paid']


			if total_revenue is None:
					total_revenue = 0

			if takehome is None:
					takehome = 0
			
			if total_expense is None:
					total_expense = 0

			if depreciation is None:
					depreciation = 0

			if amortization is None:
					amortization = 0

			opex = total_expense + takehome + depreciation + amortization

			cogs = 0
			for i in inventories:
				cogs = cogs + i.cogs

			summary['cogs'] = cogs
	
			ebit = total_revenue - (cogs + opex)

			nssf = Payroll.objects.filter(tax_rate__icontains='nssf', created_at__year=year, business=business)
			wcf = Payroll.objects.filter(tax_rate__icontains='wcf', created_at__year=year, business=business)
			loan_board = Payroll.objects.filter(tax_rate__icontains='loan board', created_at__year=year, business=business)
			paye_objs = Payroll.objects.filter(paye=True, created_at__year=year, business=business)

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

			cogs = 0
			for i in inventories:
				cogs = cogs + i.cogs

			summary['cogs'] = cogs

			total_social_funds = int(nssf_funds) + int(paye_total) + int(loan_board_funds) + int(wcf_funds) 

			tax = tax_total 	
			tax_interest = tax + interest_total

			takehome = takehome - total_social_funds


			##### Calculating OPEX #####
			opex = total_expense + takehome + depreciation + amortization
			opex_da = total_expense + takehome 

			##### Calculating EBIT #####
			ebit = total_revenue - (cogs + opex)

			##### Calculating EBITDA #####
			ebitda = total_revenue - (cogs + opex_da)				

			####### Net Income ########
			net_income = ebit - tax_interest

			summary['net_income'] = round(net_income,2)
			summary['social_funds'] = round(total_social_funds,2)
			summary['opex'] = round(opex,2)
			summary['ebit'] = round(ebit,2)
			summary['ebitda'] = round(ebitda,2)
			summary['tax_interest'] = round(tax_interest,2)

			if pdf == '1':
				return income_statement_export_pdf(request, business=business, summary=summary)
			if xl == '1':
					return income_statement_export_excel(request, business=business, summary=summary)				
			
	context = {
		'business':business,
		'summary':summary,
		'd':d,
		'year':year,
	}
	return render(request, 'income_statement.html', context)


####### Balance Sheet ########
@finance_report_required
@login_required
def balance_sheet(request, *args, **kwargs):
	pdf = request.GET.get('pdf')
	xl = request.GET.get('xl')
	id = kwargs.get('id')
	business = Business.objects.filter(id=id).first()
	interest_total = Interest.objects.filter(business=business).aggregate(Sum('remaining'))['remaining__sum']
	tax_total = Tax.objects.filter(business=business,).aggregate(total=Sum('remain'))['total']
	liabilities_total = Liability.objects.filter(business=business).aggregate(Sum('cost'))['cost__sum'] 
	assets_value = AccountsFixedAsset.objects.filter(business=business).aggregate(Sum('value'))['value__sum'] 

	if tax_total is None:
			tax_total = 0

	if interest_total is None:
			interest_total = 0

	if liabilities_total is None:
			liabilities_total = 0			

	if assets_value is None:
		assets_value = 0		

	liabilities = interest_total + tax_total + liabilities_total

	assets = assets_value
	
	equity = assets - liabilities

	if pdf == '1':
			return balance_sheet_export_pdf(request, business=business, assets=assets, liabilities=liabilities, equity=equity)
	if xl == '1':
			return balance_sheet_export_excel(request, business=business, assets=assets, liabilities=liabilities, equity=equity)		

	context = {
		'business':business,
		'assets': assets,
		'liabilities': round(liabilities,2),
		'equity' : round(equity, 2),
	}
	template_name = 'balance_sheet.html'
	return render(request, template_name, context)	


@finance_report_required
@login_required
def cashflow_time(request, *args, **kwargs):
	id = kwargs.get('id')
	business = Business.objects.filter(id=id).first()

	sales = Sale.objects.filter(branch__business=business).annotate(particular=Value("Sale",output_field=CharField()),amount=F('amount_paid'), flow=Value("IN",output_field=CharField())).values()
	purchases = PurchaseOrder.objects.filter(business=business).annotate(particular=Value("Purchase Order",output_field=CharField()),amount=Sum('purchase_order_list__total'), flow=Value("OUT",output_field=CharField())).values()
	local_purchases = LocalPurchaseOrder.objects.filter(business=business).annotate(particular=Value("Local Purchase Order",output_field=CharField()),amount=Sum('local_purchase_order_list__total'), flow=Value("OUT",output_field=CharField())).values()
	expenses = Expense.objects.all().annotate(particular=Value("Expense",output_field=CharField()),amount=F('cost'), flow=Value("OUT",output_field=CharField())).values()

	cashflow = list(sales) + list(purchases) + list(local_purchases) + list(expenses)

	def myFunc(e):
		return e['created_at']
	cashflow.sort(reverse=True,key=myFunc)
		
	context = {
		'business':business,
		'cashflow':cashflow,
	}
	return render(request, 'cashflow_time.html', context)


@finance_report_required
@login_required
def cashflow(request, *args, **kwargs):
	id = kwargs.get('id')
	pdf = request.GET.get('pdf')
	xl = request.GET.get('xl')
	fr = request.GET.get('fr')
	to = request.GET.get('to')
	business = Business.objects.filter(id=id).first()

	if request.method == 'GET':	
		cashflow = CheckAccount.objects.filter(business=business, created_at__date__gte=fr, created_at__date__lte=to)
	
	if pdf == '1':
			return cashbook_export_pdf(request, business=business, cashflow=cashflow)

	if xl == '1':
			return cashbook_export_excel(request, business=business, cashflow=cashflow)

	context = {
		'business':business,
		'cashflow':cashflow,	
		'fr':fr,
		'to':to,
	}
	return render(request, 'cashflow.html', context)


@finance_report_required
@login_required
def trial_balance_time(request, *args, **kwargs):
	id = kwargs.get('id')
	business = Business.objects.filter(id=id).first()
		
	context = {
		'business':business,
	}
	return render(request, 'trial-balance-time.html', context)

