from django import forms
from .models import *


class EmployeeModelForm(forms.ModelForm):
	class Meta:
		model = Employee
		fields = '__all__'
		exclude = ['id_no','user']