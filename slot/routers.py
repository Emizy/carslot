from rest_framework import routers
from slot.views import CarSlotViewSet

router = routers.DefaultRouter()
router.register('park', CarSlotViewSet, basename='carslot')
