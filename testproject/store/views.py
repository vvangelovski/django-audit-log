# Create your views here.
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.template import Template, RequestContext
from store.models import Product, ProductRating

def rate_product(request, product_id):
    
    if request.method == 'POST':
        product = get_object_or_404(Product, pk = long(product_id))
        product.productrating_set.create(rating = int(request.POST.get('rating')))
        return HttpResponse(status = 200)
    else:
        c = RequestContext(request, {})
        return HttpResponse(Template("""
            <html><body><form action="." method="post">{% csrf_token %}
            <input type="text" name="rating"/>
            <input type="submit" value="Submit">
            </form></body></html>   
            """).render(c)
            )

def index(request):
    request.session['hello'] = 'world'
    request.session.save()
    return HttpResponse("Hello World")
