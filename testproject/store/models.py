from django.db import models
from audit_log.models.fields import LastUserField
from audit_log.models.managers import AuditLog

class ProductCategory(models.Model):
    name = models.CharField(max_length=150, primary_key = True)
    description = models.TextField()
    
    audit_log = AuditLog()
    
class Product(models.Model):
    name = models.CharField(max_length = 150)
    description = models.TextField()
    price = models.DecimalField(max_digits = 10, decimal_places = 2)
    category = models.ForeignKey(ProductCategory)
    
    audit_log = AuditLog()

class WarehouseEntry(models.Model):
    product = models.ForeignKey(Product)
    quantity = models.DecimalField(max_digits = 10, decimal_places = 2)
    
    audit_log = AuditLog()

class SaleInvoice(models.Model):
    product = models.ForeignKey(Product)
    quantity = models.DecimalField(max_digits = 10, decimal_places = 2)
    sales_person = LastUserField()