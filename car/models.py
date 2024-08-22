from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, Group, Permission
from django.utils import timezone
from decimal import Decimal

class CustomUserManager(BaseUserManager):
    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, username, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=12)
    role = models.CharField(max_length=50, blank=True, null=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    groups = models.ManyToManyField(Group, related_name='custom_user_groups')
    user_permissions = models.ManyToManyField(Permission, related_name='custom_user_permissions')

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return self.is_superuser or super().has_perm(perm, obj)

    def has_module_perms(self, app_label):
        return self.is_superuser or super().has_module_perms(app_label)

class Garage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    location = models.CharField(max_length=255)
    phone = models.CharField(max_length=12)
    images = models.ImageField(upload_to='garage_images/', blank=True, null=True)
    approved = models.BooleanField(default=False)

class GarageService(models.Model):
    garage = models.ForeignKey(Garage, on_delete=models.CASCADE, related_name='services')
    service_name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    max_per_slot = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.service_name} at {self.garage.location}"
    
class Booking(models.Model):
    garage_id = models.IntegerField()  # Assuming you store garage as an integer reference
    date = models.DateField()
    slot = models.CharField(max_length=30)
    service = models.ForeignKey(GarageService, on_delete=models.CASCADE)

class BookingHistory(models.Model):
    garage_name = models.CharField(max_length=255)
    user_name = models.CharField(max_length=255)
    date_booked = models.DateField()
    slot_booked = models.CharField(max_length=30)
    date_of_booking = models.DateTimeField(default=timezone.now)
    service_selected = models.CharField(max_length=255)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    card_number = models.CharField(max_length=16)
    cvv = models.CharField(max_length=3)
    admin_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    is_canceled = models.BooleanField(default=False)
    final_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, default=0)
    garage_earnings = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, default=0)

    def save(self, *args, **kwargs):
        # Calculate the admin amount as 15% of the total amount
        if self.total_amount:
            # Convert 0.15 to Decimal for the calculation
            self.admin_amount = self.total_amount * Decimal('0.15')
        super().save(*args, **kwargs)

    def __str__(self):
        return f'BookingHistory for {self.user_name} at {self.garage_name}'
    
class TodayBookingStatus(models.Model):
    booking = models.OneToOneField(BookingHistory, on_delete=models.CASCADE)
    current_status = models.CharField(max_length=30, default='Pending')
    date_booked = models.DateField(default=timezone.now)

    def __str__(self):
        return f'{self.booking.user_name} - {self.current_status}'
    
class Vehicle(models.Model):
    booking_history = models.ForeignKey(BookingHistory, on_delete=models.CASCADE, related_name='vehicles')
    number_plate = models.CharField(max_length=15, unique=True)
    model = models.CharField(max_length=100)

class GarageProfile(models.Model):
    garage = models.ForeignKey(Garage, on_delete=models.CASCADE, related_name='profiles')
    owner_name = models.CharField(max_length=100)
    exact_location = models.TextField() 
    garage_policies = models.TextField()

    def __str__(self):  
        return f"Profile of {self.owner_name} for Garage at {self.garage.location}"
    
class GarageImage(models.Model):
    garage_profile = models.ForeignKey(GarageProfile, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='garage_profile_images/')