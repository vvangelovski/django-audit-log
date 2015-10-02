# Create your views here.
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.template import Template, RequestContext
from django.views import generic
from .models import (Product, ProductCategory, Employee,
                        ExtremeWidget, Property, PropertyOwner)


def index(request):
    request.session['hello'] = 'world'
    request.session.save()
    return HttpResponse("Hello World")



def rate_product(request, product_id):

    if request.method == 'POST':
        product = get_object_or_404(Product, pk = int(product_id))
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

class CategoryCreateView(generic.CreateView):
    model = ProductCategory
    template_name = 'form.html'
    success_url = '/'
    fields = ['name', 'description']

class ProductCreateView(generic.CreateView):
    model = Product
    template_name = 'form.html'
    success_url  = '/'
    fields = ['name', 'description', 'price', 'category']

class ProductUpdateView(generic.UpdateView):
    model = Product
    template_name = 'form.html'
    success_url = '/'
    fields = ['name', 'description', 'price', 'category']

class ProductDeleteView(generic.DeleteView):
    model = Product
    template_name = 'form.html'
    success_url = '/'

class ExtremeWidgetCreateView(generic.CreateView):
    model = ExtremeWidget
    template_name = 'form.html'
    success_url = '/'
    fields = ['name', 'special_power']

class PropertyOwnerCreateView(generic.CreateView):
    model = PropertyOwner
    template_name = 'form.html'
    success_url = '/'
    fields = ['name']

class PropertyCreateView(generic.CreateView):
    model = Property
    template_name = 'form.html'
    success_url = '/'
    fields = ['name', 'owned_by']

class PropertyUpdateView(generic.UpdateView):
    model = Property
    template_name = 'form.html'
    success_url = '/'
    fields = ['name', 'owned_by']

class EmployeeCreateView(generic.CreateView):
    model = Employee
    template_name = 'form.html'
    success_url = '/'
    #setting the password like this
    # worn't work in reality bu it's ok for the test
    fields = ['email', 'password']

class EmployeeUpdateView(generic.UpdateView):
    model = Employee
    template_name = 'form.html'
    success_url = '/'
    fields = ['email']
