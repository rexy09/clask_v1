from django.db import models
from django_countries.fields import CountryField
from administration.models import *
from django.contrib.auth.models import User


class Employee(models.Model):

	GENDER = [
		('Male', 'Male'),
		('Female', 'Female'),
		]

	MARITAL_STATUS = [
		('Single', 'Single'),
		('Married', 'Married'),
		]

	EMPLOYMENT_TYPE = [
		('Full-time','Full-time'),
		('Freelancer','Freelancer'),
		]

	INTERVALS = [
        ('Weeks', 'Weeks'),
        ('Months', 'Months'),
        ('Years', 'Years'),
    ]


	POSITIONS = [	
    	('CEO','CEO'),
		('Sales Manager', 'Sales Manager'),
    	('Sales Officer','Sales Officer'),
    	('Secretary','Secretary'),
		('Marketing Manager', 'Marketing Manager'),
		('Marketing Officer','Marketing Officer'),
    	('Accountant', 'Accountant'),
    	('Financial Manager', 'Financial Manager'),
		('Managing Director','Managing Director'),
    	('Director','Director'),
		('Branch Manager', 'Branch Manager'),
    	('Operational Manager', 'Operational Manager'),
		('Procurement Manager', 'Procurement Manager'),
    	('Procurement Officer','Procurement Officer'),
    	('Store Officer','Store Officer'),
    	('Assistant Store Officer','Assistant Store Officer'),
    	('Administrative Assistant','Administrative Assistant'),
    	('Operations Manager','Operations Manager'),
    	('Operations Officer','Operations Officer'),
    	('Human Resource Manager','Human Resource Manager'),
    	('Human Resource Officer','Human Resource Officer'),
    ]

	business = models.ForeignKey(Business, related_name="business_employee", on_delete=models.CASCADE)
	full_name = models.CharField(max_length=50)
	birth_date = models.DateField(blank=True, null=True)
	gender = models.CharField(max_length=10, choices=GENDER)
	marital_status = models.CharField(max_length=10, choices=MARITAL_STATUS)
	image = models.ImageField(blank=True, null=True, upload_to="profile_picture/")
	signature = models.ImageField(upload_to="signatures/")
	email = models.EmailField(max_length=254, blank=True, null=True)
	work_phone = models.CharField(max_length=15, help_text="+255 format")
	mobile_phone = models.CharField(max_length=15, help_text="+255 format",blank=True, null=True)
	address = models.CharField(max_length=50, blank=True, null=True)
	nationality = CountryField()
	country = CountryField()
	city = models.CharField(max_length=50, blank=True, null=True)
	postal_code = models.CharField(max_length=50, blank=True, null=True)
	employment_type = models.CharField(max_length=50, choices=EMPLOYMENT_TYPE, blank=True, null=True)
	department = models.ForeignKey(Department, related_name='employee_department', on_delete=models.CASCADE)
	branch = models.ForeignKey(Branch, blank=True, null=True, related_name='employee_branch' ,on_delete=models.CASCADE)
	position = models.CharField(max_length=100, choices=POSITIONS)
	other_position = models.CharField(max_length=100, null=True, blank=True)
	id_no = models.CharField(max_length=100, null=True, blank=True)
	salary = models.PositiveIntegerField()
	starting_date = models.DateField()
	contract_period = models.PositiveIntegerField()
	period = models.CharField(max_length=10, choices=INTERVALS, null=True, blank=True)	
	nida = models.PositiveIntegerField(unique=True,null=True, blank=True)
	performance = models.PositiveIntegerField()
	user = models.OneToOneField(User, related_name='user_employee', on_delete=models.SET_NULL, null=True, blank=True)
	updated_at = models.DateTimeField(auto_now=True)
	created_at = models.DateTimeField(auto_now_add=True)	


	def __str__(self):
		return self.full_name
