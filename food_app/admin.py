from django.contrib import admin
from .models import Restaurant, Customer, Driver, Meal, Order, OrderDetails


def activate_restaurant(self, request, queryset):
    for restaurant in queryset.all():
        restaurant.user.is_active = True
        restaurant.user.save()
    self.message_user(request, 'Активация ресторана')
activate_restaurant.short_description = 'Активировать ресторан'


class RestaurantAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone', 'address', 'user_is_active', 'approve_restaurant']
    actions = [activate_restaurant]

admin.site.register(Restaurant, RestaurantAdmin)
admin.site.register(Customer)
admin.site.register(Driver)
admin.site.register(Meal)
admin.site.register(Order)
admin.site.register(OrderDetails)