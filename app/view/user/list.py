from django.shortcuts import get_object_or_404
from django.views.generic import ListView
from ..base.crud import BaseCrud
from ..models import User
from django.urls import reverse_lazy

class UserListView(BaseCrud, ListView):
    model = User
    template_name_suffix = 'list'
    template_prefix = 'user'
    context_object_name = 'users'
    paginate_by = 10
    
    def get_queryset(self):
        return User.objects.all().order_by('username')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'User List'
        return context
    
    def get_filtered_data(self):
        queryset = self.model.objects.all()
        filter_params = {}

        for key, value in self.request.GET.items():
            if key in [f.name for f in self.model._meta.fields]:
                filter_params[key] = value

        return queryset.filter(**filter_params).order_by('username')
    
    def get_user_by_id(self, user_id):
        user = get_object_or_404(User, user_id)
        return user
    
