# import requests
# import yaml
# from django.core.exceptions import ValidationError
# from django.core.mail import EmailMultiAlternatives
# from django.core.validators import URLValidator
# from django.db import IntegrityError
# from yaml import load as load_yaml, Loader
#
# from .models import Shop, Category, Product, Parameter, ProductParameter, ProductInfo
# from celery import shared_task
# from django.conf.global_settings import EMAIL_HOST_USER
#
#
# @shared_task()
# def send_email(message: str, email: str, *args, **kwargs) -> str:
#     title = 'Title'
#     email_list = [email]  # No need to create an empty list and then append
#     try:
#         print(f"Sending email to: {email}")  # Log the email address
#         print(f"Message: {message}")  # Log the message
#         msg = EmailMultiAlternatives(subject=title, body=message, from_email=EMAIL_HOST_USER, to=email_list)
#         msg.send()
#         return f'Title: {msg.subject}, Message:{msg.body}'
#     except Exception as e:
#         print(f"Error sending email to {email}: {e}")  # Log any errors that occur during email sending
#         raise e


import requests
import yaml
from django.core.exceptions import ValidationError
from django.core.mail import EmailMultiAlternatives
from django.core.validators import URLValidator
from yaml import load as load_yaml, Loader
from celery import shared_task
from django.conf import settings  # Импорт настроек Django

from .models import Shop, Category, ProductInfo, ProductParameter, Parameter, Product, User, ConfirmEmailToken


# @shared_task()
# def send_email(message: str, email: str, *args, **kwargs) -> str:
#     title = 'Title'
#     email_list = [email]  # No need to create an empty list and then append
#     try:
#         print(f"Sending email to: {email}")  # Log the email address
#         print(f"Message: {message}")  # Log the message
#         msg = EmailMultiAlternatives(subject=title, body=message, from_email=settings.EMAIL_HOST_USER, to=email_list)
#         msg.send()
#         return f'Title: {msg.subject}, Message:{msg.body}'
#     except Exception as e:
#         print(f"Error sending email to {email}: {e}")  # Log any errors that occur during email sending
#         raise e

# @shared_task()
# def password_reset_token_created(reset_password_token, **kwargs):
#     """
#     Отправляем письмо с токеном для сброса пароля
#     When a token is created, an e-mail needs to be sent to the user
#     :param reset_password_token: Token Model Object
#     :param kwargs:
#     :return:
#     """
#     # send an e-mail to the user
#
#     msg = EmailMultiAlternatives(
#         # title:
#         f"Password Reset Token for {reset_password_token.user}",
#         # message:
#         reset_password_token.key,
#         # from:
#         settings.EMAIL_HOST_USER,
#         # to:
#         [reset_password_token.user.email],
#     )
#     msg.send()




@shared_task(name="new_user_registered")
def new_user_registered(user_id):
    """
    Отправляем письмо с подтверждением почты
    """
    token, _ = ConfirmEmailToken.objects.get_or_create(user_id=user_id)

    msg = EmailMultiAlternatives(
        # title:
        f"Password Reset Token for {token.user.email}",
        # message:
        token.key,
        # from:
        settings.EMAIL_HOST_USER,
        # to:
        [token.user.email]
    )
    msg.send()


@shared_task(name="new_order")
def new_order(user_id):
    """
    Отправляем письмо при изменении статуса заказа
    """
    user = User.objects.get(id=user_id)

    msg = EmailMultiAlternatives(
        # title:
        f"Обновление статуса заказа",
        # message:
        'Заказ сформирован',
        # from:
        settings.EMAIL_HOST_USER,
        # to:
        [user.email]
    )
    msg.send()

def open_file(shop):
    with open(shop.get_file(), 'r') as f:
        data = yaml.safe_load(f)
    return data


@shared_task()
def do_import(url, user_id):
    if url:
        validate_url = URLValidator()
        try:
            validate_url(url)
        except ValidationError as e:
            return {'Status': False, 'Error': str(e)}
        else:
            stream = requests.get(url).content

        data = load_yaml(stream, Loader=Loader)
        try:
            shop, _ = Shop.objects.get_or_create(name=data['shop'],
                                                 user_id=user_id)
        except IntegrityError as e:
            return {'Status': False, 'Error': str(e)}

        for category in data['categories']:
            category_object, _ = Category.objects.get_or_create(
                id=category['id'], name=category['name'])
            category_object.shops.add(shop.id)
            category_object.save()

        ProductInfo.objects.filter(shop_id=shop.id).delete()
        for item in data['goods']:
            product, _ = Product.objects.get_or_create(
                name=item['name'], category_id=item['category']
            )
            product_info = ProductInfo.objects.create(
                product_id=product.id, external_id=item['id'],
                model=item['model'], price=item['price'],
                price_rrc=item['price_rrc'], quantity=item['quantity'],
                shop_id=shop.id
            )
            for name, value in item['parameters'].items():
                parameter_object, _ = Parameter.objects.get_or_create(
                    name=name
                )
                ProductParameter.objects.create(
                    product_info_id=product_info.id,
                    parameter_id=parameter_object.id, value=value
                )
        return {'Status': True}
    return {'Status': False, 'Errors': 'Url is false'}