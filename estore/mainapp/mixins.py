import uuid
from django.views import View
from django.views.generic.detail import SingleObjectMixin

from .models import Category, Cart, Customer, Tires, Rims, User

menu = [
	{'name': 'Доставка', 'url_name': 'shipping'},
	{'name': 'О сайте', 'url_name': 'about'},
	{'name': 'Обратная связь', 'url_name': 'contact_us'},

]


class DataMixin:

	def get_user_context(self, **kwargs):
		context = kwargs
		cats = Category.objects.all()
		context['menu'] = menu
		context['cats'] = cats
		return context


class CategoryDetailMixin(SingleObjectMixin):
	CATEGORY_SLUG2PRODUCT_MODEL = {
		'tires': Tires,
		'rims': Rims
	}

	def get_context_data(self, **kwargs):
		if isinstance(self.get_object(), Category):
			model = self.CATEGORY_SLUG2PRODUCT_MODEL[self.get_object().slug]
			context = super().get_context_data(**kwargs)
			context['cats'] = Category.objects.all()
			context['category_products'] = model.objects.all()
			context['menu'] = menu

			return context
		context = super().get_context_data(**kwargs)
		context['cats'] = Category.objects.all()
		context['menu'] = menu
		return context


class CartMixin(View):
	"""Клас для отображения корзины на страницах."""

	# метод имеет доступ к request из которого берем user
	def dispatch(self, request, *args, **kwargs):
		cart = None
		if request.user.is_authenticated and request.user.is_superuser:
			# Если авторизован, ищем покупателя
			customer = Customer.objects.filter(user=request.user).first()

			if not customer:
				customer = Customer.objects.create(user=request.user)
			cart = Cart.objects.filter(owner=customer, in_order=False).first()
			# Если корзина найдена, возвращаем корзину.
			# Если нет, создаем её.
			if not cart:
				cart = Cart.objects.create(owner=customer)
			self.cart = cart
		else:
			# Если не зарегистрирован и нет корзины, то создаем новую корзину с ключем сессии UUID.
			if not request.session.get('cart_id'):
				cart = Cart.objects.create(session_key=uuid.uuid4())
				request.session['cart_id'] = cart.id
				self.cart = cart
			else:
				try:
					cart = Cart.objects.get(id=request.session['cart_id'])
				except Cart.DoesNotExist:
					cart = Cart.objects.create(session_key=uuid.uuid4())
				self.cart = cart

		# вызываем метод родителя с нашими изменениями
		return super().dispatch(request, *args, **kwargs)
