from django.urls import path
from . import views

urlpatterns = [


    path(
        '',
        views.rationale,
        name='rationale'),

    path(
        'list_models/',
        views.list_covid_models,
        name='list_covid_models'),

    path(
        'detail_ode/<int:ode_pk>/',
        views.detail_ode,
        name='detail_ode'),

    path(
        'save_ode/<int:ode_pk>/',
        views.save_ode,
        name='save_ode'),

    path(
        'save_ode_image/<int:ode_pk>/',
        views.save_ode_image,
        name='save_ode_image'),

    path(
        'new_ode/',
        views.new_ode,
        name='new_ode'),

    path(
        'solve_ode/',
        views.solve_ode_ajax,
        name='solve_ode_ajax'),

    path(
        'delete_ode/<int:ode_pk>',
        views.delete_ode,
        name='delete_ode'),

]