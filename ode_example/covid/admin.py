from django.contrib import admin

from .models import Ode


class OdeAdmin(admin.ModelAdmin):
    fields = ['created_by', 'edited_by', 'name',
              'active', 'transmission_rate', 'recovery_rate',
              'initial_percent_infected', 'max_t', 'image']


admin.site.register(Ode, OdeAdmin)
