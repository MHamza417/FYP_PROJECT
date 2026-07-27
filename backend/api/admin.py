from django.contrib import admin
# 1. Models import mein ContactMessage ko add kiya
from .models import Service, Project, Team, ContactMessage 


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("id", "title")
    search_fields = ("title",)


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "technologies")
    search_fields = ("title", "technologies")


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "position")
    search_fields = ("name", "position")


# 2. Naya ContactMessage model register kiya aapke purane style ke mutabik
@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "email", "created_at")
    search_fields = ("name", "email")
    # readonly_fields lagane se koi admin panel se data badal nahi sakega, sirf read karega
    readonly_fields = ("created_at",)