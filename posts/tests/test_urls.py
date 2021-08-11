# posts/tests/test_urls.py
from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Group, Post


class StaticURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        """ Создание группы для теста. """
        super().setUpClass()

        cls.guest_client = Client()
        cls.authorized_client = Client()

        cls.user_with_post = User.objects.create_user(username='test_w_post')
        cls.user_without_post = User.objects.create_user(
            username='test_without_post')

        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-group',
            description='Описание тестовой группы'
        )

        cls.post = Post.objects.create(
            text='Тестовый пост',
            group=cls.group,
            author=cls.user_with_post
        )
        # Объявление статичных url
        cls.new_login_url = '/auth/login/?next=/new'
        cls.new_reverse = reverse('new_post')
        cls.error404_reverse = '/404'

    def setUp(self):
        # Объявление зависимых url
        self.post_edit_reverse = reverse('post_edit', kwargs={
            'username': StaticURLTests.user_with_post.username,
            'post_id': StaticURLTests.post.id})
        self.post_reverse = reverse('post', kwargs={
            'username': StaticURLTests.user_with_post.username,
            'post_id': StaticURLTests.post.id})
        self.edit_login_url = (
            "/auth/login/?next=/"
            f"{StaticURLTests.user_with_post.username}/"
            f"{StaticURLTests.post.id}/edit/")
        # Список url
        self.urls_list = {
            f"/{StaticURLTests.user_with_post.username}/"
            f"{StaticURLTests.post.id}/":
                'templates/post.html',
            f"/{StaticURLTests.user_with_post.username}/"
            f"{StaticURLTests.post.id}/edit/":
                'templates/new_post.html',
            '': 'templates/index.html',
            '/new': 'templates/new_post.html',
            f"/group/{StaticURLTests.group.slug}/": 'templates/group.html',
            f"/{StaticURLTests.user_with_post.username}/":
                'templates/profile.html',
        }

    def test_access_urls(self):
        """ Тестирование доступа страниц. """
        StaticURLTests.authorized_client.force_login(
            StaticURLTests.user_with_post)
        # Тестирование доступа от авторизованного пользователя
        for url in self.urls_list.keys():
            with self.subTest():
                response = StaticURLTests.authorized_client.get(url)
                self.assertEqual(
                    response.status_code,
                    200,
                    f"Недоступна страница по адресу '{url}'")

        # Тестирование недоступности страницы /new для
        # неавторизованного пользователя
        non_auth_response = StaticURLTests.guest_client.get(
            StaticURLTests.new_reverse)
        self.assertRedirects(non_auth_response, StaticURLTests.new_login_url)

        # Тестироване недоступности страницы /edit для
        # неавторизованного пользователя
        non_auth_response = StaticURLTests.guest_client.get(
            self.post_edit_reverse,
            follow=True)
        self.assertRedirects(
            non_auth_response,
            self.edit_login_url)

        # тестирование недостпуности страницы для пользователя без авторства
        StaticURLTests.authorized_client.force_login(
            StaticURLTests.user_without_post)
        non_author_response = StaticURLTests.authorized_client.get(
            self.post_edit_reverse,
            follow=True)
        self.assertRedirects(
            non_author_response,
            self.post_reverse)

        # Тестирование возврата кода 404,
        # при вызове несуществующей страницы
        response = StaticURLTests.authorized_client.get(
            StaticURLTests.error404_reverse,
            follow=True)
        self.assertEqual(response.status_code, 404)

    def test_correct_htmls(self):
        """ Тестирование корректности шаблонов html. """
        StaticURLTests.authorized_client.force_login(
            StaticURLTests.user_with_post)
        for url, html in self.urls_list.items():
            with self.subTest():
                response = StaticURLTests.authorized_client.get(url)
                self.assertTemplateNotUsed(
                    response,
                    html,
                    f"Неправильный шаблон у адреса '{url}")
