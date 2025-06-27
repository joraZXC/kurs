from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.contrib import messages
from django.http import HttpResponseRedirect

class CustomLoginView(LoginView):
    template_name = 'registration/login.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        user = form.get_user()
        role = self.request.GET.get('role', 'user') 


        if user.is_staff and role == 'user':
            messages.error(self.request, "Администраторы не могут входить как обычные пользователи.")
            return HttpResponseRedirect(self.request.path)

   
        if not user.is_staff and role == 'admin':
            messages.error(self.request, "Обычные пользователи не могут входить как администраторы.")
            return HttpResponseRedirect(self.request.path)

        return super().form_valid(form)

    def get_success_url(self):
        next_url = self.request.GET.get('next')
        if next_url:
            return next_url
        return super().get_success_url()