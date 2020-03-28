from django.urls import path
from . import views

urlpatterns = [

    path(
        '',
        views.list_covid_models,
        name='list_covid_models'),

    path(
        'list_models/',
        views.list_covid_models,
        name='list_covid_models'),

    path(
        'detail_ode/<int:ode_pk>/',
        views.detail_ode,
        name='detail_ode'),

]