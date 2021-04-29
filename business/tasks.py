from celery import shared_task
from .models import *
from django.db.models import Q, Sum
from django.contrib.auth.models import User
# DateTime
from datetime import date, timedelta, datetime
from notifications.signals import notify


# Create your tasks here

@shared_task
def minimum_stock_quatity_notification(*args, **kwargs):
	products = Product.objects.all()

	if products:
		for product in products:
			if product.quantity <= product.min_quantity:
				users = User.objects.all()
				try:
					notify.send(sender=product, recipient=users, level="warning", verb="Product: {0} of Business: {1} is below minimum stock quanatity.".format(product.name, product.business.name))
				except:
					pass
			else:
				pass
	else:
		pass


