from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Booking, Chat

# @receiver(post_save, sender=Booking)
# def create_chat_for_booking(sender, instance, created, **kwargs):
#     if created:
#         Chat.objects.get_or_create(booking=instance)
