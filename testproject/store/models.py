from django.db import models
from audit_log.models.fields import LastUserField
from audit_log.models.managers import AuditLog
import datetime

class ProductCategory(models.Model):
    name = models.CharField(max_length=150, primary_key = True)
    description = models.TextField()
    
    audit_log = AuditLog()
    
    def __unicode__(self):
        return self.name
    
class Product(models.Model):
    name = models.CharField(max_length = 150)
    description = models.TextField()
    price = models.DecimalField(max_digits = 10, decimal_places = 2)
    category = models.ForeignKey(ProductCategory)
    
    audit_log = AuditLog()
    
    
    def __unicode__(self):
        return self.name

class WarehouseEntry(models.Model):
    product = models.ForeignKey(Product)
    quantity = models.DecimalField(max_digits = 10, decimal_places = 2)
    
    audit_log = AuditLog()
    
    class Meta:
        app_label = "warehouse"


class SaleInvoice(models.Model):
    date = models.DateTimeField(default = datetime.datetime.now)

    audit_log = AuditLog(exclude = ['date',])
    
    
    def __unicode__(self):
        return str(self.date)

class SoldQuantity(models.Model):
    product = models.ForeignKey(Product)
    quantity = models.DecimalField(max_digits = 10, decimal_places = 2)
    sale = models.ForeignKey(SaleInvoice)

    audit_log = AuditLog()
    
    
    def __unicode__(self):
        return "%s X %s"%(self.product.name, self.quantity)


class Widget(models.Model):
    name = models.CharField(max_length = 100)

class ExtremeWidget(Widget):
    special_power = models.CharField(max_length = 100)
    
    audit_log = AuditLog()