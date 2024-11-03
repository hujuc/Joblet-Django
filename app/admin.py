from django.contrib import admin

from app.models import Profile, Category, Service, Booking

admin.site.register(Profile)
admin.site.register(Category)
admin.site.register(Service)
admin.site.register(Booking)