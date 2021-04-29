from weasyprint import HTML
from django.template.loader import render_to_string
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse, JsonResponse
from administration.models import *
from .models import *
from django.contrib.auth.decorators import login_required



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