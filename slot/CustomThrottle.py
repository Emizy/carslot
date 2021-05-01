import random

from rest_framework.throttling import AnonRateThrottle


class AnonTenRequestThrottle(AnonRateThrottle):
    scope = 'car_slot'
    rate = '10/10'

    def parse_rate(self, rate):
        if rate is None:
            return (None, None)
        num, period = rate.split('/')
        num_of_request = int(num)
        duration = period.replace('sec', ' ')
        return num_of_request, duration

    def allow_request(self, request, view):
        if self.rate is None:
            return True
        if request.user.is_authenticated:
            return None  # Only throttle unauthenticated requests.

        return self.cache_format % {
            'scope': self.scope,
            'ident': self.get_ident(request)
        }
