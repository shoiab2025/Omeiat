from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.http import HttpResponseServerError
import logging

logger = logging.getLogger(__name__)

class BaseCrud:
    model = None
    form_class = None
    template_prefix = ''
    success_url = None

    def get_template_names(self):
        return [f"{self.template_prefix}/{self.template_name_suffix}.html"]

    def get_success_url(self):
        return self.success_url or reverse_lazy(f"{self.template_prefix}-list")
    
    def form_invalid(self, form):
        logger.warning(f"Form invalid for {self.model.__name__}: {form.errors}")
        return super().form_invalid(form)