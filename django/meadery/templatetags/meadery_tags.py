from django import template
from cart import cart
from pyment.settings import BREWER_NAME, BREWER_EMAIL, BREWER_LOCATION
from meadery.models import Product
from django.core.urlresolvers import reverse

register = template.Library()


@register.inclusion_tag("tags/cart_box.djhtml")
def cart_box(request):
    cart_item_count = cart.cart_distinct_item_count(request)
    return {'cart_item_count': cart_item_count}


@register.inclusion_tag("tags/category_list.djhtml")
def category_list(request_path):
    # should only return categories that meet the following requirements:
    # is_active is True,
    # they have products,
    # and those products have jars
    # there has to be a more django-ish way to do this
    active_categories = [(name, reverse('meadery_category', kwargs={'category_value': value})) for (value, name) in Product.MEAD_VIEWS if Product.instock.filter(category=value).exists() or value == Product.ALL]
    if len(active_categories) == 1:
        active_categories = []
    return {
        'active_categories': active_categories,
        'request_path': request_path
    }


@register.inclusion_tag("tags/footer.djhtml")
def footer():
    return {
        'name': BREWER_NAME,
        'email': BREWER_EMAIL,
        'location': BREWER_LOCATION,
    }


@register.inclusion_tag("tags/product_list.djhtml")
def product_list(products, header_text):
    return {
        'products': products,
        'header_text': header_text
    }
