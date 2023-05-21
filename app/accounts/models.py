from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.core.validators import validate_email

class CustomManager(BaseUserManager):
    
    def create_user(self, email, password, **extra_fields):
        """
        Create and save a user with the given username, email, and password.
        """
        
        if not email:
            raise ValueError("The given email must be set")
        email = self.normalize_email(email)
        
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
class User(AbstractBaseUser):
    class Type(models.TextChoices):
        BRAND = 'BRAND', 'Brand'
        SHOPPER = 'SHOPPER', 'Shopper'
        ADMIN = 'ADMIN', 'Admin'
    
    role = models.CharField(max_length=10, choices=Type.choices, default=Type.SHOPPER)
    email = models.EmailField(max_length=255)
    username = models.CharField(max_length=265, unique=True)
    USERNAME_FIELD = 'username'
    
    class Meta:
        unique_together = ('email', 'role')
    
    objects = CustomManager()
    
    @property
    def profile(self):
        if self.role == 'BRAND':
            profiles = BrandUserProfile.objects.filter(user = self)
        elif self.role == 'SHOPPER':
            profiles = ShopperProfile.objects.filter(user = self)
        else:
            return None
        
        if profiles.exists():
            return profiles[0]
        return None
    
def get_username(email, role):
    return f"{email}_{role}"
    
class ShopperProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    address = models.CharField(max_length=1024, null=True, blank=True, default=None)

class BrandUserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    name = models.CharField(max_length=200, null=False, blank=False)

def verif_and_register(email, password, type):
    # Check if the user can be registered
    # Passwords correspondance is checked on the client side
    if not validate_email_simple(email):
        return (False, {"status": "invalid", "field": "email", "message": "Email invalid"}, None)
    #Verifications on the password
    if len(password) < 8:
        return (False, {"status": "invalid", "field": "password", "message": "too short"}, None)
    
    if type == 'SHOPPER' and not User.objects.filter(email = email, role = "SHOPPER").exists():
        user = User.objects.create_user(email = email, password = password, role = "SHOPPER", username=get_username(email, "SHOPPER"))
        ShopperProfile.objects.create(user = user)
        return (True, {"status": "success", "type": "shopper"}, user)
    if type == 'SHOPPER':
        return (False, {"status": "invalid", "field": "email", "message": "already used"}, None)
    
    if len(password) < 15:
        return (False, {"status": "invalid", "field": "password", "message": "too short"}, None)
    
    if not User.objects.filter(email = email, role = "BRAND").exists():
        user = User.objects.create_user(email = email, password = password, role = "BRAND", username=get_username(email, "BRAND"))
        BrandUserProfile.objects.create(user = user)
        return (True, {"status": "success", "type": "brand"}, user)
    
    return (False, {"status": "error"}, None)
    
def validate_email_simple(email):
    # Simpler to use email validation
    try:
        validate_email(email)
        return True
    except:
        return False