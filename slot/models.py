from django.db import models
import random
from carslot.settings import park_size


# CAR SLOT MODEL
class CarSlot(models.Model):
    slot_number = models.IntegerField(null=True, blank=True)
    plate_number = models.CharField(max_length=20, null=True, blank=True)
    date_created = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return "{0}-{1}".format(self.slot_number, self.plate_number)


def generate_slot_number(model):
    status = True
    context = {'slot': 0, 'status': False}
    while status is True:
        number = random.randint(1, int(park_size))
        if not model.objects.filter(slot_number=number).exists():
            status = False
            context.update({'status': True, 'slot': number})
        else:
            if model.objects.all().count() == int(park_size):
                status = False
                context.update({'status': False})
    return context
