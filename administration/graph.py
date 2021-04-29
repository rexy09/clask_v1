from _datetime import date, timedelta
from django.db.models import Sum, F
from business.models import Product, Sale, Expense, Inventory
from .models import *



def sales_graph_data(*args, **kwargs):
	business = kwargs.get('business')
	# Date list
	base = date.today()
	date_list = [base - timedelta(days=x) for x in range(7)]
	date_list.reverse()
	
	# Data
	sales = []
	for d in date_list:
		business_dic = {'date':d.strftime('%d-%m-%Y')}			
		for b in business:
			sale = Sale.objects.filter(branch__business=b, created_at__date=d, status='Completed').aggregate(total_sales=Sum('amount_paid'))['total_sales']
			business_dic.update({b.name:sale if sale != None else 0})

		sales.append(business_dic)
	return sales



def expense_graph_data(*args, **kwargs):
	business = kwargs.get('business')

	# Date Range	
	dt = date.today() - timedelta(days=30)
	
	# Data
	expenses = []
	for b in business:
		expense = Expense.objects.filter(created_at__date__gte=dt, created_at__date__lte=date.today(), business=b).aggregate(Sum('cost'))['cost__sum'] 			
		business_dic = {'business':b.name, 'value':expense if expense != None else 0}

		expenses.append(business_dic)

	return expenses



def stock_graph_data(*args, **kwargs):
	business = kwargs.get('business')	
	# Data
	stock = []
	for b in business:
		inventory_qs = Inventory.objects.filter(business=b, exist=True).annotate(available=F('remain')-F('damage'))
		inventory = inventory_qs.aggregate(Sum('available'))['available__sum']

		business_dic = {'business':b.name, 'value':inventory if inventory != None else 0}

		stock.append(business_dic)
	return stock
