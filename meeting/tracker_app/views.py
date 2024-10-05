from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.db import connection  # Corrigir a importação de connection

from .forms import TrackerForm
from .models import Client, Status, DidTheyShow

def tracker_form_view(request):
    if request.method == 'POST':
        form = TrackerForm(request.POST)
        if form.is_valid():
            tracker_instance = form.save()

            # Obter o nome do cliente selecionado
            client_name = tracker_instance.client.name.lower().replace(' ', '_')

            # Criar nome da tabela dinamicamente
            table_name = f"{client_name}_meeting_tracker"

            # Criar a tabela se ela não existir
            with connection.cursor() as cursor:
                create_table_query = f"""
                CREATE TABLE IF NOT EXISTS {table_name} (
                    id SERIAL PRIMARY KEY,
                    date_scheduled DATE NOT NULL,
                    meeting_date DATE,
                    meeting_time TIME,
                    time_zone VARCHAR(255),
                    appointment_handler VARCHAR(255),
                    company_name VARCHAR(255) NOT NULL,
                    first_name VARCHAR(255) NOT NULL,
                    last_name VARCHAR(255) NOT NULL,
                    position VARCHAR(255),
                    phone_number VARCHAR(255),
                    lu_call_notes TEXT,
                    email VARCHAR(255) NOT NULL,
                    lu_rep VARCHAR(255) NOT NULL,
                    call_recording_link VARCHAR(255)
                );
                """
                cursor.execute(create_table_query)

                # Inserir os dados na nova tabela
                insert_data_query = f"""
                INSERT INTO {table_name} (
                    date_scheduled,
                    meeting_date,
                    meeting_time,
                    time_zone,
                    appointment_handler,
                    company_name,
                    first_name,
                    last_name,
                    position,
                    phone_number,
                    lu_call_notes,
                    email,
                    lu_rep,
                    call_recording_link
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                );
                """
                cursor.execute(insert_data_query, [
                    tracker_instance.date_scheduled,
                    tracker_instance.meeting_date,
                    tracker_instance.meeting_time,
                    tracker_instance.time_zone,
                    tracker_instance.appointment_handler,
                    tracker_instance.company_name,
                    tracker_instance.first_name,
                    tracker_instance.last_name,
                    tracker_instance.position,
                    tracker_instance.phone_number,
                    tracker_instance.lu_call_notes,
                    tracker_instance.email,
                    tracker_instance.lu_rep,
                    tracker_instance.call_recording_link
                ])

            return redirect('tracker_success')
    else:
        form = TrackerForm()
        try:
            active_status = Status.objects.get(name='ativo')
            form.fields['client'].queryset = Client.objects.filter(id_status=active_status)
        except Status.DoesNotExist:
            form.fields['client'].queryset = Client.objects.none()

        form.fields['did_they_show'].queryset = DidTheyShow.objects.all()

    return render(request, 'tracker_app/tracker_form.html', {'form': form})

# View de sucesso
def tracker_success_view(request):
    return HttpResponse('<h1>Formulário enviado com sucesso!</h1>')
