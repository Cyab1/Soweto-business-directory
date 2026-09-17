from django.contrib import admin
from .models import Category, Business, Review, VerificationLog


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name"]


@admin.register(Business)
class BusinessAdmin(admin.ModelAdmin):
    list_display = ["name", "category", "is_verified", "verified_by", "verified_at"]
    list_filter = ["is_verified", "category"]


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ["business", "user", "rating", "created_at"]


@admin.register(VerificationLog)
class VerificationLogAdmin(admin.ModelAdmin):
    list_display = ["business", "action", "performed_by", "created_at"]
    readonly_fields = ["business", "action", "performed_by", "notes", "created_at"]

    def has_delete_permission(self, request, obj=None):
        return False  # audit log — never deletable, even by admins