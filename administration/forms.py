from django import forms
from .models import *


class BusinessModelForm(forms.ModelForm):
	class Meta:
		model = Business
		fields = '__all__'


class BranchModelForm(forms.ModelForm):
	class Meta:
		model = Branch
		fields = '__all__'


class DepartmentModelForm(forms.ModelForm):
	class Meta:
		model = Department
		fields = '__all__'


class LoginForm(forms.Form):
		username = forms.CharField(label='', widget=forms.TextInput(attrs={'class':'form-control rounded-pill', 'placeholder':'Username'}))
		password = forms.CharField(label='', widget=forms.PasswordInput(attrs={'class':'form-control rounded-pill', 'placeholder':'Password'}))