from django.shortcuts import get_object_or_404
from django.views.generic import CreateView
from ..base.crud import BaseCrud
from ..models import User
from django.urls import reverse_lazy

class UserCreateView(BaseCrud, CreateView):
    model = User
    template_name_suffix = 'create'
    template_prefix = 'user'
    fields = ['username', 'email', 'first_name', 'last_name', 'password', 
              'spouse_name', 'dob', 'age', 'mother_tongue', 
              'address', 'qualification']
    success_url = reverse_lazy('user:list')

    def form_valid(self, form):
        form.instance.set_password(form.cleaned_data['password'])
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create User'
        return context
    
    
