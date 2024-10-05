from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.db import DatabaseError, connection  # Corrigir a importação de connection
from django.contrib.auth.decorators import login_required
from .models import Client, Status
import django.db.utils
from datetime import datetime


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
    return render(request, 'tracker_app/tracker_success.html')

@login_required
def select_client_view(request):
    try:
        active_status = Status.objects.get(name='ativo')
        clients = Client.objects.filter(id_status=active_status)
    except Status.DoesNotExist:
        clients = Client.objects.none()
    return render(request, 'tracker_app/select_client.html', {'clients': clients})

@login_required
def client_data_view(request, client_name):
    # Obter o valor de client_name a partir do parâmetro GET
    client_name = request.GET.get('client_name', client_name)

    # Certificar que o nome está em minúsculas e sem espaços
    table_name = f"{client_name.lower().replace(' ', '_')}_meeting_tracker"

    try:
        with connection.cursor() as cursor:
            # Verificar se a tabela existe antes de buscar os dados
            cursor.execute(f"""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = %s
                )
            """, [table_name])
            if not cursor.fetchone()[0]:
                return render(request, 'tracker_app/client_data.html', {
                    'client_name': client_name,
                    'error_message': f"Tabela '{table_name}' não encontrada."
                })

            # Buscar todos os dados da tabela do cliente
            cursor.execute(f"SELECT * FROM {table_name}")
            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()

    except DatabaseError as e:
        return render(request, 'tracker_app/client_data.html', {
            'client_name': client_name,
            'error_message': f"Erro ao acessar a tabela: {e}"
        })

    return render(request, 'tracker_app/client_data.html', {
        'client_name': client_name,
        'columns': columns,
        'rows': rows
    })

@login_required
def edit_entry_view(request, client_name, entry_id):
    table_name = f"{client_name.lower().replace(' ', '_')}_meeting_tracker"
    
    if request.method == 'POST':
        # Atualizar os dados do formulário
        updated_data = request.POST
        update_query = f"UPDATE {table_name} SET "
        params = []

        # Criar a query dinamicamente para cada coluna
        for column, value in updated_data.items():
            if column != 'csrfmiddlewaretoken':
                # Verificar se o valor está vazio e definir como NULL se necessário
                if value == "":
                    update_query += f"{column} = NULL, "
                else:
                    update_query += f"{column} = %s, "
                    params.append(value)

        # Remover a última vírgula e espaço
        update_query = update_query.rstrip(", ")
        update_query += " WHERE id = %s"
        params.append(entry_id)

        try:
            with connection.cursor() as cursor:
                cursor.execute(update_query, params)
        except DatabaseError as e:
            return render(request, 'tracker_app/edit_entry.html', {
                'client_name': client_name,
                'error_message': f"Erro ao atualizar a tabela: {e}",
                'column_value_pairs': [(column, value) for column, value in updated_data.items() if column != 'csrfmiddlewaretoken']
            })
        return redirect('client_data', client_name=client_name)

    else:
        # Buscar os dados para preencher o formulário
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT * FROM {table_name} WHERE id = %s", [entry_id])
            row = cursor.fetchone()
            columns = [col[0] for col in cursor.description]

        column_value_pairs = list(zip(columns, row)) if row else []

        return render(request, 'tracker_app/edit_entry.html', {
            'client_name': client_name,
            'column_value_pairs': column_value_pairs
        })
