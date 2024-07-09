# accounts/admin.py
# from django.contrib import admin
# from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
# from django.contrib.auth.models import User

# class UserAdmin(BaseUserAdmin):
#     # Определите поля, которые будут отображаться в списке пользователей
#     list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff')
#     list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
    
#     # Определите, какие поля будут редактироваться
#     fieldsets = (
#         (None, {'fields': ('username', 'password')}),
#         ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
#         ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
#         ('Important dates', {'fields': ('last_login', 'date_joined')}),
#     )

# # Подключите модель пользователя с кастомной настройкой
# admin.site.unregister(User)
# admin.site.register(User, UserAdmin)
