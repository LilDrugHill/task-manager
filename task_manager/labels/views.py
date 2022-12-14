from django.contrib import messages
from django.shortcuts import redirect
from django.views.generic import CreateView, ListView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.contrib.messages.views import SuccessMessageMixin

from task_manager.labels.forms import LabelForm
from task_manager.utils import CustomLoginRequiredMixin
from task_manager.labels.models import LabelModel


class ShowAllLabels(CustomLoginRequiredMixin, ListView):
    model = LabelModel
    template_name = "labels/PageWithAll.html"
    login_url = reverse_lazy("login")


class CreateLabel(CustomLoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = LabelModel
    form_class = LabelForm

    template_name = "labels/CreationPage.html"
    login_url = reverse_lazy("login")
    success_url = reverse_lazy("all_labels")
    success_message = _("Label created")


class UpdateLabel(CustomLoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = LabelModel
    form_class = LabelForm

    template_name = "labels/UpdatePage.html"
    login_url = reverse_lazy("login")
    success_url = reverse_lazy("all_labels")
    success_message = _("Label updated")


class DeleteLabel(
    CustomLoginRequiredMixin,
    SuccessMessageMixin,
    DeleteView,
):
    model = LabelModel
    success_message = _("Label deleted")
    success_url = reverse_lazy("all_labels")
    template_name = "labels/DeletePage.html"
    login_url = reverse_lazy("login")

    def post(self, request, *args, **kwargs):
        if self.get_object().taskmodel_set.exists():
            messages.add_message(
                request,
                messages.ERROR,
                _("Can't delete label because it's in use"),
            )
            return redirect(self.success_url)
        else:
            return super(DeleteLabel, self).post(request, *args, **kwargs)
