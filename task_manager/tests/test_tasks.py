from django.test import TestCase, Client
from django.urls import reverse_lazy
from django.contrib.messages import get_messages
from django.utils.translation import gettext
from django import test

from task_manager.tasks.models import TaskModel
from task_manager.tests.utils import TestUserMixin, PASSWORD


@test.modify_settings(
    MIDDLEWARE={
        "remove": [
            "rollbar.contrib.django.middleware.RollbarNotifierMiddleware",
        ]
    }
)
class TestView(TestCase, TestUserMixin):
    def setUp(self) -> None:
        self.client = Client()
        self.user_1 = self.create_test_user_1()
        self.user_2 = self.create_test_user_2()
        self.status = self.create_test_status_1()
        self.label_1 = self.create_test_label_1()
        self.label_2 = self.create_test_label_2()
        self.task = self.create_test_task_1()
        self.all_tasks_url = reverse_lazy("all_tasks")

    def create_test_task_1(self):
        user = self.user_1
        task = TaskModel.objects.create(
            name="asd",
            description="asd",
            status=self.status,
            executor=user,
            author=user,
        )
        task.labels.set([self.label_1, self.label_2])
        task.save()
        return task

    def test_create_task_GET(self):
        self.client.login(username=self.user_1.username, password=PASSWORD)
        response = self.client.get(reverse_lazy("create_task"))

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, "tasks/CreationPage.html")

    def test_create_task_POST(self):
        self.client.login(username=self.user_2.username, password=PASSWORD)
        response = self.client.post(
            reverse_lazy("create_task"),
            {
                "name": "task",
                "description": "description",
                "status": self.status.pk,
                "executor": self.user_2.pk,
                "labels": [self.label_1.pk, self.label_2.pk],
            },
        )
        message = list(get_messages(response.wsgi_request))

        self.assertEquals(response.status_code, 302)
        self.assertEquals(len(message), 1)
        self.assertEquals(str(message[0]), gettext("Task created"))
        self.assertRedirects(response, self.all_tasks_url)
        self.assertEquals(
            TaskModel.objects.get(
                name="task",
                status=self.status,
                author=self.user_2.pk,
                labels=self.label_1.pk,
            ),
            TaskModel.objects.get(author=self.user_2.pk, labels=self.label_2.pk),
        )

    def test_update_task_GET(self):
        self.client.login(username=self.user_1.username, password=PASSWORD)
        response = self.client.get(
            reverse_lazy("update_task", kwargs={"pk": self.task.pk})
        )

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, "tasks/UpdatePage.html")

    def test_update_task_POST(self):
        self.client.login(username=self.user_1.username, password=PASSWORD)
        response = self.client.post(
            reverse_lazy("update_task", kwargs={"pk": self.task.pk}),
            {
                "name": "new_test_name",
                "description": "description",
                "executor": self.user_2.pk,
                "status": self.status.pk,
                "labels": self.label_1.pk,
            },
        )
        message = list(get_messages(response.wsgi_request))

        self.assertEquals(response.status_code, 302)
        self.assertEquals(len(message), 1)
        self.assertEquals(str(message[0]), gettext("Task updated"))
        self.assertRedirects(response, self.all_tasks_url)
        self.assertTrue(TaskModel.objects.get(name="new_test_name"))
        self.assertFalse(TaskModel.objects.filter(labels=self.label_2))

    def test_delete_task_GET_owner(self):
        self.client.login(username=self.user_1.username, password=PASSWORD)
        response = self.client.get(
            reverse_lazy("delete_task", kwargs={"pk": self.task.pk})
        )

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, "tasks/DeletePage.html")

    def test_delete_task_GET_betrayer(self):
        self.client.login(username=self.user_2.username, password=PASSWORD)
        response = self.client.get(
            reverse_lazy("delete_task", kwargs={"pk": self.task.pk})
        )
        message = list(get_messages(response.wsgi_request))

        self.assertEquals(response.status_code, 302)
        self.assertRedirects(response, self.all_tasks_url)
        self.assertEquals(len(message), 1)
        self.assertEquals(
            str(message[0]), gettext("A task can only be deleted by its author.")
        )

    def test_delete_task_POST_owner(self):
        self.client.login(username=self.user_1.username, password=PASSWORD)
        response = self.client.post(
            reverse_lazy("delete_task", kwargs={"pk": self.task.pk})
        )
        message = list(get_messages(response.wsgi_request))

        self.assertEquals(response.status_code, 302)
        self.assertEquals(len(message), 1)
        self.assertEquals(str(message[0]), gettext("Task deleted"))
        self.assertRedirects(response, self.all_tasks_url)
        self.assertFalse(TaskModel.objects.filter(pk=self.task.pk).exists())

    def test_delete_task_POST_betrayer(self):
        self.client.login(username=self.user_2.username, password=PASSWORD)
        response = self.client.post(
            reverse_lazy("delete_task", kwargs={"pk": self.task.pk})
        )
        message = list(get_messages(response.wsgi_request))

        self.assertEquals(response.status_code, 302)
        self.assertRedirects(response, self.all_tasks_url)
        self.assertEquals(len(message), 1)
        self.assertEquals(
            str(message[0]), gettext("A task can only be deleted by its author.")
        )