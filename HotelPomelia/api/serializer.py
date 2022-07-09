from rest_framework.serializers import ModelSerializer
from .models import Energy

class EnergySerializer(ModelSerializer):
    class Meta:
        model = Energy
        fields = '__all__'