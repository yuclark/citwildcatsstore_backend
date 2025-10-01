from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'full_name', 'user_type', 'student_id', 'staff_id', 'is_active')
    list_filter = ('user_type', 'is_active', 'is_staff')
    search_fields = ('username', 'full_name', 'student_id', 'staff_id', 'email')
    
    fieldsets = UserAdmin.fieldsets + (
        ('Custom Fields', {
            'fields': ('full_name', 'user_type', 'student_id', 'staff_id', 'phone_number', 'address')
        }),
    )
