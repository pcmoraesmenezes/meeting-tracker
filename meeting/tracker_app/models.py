from django.db import models

class Status(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class Client(models.Model):
    name = models.CharField(max_length=255)
    id_status = models.ForeignKey(Status, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class DidTheyShow(models.Model):
    option_name = models.CharField(max_length=255)  # Alterei o nome do campo

    def __str__(self):
        return self.option_name

class Tracker(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    did_they_show = models.ForeignKey(DidTheyShow, on_delete=models.SET_NULL, null=True)
    date_scheduled = models.DateField()
    meeting_date = models.DateField(null=True, blank=True)
    meeting_time = models.TimeField(null=True, blank=True)
    time_zone = models.CharField(max_length=255, null=True, blank=True)
    appointment_handler = models.CharField(max_length=255, null=True, blank=True)
    company_name = models.CharField(max_length=255)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    position = models.CharField(max_length=255, null=True, blank=True)
    phone_number = models.CharField(max_length=255, null=True, blank=True)
    lu_call_notes = models.TextField(null=True, blank=True)
    email = models.CharField(max_length=255)
    lu_rep = models.CharField(max_length=255)
    call_recording_link = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"{self.client.name} - {self.company_name}"
