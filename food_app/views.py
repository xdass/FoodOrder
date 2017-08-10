from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from food_app.forms import UserForm, RestaurantForm, UserFormForEdit, MealForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.db.models import Sum, Count, Case, When

from .models import Restaurant, Meal, Order, Driver, Customer


# Create your views here.
def home(request):
    return redirect(restaurant_home)


@login_required(login_url='/restaurant/sign-in/')
def restaurant_home(request):
    restaurant = Restaurant.objects.filter(user_id__exact=request.user).exists()
    if restaurant:
        return redirect(restaurant_order)
    else:
        return redirect(restaurant_account)


def restaurant_sign_up(request):
    user_form = UserForm()
    #user_form.email = request.session.get('user_id')
    #user_form.save()
    restaurant_form = RestaurantForm()

    if request.method == 'POST':
        user_form = UserForm(request.POST)
        restaurant_form = RestaurantForm(request.POST, request.FILES)

        if user_form.is_valid() and restaurant_form.is_valid():
            new_user = User.objects.create_user(**user_form.cleaned_data)
            new_restaurant = restaurant_form.save(commit=False)
            new_restaurant.user = new_user
            new_restaurant.save()

            login(request, authenticate(
                username=user_form.cleaned_data['username'],
                password=user_form.cleaned_data['password']
            ))

            return redirect(restaurant_home)

    return render(request, 'restaurant/sign-up.html', {
        'user_form': user_form,
        'restaurant_form': restaurant_form
    })


@login_required(login_url='/restaurant/sign-in/')
def restaurant_account(request):
    user_form = UserFormForEdit(instance=request.user)
    restaurant = Restaurant.objects.filter(user_id=request.user.id).exists()
    if restaurant:
        restaurant_form = RestaurantForm(instance=request.user.restaurant)
    else:
        restaurant_form = RestaurantForm()

    if request.method == 'POST':
        user_form = UserFormForEdit(request.POST, instance=request.user)
        if restaurant:
            restaurant_form = RestaurantForm(request.POST, request.FILES, instance=request.user.restaurant)
        else:
            restaurant_form = RestaurantForm(request.POST, request.FILES)

        if user_form.is_valid() and restaurant_form.is_valid():
            if not restaurant:
                new_restaurant = restaurant_form.save(commit=False)
                new_restaurant.user = request.user

            user_form.save()
            restaurant_form.save()

    return render(request, 'restaurant/account.html', {
        'user_form': user_form,
        'restaurant_form': restaurant_form
    })


@login_required(login_url='/restaurant/sign-in/')
def restaurant_meal(request):
    meals = Meal.objects.filter(restaurant=request.user.restaurant).order_by('-id')

    return render(request, 'restaurant/meal.html', {'meals': meals})


@login_required(login_url='/restaurant/sign-in/')
def restaurant_add_meal(request):
    form = MealForm()

    if request.method == 'POST':
        form = MealForm(request.POST, request.FILES)

        if form.is_valid():
            meal = form.save(commit=False)
            meal.restaurant = request.user.restaurant
            meal.save()
            return redirect('restaurant/meal')

    return render(request, 'restaurant/add_meal.html', {'form': form})


@login_required(login_url='/restaurant/sign-in/')
def restaurant_edit_meal(request, meal_id):
    form = MealForm(instance=Meal.objects.get(id=meal_id))

    if request.method == 'POST':
        form = MealForm(request.POST, request.FILES, instance=Meal.objects.get(id=meal_id))

        if form.is_valid():
            form.save()
            return redirect('restaurant/meal')

    return render(request, 'restaurant/edit_meal.html', {'form': form})


@login_required(login_url='/restaurant/sign-in/')
def restaurant_order(request):
    if request.method == 'POST':
        order = Order.objects.get(id=request.POST['id'], restaurant=request.user.restaurant)

        if order.status == Order.COOKING:
            order.status = Order.READY
            order.save()

    orders = Order.objects.filter(restaurant=request.user.restaurant).order_by('-id')
    return render(request, 'restaurant/order.html', {'orders': orders})


@login_required(login_url='/restaurant/sign-in')
def customers_ever_ordered(request):
    customers = Customer.objects.filter(
        order__restaurant=request.user.restaurant,
    ).annotate(orders_count=Count('order'))
    return render(request, 'restaurant/customers.html', {'customers': customers})


@login_required(login_url='/restaurant/sign-in')
def drivers_ever_delivered(request):
    drivers = Driver.objects.filter(
        order__restaurant=request.user.restaurant,
    ).annotate(orders_count=Count('order'))
    return render(request, 'restaurant/drivers.html', {'drivers': drivers})


@login_required(login_url='/restaurant/sign-in/')
def restaurant_report(request):
    # Calculate revenue and number of orders by current week
    from datetime import datetime, timedelta

    revenue = []
    orders = []

    # Calculate weekdays
    today = datetime.now()
    current_weekdays = [today + timedelta(days=i) for i in range(0 - today.weekday(), 7 - today.weekday())]

    for day in current_weekdays:
        delivered_orders = Order.objects.filter(
            restaurant=request.user.restaurant,
            status=Order.DELIVERED,
            created_at__year=day.year,
            created_at__month=day.month,
            created_at__day=day.day
        )
        revenue.append(sum(order.total for order in delivered_orders))
        orders.append(delivered_orders.count())

    # Top 3 meals
    top3_meals = Meal.objects.filter(restaurant=request.user.restaurant)\
        .annotate(total_order=Sum('orderdetails__quantity'))\
        .order_by('-total_order')[:2]

    meal = {
        "labels": [meal.name for meal in top3_meals],
        "data": [meal.total_order or 0 for meal in top3_meals]
    }

    # Top 3 drivers
    top3_driver = Driver.objects.annotate(
        total_order=Count(
            Case(
                When(order__restaurant=request.user.restaurant, then=1)
            )
        )
    ).order_by('-total_order')[:3]

    driver = {
        "labels": [driver.user.get_full_name() for driver in top3_driver],
        "data": [driver.total_order for driver in top3_driver]
    }

    # Top 3 customers
    top3_customers = Driver.objects.annotate(
        total_order=Count(
            Case(
                When(order__restaurant=request.user.restaurant, then=1)
            )
        )
    ).order_by('-total_order')[:3]

    customer = {
        "labels": [driver.user.get_full_name() for driver in top3_customers],
        "data": [driver.total_order for driver in top3_customers]
    }

    return render(request, 'restaurant/report.html', {
        'revenue': revenue,
        'orders': orders,
        'meal': meal,
        'driver': driver,
        'customer': customer
    })
