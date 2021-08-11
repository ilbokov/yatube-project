from django.test import Client, TestCase
from django.urls import reverse


class ViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        """ Создание тестовой группы, польователя и поста. """
        super().setUpClass()
        cls.guest_client = Client()
        cls.author_reverse = reverse('about:author')
        cls.tech_reverse = reverse('about:tech')

    def test_pages_uses_correct_templates(self):
        """ Тест вывода корректных шаблонов для view-функций. """
        templates_pages_names = {
            'about/author.html': (
                ViewsTests.author_reverse
            ),
            'about/tech.html': (
                ViewsTests.tech_reverse
            )
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = ViewsTests.guest_client.get(reverse_name)
                self.assertTemplateUsed(response, template)
