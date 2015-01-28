from django.test import TestCase
from django.db import models
from .models import (Product, WarehouseEntry, ProductCategory, ExtremeWidget,
                        SaleInvoice, Employee, ProductRating, Property, PropertyOwner)


class DisablingTrackingTest(TestCase):


    def test_disable_enable_instance(self):
        ProductCategory.objects.create(name = 'test category', description = 'test')
        ProductCategory.objects.create(name = 'test category2', description = 'test')
        c1 = ProductCategory.objects.get(name = 'test category')
        c2 = ProductCategory.objects.get(name = 'test category2')
        self.assertTrue(c1.audit_log.is_tracking_enabled())
        c1.audit_log.disable_tracking()
        self.assertFalse(c1.audit_log.is_tracking_enabled())
        self.assertTrue(c2.audit_log.is_tracking_enabled())


    def test_disable_enable_class(self):
        self.assertRaises(ValueError, ProductCategory.audit_log.disable_tracking)
        self.assertRaises(ValueError, ProductCategory.audit_log.enable_tracking)
        self.assertRaises(ValueError, ProductCategory.audit_log.is_tracking_enabled)

    def test_disabled_not_tracking(self):
        ProductCategory(name = 'test category', description = 'test').save()
        ProductCategory(name = 'test category2', description = 'test').save()
        c1 = ProductCategory.objects.get(name = 'test category')
        c2 = ProductCategory.objects.get(name = 'test category2')
        c1.description = 'best'
        c1.audit_log.disable_tracking()
        c1.save()
        self.assertEquals(c1.audit_log.all().count(), 1)
        c1.audit_log.enable_tracking()
        c1.description = 'new desc'
        c1.save()
        self.assertEquals(c1.audit_log.all().count(), 2)
        c1.audit_log.disable_tracking()
        c1.delete()
        self.assertEquals(ProductCategory.audit_log.all().count(), 3)
