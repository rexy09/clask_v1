from django.db import models
from django.contrib.auth.models import User
from django.db.models import Avg, F, FloatField, Sum
from administration.models import *
from human_resource.models import *
from multiselectfield import MultiSelectField
from django.urls import reverse

# Create your models here.


class Product(models.Model):
	CURRENCY_CHOICES = (
	('TZS', 'TZS'),
	('USD', 'USD') 
	)
	business = models.ForeignKey(Business, related_name="product", on_delete=models.CASCADE)
	name = models.CharField(max_length=256)
	product_code = models.CharField(max_length=100, blank=True, null=True)
	unit = models.CharField(max_length=50,)
	min_quantity = models.PositiveIntegerField(default=0)
	currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES)
	sell_price = models.DecimalField(max_digits=19, decimal_places=2)
	updated_at = models.DateTimeField(auto_now=True)
	created_at = models.DateTimeField(auto_now_add=True) 
	
	def __str__(self):
		return self.name

	@property
	def average_cost(self):
		return self.inventory_product.filter(exist=True).aggregate(product_cost=Avg('product_cost'))

	@property
	def quantity(self):
		try:
			available = self.inventory_product.filter(exist=True).aggregate(remain=Sum('remain'))['remain'] - self.inventory_product.filter(exist=True).aggregate(damage=Sum('damage'))['damage']
		except:
			available = 0
		return available

	@property
	def worth(self):		
		try:
			available = self.inventory_product.filter(exist=True).aggregate(remain=Sum('remain'))['remain'] - self.inventory_product.filter(exist=True).aggregate(damage=Sum('damage'))['damage']
			worth = available * self.sell_price
		except:
			worth = 0
		return worth

	
	def get_absolute_url(self):
		return reverse("business:stock_list", kwargs={"id": self.business.id}) 	
			

	class Meta:
		verbose_name = 'Product'
		verbose_name_plural = 'Products'


class Inventory(models.Model):
	CURRENCY_CHOICES = (
	('TZS', 'TZS'),
	('USD', 'USD') 
	)
	business = models.ForeignKey(Business, related_name="inventory", on_delete=models.CASCADE)
	product = models.ForeignKey(Product, related_name="inventory_product", on_delete=models.CASCADE)
	quantity = models.PositiveIntegerField()
	remain = models.PositiveIntegerField()
	damage = models.PositiveIntegerField(default=0)    
	currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES)
	product_cost = models.DecimalField(max_digits=19, decimal_places=2)
	exist = models.BooleanField(default=True)
	updated_at = models.DateTimeField(auto_now=True)
	created_at = models.DateTimeField(auto_now_add=True) 
	
	
	def __str__(self):
		available = self.remain - self.damage
		return "Product: {0}, Avaible: {1}, Cost: {2} {4}, Sell: {3} {4}".format(self.product.name, available, self.product_cost, self.product.sell_price,  self.currency)

	@property
	def cogs(self):
		try:
			amount = ((self.product_cost * self.quantity)*(self.quantity + self.damage))/(self.quantity - self.remain)
		except:
			amount = 0
		
		return amount

	@property
	def get_available(self):
		available = self.remain - self.damage
		return available

	class Meta:
		verbose_name = 'Inventory'
		verbose_name_plural = 'Inventories'


class Customer(models.Model):

	CATEGORY = [
		('Loyal','Loyal'),
		('Normal','Normal'),
	]

	GENDER = (
		('M','Male'),
		('F','Female'),
	)

	business = models.ForeignKey(Business, related_name="customer", on_delete=models.CASCADE)
	full_name = models.CharField(max_length=100)
	company = models.CharField(max_length=100, blank=True, null=True)
	contact = models.CharField(max_length=15, help_text="+255 format")
	gender = models.CharField(max_length=10, choices=GENDER)
	email = models.EmailField(max_length=254, blank=True, null=True)
	address = models.CharField(max_length=254)
	category = models.CharField(choices=CATEGORY, default=CATEGORY[1][0], max_length=20)
	points = models.PositiveIntegerField(default=0)
	updated_at = models.DateTimeField(auto_now=True)
	created_at = models.DateTimeField(auto_now_add=True) 

	
	def __str__(self):
		return "{0} ({1})".format(self.full_name, self.contact)

	class Meta:
		verbose_name = 'Customer'
		verbose_name_plural = 'Customers'


class Sale(models.Model):
	DISCOUNT = (
		('%','%'),
		('flat','Flat Rate')
	)
	TAX = (
		('%','%'),
	)
	STATUS = (
		('Completed', 'Completed'),
		('Awaiting Payment', 'Awaiting Payment'),
	)
	branch = models.ForeignKey(Branch, related_name="sale", on_delete=models.CASCADE)
	inventory = models.ForeignKey(Inventory, related_name="sale_inventory", on_delete=models.CASCADE)
	customer = models.ForeignKey(Customer, related_name="sale_customer", on_delete=models.SET_NULL, blank=True, null=True)
	user = models.ForeignKey(User, related_name="sale_user", on_delete=models.SET_NULL,blank=True, null=True)
	quantity = models.PositiveIntegerField()
	price = models.DecimalField(max_digits=19, decimal_places=2)
	total = models.DecimalField(max_digits=19, decimal_places=2)
	discount_unit = models.CharField(max_length=10, choices=DISCOUNT, default='flat')
	discount = models.PositiveIntegerField(default=0)
	tax_unit = models.CharField(max_length=10, choices=TAX, default='%')
	tax = models.PositiveIntegerField(default=0)
	amount_paid = models.DecimalField(max_digits=19, decimal_places=2)
	profit = models.DecimalField(max_digits=19, decimal_places=2)
	order_no = models.CharField(max_length=100, unique=True)
	note = models.TextField(blank=True, null=True)    
	status = models.CharField(max_length=30, choices=STATUS)
	updated_at = models.DateTimeField(auto_now=True)
	created_at = models.DateTimeField(auto_now_add=True) 

	def __str__(self):
		return self.inventory.product.name

	class Meta:
		verbose_name = 'Sale'
		verbose_name_plural = 'Sales'


class Expense(models.Model):

	CATEGORIES = [
		('Advertising','Advertising'),
		('Contractors','Contractors'),
		('Rent or Lease','Rent or Lease'),
		('Travel','Travel'),
		('Education and Training','Education and Training'),
		('Professional Services','Professional Services'),
		('Utilities','Utilities'),
		('Other Expenses','Other Expenses'),
	]
	business = models.ForeignKey(Business, related_name="business_expense", on_delete=models.CASCADE)
	name = models.CharField(max_length=100)
	details = models.TextField(null=True, blank=True)
	category = models.CharField(max_length=100  , choices=CATEGORIES)
	date = models.DateField()
	cost = models.PositiveIntegerField()
	updated_at = models.DateTimeField(auto_now=True)
	created_at = models.DateTimeField(auto_now_add=True) 

	def __str__(self):
		return self.name


class Payroll(models.Model):

	TAXES_RATE = [
		('nssf','NSSF'),
		('wcf','WCF'),
		('loan board','HESLB'),
	]
	business = models.ForeignKey(Business, related_name="business_payroll", on_delete=models.CASCADE)
	employee = models.ForeignKey(Employee, related_name='employee_payroll', on_delete=models.SET_NULL, blank=True, null=True)
	tax_rate = MultiSelectField(choices=TAXES_RATE, null=True, blank=True)
	bonus = models.PositiveIntegerField(default=0)
	overtime = models.PositiveIntegerField(default=0)
	deduction = models.PositiveIntegerField(default=0)
	sdl = models.BooleanField(default=False)
	paye = models.BooleanField(default=False)
	sdl_amount = models.PositiveIntegerField(default=0, null=True, blank=0)
	paye_amount = models.PositiveIntegerField(default=0, null=True, blank=0)
	tax_amount = models.PositiveIntegerField(default=0, null=True, blank=0)
	loan_debt = models.PositiveIntegerField(default=0, null=True, blank=0)
	updated_at = models.DateTimeField(auto_now=True)
	created_at = models.DateTimeField(auto_now_add=True) 

	def __str__(self):
		return self.employee.full_name


class Takehome(models.Model):
	business = models.ForeignKey(Business, related_name="business_takehome", on_delete=models.CASCADE)
	payroll = models.OneToOneField(Payroll, related_name='takehome_payroll', on_delete=models.CASCADE)
	salary = models.PositiveIntegerField()    
	updated_at = models.DateTimeField(auto_now=True)
	created_at = models.DateTimeField(auto_now_add=True) 

	def __str__(self):
		return self.payroll.employee.full_name



class Interest(models.Model):
	business = models.ForeignKey(Business, related_name="business_interest", on_delete=models.CASCADE)
	lender = models.CharField(max_length=150)
	loan_date = models.DateField()
	principal = models.DecimalField(max_digits=19, decimal_places=2)
	rate = models.FloatField()
	time = models.PositiveIntegerField()
	remaining = models.DecimalField(max_digits=19, decimal_places=2)
	debt = models.BooleanField(default=True)
	repayment = models.DecimalField(max_digits=19, decimal_places=2)
	updated_at = models.DateTimeField(auto_now=True)
	created_at = models.DateTimeField(auto_now_add=True) 

	def __str__(self):
		return self.lender
	
	class Meta:
		ordering = ["-id"]


class FixedAsset(models.Model):
	
	TYPES =[
		('tangible','Tangible'),
		('intangible','Intangible'),
	]


	INTERVALS = [
		('weeks', 'Weeks'),
		('months', 'Months'),
		('years', 'Years'),
	]

	PERIOD = [
		('months', 'Months'),
		('years', 'Years'),
	]

	business = models.ForeignKey(Business, related_name="business_asset", on_delete=models.CASCADE)
	name = models.CharField(max_length=150)
	asset_type = models.CharField(max_length=100, choices=TYPES)
	quantity = models.PositiveIntegerField()
	location = models.ForeignKey(Branch, related_name="fixed_asset_branch", on_delete=models.CASCADE)
	date_bought = models.DateField()
	usage_period_estimation = models.PositiveIntegerField()
	usage_period_intervals = models.CharField(max_length=10, choices=PERIOD, null=True, blank=True)
	maintanance_schedule = models.PositiveIntegerField()
	maintanance_schedule_period = models.CharField(max_length=10, choices=INTERVALS, null=True, blank=True)
	buying_price = models.PositiveIntegerField()
	maintanance_fee = models.PositiveIntegerField()
	depreciation_value = models.PositiveIntegerField(default=0, blank=True, null=True)
	depreciation_percent = models.FloatField(default=0, blank=True, null=True)	
	amortization_value = models.PositiveIntegerField(default=0, blank=True, null=True)
	amortization_percent = models.FloatField(default=0, blank=True, null=True)	
	value = models.IntegerField(default=0, null=True, blank=True)	
	updated_at = models.DateTimeField(auto_now=True)
	created_at = models.DateTimeField(auto_now_add=True)            


	def __str__(self):
		return self.name



class FixedAssetCost(models.Model):
	asset = models.ForeignKey(FixedAsset, related_name="fixed_asset_cost", on_delete=models.CASCADE)
	cost = models.PositiveIntegerField()
	updated_at = models.DateTimeField(auto_now=True)
	created_at = models.DateTimeField(auto_now_add=True) 

	def __str__(self):
		return self.asset.name


class Supplier(models.Model):
	business = models.ForeignKey(Business, related_name="supplier", on_delete=models.CASCADE)
	name = models.CharField(max_length=100)
	updated_at = models.DateTimeField(auto_now=True)
	created_at = models.DateTimeField(auto_now_add=True)   

	class Meta:
		ordering = ["name"]
		verbose_name = ("Supplier")
		verbose_name_plural = ("Suppliers")

	def __str__(self):
		return self.name


class PurchaseOrder(models.Model):
	business = models.ForeignKey(Business, related_name="purchase_order", on_delete=models.CASCADE)
	supplier = models.ForeignKey(Supplier, related_name="purchase_order_supplier", on_delete=models.SET_NULL, null=True, blank=True)
	employee = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
	delivery = models.ForeignKey(Branch, related_name="purchase_order_branch", on_delete=models.CASCADE)
	po_no = models.CharField(max_length=100, unique=True)
	shipping = models.DecimalField(max_digits=19, decimal_places=2)
	customs = models.DecimalField(max_digits=19, decimal_places=2)
	tax = models.DecimalField(max_digits=19, decimal_places=2)
	published = models.BooleanField(default=False)
	authorized = models.BooleanField(default=False)
	updated_at = models.DateTimeField(auto_now=True)
	created_at = models.DateTimeField(auto_now_add=True)    

	@property
	def positive_check_list(self):
		return self.purchase_order_check.filter(checked=True)
	
	@property
	def positive_approve_list(self):
		return self.purchase_order_approve.filter(approved=True) 

	@property
	def positive_authorize_list(self):
		return self.purchase_order_authorize.filter(authorized=True) 	

	@property
	def total(self):
		return self.purchase_order_list.all().aggregate(total=Sum('total'))['total'] + self.shipping + self.customs + self.tax	

	def get_absolute_url(self):
		return reverse("business:view_purchase_order", kwargs={"id": self.pk})

	class Meta:
		ordering = ["-id"]
		verbose_name = ("Purchase Order")
		verbose_name_plural = ("Purchase Orders")

	def __str__(self):
		return self.po_no

	
class PurchaseOrderList(models.Model):
	purchase_order = models.ForeignKey(PurchaseOrder, related_name="purchase_order_list", on_delete=models.CASCADE)
	description = models.CharField(max_length=256)
	unit = models.CharField(max_length=100)
	quantity = models.IntegerField()
	price = models.DecimalField(max_digits=19, decimal_places=2)
	total = models.DecimalField(max_digits=19, decimal_places=2)
	updated_at = models.DateTimeField(auto_now=True)
	created_at = models.DateTimeField(auto_now_add=True)     
	

	class Meta:
		verbose_name = ("Purchase Order List")
		verbose_name_plural = ("Purchase Order List")

	def __str__(self):
		return self.description


class PurchaseOrderAuthorize(models.Model):    
	purchase_order = models.ForeignKey(PurchaseOrder, related_name="purchase_order_authorize", on_delete=models.CASCADE)
	supervisor = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
	authorized = models.BooleanField(default=False)
	updated_at = models.DateTimeField(auto_now=True)
	created_at = models.DateTimeField(auto_now_add=True)     

	class Meta:
		ordering = ["-id"]
		verbose_name = "Purchase Order Authorize"
		verbose_name_plural = "Purchase Orders Authorize"


class PurchaseOrderApprove(models.Model):    
	purchase_order = models.ForeignKey(PurchaseOrder, related_name="purchase_order_approve", on_delete=models.CASCADE)
	supervisor = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
	approved = models.BooleanField(default=False)
	updated_at = models.DateTimeField(auto_now=True)
	created_at = models.DateTimeField(auto_now_add=True)     

	class Meta:
		ordering = ["-id"]
		verbose_name = "Purchase Order Approve"
		verbose_name_plural = "Purchase Orders Approve"


class PurchaseOrderCheck(models.Model):
	purchase_order = models.ForeignKey(PurchaseOrder, related_name="purchase_order_check", on_delete=models.CASCADE)
	supervisor = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
	checked = models.BooleanField(default=False)
	updated_at = models.DateTimeField(auto_now=True)
	created_at = models.DateTimeField(auto_now_add=True)     

	class Meta:
		ordering = ["-id"]
		verbose_name = "Purchase Order Check"
		verbose_name_plural = "Purchase Orders Check"


class LocalPurchaseOrder(models.Model):
	business = models.ForeignKey(Business, related_name="local_purchase_order", on_delete=models.CASCADE)
	supplier = models.ForeignKey(Supplier, related_name="local_purchase_order_supplier", on_delete=models.SET_NULL, null=True, blank=True)
	employee = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
	delivery = models.ForeignKey(Branch, related_name="local_purchase_order_branch", on_delete=models.CASCADE)
	lpo_no = models.CharField(max_length=100, unique=True)
	published = models.BooleanField(default=False)
	authorized = models.BooleanField(default=False)
	updated_at = models.DateTimeField(auto_now=True)
	created_at = models.DateTimeField(auto_now_add=True)    

	@property
	def positive_check_list(self):
		return self.local_purchase_order_check.filter(checked=True)
	
	@property
	def positive_approve_list(self):
		return self.local_purchase_order_approve.filter(approved=True) 

	@property
	def positive_authorize_list(self):
		return self.local_purchase_order_authorize.filter(authorized=True) 	

	@property
	def total(self):
		return self.local_purchase_order_list.all().aggregate(total=Sum('total'))['total']

	def get_absolute_url(self):
		return reverse("business:view_local_purchase_order", kwargs={"id": self.pk}) 
	

	class Meta:
		ordering = ["-id"]
		verbose_name = ("Local Purchase Order")
		verbose_name_plural = ("Local Purchase Orders")

	def __str__(self):
		return self.lpo_no

 
class LocalPurchaseOrderList(models.Model):
	local_purchase_order = models.ForeignKey(LocalPurchaseOrder, related_name="local_purchase_order_list", on_delete=models.CASCADE)
	description = models.CharField(max_length=256)
	unit = models.CharField(max_length=100)
	quantity = models.IntegerField()
	price = models.DecimalField(max_digits=19, decimal_places=2)
	total = models.DecimalField(max_digits=19, decimal_places=2)
	updated_at = models.DateTimeField(auto_now=True)
	created_at = models.DateTimeField(auto_now_add=True)     
	

	class Meta:
		verbose_name = ("Local Purchase Order List")
		verbose_name_plural = ("Local Purchase Order List")

	def __str__(self):
		return self.description


class LocalPurchaseOrderAuthorize(models.Model):    
	local_purchase_order = models.ForeignKey(LocalPurchaseOrder, related_name="local_purchase_order_authorize", on_delete=models.CASCADE)
	supervisor = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
	authorized = models.BooleanField(default=False)
	updated_at = models.DateTimeField(auto_now=True)
	created_at = models.DateTimeField(auto_now_add=True)     

	class Meta:
		ordering = ["-id"]
		verbose_name = "Local Purchase Order Authorize"
		verbose_name_plural = "Local Purchase Orders Authorize"


class LocalPurchaseOrderApprove(models.Model):    
	local_purchase_order = models.ForeignKey(LocalPurchaseOrder, related_name="local_purchase_order_approve", on_delete=models.CASCADE)
	supervisor = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
	approved = models.BooleanField(default=False)
	updated_at = models.DateTimeField(auto_now=True)
	created_at = models.DateTimeField(auto_now_add=True)     

	class Meta:
		ordering = ["-id"]
		verbose_name = "Local Purchase Order Approve"
		verbose_name_plural = "Local Purchase Orders Approve"


class LocalPurchaseOrderCheck(models.Model):
	local_purchase_order = models.ForeignKey(LocalPurchaseOrder, related_name="local_purchase_order_check", on_delete=models.CASCADE)
	supervisor = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
	checked = models.BooleanField(default=False)
	updated_at = models.DateTimeField(auto_now=True)
	created_at = models.DateTimeField(auto_now_add=True)     

	class Meta:
		ordering = ["-id"]
		verbose_name = "Local Purchase Order  Check"
		verbose_name_plural = "Local Purchase Orders Checks"
	


class AccountsFixedAsset(models.Model):

	TYPES =[
		('tangible','Tangible'),
		('intangible','Intangible'),
	]


	INTERVALS = [
		('weeks', 'Weeks'),
		('months', 'Months'),
		('years', 'Years'),
	]

	PERIOD = [
		('months', 'Months'),
		('years', 'Years'),
	]

	business = models.ForeignKey(Business, related_name="business_fixed_asset", on_delete=models.CASCADE)
	name = models.CharField(max_length=150)
	cost = models.PositiveIntegerField()
	quantity = models.PositiveIntegerField()
	location = models.ForeignKey(Branch, related_name="accounts_fixed_asset_branch", on_delete=models.CASCADE)	
	asset_type = models.CharField(max_length=100, choices=TYPES)
	date_bought = models.DateField()
	usage_period_estimation = models.PositiveIntegerField()
	usage_period_intervals = models.CharField(max_length=10, choices=PERIOD, null=True, blank=True)
	maintanance_schedule = models.PositiveIntegerField()
	maintanance_schedule_period = models.CharField(max_length=10, choices=INTERVALS, null=True, blank=True)	
	maintanance_fee = models.PositiveIntegerField()
	depreciation_value = models.PositiveIntegerField(default=0, blank=True, null=True)
	depreciation_percent = models.FloatField(default=0, blank=True, null=True)
	amortization_value = models.PositiveIntegerField(default=0, blank=True, null=True)
	amortization_percent = models.FloatField(default=0, blank=True, null=True)
	value = models.IntegerField(default=0, null=True, blank=True)	
	updated_at = models.DateTimeField(auto_now=True)
	created_at = models.DateTimeField(auto_now_add=True)  


	def __str__(self):
		return self.name       


class AccountsCurrentAsset(models.Model):
	business = models.ForeignKey(Business, related_name="business_current_asset", on_delete=models.CASCADE)
	name = models.CharField(max_length=150)
	cost = models.PositiveIntegerField()
	updated_at = models.DateTimeField(auto_now=True)
	created_at = models.DateTimeField(auto_now_add=True)    

	def __str__(self):
		return self.name  
		

class Liability(models.Model):
	business = models.ForeignKey(Business, related_name="business_liability", on_delete=models.CASCADE)
	name = models.CharField(max_length=150)
	cost = models.PositiveIntegerField()
	updated_at = models.DateTimeField(auto_now=True)
	created_at = models.DateTimeField(auto_now_add=True)    

	def __str__(self):
		return self.name          

	class Meta:
		verbose_name = 'Liability'
		verbose_name_plural = 'Liabilities'        


class Total(models.Model):
	business = models.ForeignKey(Business, related_name="business_total", on_delete=models.CASCADE)
	bonus = models.PositiveIntegerField(default=0)
	overtime = models.PositiveIntegerField(default=0)
	deduction = models.PositiveIntegerField(default=0)
	paye = models.PositiveIntegerField(default=0)
	nssf = models.PositiveIntegerField(default=0)
	wcf = models.PositiveIntegerField(default=0)
	loan_board = models.PositiveIntegerField(default=0)
	opex = models.PositiveIntegerField(default=0)
	updated_at = models.DateTimeField(auto_now=True)
	created_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return f'{self.id}'         


class CheckAccount(models.Model):
	business = models.ForeignKey(Business, related_name="check_account", on_delete=models.CASCADE)
	employee = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
	description = models.TextField(null=True, blank=True)
	debit = models.DecimalField(max_digits=19, decimal_places=2, null=True, blank=True)
	credit = models.DecimalField(max_digits=19, decimal_places=2, null=True, blank=True)
	balance = models.DecimalField(max_digits=19, decimal_places=2)
	updated_at = models.DateTimeField(auto_now=True)
	created_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return f"{self.balance}"


class SavingAccount(models.Model):
	business = models.ForeignKey(Business, related_name="saving_account", on_delete=models.CASCADE)
	employee = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
	description = models.TextField(null=True, blank=True)
	debit = models.DecimalField(max_digits=19, decimal_places=2)
	credit = models.DecimalField(max_digits=19, decimal_places=2)
	balance = models.DecimalField(max_digits=19, decimal_places=2)
	updated_at = models.DateTimeField(auto_now=True)
	created_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return f"{self.balance}"			


class Transaction(models.Model):

	ACCOUNTS = [
	('Check Account','Check Account'),
	('Saving Account','Saving Account'),
	]

	amount = models.PositiveIntegerField()
	transaction_from = models.CharField(max_length=100, choices=ACCOUNTS)
	transaction_to = models.CharField(max_length=100, choices=ACCOUNTS)
	updated_at = models.DateTimeField(auto_now=True)
	created_at = models.DateTimeField(auto_now_add=True)


	def __str__(self):
		return f"{self.transaction_from}"	


class Tax(models.Model):
	business = models.ForeignKey(Business, related_name="tax", on_delete=models.CASCADE)
	name = models.CharField(max_length=100)
	authority = models.CharField(max_length=100)
	amount = models.DecimalField(max_digits=19, decimal_places=2)
	remain = models.DecimalField(max_digits=19, decimal_places=2)
	updated_at = models.DateTimeField(auto_now=True)
	created_at = models.DateTimeField(auto_now_add=True)
	
	def __str__(self):
		return self.name

	class Meta:
		verbose_name = 'Tax'
		verbose_name_plural = 'Taxes'


class Loan(models.Model):
	business = models.ForeignKey(Business, related_name="business_loan", on_delete=models.CASCADE)
	employee = models.ForeignKey(Employee, related_name='employee_loan', on_delete=models.SET_NULL, blank=True, null=True)
	loan_amount = models.PositiveIntegerField(default=0)
	remaining_debt = models.PositiveIntegerField(default=0)
	amount_paid = models.PositiveIntegerField(default=0)
	loan_date = models.DateField()
	due_date = models.DateField()
	debt = models.BooleanField(default=False)
	updated_at = models.DateTimeField(auto_now=True)
	created_at = models.DateTimeField(auto_now_add=True)				

	def __str__(self):
		return self.employee.full_name

	class Meta:
		verbose_name = 'Loan'
		verbose_name_plural = 'Loans'	