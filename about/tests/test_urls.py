from django.test import Client, TestCase


class StaticURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        """ Создание группы для теста. """
        super().setUpClass()
        cls.guest_client = Client()
        cls.urls = ['/about/author/', '/about/tech/']

    def test_access_urls(self):
        for url in StaticURLTests.urls:
            response = StaticURLTests.guest_client.get(url)
            self.assertEqual(response.status_code, 200)
