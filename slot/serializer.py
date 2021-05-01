from rest_framework import serializers
from slot.models import CarSlot


# CarSlot Serializer definition begins here.
class CarSlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarSlot
        fields = ['slot_number', 'plate_number', 'date_created']
