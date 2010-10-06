from django.test import TestCase
from testproject.store.models import Product, WarehouseEntry

class EntryManagerSelectTest(TestCase):
    fixtures = ['test_data.json']
    
    def test_model_level_select(self):
        self.failUnlessEqual(Product.audit_log.all().count(), 10)
        
    def test_instance_level_select(self):
        self.failUnlessEqual(Product.objects.get(pk = 4).audit_log.all().count(), 3)
        self.failUnlessEqual(Product.objects.get(pk = 1).audit_log.all().count(), 2)
        

class LogEntryMetaOptionsTest(TestCase):
    
    def test_app_label(self):
        self.failUnlessEqual(Product.audit_log.model._meta.app_label, Product._meta.app_label)
        self.failUnlessEqual(WarehouseEntry.audit_log.model._meta.app_label, WarehouseEntry._meta.app_label)
    
    def test_table_name(self):
        self.failUnlessEqual(Product.audit_log.model._meta.db_table, "%sauditlogentry"%Product._meta.db_table)
        self.failUnlessEqual(WarehouseEntry.audit_log.model._meta.db_table, "%sauditlogentry"%WarehouseEntry._meta.db_table)