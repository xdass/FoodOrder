from django.utils import timezone
from django.utils.html import format_html
from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Restaurant(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='restaurant', verbose_name='Владелец')
    name = models.CharField(max_length=500, verbose_name='Название ресторана')
    phone = models.CharField(max_length=500, verbose_name='Телефон')
    address = models.CharField(max_length=500, verbose_name='Адрес')
    logo = models.ImageField(upload_to='restaurant_logo/', blank=False, verbose_name='Логотип')

    def user_is_active(self):
        return self.user.is_active
    user_is_active.admin_order_field = 'user_is_active'
    user_is_active.boolean = True
    user_is_active.short_description = 'Ресторан подтвержден'

    def approve_restaurant(self):
        if self.user.is_active:
            info = '<span style="color: grey">Активирован</span>'
        else:
            info = '<a href="#" class="btn btn-primary">Активировать</a>'
        return format_html(
            info
        )
    approve_restaurant.short_description = 'Активация ресторана'

    def __str__(self):
        return self.name


class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer')
    avatar = models.CharField(max_length=500)
    phone = models.CharField(max_length=500, blank=True)
    address = models.CharField(max_length=500, blank=True)

    def __str__(self):
        return self.user.get_full_name()


class Driver(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='driver')
    avatar = models.CharField(max_length=500)
    phone = models.CharField(max_length=500, blank=True)
    address = models.CharField(max_length=500, blank=True)
    location = models.CharField(max_length=500, blank=True)

    def __str__(self):
        return self.user.get_full_name()


class Meal(models.Model):
    restaurant = models.ForeignKey(Restaurant)
    name = models.CharField(max_length=500)
    short_description = models.CharField(max_length=500)
    image = models.ImageField(upload_to='meal_images/', blank=False)
    price = models.IntegerField(default=0)

    def __str__(self):
        return self.name


class Order(models.Model):
    COOKING = 1
    READY = 2
    ONTHEWAY = 3
    DELIVERED = 4

    STATUS_CHOICES = (
        (COOKING, 'Готовится'),
        (READY, 'Готов'),
        (ONTHEWAY, 'В пути'),
        (DELIVERED, 'Доставлено'),
    )

    customer = models.ForeignKey(Customer)
    restaurant = models.ForeignKey(Restaurant)
    driver = models.ForeignKey(Driver, blank=True, null=True)
    address = models.CharField(max_length=500)
    total = models.IntegerField(default=0)
    status = models.IntegerField(choices=STATUS_CHOICES)
    created_at = models.DateTimeField(default=timezone.now)
    picked_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return str(self.id)


class OrderDetails(models.Model):
    order = models.ForeignKey(Order, related_name='order_details')
    meal = models.ForeignKey(Meal)
    quantity = models.IntegerField()
    sub_total = models.IntegerField()

    def __str__(self):
        return str(self.id)