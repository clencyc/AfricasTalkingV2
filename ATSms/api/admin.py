from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Mentee, Mentor, Mentorship, Resource

class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'phone', 'is_mentor', 'is_mentee', 'is_staff')
    list_filter = ('is_mentor', 'is_mentee', 'is_staff')
    fieldsets = (
        (None, {'fields': ('email', 'phone', 'password')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'is_mentor', 'is_mentee')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'phone', 'password1', 'password2', 'is_mentor', 'is_mentee'),
        }),
    )
    search_fields = ('email', 'phone')
    ordering = ('email',)

class MenteeAdmin(admin.ModelAdmin):
    list_display = ('name', 'age', 'county', 'language', 'communication_preference')
    list_filter = ('county', 'language', 'communication_preference')
    search_fields = ('name', 'county')

class MentorAdmin(admin.ModelAdmin):
    list_display = ('name', 'language_preference', 'mentees_count', 'max_mentees', 'visibility')
    list_filter = ('language_preference', 'visibility')
    search_fields = ('name',)

class MentorshipAdmin(admin.ModelAdmin):
    list_display = ('mentee', 'mentor', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('mentee__name', 'mentor__name')

class ResourceAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_by', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('title', 'description', 'tags')

admin.site.register(User, CustomUserAdmin)
admin.site.register(Mentee, MenteeAdmin)
admin.site.register(Mentor, MentorAdmin)
admin.site.register(Mentorship, MentorshipAdmin)
admin.site.register(Resource, ResourceAdmin)
