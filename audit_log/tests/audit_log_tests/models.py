from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser
)

from audit_log.models.fields import LastUserField, LastSessionKeyField, CreatingUserField
from audit_log.models.managers import AuditLog

import datetime


class EmployeeManager(BaseUserManager):
    def create_user(self, email, password=None):

        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=EmployeeManager.normalize_email(email),
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        u = self.create_user(email, password = password,)
        u.save(using=self._db)
        return u


class Employee(AbstractBaseUser):
    email = models.EmailField(
                        verbose_name='email address',
                        max_length=255, unique = True,
                    )
    USERNAME_FIELD = 'email'

    objects = EmployeeManager()

    @property
    def is_active(self):
        return True

    @property
    def is_superuser(self):
        return True

    @property
    def is_staff(self):
        return True

    @property
    def username(self):
        return self.email

    def get_full_name(self):
        return self.email

    def get_short_name(self):
        return self.email

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

class ProductCategory(models.Model):
    created_by = CreatingUserField(related_name = "created_categories")
    modified_by = LastUserField(related_name = "modified_categories")
    name = models.CharField(max_length=150, primary_key = True)
    description = models.TextField()

    audit_log = AuditLog()

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length = 150)
    description = models.TextField()
    price = models.DecimalField(max_digits = 10, decimal_places = 2)
    category = models.ForeignKey(ProductCategory)

    audit_log = AuditLog()


    def __str__(self):
        return self.name

class ProductRating(models.Model):
    user = LastUserField()
    session = LastSessionKeyField()
    product = models.ForeignKey(Product)
    rating = models.PositiveIntegerField()

class WarehouseEntry(models.Model):
    product = models.ForeignKey(Product)
    quantity = models.DecimalField(max_digits = 10, decimal_places = 2)

    audit_log = AuditLog()

    class Meta:
        app_label = "warehouse"


class SaleInvoice(models.Model):

    date = models.DateTimeField(default = datetime.datetime.now)

    audit_log = AuditLog(exclude = ['date',])


    def __str__(self):
        return str(self.date)

class SoldQuantity(models.Model):
    product = models.ForeignKey(Product)
    quantity = models.DecimalField(max_digits = 10, decimal_places = 2)
    sale = models.ForeignKey(SaleInvoice)

    audit_log = AuditLog()


    def __str__(self):
        return "%s X %s"%(self.product.name, self.quantity)


class Widget(models.Model):
    name = models.CharField(max_length = 100)

class ExtremeWidget(Widget):
    special_power = models.CharField(max_length = 100)

    audit_log = AuditLog()


class PropertyOwner(models.Model):
    name = models.CharField(max_length = 100)

class Property(models.Model):
    name = models.CharField(max_length = 100)
    owned_by = models.OneToOneField(PropertyOwner)

    audit_log = AuditLog()
