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
        
        # Definir os campos obrigatórios
        self.fields['client'].required = True
        self.fields['date_scheduled'].required = True
        self.fields['company_name'].required = True
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['email'].required = True
        self.fields['lu_rep'].required = True

        # Definir os campos não obrigatórios
        self.fields['did_they_show'].required = False
        self.fields['meeting_date'].required = False
        self.fields['meeting_time'].required = False
        self.fields['time_zone'].required = False
        self.fields['appointment_handler'].required = False
        self.fields['position'].required = False
        self.fields['phone_number'].required = False
        self.fields['lu_call_notes'].required = False
        self.fields['call_recording_link'].required = False
