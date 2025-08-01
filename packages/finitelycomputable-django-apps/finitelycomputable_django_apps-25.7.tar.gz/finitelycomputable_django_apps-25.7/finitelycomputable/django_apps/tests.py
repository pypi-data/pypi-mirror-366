from django.test import Client, TestCase

class DjangoAppsTest(TestCase):
    def setUp(self):
        self.c = Client()

    def test_wsgi_info(self):
        resp = self.c.get('/wsgi_info/')
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, b'using finitelycomputable.django_apps')
