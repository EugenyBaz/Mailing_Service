from django.test import TestCase, Client
from django.urls import reverse

from mail.models import Mail
from users.models import User


class MailTestCase(TestCase):

    def setUp(self):

        self.user= User.objects.create(email= "test@test.com")

        self.client = Client()

        self.mail = Mail.objects.create(
            author=self.user,
            subject_letter="Test invitation",
            body_letter="Hello!"
        )

        self.client = Client()
        self.client.force_login(self.user)

    def test_mail_retrieve(self):
        url = reverse("mail:mail_detail", args=(self.mail.pk,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.mail.subject_letter)