import shutil
import tempfile

from django.conf import settings
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Group, Post


class FormsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        """ Создание тестовых данных. """
        super().setUpClass()

        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

        cls.user = User.objects.create_user(username='test')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-group',
            description='Описание тестовой группы'
        )
        cls.post = Post.objects.create(
            text='Проверка редактирования',
            author=FormsTests.user
        )
        # Объявление статичных url
        cls.new_post_reverse = reverse('new_post')
        # Картинка
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        """ Создание тестового клиента. """
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

        # Объявление зависимых url
        self.post_edit_reverse = reverse('post_edit', kwargs={
            'username': FormsTests.user.username,
            'post_id': FormsTests.post.id}
        )

    def test_edit_post(self):
        form_data = {
            'text': 'Отредактировано!'
        }

        self.authorized_client.post(
            self.post_edit_reverse,
            data=form_data,
            follow=True
        )
        # Проверка, что пост в базе только один
        self.assertEqual(Post.objects.count(), 1)
        # Проверка изменений
        FormsTests.post = Post.objects.get(pk=FormsTests.post.id)
        self.assertEqual(FormsTests.post.text, form_data['text'])

    def test_create_post(self):
        """ Тест создания поста. """
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Создание поста!',
            'group': 1,
            'image': FormsTests.uploaded
        }
        response = self.authorized_client.post(
            FormsTests.new_post_reverse,
            data=form_data,
            follow=True
        )
        # Проверка на редирект на главную страницу
        self.assertRedirects(response, reverse('index'))
        # Проверка на добавление нового поста
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text='Создание поста!',
                group=self.group,
                author=self.user
            ).exists()
        )
