from django.db import models
from audit_log.models.fields import LastUserField

class ProductCategory(models.Model):
    name = models.CharField(max_length=150, primary_key = True)
    
class Product(models.Model):
    name = models.CharField(max_length = 150)
    price = models.DecimalField(max_digits = 10, decimal_places = 2)
    category = models.ForeignKey(Product)

class WarehouseEntry(models.Model):
    product = models.ForeignKey(Product)
    quantity = models.DecimalField(max_digits = 10, decimal_places = 2)

class SaleInvoice(models.Model):
    product = models.ForeignKey(Product)
    quantity = models.DecimalField(max_digits = 10, decimal_places = 2)
    sales_person = models.LastUserField()