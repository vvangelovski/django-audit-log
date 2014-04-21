from django.test import TestCase
from testproject.store.models import Product, WarehouseEntry, ProductCategory, ExtremeWidget, SaleInvoice, Employee
from django.test.client import Client

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
    from store.models import Employee
    Employee.objects.all().delete()
    admin = Employee(email = "admin@example.com",)
    admin.set_password("admin")
    admin.save()
    admin = Employee(email = "admin1@example.com",)
    admin.set_password("admin1")
    admin.save()

def _setup_admin():
    from django.conf import settings
    if settings.AUTH_USER_MODEL =="store.Employee":
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

class TrackingFieldsTest(TestCase):
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
        #product = Product.objects.get(pk = 1)
        #self.assertEqual(product.productrating_set.all().count(), 0)
        #c = Client()
        #resp = c.get('/')
        #self.assert_(hasattr(resp, "session"))
        #key = c.session.session_key
        #c.post('/rate/1', {'rating': 4})
        #self.assertEqual(product.productrating_set.all().count(), 1)
        #self.assertIsNotNone(product.productrating_set.all()[0].session)
        #self.assertEqual(product.productrating_set.all()[0].session, key)

    def test_logging_user_none(self):
        product = Product.objects.get(pk = 1)
        self.assertEqual(product.productrating_set.all().count(), 0)
        c = Client()
        c.post('/rate/1/', {'rating': 4})
        self.assertEqual(product.productrating_set.all().count(), 1)
        self.assertEqual(product.productrating_set.all()[0].user, None)



class LoggingTest(TestCase):
    
    def setup_client(self):
        c = Client()
        c.login(username = "admin@example.com", password = "admin")
        return c
    
    def test_logging_insert_update(self):
        _setup_admin()
        c = self.setup_client()
        c.post('/admin/store/productcategory/add/', {'name': 'Test Category', 'description': 'Test description'})
        self.failUnlessEqual(ProductCategory.objects.all().count(), 1)
        category = ProductCategory.objects.all()[0]
        self.failUnlessEqual(category.audit_log.all()[0].name, category.name)
        self.failUnlessEqual(category.audit_log.all()[0].description, category.description)
        self.failUnlessEqual(category.audit_log.all()[0].action_type, "I")
        self.failUnlessEqual(category.audit_log.all()[0].action_user.username, "admin@example.com")
    
        c.post('/admin/store/productcategory/%s/'%'Test Category', {'name': 'Test Category new name', 'description': 'Test description'})
        category = ProductCategory.objects.get(pk = "Test Category new name")
        self.failUnlessEqual(category.audit_log.all().count(), 1)
        self.failUnlessEqual(category.audit_log.all()[0].name, "Test Category new name")
        self.failUnlessEqual(category.audit_log.all()[0].action_type, "I")
        
        c.post('/admin/store/productcategory/%s/'%'Test Category new name', {'name': 'Test Category new name', 
                                                                            'description': 'Test modified description'})
        category = ProductCategory.objects.get(pk = "Test Category new name")
        self.failUnlessEqual(category.audit_log.all().count(), 2)
        self.failUnlessEqual(category.audit_log.all()[0].description, "Test modified description")
        self.failUnlessEqual(category.audit_log.all()[0].action_type, "U")
    
    def test_logging_delete(self):
        _setup_admin()
        c = self.setup_client()
        c.post('/admin/store/productcategory/add/', {'name': 'Test', 'description': 'Test description'})
        self.failUnlessEqual(ProductCategory.objects.all().count(), 1)
        c.post('/admin/store/productcategory/Test/delete/', {'post': 'yes'})
        self.failUnlessEqual(ProductCategory.objects.all().count(), 0)
        self.failUnlessEqual(ProductCategory.audit_log.all().count(), 2)
        self.failUnlessEqual(ProductCategory.audit_log.all()[0].action_type, "D")        
        
        
    def test_logging_inherited(self):
        _setup_admin()
        c = Client()
        c.login(username = "admin@example.com", password = "admin")
        c.post('/admin/store/extremewidget/add/', {'name': 'Test name', 'special_power': 'Testpower'})
        widget = ExtremeWidget.objects.all()[0]
        self.failUnlessEqual(widget.audit_log.all()[0].name, 'Test name')
        self.failUnlessEqual(hasattr(widget.audit_log.all()[0], 'special_power'), True)
        self.failUnlessEqual(widget.audit_log.all()[0].special_power, "Testpower")
        
        