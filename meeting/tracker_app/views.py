from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.db import DatabaseError, connection  # Corrigir a importação de connection
from django.contrib.auth.decorators import login_required
from .models import Client, Status
import django.db.utils
from datetime import datetime
from django.urls import reverse


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
                    did_they_show INT REFERENCES did_they_show(id),
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
                did_they_show_value = tracker_instance.did_they_show.id if tracker_instance.did_they_show else None

                # Cast explícito para garantir que o valor seja tratado como int
                if did_they_show_value is not None:
                    did_they_show_value = int(did_they_show_value)
                print("Valor enviado para did_they_show:", tracker_instance.did_they_show.id if tracker_instance.did_they_show else None)

                insert_data_query = f"""
                INSERT INTO {table_name} (
                    did_they_show,
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
                   %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                );
                """
                cursor.execute(insert_data_query, [
                    did_they_show_value,
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
    client_name = request.GET.get('client_name', client_name)
    table_name = f"{client_name.lower().replace(' ', '_')}_meeting_tracker"

    if request.method == 'POST':
        try:
            with connection.cursor() as cursor:
                for key, value in request.POST.items():
                    if key.startswith('did_they_show_'):
                        entry_id = key.split('_')[-1]
                        # Atualizar did_they_show para a entrada específica
                        cursor.execute(f"""
                            UPDATE {table_name}
                            SET did_they_show = %s
                            WHERE id = %s
                        """, [value, entry_id])
        except DatabaseError as e:
            return render(request, 'tracker_app/client_data.html', {
                'client_name': client_name,
                'error_message': f"Erro ao atualizar a tabela: {e}"
            })

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

            # Buscar todos os dados da tabela do cliente com JOIN para obter o valor descritivo de did_they_show
            cursor.execute(f"""
                SELECT t.id, t.date_scheduled, t.meeting_date, t.meeting_time, 
                       t.time_zone, t.appointment_handler, t.company_name, 
                       t.first_name, t.last_name, t.position, t.phone_number, 
                       t.lu_call_notes, t.email, t.lu_rep, t.call_recording_link, 
                       COALESCE(d.option_name, '-') AS did_they_show_name
                FROM {table_name} t
                LEFT JOIN did_they_show d ON t.did_they_show = d.id
                ORDER BY t.id ASC
            """)
            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()

            # Criar uma lista de dicionários para facilitar o acesso no template
            data = [
                dict(zip(columns, row))
                for row in rows
            ]

    except DatabaseError as e:
        return render(request, 'tracker_app/client_data.html', {
            'client_name': client_name,
            'error_message': f"Erro ao acessar a tabela: {e}"
        })

    did_they_show_options = DidTheyShow.objects.all()

    return render(request, 'tracker_app/client_data.html', {
        'client_name': client_name,
        'columns': columns,
        'data': data,
        'did_they_show_options': did_they_show_options,
    })

@login_required
def edit_entry_view(request, client_name, entry_id):
    table_name = f"{client_name.lower().replace(' ', '_')}_meeting_tracker"
    
    if request.method == 'POST':
        updated_data = request.POST
        update_query = f"UPDATE {table_name} SET "
        params = []

        # Buscar os valores atuais para garantir que os campos obrigatórios sejam mantidos
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT * FROM {table_name} WHERE id = %s", [entry_id])
            current_row = cursor.fetchone()
            columns = [col[0] for col in cursor.description]
            current_data = dict(zip(columns, current_row))

        # Criar a query dinamicamente para cada coluna
        for column, value in updated_data.items():
            if column != 'csrfmiddlewaretoken' and column != 'id':
                if value == "":
                    # Se o campo for obrigatório, mantenha o valor atual do banco
                    if column in ['client', 'date_scheduled', 'company_name', 'first_name', 'last_name', 'email', 'lu_rep']:
                        value = current_data[column]
                    else:
                        value = None

                # Atualizar o valor na query
                if column == 'did_they_show' and value:
                    if DidTheyShow.objects.filter(id=value).exists():
                        update_query += f"{column} = %s, "
                        params.append(value)
                    else:
                        update_query += f"{column} = NULL, "
                elif value is None:
                    update_query += f"{column} = NULL, "
                else:
                    update_query += f"{column} = %s, "
                    params.append(value)

        update_query = update_query.rstrip(", ")
        update_query += " WHERE id = %s"
        params.append(entry_id)

        # Executar a query de atualização
        try:
            with connection.cursor() as cursor:
                cursor.execute(update_query, params)
        except DatabaseError as e:
            return render(request, 'tracker_app/edit_entry.html', {
                'client_name': client_name,
                'error_message': f"Erro ao atualizar a tabela: {e}",
                'column_value_pairs': [(column, value) for column, value in updated_data.items() if column != 'csrfmiddlewaretoken' and column != 'id'],
                'did_they_show_options': DidTheyShow.objects.all(),
                'current_did_they_show': updated_data.get('did_they_show', None)
            })
        return redirect('client_data', client_name=client_name)

    else:
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT * FROM {table_name} WHERE id = %s", [entry_id])
            row = cursor.fetchone()
            columns = [col[0] for col in cursor.description]

        # Formatar os valores de data e hora para o formato adequado
        column_value_pairs = []
        current_did_they_show = None
        if row:
            for col, val in zip(columns, row):
                if col == 'did_they_show':
                    current_did_they_show = val
                if col in ['date_scheduled', 'meeting_date'] and val:
                    val = val.strftime('%Y-%m-%d')
                elif col == 'meeting_time' and val:
                    val = val.strftime('%H:%M')
                column_value_pairs.append((col, val))

        return render(request, 'tracker_app/edit_entry.html', {
            'client_name': client_name,
            'column_value_pairs': [pair for pair in column_value_pairs if pair[0] != 'id'],  # Remover o campo 'id'
            'did_they_show_options': DidTheyShow.objects.all(),
            'current_did_they_show': current_did_they_show
        })