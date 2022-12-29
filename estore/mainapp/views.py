from django.contrib.auth import logout, login
from django.contrib.auth.views import LoginView
from django.db import transaction
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import DetailView, ListView, CreateView
from django.contrib import messages

from .mixins import DataMixin, CartMixin, CategoryDetailMixin
from .models import *
from .forms import OrderForm, RegisterUserForm, LoginUserForm
from .utils import recalc_cart

# Create your views here.


class HomeView(CartMixin, DataMixin, ListView):
	template_name = 'index.html'
	context_object_name = 'latest_products'

	def get_context_data(self, *, object_list=None, **kwargs):
		context = super().get_context_data(**kwargs)
		c_def = self.get_user_context(title='Главная')
		context['cart'] = self.cart
		context = dict(list(context.items()) + list(c_def.items()))
		return context

	def get_queryset(self):
		return LatestProducts.objects.get_products_for_main_page('rims', 'tires')


class ProductDetailView(CartMixin, DataMixin, DetailView):
	CT_MODEL_MODEL_CLASS = {
		'rims': Rims,
		'tires': Tires
	}

	context_object_name = 'product'
	template_name = 'product_detail.html'
	slug_url_kwarg = 'slug'

	def dispatch(self, request, *args, **kwargs):
		self.model = self.CT_MODEL_MODEL_CLASS[kwargs['ct_model']]
		self.queryset = self.model._base_manager.all()
		return super().dispatch(request, *args, **kwargs)

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['ct_model'] = self.model._meta.model_name
		context['cart'] = self.cart
		c_def = self.get_user_context(title=kwargs['object'].title)
		context = dict(list(context.items()) + list(c_def.items()))
		return context


class CategoryDetailView(CartMixin, CategoryDetailMixin, DetailView):
	model = Category
	queryset = Category.objects.all()
	context_object_name = 'category'
	template_name = 'category_detail.html'
	slug_url_kwarg = 'slug'

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['cart'] = self.cart
		return context

	# def get_queryset(self):
	#
	# 	return queryset


class AddToCartView(CartMixin, View):

	def get(self, request, *args, **kwargs):
		ct_model, product_slug = kwargs.get('ct_model'), kwargs.get('slug')
		content_type = ContentType.objects.get(model=ct_model)
		product = content_type.model_class().objects.get(slug=product_slug)
		cart_product, created = CartProduct.objects.get_or_create(
			user=self.cart.owner, cart=self.cart, content_type=content_type, object_id=product.id,
		)
		if created:
			self.cart.products.add(cart_product)
		recalc_cart(self.cart)
		messages.add_message(request, messages.INFO, 'Товар успешно добавлен.')
		return HttpResponseRedirect('/cart/')


class DeleteFromCartView(CartMixin, View):

	def get(self, request, *args, **kwargs):
		ct_model, product_slug = kwargs.get('ct_model'), kwargs.get('slug')
		content_type = ContentType.objects.get(model=ct_model)
		product = content_type.model_class().objects.get(slug=product_slug)
		cart_product = CartProduct.objects.get(
			user=self.cart.owner, cart=self.cart, content_type=content_type, object_id=product.id
		)
		self.cart.products.remove(cart_product)
		cart_product.delete()
		recalc_cart(self.cart)
		messages.add_message(request, messages.INFO, 'Товар успешно удален.')
		return HttpResponseRedirect('/cart/')


class ChangeQTYView(CartMixin, View):

	def post(self, request, *args, **kwargs):
		ct_model, product_slug = kwargs.get('ct_model'), kwargs.get('slug')
		content_type = ContentType.objects.get(model=ct_model)
		product = content_type.model_class().objects.get(slug=product_slug)
		cart_product = CartProduct.objects.get(
			user=self.cart.owner, cart=self.cart, content_type=content_type, object_id=product.id
		)
		qty = int(request.POST.get('qty'))
		cart_product.qty = qty
		cart_product.save()
		recalc_cart(self.cart)
		messages.add_message(request, messages.INFO, 'Количество изменено успешно.')
		return HttpResponseRedirect('/cart/')


class CartView(CartMixin, DataMixin, View):

	def get(self, request, *args, **kwargs):
		categories = Category.objects.all()
		context = {
			'cart': self.cart,
			'cats': categories,
		}
		return render(request, 'cart.html', context)


class CheckoutView(CartMixin, DataMixin, View):

	def get(self, request, *args, **kwargs):
		categories = Category.objects.all()
		form = OrderForm(request.POST or None)
		context = {
			'cart': self.cart,
			'cats': categories,
			'form': form,
		}
		return render(request, 'checkout.html', context)


class MakeOrderView(CartMixin, View):

	@transaction.atomic  # Для корректной записи в базу. Если ошибка, база вернется в предыдущее состояние
	def post(self, request, *args, **kwargs):
		form = OrderForm(request.POST or None)
		customer = Customer.objects.get(user=request.user)
		if form.is_valid():
			new_order = form.save(commit=False)
			new_order.customer = customer
			new_order.first_name = form.cleaned_data['first_name']
			new_order.last_name = form.cleaned_data['last_name']
			new_order.phone = form.cleaned_data['phone']
			new_order.address = form.cleaned_data['address']
			new_order.buying_type = form.cleaned_data['buying_type']
			new_order.order_date = form.cleaned_data['order_date']
			new_order.comment = form.cleaned_data['comment']
			new_order.save()
			self.cart.in_order = True
			self.cart.save()
			new_order.cart = self.cart
			new_order.save()
			customer.orders.add(new_order)
			messages.add_message(request, messages.INFO, 'Спасибо за заказ! Менеджер с Вами свяжется')
			return HttpResponseRedirect('/')
		return HttpResponseRedirect('/checkout/')


class SearchListView(ListView):

	template_name = 'search_results.html'
	context_object_name = 'search_results'

	def get_queryset(self):
		search_title = self.request.GET.get('search_title')
		search_cat = self.request.GET.get('category')
		products = []
		if search_cat and search_title:
			ct_model = ContentType.objects.get(model=search_cat)
			return ct_model.get_all_objects_for_this_type(title__contains=search_title)
		elif search_title:
			ct_models = ContentType.objects.filter(model__in=('rims', 'tires'))
			for ct_model in ct_models:
				products.extend(ct_model.get_all_objects_for_this_type(title__contains=search_title))
			print(products)
			return products
		else:
			return None


class RegisterUser(CartMixin, DataMixin, CreateView):
	form_class = RegisterUserForm
	template_name = 'register.html'
	success_url = reverse_lazy('login')

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['cart'] = self.cart
		c_def = self.get_user_context(title='Регистрация')
		return dict(list(context.items()) + list(c_def.items()))

	def form_valid(self, form):
		user = form.save()
		login(self.request, user)
		return redirect('home')


class LoginUser(CartMixin, DataMixin, LoginView):

	form_class = LoginUserForm
	template_name = 'login.html'

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['cart'] = self.cart
		c_def = self.get_user_context(title='Авторизация')
		return dict(list(context.items()) + list(c_def.items()))

	def get_success_url(self):
		return reverse_lazy('home')


def logout_user(request):
	logout(request)
	return redirect('login')



