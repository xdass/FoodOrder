from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from food_app.forms import UserForm, RestaurantForm, UserFormForEdit
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from .models import Restaurant


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
    return render(request, 'restaurant/meal.html')


@login_required(login_url='/restaurant/sign-in/')
def restaurant_order(request):
    return render(request, 'restaurant/order.html')


@login_required(login_url='/restaurant/sign-in/')
def restaurant_report(request):
    return render(request, 'restaurant/report.html')
