from django.shortcuts import redirect
from food_app.models import Customer, Driver, User, Restaurant
from social_core.pipeline.partial import partial


@partial
def create_user_by_type(strategy, backend, user, request, response, *args, **kwargs):
    if backend.name == 'vk-oauth2':
        avatar = response['user_photo']
        strategy.session_set('user_id', response.get('id'))

    if request.get('user_type', '') == 'driver' and not Driver.objects.filter(user_id=user.id):
        Driver.objects.create(user_id=user.id, avatar=avatar)
    elif request.get('user_type', '') == 'customer' and not Customer.objects.filter(user_id=user.id):
        Customer.objects.create(user_id=user.id, avatar=avatar)
    # if response.get('access_token', ''):
    #     email = response.get('email')
    #     user_id = response.get('user_id')
    #     first_name = response.get('first_name')
    #     last_name = response.get('last_name')
    #     User.objects.create_user(username=user_id, first_name=first_name, last_name=last_name, email=email)
    #     return