import django_filters
from django.utils.translation import gettext_lazy as _
from django import forms

from task_manager.labels.models import LabelModel
from task_manager.statuses.models import StatusModel
from task_manager.auth.models import UserStr
from task_manager.tasks.forms import TaskModel


class TaskFilter(django_filters.FilterSet):
    label = django_filters.ModelChoiceFilter(
        field_name="labels",
        queryset=LabelModel.objects.all(),
        label=_("Label"),
        widget=forms.Select(attrs={"class": "form-control mr-3 ml-2"}),
    )
    status = django_filters.ModelChoiceFilter(
        field_name="status",
        queryset=StatusModel.objects.all(),
        label=_("Status"),
        widget=forms.Select(attrs={"class": "form-control mr-3 ml-2"}),
    )
    executor = django_filters.ModelChoiceFilter(
        field_name="executor",
        queryset=UserStr.objects.all(),
        label=_("Executor"),
        widget=forms.Select(attrs={"class": "form-control mr-3 ml-2"}),
    )

    self_task = django_filters.BooleanFilter(
        method="show_self_task",
        widget=forms.CheckboxInput(attrs={"class": "form-check-input mr-1 ml-2"}),
        label=_("Only own tasks"),
    )

    class Meta:
        model = TaskModel
        fields = ()

    def show_self_task(self, queryset, name, value):
        if value is True:
            return queryset.filter(author_id=self.request.user.pk)
        return queryset
