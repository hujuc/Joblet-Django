from django.contrib import admin
from django import forms
from django.utils.dateparse import parse_datetime

from app.models import *

admin.site.register(Review)
admin.site.register(Chat)
admin.site.register(Message)
admin.site.register(Provider)
admin.site.register(Notification)

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'full_name', 'wallet', 'location', 'phone')
    search_fields = ('user__username', 'user__email', 'location')
    list_filter = ('wallet',)
    fieldsets = (
        ('User Information', {'fields': ('user', 'avatar')}),
        ('Contact Details', {'fields': ('phone', 'location')}),
        ('Financial Info', {'fields': ('wallet',)}),
    )


class BookingInline(admin.TabularInline):
    model = Booking
    extra = 0

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('title', 'provider', 'price', 'approval', 'is_active')
    inlines = [BookingInline]
    search_fields = ('service__title', 'customer__user__username', 'status')
    ordering = ('-created_at',)
    actions = ['approve_services']

    def save_model(self, request, obj, form, change):
        # Combine date and time for scheduled_time
        date = form.cleaned_data.get('scheduled_time_0')
        time = form.cleaned_data.get('scheduled_time_1')
        if date and time:
            obj.scheduled_time = parse_datetime(f"{date} {time}")
        super().save_model(request, obj, form, change)

    def approve_services(self, request, queryset):
        queryset.update(approval='approved')
        self.message_user(request, f"{queryset.count()} services approved.")
    approve_services.short_description = "Approve selected services"

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'icon')
    list_editable = ('icon',)

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.TextField: {'widget': forms.Textarea(attrs={'rows': 3, 'cols': 40})},
    }
    list_display = ('id', 'service', 'customer', 'status', 'created_at')
    list_select_related = ('service', 'customer__user')
    list_filter = ('status', 'scheduled_time')
    search_fields = ('service__title', 'customer__user__username')
