from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

class EquipmentUpload(models.Model):
    uploaded_at = models.DateTimeField(auto_now_add=True)
    csv_file = models.FileField(upload_to='uploads/')
    
    class Meta:
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"Upload {self.id} at {self.uploaded_at}"

@receiver(post_save, sender=EquipmentUpload)
def delete_old_uploads(sender, instance, created, **kwargs):
    if created:
        uploads = EquipmentUpload.objects.all()
        if uploads.count() > 5:
            old_uploads = uploads[5:]
            for old_upload in old_uploads:
                if old_upload.csv_file:
                    old_upload.csv_file.delete()
                old_upload.delete()
