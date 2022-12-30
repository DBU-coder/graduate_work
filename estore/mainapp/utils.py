from django.db import models
from mainapp.models import Cart, Customer


def recalc_cart(cart):
    cart_data = cart.products.aggregate(models.Sum('final_price'), models.Count('id'))
    if cart_data.get('final_price__sum'):
        cart.final_price = cart_data['final_price__sum']
    else:
        cart.final_price = 0
    cart.total_products = cart_data['id__count']
    cart.save()


def create_cart(request):
    customer = Customer.objects.get(user=request.user)
    customer_cart = customer.cart_set.filter(in_order=False).first()
    if customer_cart:
        customer_cart.delete()
    cart = Cart.objects.get(id=request.session['cart_id'])
    cart.session_key = None
    cart.owner = customer
    cart.products.update(user=cart.owner, session_key=None)
    cart.save()
    del request.session['cart_id']

