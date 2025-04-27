from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.contrib.postgres.fields import ArrayField
import uuid

class UserManager(BaseUserManager):
    def create_user(self, phone=None, email=None, password=None, **extra_fields):
        if not (phone or email):
            raise ValueError('User must have either phone or email')
        
        if email:
            email = self.normalize_email(email)
        
        user = self.model(phone=phone, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, phone=None, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        
        return self.create_user(phone, email, password, **extra_fields)

class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(max_length=150, unique=True, null=True, blank=True)
    email = models.EmailField(unique=True, null=True, blank=True)
    phone = models.CharField(max_length=15, unique=True, null=True, blank=True)
    is_mentor = models.BooleanField(default=False)
    is_mentee = models.BooleanField(default=False)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    objects = UserManager()
    
    def save(self, *args, **kwargs):
        if not self.username and self.email:
            self.username = self.email
        elif not self.username and self.phone:
            self.username = self.phone
        super().save(*args, **kwargs)

class Mentee(models.Model):
    COMMUNICATION_CHOICES = (
        ('ussd', 'USSD'),
        ('app', 'App'),
        ('both', 'Both'),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='mentee_profile')
    name = models.CharField(max_length=100)
    age = models.PositiveIntegerField()
    county = models.CharField(max_length=50)
    language = models.CharField(max_length=5, default='en')  # 'en' or 'sw'
    device = models.CharField(max_length=50)
    interests = ArrayField(models.CharField(max_length=50), blank=True, default=list)
    communication_preference = models.CharField(max_length=10, choices=COMMUNICATION_CHOICES, default='app')
    
    def __str__(self):
        return self.name

class Mentor(models.Model):
    VISIBILITY_CHOICES = (
        ('visible', 'Visible'),
        ('anonymous', 'Anonymous'),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='mentor_profile')
    name = models.CharField(max_length=100)
    expertise = ArrayField(models.CharField(max_length=50), blank=True, default=list)
    language_preference = models.CharField(max_length=5, default='en')  # 'en' or 'sw'
    counties = ArrayField(models.CharField(max_length=50), blank=True, default=list)
    max_mentees = models.PositiveIntegerField(default=3)
    mentees_count = models.PositiveIntegerField(default=0)
    visibility = models.CharField(max_length=10, choices=VISIBILITY_CHOICES, default='visible')
    
    def __str__(self):
        return self.name

class Mentorship(models.Model):
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('completed', 'Completed'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    mentee = models.ForeignKey(Mentee, on_delete=models.CASCADE, related_name='mentorships')
    mentor = models.ForeignKey(Mentor, on_delete=models.CASCADE, related_name='mentorships')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.mentee.name} - {self.mentor.name}"

class Resource(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField()
    tags = ArrayField(models.CharField(max_length=50), blank=True, default=list)
    link = models.URLField(blank=True, null=True)
    sms_text = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(Mentor, on_delete=models.SET_NULL, null=True, related_name='uploaded_resources')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title