from django.contrib import admin
from django.utils.html import format_html
from unfold.admin import ModelAdmin, StackedInline
from accounts.models import User, UserProfile


class UserProfileInline(StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = "Profile Details"
    fk_name = "user"


@admin.register(User)
class UserAdmin(ModelAdmin):
    model = User
    inlines = [UserProfileInline]

    list_display = (
        "id",
        "email",
        "get_full_name",
        "is_active",
        "is_staff",
        "is_superuser",
        "created_at",
    )

    search_fields = ("email", "profile__first_name", "profile__last_name")
    list_filter = ("is_active", "is_staff", "is_superuser")
    ordering = ("email",)

    exclude = ("password",)
    readonly_fields = ("created_at",)

    fieldsets = (
        (
            "Account Info",
            {
                "fields": (
                    "email",
                    "is_active",
                    "is_staff",
                    "is_superuser",
                )
            },
        ),
        (
            "Permissions",
            {
                "classes": ["collapse"],
                "fields": (
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        ("Important dates", {"fields": ("last_login", "created_at")}),
    )

    def get_full_name(self, obj):
        try:
            return obj.profile.full_name
        except UserProfile.DoesNotExist:
            return "-"
    get_full_name.short_description = "Full Name"


@admin.register(UserProfile)
class UserProfileAdmin(ModelAdmin):
    list_display = ("user_email", "first_name", "last_name", "phone_number")
    search_fields = ("user__email", "first_name", "last_name", "phone_number")
    
    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = "User Email"
