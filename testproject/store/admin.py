from django.contrib import admin
from models import *

class CategoryAdmin(admin.ModelAdmin):
    pass


class ProductAdmin(admin.ModelAdmin):
    pass


class InvoiceAdmin(admin.ModelAdmin):
    exclude = ('sales_person',)
    list_display = ('product', 'quantity', 'sales_person',)
    


admin.site.register(ProductCategory, CategoryAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(WarehouseEntry, admin.ModelAdmin)
admin.site.register(SaleInvoice, InvoiceAdmin)
