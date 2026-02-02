from rest_framework import serializers
from .models import EquipmentUpload

class EquipmentUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = EquipmentUpload
        fields = ['id', 'uploaded_at', 'csv_file']
        read_only_fields = ['id', 'uploaded_at']
