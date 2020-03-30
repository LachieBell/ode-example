from django.db.models.signals import post_delete
from django.dispatch import receiver
from .models import Ode


@receiver(post_delete, sender=Ode)
def delete_local_file(sender, instance, using, **kwargs):
	"""Deleting images files from the ODE"""
	instance.image.delete(save=False)
