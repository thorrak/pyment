# Create your views here.
from django.shortcuts import get_object_or_404, render
from catalog.models import Category, Product
from django.core import urlresolvers
from cart.cart import add_to_cart
from django.http import HttpResponseRedirect
from catalog.forms import ProductAddToCartForm

def index(request, template_name='catalog/index.djhtml'):
    page_title = 'Only The Best Fermented Honey Wine'
    return render(request, template_name, locals())
    
def show_category(request, category_slug, template_name='catalog/category.djhtml'):
    c = get_object_or_404(Category, slug=category_slug)
    products = c.product_set.all()
    page_title = c.name
    meta_keywords = c.meta_keywords
    meta_description = c.meta_description
    return render(request, template_name, locals())

# new product view, with POST vs GET detection
def show_product(request, product_slug, template_name="catalog/product.djhtml"):
    p = get_object_or_404(Product, slug=product_slug)
    page_title = p.name
    meta_keywords = p.meta_keywords
    meta_description = p.meta_description
    # need to evaluate the HTTP method
    if request.method == 'POST':
        # add to cart...create the bound form
        postdata = request.POST.copy()
        form = ProductAddToCartForm(request, postdata)
        # check if posted data is valid
        if form.is_valid():
            #add to cart and redirect to cart page
            add_to_cart(request)
            # if test cookie worked, get rid of it
            if request.session.test_cookie_worked():
                request.session.delete_test_cookie()
            url = urlresolvers.reverse('show_cart')
            return HttpResponseRedirect(url)
    else:
        # it's a GET, create the unbound form. Note request as a kwarg
        form = ProductAddToCartForm(request=request, label_suffix=':')
    # assign the hidden input the product slug
    form.fields['product_slug'].widget.attrs['value'] = product_slug
    # set the test cookie on our first GET request
    request.session.set_test_cookie()
    return render(request, 'catalog/product.djhtml', locals())


