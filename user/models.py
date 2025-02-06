from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from datetime import datetime
from product.models import Product, ProductVariant
from decimal import Decimal



class MyUserManager(BaseUserManager):
    def create_user(self, email, password=None):
        """
        Creates and saves a User with the given email, date of
        birth and password.
        """
        if not email:
            raise ValueError("Users must have an email address")

        user = self.model(
            email=self.normalize_email(email),
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        user = self.create_user(
            email,
            password=password,
        )
        user.is_admin = True
        user.save(using=self._db)
        return user


class MyUser(AbstractBaseUser):
    username = models.CharField(max_length=100)
    email = models.EmailField(
        verbose_name="email address",
        max_length=255,
        unique=True,
    )
    first_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100, blank=True, null=True)

    is_active = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)

    objects = MyUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return self.email
    

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin
    

class Address(models.Model):
    users = models.ForeignKey('MyUser',on_delete=models.CASCADE, related_name='addresses')
    street = models.CharField(max_length=100)
    city=models.CharField(max_length=100)
    district=models.CharField(max_length=100)
    state=models.CharField(max_length=100)
    pincode=models.IntegerField()

class Cart(models.Model):
    user = models.ForeignKey('MyUser', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cart for {self.user}"
    
class CartItem(models.Model):
    cart = models.ForeignKey('Cart', on_delete=models.CASCADE,related_name='items')
    product = models.ForeignKey('product.Product', on_delete=models.CASCADE)
    variant = models.ForeignKey('product.ProductVariant', on_delete=models.CASCADE, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        if self.variant:
            return f"{self.product.name} - {self.variant.color} (x{self.quantity})"
        return f"{self.product.name} (x{self.quantity})"

    @property
    def image(self):
        # Return variant image if exists, else fallback to product base image
        return self.variant.variant_image.url if self.variant and self.variant.variant_image else self.product.base_image.url
    
    
class Wishlist(models.Model):
    user = models.ForeignKey('MyUser', on_delete=models.CASCADE, related_name='wishlists')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Wishlist for {self.user.email}"


class WishlistItem(models.Model):
    wishlist = models.ForeignKey('Wishlist', on_delete=models.CASCADE, related_name='wishlist_items')
    product = models.ForeignKey('product.Product', on_delete=models.CASCADE, null=True)
    
    variant = models.ForeignKey('product.ProductVariant', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        if self.variant:
            return f"{self.product.name} - {self.variant.color}"
        return f"{self.product.name}"

class Wallet(models.Model):
    user = models.OneToOneField('MyUser', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)

    def __str__(self):
        return f"{self.user.username}'s Wallet - Balance: ${self.amount}"

    def credit(self, amount):
        self.amount += Decimal(amount)
        self.save()

    def debit(self, amount):
        if self.amount >= Decimal(amount):
            self.amount -= Decimal(amount)
            self.save()
            return True
        return False


class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('credit', 'Credit'),
        ('debit', 'Debit'),
        ('refund', 'Refund'),
    ]

    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.transaction_type.title()} - ${self.amount} - {self.transaction_date.strftime('%Y-%m-%d %H:%M:%S')}"   


