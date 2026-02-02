from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

class EquipmentUpload(models.Model):
    uploaded_at = models.DateTimeField(auto_now_add=True)
    csv_file = models.FileField(upload_to='uploads/')
    total_equipment = models.IntegerField(default=0)
    average_flowrate = models.FloatField(default=0.0)
    average_pressure = models.FloatField(default=0.0)
    average_temperature = models.FloatField(default=0.0)
    
    class Meta:
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"Upload {self.id} at {self.uploaded_at}"

@receiver(post_save, sender=EquipmentUpload)
def delete_old_uploads(sender, instance, created, **kwargs):
    if created:
        uploads = EquipmentUpload.objects.order_by('uploaded_at')
        extra_count = uploads.count() - 5
        if extra_count > 0:
            # Delete oldest uploads beyond the last 5, including CSV files.
            for old_upload in uploads[:extra_count]:
                if old_upload.csv_file:
                    old_upload.csv_file.delete()
                old_upload.delete()
