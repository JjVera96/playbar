# grap_main/signals/handlers.py
from paypal.standard.ipn.signals import payment_was_successful, payment_was_flagged
from paypal.standard.ipn.signals import valid_ipn_received, invalid_ipn_received
from django.dispatch import receiver
from playlist.models import Payments,User
from datetime import timedelta
import datetime
import calendar

def add_months(sourcedate,months):
	month = sourcedate.month - 1 + months
	year = sourcedate.year + month // 12
	month = month % 12 + 1
	day = min(sourcedate.day,calendar.monthrange(year,month)[1])
	return datetime.date(year,month,day)

#@receiver(valid_ipn_received)
def show_me_the_money(sender, **kwargs):
	print("show_me_the_money")

	'''ipn_obj = sender
	customer_user = User.objects.filter(username=ipn_obj.custom)[0]
	expiration = datetime.date.today()
	Payments.objects.create(customer=customer_user, payment_expiration=add_months(expiration,1))
'''

def do_not_show_me_the_money(sender, **kwargs):
	print("HANDLERS do_not_show_me_the_money")

#@receiver(payment_was_successful)
def show_me_the_money_successful(sender, **kwargs):
	print("show_me_the_money_successful")
	print(sender.custom)
	ipn_obj=sender.custom.split('~')
	print(ipn_obj[0])
	print(ipn_obj[1])
	customer_user = User.objects.filter(username=ipn_obj[0])[0]
	expiration = datetime.date.today()
	Payments.objects.create(customer=customer_user, payment_expiration=add_months(expiration,int(ipn_obj[1])))


def show_me_the_money_flagged(sender, **kwargs):
	print("show_me_the_money_flagged")

payment_was_flagged.connect(show_me_the_money_flagged)
payment_was_successful.connect(show_me_the_money_successful)

valid_ipn_received.connect(show_me_the_money)
invalid_ipn_received.connect(do_not_show_me_the_money)
