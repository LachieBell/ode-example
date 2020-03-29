from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.contrib.auth.decorators import permission_required, login_required
from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from .models import Ode
from .forms import OdeForm, SimpleOdeForm
import json
from django.core.files.base import ContentFile
from django.db.models import Q

def _try_to_float(v):
    try:
        return float(v)
    except ValueError:
        return v


def rationale(request):

    ode_models = Ode.objects.exclude(Q(image=None)|Q(image='')).order_by('-edited')
    ode_model = ode_models.first()
    context = {'ode_model': ode_model}
    return render(request, 'covid/rationale.html', context)


@login_required
def list_covid_models(request):
    """Doubles as the home page. This page lists out ODE models and allows
    you to create new ones"""
    user = request.user
    ode_models = Ode.objects.accessible(user)
    form = SimpleOdeForm()
    context = {
        'ode_models': ode_models,
        'form': form
    }

    return render(request, 'covid/list_covid_models.html', context)


@login_required
def save_ode(request, ode_pk):
    """Updates an ode based on the form from the detail page"""

    if request.method == 'POST':
        accessible_ode_models = Ode.objects.accessible(request.user)
        ode_model = get_object_or_404(accessible_ode_models, pk=ode_pk)
        ode_form = OdeForm(request.POST, instance=ode_model)
        if ode_form.is_valid():
            ode_model = ode_form.save()
            resp = ode_model.solve_ode()
            return JsonResponse(resp)

    resp = {"status": "NOT SAVED"}
    return JsonResponse(resp)


@login_required
def new_ode(request):
    """Creates a new ODE from the ode_list page."""

    if request.method == 'POST':
        ode_form = SimpleOdeForm(request.POST)
        if ode_form.is_valid():
            ode_model = ode_form.save(commit=False)
            ode_model.created_by = request.user
            ode_model.edited_by = request.user
            ode_model.save()
            # Redirect to the detail page of the ODE
            return redirect("covid:detail_ode", ode_pk=ode_model.pk)

    # I appreciate this is not the best work flow. Normally you would do
    # something like this and allow for errors to clearly be displayed
    # for the user.
    return redirect("covid:list_covid_models")


def solve_ode_ajax(request):
    """A VERY simplistic API endpoint

    data = {
        "transmission_rate": 0.6,
        "recovery_rate": 0.1,
        "initial_percent_infected": 0.1,
        "max_t": 50
        }

    Note, we do not touch the database in this call. It is a very "pubic" api.
    """
    try:
        data = {k: _try_to_float(v) for k, v in request.GET.items()}
        ode_model = Ode(**data)
        resp = ode_model.solve_ode()
        return JsonResponse(resp)
    except Exception as e:
        return JsonResponse({'error': str(e)})


@login_required
def detail_ode(request, ode_pk):
    """Shows the a detailed page of the ODE. This is also the main interface
    for editing the parameters

    On every request, it solves the ODE and puts puts it in the DOM.
    """

    ode_model = get_object_or_404(Ode, pk=ode_pk)
    ode_model_form = OdeForm(instance=ode_model)
    data = ode_model.solve_ode()

    context = {
        'ode_model': ode_model,
        'ode_model_form': ode_model_form,
        'data': json.dumps(data)

    }

    return render(request, 'covid/detail_covid_model.html', context)


@login_required
def delete_ode(request, ode_pk):

    accessible_ode_models = Ode.objects.accessible(request.user)
    ode_model = get_object_or_404(accessible_ode_models, pk=ode_pk)
    ode_model.delete()
    return redirect('covid:list_covid_models')


@login_required
def save_ode_image(request, ode_pk):

    if request.method == "POST":
        accessible_ode_models = Ode.objects.accessible(request.user)
        ode_model = get_object_or_404(accessible_ode_models, pk=ode_pk)
        raw_html = request.POST['html']

        # Keeping people's drives clean
        if ode_model.image.name:
            ode_model.image.delete()

        new_image = ContentFile(raw_html)
        ode_model.image.save(f"{ode_model.name}_({ode_model.pk}).svg", new_image, save=True)
        ode_model.save()

    return JsonResponse({"error": "Must be a post method"})