from django.forms import ModelChoiceField
from django.contrib import admin
from django.contrib.sessions.models import Session

from .models import *

# Register your models here.


class TiresAdmin(admin.ModelAdmin):
	list_display = ('sku', 'brand', 'model', 'category', 'diameter', 'season', 'vehicle_type', 'status')
	list_display_links = ('sku', 'brand', 'model')
	search_fields = ('sku', 'brand', 'model')
	list_editable = ('status',)
	list_filter = ('brand', 'model', 'category', 'diameter', 'vehicle_type', 'status')
	prepopulated_fields = {'slug': ('brand', 'model', 'width', 'profile', 'diameter')}

	def formfield_for_foreignkey(self, db_field, request, **kwargs):
		if db_field.name == 'category':
			return ModelChoiceField(Category.objects.filter(slug='tires'))
		return super().formfield_for_foreignkey(db_field, request, **kwargs)


class RimsAdmin(admin.ModelAdmin):

	list_display = ('sku', 'brand', 'model', 'category', 'diameter', 'type', 'color', 'status')
	list_display_links = ('sku', 'brand', 'model')
	search_fields = ('sku', 'brand', 'model', 'color')
	list_editable = ('status',)
	list_filter = ('brand', 'model', 'category', 'diameter', 'type', 'status', 'color')

	prepopulated_fields = {'slug': ('brand', 'model', 'diameter', 'width', 'psd', 'et', 'dia')}

	def formfield_for_foreignkey(self, db_field, request, **kwargs):
		if db_field.name == 'category':
			return ModelChoiceField(Category.objects.filter(slug='rims'))
		return super().formfield_for_foreignkey(db_field, request, **kwargs)


class OrderAdmin(admin.ModelAdmin):

	list_display = ('id', 'status', 'first_name', 'last_name', 'customer', 'order_date', 'created_at', 'buying_type')
	list_display_links = ('id', 'customer', 'first_name', 'last_name')
	search_fields = ('id', 'first_name', 'last_name', 'customer')
	list_editable = ('status', 'order_date')
	list_filter = ('status', 'first_name', 'last_name', 'customer', 'order_date', 'created_at')


admin.site.register(Category)
admin.site.register(Tires, TiresAdmin)
admin.site.register(Rims, RimsAdmin)
admin.site.register(CartProduct)
admin.site.register(Cart)
admin.site.register(Customer)
admin.site.register(Order, OrderAdmin)
admin.site.register(Session)

