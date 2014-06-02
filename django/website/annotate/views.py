import datetime
import jwt
from django.conf import settings
from django.views.generic.base import View
from django.http import HttpResponse

from braces.views import LoginRequiredMixin

CONSUMER_KEY = settings.ANNOTATEIT_KEY
CONSUMER_SECRET = settings.ANNOTATEIT_SECRET
# Only change this if you're sure you know what you're doing
CONSUMER_TTL = 86400


def generate_token(user_id):
    now = datetime.datetime.utcnow().replace(microsecond=0)
    return jwt.encode({
        'consumerKey': CONSUMER_KEY,
        'userId': user_id,
        'issuedAt': now.isoformat() + 'Z',
        'ttl': CONSUMER_TTL},
        CONSUMER_SECRET)


class GetToken(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        token = generate_token(request.user.username)
        return HttpResponse(token)
