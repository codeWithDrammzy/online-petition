from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Petition, Signature


class UserAdmin(BaseUserAdmin):
    model = User
    list_display = ("email", "is_staff", "is_superuser", "is_active")
    list_filter = ("is_staff", "is_superuser", "is_active")
    search_fields = ("email",)
    ordering = ("email",)

    # fields for the admin user form
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Permissions", {"fields": ("is_staff", "is_active", "is_superuser", "groups", "user_permissions")}),
        ("Important dates", {"fields": ("last_login",)}),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "password1", "password2", "is_staff", "is_active")}
        ),
    )


@admin.register(Petition)
class PetitionAdmin(admin.ModelAdmin):
    list_display = ("title", "created_by", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("title", "description")
    ordering = ("-created_at",)


@admin.register(Signature)
class SignatureAdmin(admin.ModelAdmin):
    list_display = ("petition", "signed_by", "signed_at")
    list_filter = ("signed_at",)
    search_fields = ("petition__title", "user__email")
    ordering = ("-signed_at",)

    def signed_by(self, obj):
        return obj.user.email   # or obj.user.get_full_name()
    signed_by.short_description = "Signed By"



admin.site.register(User, UserAdmin)
