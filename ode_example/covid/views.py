from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.contrib.auth.decorators import permission_required, login_required
from django.contrib.auth import authenticate, login
from .models import Ode
from .forms import OdeForm
import json
import numpy as np


@login_required
def list_covid_models(request):

    user = request.user
    ode_models = Ode.objects.accessible(user)
    context = {
        'ode_models': ode_models
    }

    return render(request, 'covid/list_covid_models.html', context)


def solve_ode(ode_model, time_step=1):
    tr = ode_model.transmission_rate
    rr = ode_model.recovery_rate

    total = 100
    i = ode_model.initial_percent_infected/100
    r = 0
    s = total/100 - i - r  # Everyone else.

    susceptible_data = [s]
    infected_data = [i]
    recovered_data = [r]

    for _ in np.arange(0, ode_model.max_t, time_step):

        s_prime = - tr * s * i
        i_prime = tr * s * i - rr * i
        r_prime = rr * i

        s += s_prime
        i += i_prime
        r += r_prime

        s = min(max(s, 0), 1)
        i = min(max(i, 0), 1)
        r = min(max(r, 0), 1)

        print(s)

        susceptible_data.append(s)
        infected_data.append(i)
        recovered_data.append(r)

        # print(s)

    return {
        'recovered': recovered_data,
        'infected': infected_data,
        'susceptible': susceptible_data}


@login_required
def save_ode(request, ode_pk):
    pass


@login_required
def resolve_ode(request):
    pass


@login_required
def detail_ode(request, ode_pk):
    ode_model = get_object_or_404(Ode, pk=ode_pk)
    ode_model_form = OdeForm(instance=ode_model)
    data = solve_ode(ode_model)

    context = {
        'ode_model': ode_model,
        'ode_model_form': ode_model_form,
        'data': json.dumps(data)

    }

    return render(request, 'covid/detail_covid_model.html', context)