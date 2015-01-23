from django.test import TestCase
from django.db import models
from .models import (Product, WarehouseEntry, ProductCategory, ExtremeWidget,
                        SaleInvoice, Employee, ProductRating, Property, PropertyOwner)
from .views import (index, rate_product, CategoryCreateView, ProductCreateView,
                    ProductDeleteView, ProductUpdateView, ExtremeWidgetCreateView,
                    PropertyOwnerCreateView, PropertyCreateView, PropertyUpdateView)
from django.test.client import Client

from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^/$', index),
    url(r'^rate/(\d)/$', rate_product),
    url(r'^category/create/$', CategoryCreateView.as_view()),
    url(r'^product/create/$', ProductCreateView.as_view()),
    url(r'^product/update/(?P<pk>\d+)/$', ProductUpdateView.as_view()),
    url(r'^product/delete/(?P<pk>\d+)/$', ProductDeleteView.as_view()),
    url(r'^extremewidget/create/$', ExtremeWidgetCreateView.as_view()),
    url(r'^propertyowner/create/$', PropertyOwnerCreateView.as_view()),
    url(r'^property/create/$', PropertyCreateView.as_view()),
    url(r'^property/update/(?P<pk>\d+)/$', PropertyUpdateView.as_view()),

)



def __setup_admins():
    from django.contrib.auth.models import User
    User.objects.all().delete()
    admin = User(username = "admin@example.com", is_staff = True, is_superuser = True)
    admin.set_password("admin")
    admin.save()
    admin = User(username = "admin1@example.com", is_staff = True, is_superuser = True)
    admin.set_password("admin1")
    admin.save()

def __setup_employees():
    from .models import Employee
    Employee.objects.all().delete()
    admin = Employee(email = "admin@example.com",)
    admin.set_password("admin")
    admin.save()
    admin = Employee(email = "admin1@example.com",)
    admin.set_password("admin1")
    admin.save()

def _setup_admin():
    from django.conf import settings
    if settings.AUTH_USER_MODEL =="audit_log.Employee":
        __setup_employees()
    else:
        __setup_admins()


class LogEntryMetaOptionsTest(TestCase):


    def test_app_label(self):
        self.failUnlessEqual(Product.audit_log.model._meta.app_label, Product._meta.app_label)
        self.failUnlessEqual(WarehouseEntry.audit_log.model._meta.app_label, WarehouseEntry._meta.app_label)

    def test_table_name(self):
        self.failUnlessEqual(Product.audit_log.model._meta.db_table, "%sauditlogentry"%Product._meta.db_table)
        self.failUnlessEqual(WarehouseEntry.audit_log.model._meta.db_table, "%sauditlogentry"%WarehouseEntry._meta.db_table)


class TrackingAuthFieldsTest(TestCase):
    urls = __name__

    def setUp(self):
        category  = ProductCategory.objects.create(name = "gadgets", description = "gadgetry")
        category.product_set.create(name = "new gadget", description = "best gadget eva", price = 100)


    def test_logging_user(self):
        _setup_admin()
        product = Product.objects.get(pk = 1)
        self.assertEqual(product.productrating_set.all().count(), 0)
        c = Client()
        c.login(username = "admin@example.com", password = "admin")
        c.post('/rate/1/', {'rating': 4})
        self.assertEqual(product.productrating_set.all().count(), 1)
        self.assertEqual(product.productrating_set.all()[0].user.username, "admin@example.com")

    def test_logging_session(self):
        _setup_admin()
        product = Product.objects.get(pk = 1)
        self.assertEqual(product.productrating_set.all().count(), 0)
        c = Client()
        c.login(username = "admin@example.com", password = "admin")
        c.get('/rate/1/',)
        key = c.session.session_key
        resp = c.post('/rate/1/', {'rating': 4})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(product.productrating_set.all().count(), 1)
        self.assertIsNotNone(product.productrating_set.all()[0].session)
        self.assertEqual(product.productrating_set.all()[0].session, key)

    def test_logging_anon_session(self):
        pass
        #TODO need to find a way to test this


    def test_logging_user_none(self):
        product = Product.objects.get(pk = 1)
        self.assertEqual(product.productrating_set.all().count(), 0)
        c = Client()
        c.post('/rate/1/', {'rating': 4})
        self.assertEqual(product.productrating_set.all().count(), 1)
        self.assertEqual(product.productrating_set.all()[0].user, None)


class TrackingChangesTest(TestCase):
    urls = __name__

    def run_client(self, client):
        client.post('/category/create/', {'name': 'Test Category', 'description': 'Test description'})
        client.post('/category/create/', {'name': 'Test Category 2', 'description': 'Test description 2'})
        client.post('/product/create/', {'name': 'Test Product', 'description': 'Test description', 'price': '2.22', 'category': 'Test Category'})
        client.post('/product/update/1/', {'name': 'Test Product', 'description': 'Test description new', 'price': '5.00', 'category': 'Test Category'})


    def test_logging_insert_anon(self):
        c = Client()
        self.run_client(c)
        category = ProductCategory.objects.get(name = 'Test Category')
        self.assertEqual(category.audit_log.all()[0].name, category.name)
        self.assertEqual(category.audit_log.all()[0].description, category.description)
        self.assertEqual(category.audit_log.all()[0].action_type, "I")
        self.assertEqual(category.audit_log.all()[0].action_user, None)


    def test_logging_insert_auth(self):
        _setup_admin()
        c = Client()
        c.login(username = "admin@example.com", password = "admin")
        self.run_client(c)
        category = ProductCategory.objects.get(name = 'Test Category 2')
        self.assertEqual(category.audit_log.all()[0].name, category.name)
        self.assertEqual(category.audit_log.all()[0].description, category.description)
        self.assertEqual(category.audit_log.all()[0].action_type, "I")
        self.assertNotEqual(category.audit_log.all()[0].action_user, None)
        self.assertEqual(category.audit_log.all()[0].action_user.username, 'admin@example.com')

    def test_loggin_update_anon(self):
        c = Client()
        self.run_client(c)
        product=  Product.objects.get(name = 'Test Product')
        self.assertGreater(product.audit_log.all()[0].action_date, product.audit_log.all()[1].action_date)
        self.assertEqual(product.audit_log.all()[1].action_type, 'I')
        self.assertEqual(product.audit_log.all()[0].action_type, 'U')
        self.assertEqual(product.audit_log.all()[0].description, 'Test description new')
        self.assertEqual(product.audit_log.all()[0].price, 5.00)
        self.assertEqual(product.audit_log.all()[0].action_user, None)

    def test_loging_update_auth(self):
        _setup_admin()
        c = Client()
        c.login(username = 'admin@example.com', password = 'admin')
        self.run_client(c)
        product=  Product.objects.get(name = 'Test Product')
        self.assertNotEqual(product.audit_log.all()[0].action_user, None)
        self.assertEqual(product.audit_log.all()[0].action_user.username, 'admin@example.com')

    def test_logging_delete_anon(self):
        c = Client()
        self.run_client(c)
        c.post('/product/delete/1/')
        self.assertEqual(Product.objects.all().count(), 0)
        self.assertEqual(Product.audit_log.all()[0].action_type, 'D')
        self.assertEqual(Product.audit_log.all()[0].name, 'Test Product')
        self.assertEqual(Product.audit_log.all()[0].action_user, None)

    def test_logging_delete_auth(self):
        _setup_admin()
        c = Client()
        c.login(username = 'admin@example.com', password = 'admin')
        self.run_client(c)
        self.assertEqual(Product.objects.all().count(), 1)
        c.post('/product/delete/1/')
        self.assertEqual(Product.objects.all().count(), 0)
        self.assertEqual(Product.audit_log.all()[0].action_type, 'D')
        self.assertEqual(Product.audit_log.all()[0].name, 'Test Product')
        self.assertNotEqual(Product.audit_log.all()[0].action_user, None)
        self.assertEqual(Product.audit_log.all()[0].action_user.username, 'admin@example.com')

    def test_logging_inherited(self):
        _setup_admin()
        c = Client()
        c.login(username = "admin@example.com", password = "admin")
        c.post('/extremewidget/create/', {'name': 'Test name', 'special_power': 'Testpower'})
        widget = ExtremeWidget.objects.all()[0]
        self.failUnlessEqual(widget.audit_log.all()[0].name, 'Test name')
        self.failUnlessEqual(hasattr(widget.audit_log.all()[0], 'special_power'), True)
        self.failUnlessEqual(widget.audit_log.all()[0].special_power, "Testpower")

class TestOneToOne(TestCase):
    urls = __name__

    def run_client(self, client):
        client.post('/propertyowner/create/', {'name': 'John Dory'})
        client.post('/propertyowner/create/', {'name': 'Jane Doe'})
        client.post('/property/create/', {'name': 'Property1', 'owned_by': '1'})
        client.post('/property/update/1/', {'name': 'Property2', 'owned_by': '2'})

    def test_fields(self):
        c = Client()
        self.run_client(c)
        owner = PropertyOwner.objects.get(pk = 1)
        prop = Property.objects.get(pk = 1)
        self.assertEqual(prop.audit_log.all()[0]._meta.get_field('owned_by').__class__, models.ForeignKey)

    def test_logging(self):
        c = Client()
        self.run_client(c)
        owner1 = PropertyOwner.objects.get(pk = 1)
        owner2 = PropertyOwner.objects.get(pk = 2)
        prop = Property.objects.get(pk = 1)
        self.assertEqual(prop.audit_log.all().count(), 2)
        self.assertEqual(prop.audit_log.all()[0].action_type, 'U')
        self.assertEqual(prop.audit_log.all()[1].action_type, 'I')
        self.assertEqual(prop.audit_log.all()[0].owned_by, owner2)
        self.assertEqual(prop.audit_log.all()[1].owned_by, owner1)
