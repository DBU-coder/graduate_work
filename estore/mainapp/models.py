from django.conf import settings
from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.urls import reverse
from django.utils import timezone


def get_product_url(obj, viewname):
	ct_model = obj.__class__._meta.model_name
	return reverse(viewname, kwargs={'ct_model': ct_model, 'slug': obj.slug})


User = get_user_model()


# Create your models here.

class LatestProductsManager:

	def get_products_for_main_page(self, *args, **kwargs):
		products = []
		ct_models = ContentType.objects.filter(model__in=args)
		for ct_model in ct_models:
			model_products = ct_model.model_class()._base_manager.all().order_by('-id')[:4]
			products.extend(model_products)
		return products


class LatestProducts:
	objects = LatestProductsManager()

# def get_absolute_url(self):
# 	return get_product_url(self, 'product_detail')


class Category(models.Model):
	class Meta:
		verbose_name = 'Категорию'
		verbose_name_plural = 'Категории'
		ordering = ['name']

	name = models.CharField(max_length=255, verbose_name='Имя категории')
	slug = models.SlugField(unique=True)

	def __str__(self):
		return self.name

	def get_absolute_url(self):
		return reverse('category_detail', kwargs={'slug': self.slug})


class Product(models.Model):
	STATUS_CHOICES = [
		('in_stock', 'в наличии'),
		('out_stock', 'нет в наличии'),
		('running_out', 'заканчивается'),
		('coming_soon', 'ожидается')
	]

	class Meta:
		abstract = True

	sku = models.CharField(max_length=20, unique=True, verbose_name='Артикул')
	status = models.CharField(max_length=11, choices=STATUS_CHOICES, verbose_name='Статус', default='in_stock')
	category = models.ForeignKey(Category, verbose_name='Категория', on_delete=models.CASCADE)
	brand = models.CharField(max_length=50, verbose_name='Бренд')
	model = models.CharField(max_length=100, verbose_name='Модель')
	title = models.CharField(max_length=255, verbose_name='Наименование')
	diameter = models.CharField(max_length=5, verbose_name='Диаметр')
	width = models.CharField(max_length=5, verbose_name='Ширина')
	slug = models.SlugField(unique=True)
	image = models.ImageField(verbose_name='Изображение')
	description = models.TextField(verbose_name='Описание', blank=True)
	price = models.DecimalField(max_digits=9, decimal_places=2, verbose_name='Цена')

	def __str__(self):
		return f'Product: {self.brand} {self.model}'

	def get_model_name(self):
		return self.__class__.__name__.lower()


class Tires(Product):
	class Meta:
		verbose_name = 'Шину'
		verbose_name_plural = 'Шины'
		ordering = ['brand', 'model']

	SEASON_CHOICE = [
		(None, 'выберите значение'),
		('W', 'Зимние'),
		('S', 'Летние'),
		('A', 'всесезонные')
	]

	season = models.CharField(max_length=1, choices=SEASON_CHOICE, verbose_name='Сезон')
	prod_country = models.CharField(max_length=50, verbose_name='Страна производитель', null=True)
	prod_year = models.PositiveSmallIntegerField(verbose_name='Год производства', null=True)
	vehicle_type = models.CharField(max_length=50, verbose_name='Тип Т/С')
	profile = models.CharField(max_length=5, verbose_name='Профиль')
	speed_index = models.CharField(max_length=50, verbose_name='Индекс скорости')
	load_index = models.CharField(max_length=50, verbose_name='Индекс нагрузки')
	spikes = models.BooleanField(default=False, verbose_name='Шипы')
	protector_type = models.CharField(max_length=50, verbose_name='Тип протектора')

	def __str__(self):
		return f'{self.category.name} : {self.model} | {self.diameter}'

	def get_absolute_url(self):
		return get_product_url(self, 'product_detail')


class Rims(Product):
	class Meta:
		verbose_name = 'Диск'
		verbose_name_plural = 'Диски'
		ordering = ['brand', 'model']

	TYPE_CHOICE = [
		(None, 'выберите тип'),
		('alloy', 'легкосплавные'),
		('steel', 'стальные')
	]

	bolt_spacing = models.SmallIntegerField(verbose_name='Межболтовое расстояние')
	et = models.SmallIntegerField(verbose_name='ET')
	dia = models.DecimalField(max_digits=5, decimal_places=1, verbose_name='DIA')
	color = models.CharField(max_length=50, verbose_name='Цвет')
	type = models.CharField(max_length=5, choices=TYPE_CHOICE, verbose_name='Тип диска')
	bolts = models.SmallIntegerField(verbose_name='Количество болтов')
	psd = models.CharField(max_length=10, verbose_name='PSD')

	def __str__(self):
		return f'{self.category.name} : {self.model}|{self.diameter}|{self.type}'

	def get_absolute_url(self):
		return get_product_url(self, 'product_detail')


class CartProduct(models.Model):
	user = models.ForeignKey('Customer', null=True, blank=True, verbose_name='Покупатель', on_delete=models.CASCADE)
	cart = models.ForeignKey('Cart', verbose_name='Корзина', on_delete=models.CASCADE, related_name='related_products')
	content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
	object_id = models.PositiveIntegerField()
	content_object = GenericForeignKey('content_type', 'object_id')
	qty = models.PositiveIntegerField(default=1, verbose_name='Количество')
	session_key = models.CharField(max_length=1024, verbose_name='Ключ сессии', null=True, blank=True)
	final_price = models.DecimalField(max_digits=9, default=0, decimal_places=2, verbose_name='Общая цена')

	def save(self, *args, **kwargs):
		self.final_price = self.qty * self.content_object.price
		super().save(*args, **kwargs)

	def __str__(self):
		return f'Продукт: {self.content_object.title} (для корзины)'


class Cart(models.Model):

	class Meta:
		verbose_name = 'Корзина'
		verbose_name_plural = 'Корзины'
		ordering = ['owner', 'id']

	owner = models.ForeignKey('Customer', null=True, blank=True, verbose_name='Владелец', on_delete=models.CASCADE)
	products = models.ManyToManyField(CartProduct, blank=True, related_name='related_cart')
	total_products = models.PositiveIntegerField(default=0)
	final_price = models.DecimalField(max_digits=9, default=0, decimal_places=2, verbose_name='Общая цена')
	in_order = models.BooleanField(default=False)
	session_key = models.CharField(max_length=1024, verbose_name='Ключ сессии', null=True, blank=True)

	def __str__(self):
		return str(self.id)


class Customer(models.Model):
	class Meta:
		verbose_name = 'Клиента'
		verbose_name_plural = 'Клиенты'
		ordering = ['user']

	user = models.OneToOneField(settings.AUTH_USER_MODEL, verbose_name='Пользователь', on_delete=models.CASCADE)
	phone = models.CharField(max_length=20, null=True, blank=True, verbose_name='Номер телефона')
	address = models.CharField(max_length=255, null=True, blank=True, verbose_name='Адрес')
	orders = models.ManyToManyField('Order', null=True, blank=True, verbose_name='Заказы покупателя', related_name='related_order')

	def __str__(self):
		return f'Покупатель: {self.user.first_name} {self.user.last_name}'


class Order(models.Model):

	class Meta:
		verbose_name = 'Заказ'
		verbose_name_plural = 'Заказы'
		ordering = ['status', 'customer']

	STATUS_NEW = 'new'
	STATUS_IN_PROGRESS = 'in_progress'
	STATUS_READY = 'is_ready'
	STATUS_COMPLETED = 'completed'

	BUYING_TYPE_SELF = 'self'
	BUYING_TYPE_DELIVERY = 'delivery'

	STATUS_CHOICES = (
		(STATUS_NEW, 'Новый заказ'),
		(STATUS_IN_PROGRESS, 'Заказ в обработке'),
		(STATUS_READY, 'Заказ готов'),
		(STATUS_COMPLETED, 'Заказ выполнен')
	)

	BUYING_TYPE_CHOICES = (
		(BUYING_TYPE_SELF, 'Самовывоз'),
		(BUYING_TYPE_DELIVERY, 'Доставка')
	)

	customer = models.ForeignKey(Customer, verbose_name='Покупатель', related_name='related_orders',
	                             on_delete=models.CASCADE)
	first_name = models.CharField(max_length=255, verbose_name='Имя')
	last_name = models.CharField(max_length=255, verbose_name='Фамилия')
	phone = models.CharField(max_length=20, verbose_name='Телефон')
	cart = models.ForeignKey(Cart, verbose_name='Корзина', on_delete=models.CASCADE, null=True, blank=True)
	address = models.CharField(max_length=1024, verbose_name='Адрес', null=True, blank=True)
	status = models.CharField(
		max_length=100,
		verbose_name='Статус заказ',
		choices=STATUS_CHOICES,
		default=STATUS_NEW
	)
	buying_type = models.CharField(
		max_length=100,
		verbose_name='Тип заказа',
		choices=BUYING_TYPE_CHOICES,
		default=BUYING_TYPE_SELF
	)
	comment = models.TextField(verbose_name='Комментарий к заказу', null=True, blank=True)
	created_at = models.DateTimeField(auto_now=True, verbose_name='Дата создания заказа')
	order_date = models.DateField(verbose_name='Дата получения заказа', default=timezone.now)

	def __str__(self):
		return str(self.id)
