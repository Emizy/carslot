from datetime import datetime
import pytz
from django.utils.timezone import make_aware

from rest_framework.test import APITestCase
from rest_framework.views import status

from slot.models import CarSlot


class CarSlotTestView(APITestCase):

    def test_create_slot(self):
        self.assertEquals(
            CarSlot.objects.count(),
            0
        )
        data = {
            'plate_number': '44-90-11',
        }
        response = self.client.post('http://127.0.0.1:8000/park/', data=data, format='json')
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)
        self.assertEquals(
            CarSlot.objects.count(),
            1
        )
        slot = CarSlot.objects.first()
        self.assertEquals(
            slot.plate_number,
            data['plate_number']
        )


class CarSlotGetDeleteTest(APITestCase):
    def setUp(self) -> None:
        self.slot = CarSlot(plate_number='22-42', slot_number=10,
                            date_created=make_aware(datetime.today(), timezone=pytz.timezone('Africa/Lagos')))
        self.slot.save()

    def get_test_slot(self):
        data = {
            'plate_number': '22-42'
        }
        response = self.client.get('http://127.0.0.1:8000/park/fetch_slot/', data=data, format='json')
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        payload = response.json()
        data = payload['data']
        self.assertEquals(
            data['slot_number'],
            int(self.slot.slot_number)
        )

    def test_delete_post(self):
        self.assertEquals(
            CarSlot.objects.count(),
            1
        )
        response = self.client.delete('http://127.0.0.1:8000/park/delete_slot/10/',
                                      format='json')
        self.assertEquals(
            response.status_code,
            status.HTTP_200_OK
        )
