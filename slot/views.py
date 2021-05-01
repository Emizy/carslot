from django.db.models import Q
from django.shortcuts import get_object_or_404
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from datetime import datetime
import pytz
from django.utils.timezone import make_aware
from rest_framework.decorators import action
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework.decorators import throttle_classes
from rest_framework.viewsets import ModelViewSet, ViewSet

from slot.CustomThrottle import AnonTenRequestThrottle
from slot.models import CarSlot, generate_slot_number
from slot.serializer import CarSlotSerializer
from carslot.settings import park_size


class CarSlotViewSet(ViewSet):
    parser_class = (JSONParser,)
    queryset = CarSlot.objects.all()
    serializer_class = CarSlotSerializer
    create_response = {
        201: openapi.Response(
            description="CREATED",
            examples={
                "application/json": {
                    "status": 201,
                    "message": "CREATED",
                    "data": {
                        "id": 1,
                        "slot_number": "1",
                        "plate_number": "www-043-11",
                        "date_created": "17/04/2021 02:35 PM"
                    },
                }
            }
        ),

    }
    fetch_response = {
        200: openapi.Response(
            description="OK",
            examples={
                "application/json": {
                    "status": 200,
                    "message": "ok",
                    "data": {
                        "id": 1,
                        "slot_number": "1",
                        "plate_number": "www-043-11",
                        "date_created": "17/04/2021 02:35 PM"
                    },
                }
            }
        ),

    }

    @staticmethod
    def get_data(request) -> dict:
        return request.data if isinstance(request.data, dict) else request.data.dict()

    @action(detail=False,
            methods=['get'],
            description='Retrieve slot information',
            url_path=r'fetch_slot/(?P<number>[^/]+)',
            url_name="Get slot information"
            )
    @swagger_auto_schema(operation_description="*GET SLOT INFORMATION*: This allow users to get "
                                               "slot  information after inputting their plate number or slot number",
                         operation_summary='GET SLOT INFORMATION')
    def fetch_slot(self, request, number=None):
        try:
            try:
                instance = CarSlot.objects.get(slot_number=number)
            except:
                instance = None
            if instance:
                context = {'status': status.HTTP_200_OK,
                           'message': 'OK',
                           'data': self.serializer_class(instance).data
                           }
            else:
                slot = CarSlot.objects.filter(plate_number=number).first()
                if CarSlot.objects.filter(plate_number=number).exists():
                    context = {'status': status.HTTP_200_OK,
                               'message': 'OK',
                               'data': self.serializer_class(slot).data
                               }
                else:
                    context = {'status': status.HTTP_400_BAD_REQUEST, 'message': 'NO_CONTENT.'}
        except Exception as ex:
            print(ex)
            context = {'status': status.HTTP_400_BAD_REQUEST, 'message': 'NO_CONTENT.'}
        return Response(context, status=context['status'])

    @swagger_auto_schema(request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'plate_number': openapi.Schema(type=openapi.TYPE_STRING, description='')
        }
    ), operation_description="*GENERATE SLOT NUMBER*: This allow users to get "
                             "slot  number after inputting their plate number",
        operation_summary='CREATE SLOT NUMBER',
        responses={**create_response})
    @throttle_classes([AnonTenRequestThrottle])
    def create(self, request, *args, **kwargs):
        try:
            data = self.get_data(request)
            if data.get('plate_number') is None:
                return Response(
                    {'status': status.HTTP_400_BAD_REQUEST, 'message': "Kindly supply a valid plate  number"},
                    status=status.HTTP_400_BAD_REQUEST)
            if self.queryset.filter(plate_number=data.get('plate_number')).exists():
                return Response({'status': status.HTTP_400_BAD_REQUEST,
                                 'message': "You currently have an allocated slot for this car"},
                                status=status.HTTP_400_BAD_REQUEST)
                # check if there is any empty slot number
            if self.queryset.filter(plate_number__isnull=True).exists():
                exist_slot = self.queryset.filter(plate_number__isnull=True).first()
                exist_slot.__setattr__('plate_number', data.get('plate_number'))
                exist_slot.__setattr__('date_created',
                                       make_aware(datetime.today(), timezone=pytz.timezone('Africa/Lagos')))
                exist_slot.save()
                return Response(
                    {'status': status.HTTP_201_CREATED, 'message': 'SLOT CREATED',
                     'data': self.serializer_class(exist_slot).data}, status=status.HTTP_201_CREATED)
            # check if the slot is full
            if self.queryset.filter(plate_number__isnull=False).count() == int(park_size):
                return Response({'status': status.HTTP_400_BAD_REQUEST, 'message': "Parking lot currently filled up"},
                                status=status.HTTP_400_BAD_REQUEST)

            slot = generate_slot_number(CarSlot)
            if slot['status']:
                payload = {'slot_number': slot['slot'], 'plate_number': data.get('plate_number'),
                           'date_created': make_aware(datetime.today(), timezone=pytz.timezone('Africa/Lagos'))}
                serialize = self.serializer_class(data=payload)
                if serialize.is_valid():
                    obj = serialize.save()
                    return Response(
                        {'status': status.HTTP_201_CREATED, 'message': 'SLOT CREATED',
                         'data': self.serializer_class(obj).data}, status=status.HTTP_201_CREATED)
                else:
                    return Response({'status': status.HTTP_400_BAD_REQUEST, 'message': 'Supplied data not valid'},
                                    status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'status': status.HTTP_400_BAD_REQUEST, 'message': 'Supplied data not valid'},
                                status=status.HTTP_400_BAD_REQUEST)
        except Exception as ex:
            return Response({'status': status.HTTP_400_BAD_REQUEST,
                             'message': 'Something went wrong while processing your request'},
                            status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['delete'], description='Delete a slot by supplying the slot id',
            url_path=r'delete_slot/(?P<slot_number>[^/]+)', url_name='Empty slot endpoint')
    @swagger_auto_schema(
        operation_description="*DE-ALLOCATE A SLOT*: This endpoint accept slot number and de-allocate the plate-number assign to the slot",
        operation_summary='DELETE SLOT')
    def delete_slot(self, request, slot_number=None):
        context = {'status': status.HTTP_400_BAD_REQUEST}
        try:
            if self.queryset.filter(slot_number=slot_number).exists():
                instance = self.queryset.get(slot_number=slot_number)
                instance.__setattr__('plate_number', None)
                instance.save()
                context.update({'status': status.HTTP_200_OK, 'message': 'Car slot unpacked'})
            else:
                context.update(
                    {'status': status.HTTP_400_BAD_REQUEST, 'message': 'Kindly provide a valid slot number'})
        except:
            context.update(
                {'status': status.HTTP_400_BAD_REQUEST, 'message': 'Something went wrong while performing this action'})
        return Response(context, status=context['status'])
