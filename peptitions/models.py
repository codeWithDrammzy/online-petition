from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models

# --- Custom User Manager ---
class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)


# --- Custom User Model ---
class User(AbstractUser):
    username = None  # remove username field
    email = models.EmailField(unique=True)  # make email unique

    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    
    created_at = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = "email"  # login with email
    REQUIRED_FIELDS = []  # require full_name when creating superuser

    objects = CustomUserManager()

    def __str__(self):
        return self.first_name or self.email


class Petition(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending Approval"),  
        ("active", "Active"),
        ("closed", "Closed"),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField()
    image = models.ImageField(upload_to="petitions/", blank=True, null=True)  
    category = models.CharField(max_length=100, blank=True, null=True)
    target_signatures = models.PositiveIntegerField(default=100)
    current_signatures = models.PositiveIntegerField(default=0)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending"   # when user creates, it starts as pending
    )
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="petitions")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class Signature(models.Model):
    petition = models.ForeignKey(
        Petition, 
        on_delete=models.CASCADE, 
        related_name="signatures"
    )
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name="signatures"
    )
    comment = models.TextField(blank=True, null=True)  # optional reason for signing
    signed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("petition", "user")  # ✅ prevents double signing

    def __str__(self):
        return f"{self.user.email} signed {self.petition.title}"
