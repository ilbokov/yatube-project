import shutil
import tempfile

from django import forms
from django.conf import settings
from django.contrib.auth.models import User
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Comment, Follow, Group, Post


class ViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        """ Создание тестовых данных. """
        super().setUpClass()

        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-group',
            description='Описание тестовой группы'
        )
        cls.second_group = Group.objects.create(
            title='Вторая тестовая группа',
            slug='test-group2',
            description='Описание второй тестовой группы'
        )
        cls.creator = User.objects.create_user(username='creator')
        # Картинка для теста изображения
        # в контектсных словарях
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            text='Тестовый пост',
            author=cls.creator,
            group=cls.group,
            image=cls.uploaded
        )
        # Объявление статичных url
        cls.index_reverse = reverse('index')
        cls.new_post_reverse = reverse('new_post')
        cls.group_reverse = reverse('group', kwargs={'slug': cls.group.slug})
        cls.group_sec_reverse = reverse(
            'group',
            kwargs={'slug': cls.second_group.slug})
        cls.profile_reverse = reverse(
            'profile',
            kwargs={'username': cls.creator.username})
        cls.follow_reverse = reverse(
            'profile_follow',
            kwargs={'username': cls.creator.username})
        cls.unfollow_reverse = reverse(
            'profile_unfollow',
            kwargs={'username': cls.creator.username})
        cls.follow_index_reverse = reverse(
            'follow_index')
        cls.add_comment_reverse = reverse(
            'add_comment',
            kwargs={'username': cls.creator.username, 'post_id': cls.post.id}
        )

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        """ Создание тестовых клиентов - авторизованный и нет. """
        self.guest_client = Client()
        self.user = User.objects.create_user(username='test')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

        # Объявление зависимых url
        self.post_edit_reverse = reverse('post_edit', kwargs={
            'post_id': ViewsTests.post.id,
            'username': ViewsTests.creator.username})
        self.post_reverse = reverse('post', kwargs={
            'post_id': ViewsTests.post.id,
            'username': ViewsTests.creator.username})
        self.guest_add_comment = (
            "/auth/login/?next=/"
            f"{ViewsTests.creator.username}/"
            f"{ViewsTests.post.id}/comment")

    def test_pages_uses_correct_templates(self):
        """ Тест вывода корректных шаблонов для view-функций. """
        templates_pages_names = {
            'index.html': ViewsTests.index_reverse,
            'new_post.html': ViewsTests.new_post_reverse,
            'group.html': ViewsTests.group_reverse,
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_view(self):
        """ Тест контекстного словаря index и появления нового поста. """
        response = self.authorized_client.get(ViewsTests.index_reverse)
        first_object = response.context['page'][0]
        # Проверка появления нового поста на странице index
        self.assertEqual(first_object, ViewsTests.post)
        # Проверка количества постов в паджинаторе
        self.assertEqual(response.context['page'].paginator.per_page, 10)

    def test_group_view(self):
        """ Тест контекстного словаря group и появления нового поста. """
        response = self.authorized_client.get(
            ViewsTests.group_reverse)
        first_object = response.context['page'][0]
        current_group = response.context['group']
        # Проверка появления нового поста на странице группы
        self.assertEqual(first_object, self.post)
        # Проверка параметров поста из словаря context
        self.assertEqual(str(first_object.text), 'Тестовый пост')
        self.assertEqual(str(current_group), 'Тестовая группа')

        # Проверка того, что созданный пост не попал не в ту группу
        second_response = self.authorized_client.get(
            ViewsTests.group_sec_reverse)
        self.assertIsNot(second_response.context['page'], self.post)

    def test_new_post_view(self):
        """ Тест контекстного словаря new_post. """
        response = self.authorized_client.get(ViewsTests.new_post_reverse)
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_post_edit_view(self):
        """ Тест контекстного словаря edit_post. """
        self.authorized_client.force_login(ViewsTests.creator)
        response = self.authorized_client.get(
            self.post_edit_reverse)
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_profile_view(self):
        """ Тест вывода профиля пользователя. """
        response = self.authorized_client.get(
            ViewsTests.profile_reverse)
        user_profile = ViewsTests.creator
        count_posts = len(Post.objects.filter(author=user_profile))
        current_user = self.user
        self.assertEqual(response.context['current_user'], current_user)
        self.assertEqual(response.context['count_posts'], count_posts)

    def test_post_view(self):
        """ Тест вывода поста. """
        response = self.authorized_client.get(
            self.post_reverse)
        post = Post.objects.get()
        self.assertEqual(response.context['post'], post)
        self.assertEqual(response.context['post_id'], post.id)

    def test_image_views(self):
        """ Тест вывода картинки из поста на страницах. """
        # Тестирование словарей страниц
        # index, profile & group
        url_image_test = [
            ViewsTests.index_reverse,
            ViewsTests.profile_reverse,
            ViewsTests.group_reverse]
        for url in url_image_test:
            with self.subTest(url=url):
                response = self.authorized_client.get(
                    url)
                self.assertEqual(
                    response.context['page'].object_list[0].image,
                    ViewsTests.post.image)
        # Тестирование страницы поста
        response = self.authorized_client.get(
            self.post_reverse
        )
        self.assertEqual(
            response.context['post'].image,
            ViewsTests.post.image
        )

    def test_cache_index(self):
        """ Тест проверки кэша. """
        response = self.authorized_client.get(ViewsTests.index_reverse)
        page_first_response = response.content
        Post.objects.create(
            text='Тестовый пост 2',
            author=ViewsTests.creator,
            group=ViewsTests.group
        )
        response = self.authorized_client.get(ViewsTests.index_reverse)
        page_second_response = response.content
        # Проверка, что кэш не успел обновиться и содержимое
        # не изменилось
        self.assertEqual(
            page_first_response,
            page_second_response,
            'Кэш не отработал!')
        # После очистки кэша, содержимое должно поменяться
        cache.clear()
        response = self.authorized_client.get(ViewsTests.index_reverse)
        page_third_response = response.content
        self.assertIsNot(
            page_third_response,
            page_second_response,
            'Содержимое не поменялось!')

    def test_follow_unfollow(self):
        """ Тест системы подписок. """
        self.authorized_client.post(ViewsTests.follow_reverse)
        # Подписка оформлена
        self.assertTrue(
            Follow.objects.filter(
                user=self.user,
                author=ViewsTests.creator).exists())
        self.authorized_client.post(ViewsTests.unfollow_reverse)
        # Подписка отменена
        self.assertFalse(
            Follow.objects.filter(
                user=self.user,
                author=ViewsTests.creator).exists())

    def test_follow_index(self):
        """ Тест страницы подписок. """
        # Подписываемся на пользователя с постом
        self.authorized_client.post(ViewsTests.follow_reverse)
        response = self.authorized_client.get(ViewsTests.follow_index_reverse)
        # Проверяем, что пост появился в ленте
        self.assertIn(
            ViewsTests.post,
            response.context['page']
        )
        # Отписываеся от пользователя
        self.authorized_client.post(ViewsTests.unfollow_reverse)
        # Проверяем, что поста нет в ленте
        response = self.authorized_client.get(ViewsTests.follow_index_reverse)
        self.assertNotIn(
            ViewsTests.post,
            response.context['page'])

    def test_comment_post(self):
        """ Тест комментирования постов от авторизованного пользователя. """
        form_data = {'text': 'Тестовый комментарий!'}
        # Добавляем комментарий
        self.authorized_client.post(
            ViewsTests.add_comment_reverse,
            data=form_data,
            follow=True)
        # Проверяем, что он успешно добавлен
        self.assertTrue(
            Comment.objects.filter(
                author=self.user,
                post=ViewsTests.post
            ).exists())
        # Пытаемся добавить комментарий от гостя
        response = self.guest_client.post(
            ViewsTests.add_comment_reverse,
            data=form_data,
            follow=True
        )
        # Проверяем, что попали на страницу авторизации
        self.assertRedirects(
            response,
            self.guest_add_comment)
