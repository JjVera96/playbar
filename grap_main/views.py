from django.shortcuts import redirect
from django.urls import reverse
from django.shortcuts import render
from django.http import JsonResponse
from paypal.standard.forms import PayPalPaymentsForm
from paypal.standard.forms import PayPalSharedSecretEncryptedPaymentsForm
from playlist.models import User, Payments

def view_that_asks_for_money(request):

    print("view_that_asks_for_money")

    user = User.objects.filter(username=request.user)[0]
    print(user.username)

    if Payments.objects.filter(customer=user) and Payments.objects.filter(customer=user)[0].is_active:
        return redirect("/listas")

    paypal_dict = {
        "cmd": "_xclick-subscriptions",
        "business": 'eplayit.info-vendedor10@gmail.com',
        "a3": "9.99",                      # monthly price
        "p3": 1,                           # duration of each unit (depends on unit)
        "t3": "M",                         # duration unit ("M for Month")
        "src": "1",                        # make payments recur
        "sra": "1",                        # reattempt payment on payment error
        "no_note": "1",                    # remove extra notes (optional)
        "item_name": "Suscripcion de ePlayt por un mes",
        "notify_url": request.build_absolute_uri(reverse('paypal-ipn')),
        "return": request.build_absolute_uri(reverse('paypal_return')),
        "cancel_return": request.build_absolute_uri(reverse('payment')),
        "custom": user.username + "~" + str(1), # Custom command to correlate to some function later (optional)
    }

    paypal_dict2 = {
        "cmd": "_xclick-subscriptions",
        "business": 'eplayit.info-vendedor10@gmail.com',
        "a3": "19.99",                      # monthly price
        "p3": 6,                           # duration of each unit (depends on unit)
        "t3": "M",                         # duration unit ("M for Month")
        "src": "1",                        # make payments recur
        "sra": "1",                        # reattempt payment on payment error
        "no_note": "1",                    # remove extra notes (optional)
        "item_name": "Suscripcion de ePlayt por seis mes",
        "notify_url": request.build_absolute_uri(reverse('paypal-ipn')),
        "return": request.build_absolute_uri(reverse('paypal_return')),
        "cancel_return": request.build_absolute_uri(reverse('payment')),
        "custom": user.username + "~" + str(6),   # Custom command to correlate to some function later (optional)
    }

    paypal_dict3 = {
        "cmd": "_xclick-subscriptions",
        "business": 'eplayit.info-vendedor10@gmail.com',
        "a3": "29.99",                      # monthly price
        "p3": 12,                           # duration of each unit (depends on unit)
        "t3": "M",                         # duration unit ("M for Month")
        "src": "1",                        # make payments recur
        "sra": "1",                        # reattempt payment on payment error
        "no_note": "1",                    # remove extra notes (optional)
        "item_name": "Suscripcion de ePlayt por un año",
        "notify_url": request.build_absolute_uri(reverse('paypal-ipn')),
        "return": request.build_absolute_uri(reverse('paypal_return')),
        "cancel_return": request.build_absolute_uri(reverse('payment')),
        "custom":  user.username + "~" + str(12),  # Custom command to correlate to some function later (optional)
    }

    # Create the instance.
    form = PayPalPaymentsForm(initial=paypal_dict, button_type="subscribe")
    form2 = PayPalPaymentsForm(initial=paypal_dict2, button_type="subscribe")
    form3 = PayPalPaymentsForm(initial=paypal_dict3, button_type="subscribe")

    # Works just like before!
    #form.render()
    context = {
        "form": form,
        "form2": form2,
        "form3": form3,
        }
    return render(request, "planes.html", context)
