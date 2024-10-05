from django import forms
from .models import Tracker, Client, DidTheyShow, Status

class TrackerForm(forms.ModelForm):
    class Meta:
        model = Tracker
        fields = [
            'client',
            'did_they_show',
            'date_scheduled',
            'meeting_date',
            'meeting_time',
            'time_zone',
            'appointment_handler',
            'company_name',
            'first_name',
            'last_name',
            'position',
            'phone_number',
            'lu_call_notes',
            'email',
            'lu_rep',
            'call_recording_link',
        ]
        widgets = {
            'date_scheduled': forms.DateInput(attrs={'type': 'date'}),
            'meeting_date': forms.DateInput(attrs={'type': 'date'}),
            'meeting_time': forms.TimeInput(attrs={'type': 'time'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Obter o ID do status "ativo"
        try:
            active_status = Status.objects.get(name='ativo')
            # Filtrar apenas clientes ativos
            self.fields['client'].queryset = Client.objects.filter(id_status=active_status.id)
        except Status.DoesNotExist:
            self.fields['client'].queryset = Client.objects.none()
        # Tornar `did_they_show` um dropdown com todas as opções
        self.fields['did_they_show'].queryset = DidTheyShow.objects.all()
