from django.test import TestCase, Client
from django.urls import reverse_lazy
from django.contrib.messages import get_messages
from django.utils.translation import gettext
from django import test

from task_manager.auth.models import User
from task_manager.tests.utils import TestUserMixin, PASSWORD
from task_manager.tasks.models import TaskModel


@test.modify_settings(
    MIDDLEWARE={
        "remove": [
            "rollbar.contrib.django.middleware.RollbarNotifierMiddleware",
        ]
    }
)
class TestViews(TestCase, TestUserMixin):
    def setUp(self):
        self.user_1 = self.create_test_user_1()
        self.user_2 = self.create_test_user_2()
        self.client = Client()
        self.registration_url = reverse_lazy("register")
        self.betrayer_message = gettext("You are betrayer")
        self.all_users_url = reverse_lazy("all_users")

    def test_register_user_GET(self):
        response = self.client.get(self.registration_url)

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, "auth/SignUpPage.html")

    def test_register_user_POST_success_reg(self):
        response = self.client.post(
            self.registration_url,
            {
                "username": "ddenis",
                "first_name": "den",
                "last_name": "cos",
                "password1": "asdasd11Asd",
                "password2": "asdasd11Asd",
            },
        )

        self.assertEquals(response.status_code, 302)
        self.assertTrue(User.objects.get(username="ddenis"))

    def test_update_user_GET_owner(self):
        self.client.login(username=self.user_1.username, password=PASSWORD)
        response = self.client.get(
            reverse_lazy("update_user", kwargs={"pk": self.user_1.pk})
        )

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, "auth/UpdateUserPage.html")

    def test_update_user_GET_betrayer(self):
        self.client.login(username=self.user_2.username, password=PASSWORD)
        response = self.client.get(
            reverse_lazy("update_user", kwargs={"pk": self.user_1.pk})
        )
        messages = list(get_messages(response.wsgi_request))

        self.assertEquals(response.status_code, 302)
        self.assertEquals(len(messages), 1)
        self.assertEquals(str(messages[0]), self.betrayer_message)
        self.assertRedirects(response, self.all_users_url)

    def test_update_user_POST(self):
        self.client.login(username=self.user_1.username, password=PASSWORD)
        response = self.client.post(
            reverse_lazy("update_user", kwargs={"pk": self.user_1.pk}),
            {
                "first_name": "some_f_name",
                "last_name": "some_l_name",
                "username": self.user_1.username,
                "password1": PASSWORD,
                "password2": PASSWORD,
            },
        )
        messages = list(get_messages(response.wsgi_request))

        self.assertEquals(response.status_code, 302)
        self.assertEquals(len(messages), 1)
        self.assertEquals(str(messages[0]), gettext("User changed successfully"))
        self.assertTrue(
            User.objects.get(username=self.user_1.username, first_name="some_f_name")
        )
        self.assertRedirects(response, self.all_users_url)

    def test_delete_user_GET_owner(self):
        self.client.login(username=self.user_1.username, password=PASSWORD)
        response = self.client.get(
            reverse_lazy("delete_user", kwargs={"pk": self.user_1.pk})
        )

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, "auth/DeletePage.html")

    def test_delete_user_GET_betrayer(self):
        self.client.login(username=self.user_2.username, password=PASSWORD)
        response = self.client.get(
            reverse_lazy("delete_user", kwargs={"pk": self.user_1.pk})
        )
        messages = list(get_messages(response.wsgi_request))

        self.assertEquals(response.status_code, 302)
        self.assertEquals(len(messages), 1)
        self.assertEquals(str(messages[0]), self.betrayer_message)
        self.assertRedirects(response, self.all_users_url)

    def test_delete_user_POST_free_owner(self):
        self.client.login(username=self.user_1.username, password=PASSWORD)
        response = self.client.post(
            reverse_lazy("delete_user", kwargs={"pk": self.user_1.pk})
        )
        messages = list(get_messages(response.wsgi_request))

        self.assertEquals(response.status_code, 302)
        self.assertEquals(len(messages), 1)
        self.assertEquals(str(messages[0]), gettext("User deleted"))
        self.assertRedirects(response, self.all_users_url)
        self.assertFalse(User.objects.filter(pk=self.user_1.pk).exists())

    def test_delete_user_POST_author_task(self):
        self.client.login(username=self.user_1.username, password=PASSWORD)

        task = TaskModel.objects.create(
            name="asd",
            description="asd",
            status=self.create_test_status_1(),
            executor=self.user_1,
            author=self.user_1,
        )
        task.save()

        response = self.client.post(
            reverse_lazy("delete_user", kwargs={"pk": self.user_1.pk})
        )
        message = list(get_messages(response.wsgi_request))

        self.assertEquals(response.status_code, 302)
        self.assertEquals(len(message), 1)
        self.assertEquals(
            str(message[0]), gettext("Cannot delete user because it's in use")
        )
        self.assertRedirects(response, self.all_users_url)

    def test_delete_user_POST_betrayer(self):
        self.client.login(username=self.user_2.username, password=PASSWORD)
        response = self.client.post(
            reverse_lazy("delete_user", kwargs={"pk": self.user_1.pk})
        )
        message = list(get_messages(response.wsgi_request))

        self.assertEquals(response.status_code, 302)
        self.assertEquals(len(message), 1)
        self.assertEquals(str(message[0]), self.betrayer_message)
        self.assertRedirects(response, self.all_users_url)