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
		if request.user.is_authenticated:
			# Если авторизован, ищем покупателя и корзину.
			customer = Customer.objects.filter(user=request.user).first()
			cart = Cart.objects.filter(owner=customer, in_order=False).first()
			if not customer:
				customer = Customer.objects.create(user=request.user)
			# Если корзина найдена, возвращаем корзину.
			# Если нет, создаем её.
			if not cart:
				cart = Cart.objects.create(owner=customer)
		else:
			# Если не зарегистрирован, то проверяем есть ли у него корзина "заглушка"
			cart = Cart.objects.filter(for_anonymous_user=True).first()
			if not cart:
				# если нет, создаем.
				cart = Cart.objects.create(for_anonymous_user=True)
		self.cart = cart
		self.cart.save()
		# вызываем метод родителя с нашими изменениями
		return super().dispatch(request, *args, **kwargs)
