# Create your views here.
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from store.models import Product, ProductRating

def rate_product(request, product_id):
    
    if request.method == 'POST':
        product = get_object_or_404(Product, pk = long(product_id))
        product.productrating_set.create(rating = int(request.POST.get('rating')))
        return HttpResponse(status=200)
    else:
        return HttpResponse(status=405)

def index(request):
    request.session['hello'] = 'world'
    request.session.save()
    return HttpResponse("Hello World")
