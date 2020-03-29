from django.db import models

from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth.models import User

# from django.core.exceptions import SuspiciousOperation
# from user_registration.models import Company
# from meta_model.models import AbstractUserStorage, AbstractDateStorage
from django.core.exceptions import SuspiciousOperation


class OdeQuerySet(models.QuerySet):
    def active(self):
        return self.filter(active=True)

    def accessible(self, user):
        if user.is_staff:
            return self.all()
        else:
            return self.filter(created_by=user)


class OdeManager(models.Manager):

    def get_queryset(self):
        return OdeQuerySet(self.model, using=self._db)

    def active(self):
        return self.get_queryset().active()

    def accessible(self, user):
        return self.get_queryset().accessible(user)


class Ode(models.Model):
    """
    Primary model used to hold parameters and starting conditions for our ODE.
    """
    objects = OdeManager()

    # ================================
    # Meta Data
    # ================================
    created_by = models.ForeignKey(User,
                                   on_delete=models.PROTECT,
                                   related_name='+',
                                   )
    edited_by = models.ForeignKey(User,
                                  on_delete=models.PROTECT,
                                  related_name='+')

    created = models.DateTimeField(auto_now_add=True)
    edited = models.DateTimeField(auto_now=True)

    name = models.CharField(max_length=255, blank=False)
    active = models.BooleanField(default=False)

    # ================================
    # Simulation Parameters
    # ================================
    transmission_rate = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(100)], default=10
    )

    recovery_rate = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(100)], default=1)

    # Where 100 is 100%
    initial_percent_infected = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(100)], default=1
    )

    max_t = models.IntegerField(
        validators=[MinValueValidator(0)], default=10
    )

    # ================================
    # Saved graphic
    # ================================
    image = models.FileField(null=True, blank=True, upload_to='images/')

    def solve_ode(self):
        tr = self.transmission_rate
        rr = self.recovery_rate

        total = 100
        i = self.initial_percent_infected / 100
        r = 0
        s = total / 100 - i - r  # Everyone else.

        susceptible_data = [s]
        infected_data = [i]
        recovered_data = [r]

        for _ in range(int(self.max_t)):
            s_prime = - tr * s * i
            i_prime = tr * s * i - rr * i
            r_prime = rr * i

            s += s_prime
            i += i_prime
            r += r_prime

            s = min(max(s, 0), 1)
            i = min(max(i, 0), 1)
            r = min(max(r, 0), 1)

            susceptible_data.append(s)
            infected_data.append(i)
            recovered_data.append(r)

        return {
            'recovered': recovered_data,
            'infected': infected_data,
            'susceptible': susceptible_data,
            'peak_infected': round(100*max(infected_data)),
            'total_recovered': round(100*recovered_data[-1])

        }

    def __str__(self):
        return str(self.name)

    class Meta:
        ordering = ['-created']