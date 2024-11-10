from django.contrib import admin
from django.utils.dateparse import parse_datetime

from app.models import *

admin.site.register(Profile)
admin.site.register(Service)
admin.site.register(Review)
admin.site.register(Chat)
admin.site.register(Message)
admin.site.register(Provider)
admin.site.register(Notification)

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'service', 'customer', 'scheduled_time', 'status', 'created_at')
    search_fields = ('service__title', 'customer__user__username', 'status')
    list_filter = ('status', 'created_at')
    ordering = ('-created_at',)

    def save_model(self, request, obj, form, change):
        # Combine date and time for scheduled_time
        date = form.cleaned_data.get('scheduled_time_0')
        time = form.cleaned_data.get('scheduled_time_1')
        if date and time:
            obj.scheduled_time = parse_datetime(f"{date} {time}")
        super().save_model(request, obj, form, change)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'icon')
    list_editable = ('icon',)
