import json

from django.contrib.auth.decorators import login_required
from django.core.files.base import ContentFile
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect

from .forms import OdeForm, SimpleOdeForm
from .models import Ode


def _try_to_float(v):
    try:
        return float(v)
    except ValueError:
        return v


def rationale(request):
    """Used for the landing page this presents the core concept of the site.

    In the template rendering, it wants to provide an example of a saved image.
    In order for us to get that, we try and get the most recently edited ode,
    that has an image. This isn't exactly full proof, but this is pretty
    contrived to begin with. If no model exists that fits the criteria, then
    some place holder text is used.
    """
    ode_models = Ode.objects.exclude(Q(image=None)|Q(image='')).order_by('-edited')
    ode_model = ode_models.first()
    context = {'ode_model': ode_model}
    return render(request, 'covid/rationale.html', context)


@login_required
def list_covid_models(request):
    """This page lists out ODE models and allows you to create new ones"""
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
    """Updates an ode based on the form from the detail page

    In a practical setting, this should probably be called "update_ode" and use
    a update_or_create logic.
    """

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
    """A VERY simplistic API endpoint. This bad boy runs a simulation with the
    given parameters. If any of the parameters are missing, than it will use
    the default parameters for the ODE model.

    params = {
        "transmission_rate": 0.6,
        "recovery_rate": 0.1,
        "initial_percent_infected": 0.1,
        "max_t": 50
        }

    Note, we do not touch the database in this call. It is a very "pubic" api.
    >>> import requests
    >>> url = 'http://localhost:8000/solve_ode/'
    >>> data = {'transmission_rate': transmission_rate,
    >>>        'recovery_rate': recovery_rate,
    >>>        'initial_percent_infected': initial_percent_infected,
    >>>        'max_t': max_t}
    >>> requests.get(url, params=data).json()
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

    On every request, it solves the ODE and puts puts it in a data div.
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
    """Normally in a production setting, straight up deleting models like this
    is frowned upon. It is always safest practice to "deactivate" the model.
    """
    accessible_ode_models = Ode.objects.accessible(request.user)
    ode_model = get_object_or_404(accessible_ode_models, pk=ode_pk)
    ode_model.delete()
    return redirect('covid:list_covid_models')


@login_required
def save_ode_image(request, ode_pk):
    """Saves the svg file from the dom to the file system. This allows for the
    svgs to render in the rationale page. This is mostly an exercise in making
    a little more interesting endpoint"""

    if request.method == "POST":
        accessible_ode_models = Ode.objects.accessible(request.user)
        ode_model = get_object_or_404(accessible_ode_models, pk=ode_pk)
        raw_html = request.POST['html']

        # Keeping people's drives clean because I'm polite.
        if ode_model.image.name:
            ode_model.image.delete()

        new_image = ContentFile(raw_html)
        ode_model.image.save(f"{ode_model.name}_({ode_model.pk}).svg", new_image, save=True)
        ode_model.save()

    return JsonResponse({"error": "Must be a post method"})