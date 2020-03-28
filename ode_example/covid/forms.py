from django import forms
from .models import Ode


class OdeForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._add_bootstrap()

    def _add_bootstrap(self):
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control input-block'

    class Meta:
        model = Ode
        fields = ['name',
                  'transmission_rate',
                  'recovery_rate',
                  'initial_percent_infected',
                  'max_t']

        widgets = {
            'transmission_rate': forms.NumberInput(attrs={'max': 10, 'min':0, 'step': '0.1'}),
            'recovery_rate': forms.NumberInput(attrs={'max': 10, 'min':0, 'step': '0.1'}),
        }
