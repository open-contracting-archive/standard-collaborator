from django.http import HttpResponseRedirect
from registration.backends.simple.views import RegistrationView


class CustomRegistrationView(RegistrationView):
    def get_success_url(self, *args, **kwargs):
        return self.next

    def post(self, request, *args, **kwargs):
        self.next = request.POST.get('next')
        return super(CustomRegistrationView,
                     self).post(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        self.next = request.GET.get('next')
        return super(CustomRegistrationView,
                     self).get(request, *args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        context = super(CustomRegistrationView,
                        self).get_context_data(*args, **kwargs)
        context['next'] = self.next
        return context
